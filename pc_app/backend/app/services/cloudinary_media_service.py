import os
import uuid
from typing import Optional, Any, cast, BinaryIO
from dataclasses import dataclass

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.loggers import logger

import cloudinary
import cloudinary.uploader


@dataclass
class MediaUploadResult:
    provider: str
    public_id: Optional[str]
    secure_url: str
    resource_type: str = "image"
    folder: Optional[str] = None
    format: Optional[str] = None
    bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_filename: Optional[str] = None


class CloudinaryMediaService:
    def __init__(self):
        self.enabled = settings.cloudinary_enabled

        if not self.enabled:
            return

        if (
            not settings.cloudinary_cloud_name
            or not settings.cloudinary_api_key
            or not settings.cloudinary_api_secret
        ):
            logger.warning(
                "Cloudinary configured as ENABLED but missing credentials. Falling back to local."
            )
            self.enabled = False
            return

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )

    def is_enabled(self) -> bool:
        return self.enabled

    @staticmethod
    def upload_image_to_cloudinary(
        upload_source: BinaryIO,
        *,
        upload_folder: str,
        public_id: str | None = None,
    ) -> dict[str, Any]:
        upload_options: dict[str, Any] = {
            "folder": upload_folder,
            "resource_type": "image",
        }

        if public_id:
            upload_options["public_id"] = public_id

        upload_response = cloudinary.uploader.upload(
            upload_source,
            **upload_options,
        )

        return cast(dict[str, Any], upload_response)

    async def upload_image(
        self,
        uploaded_file: UploadFile,
        folder: str,
        filename: Optional[str] = None,
    ) -> MediaUploadResult:
        if not self.enabled:
            return await self._upload_local(uploaded_file.file, folder, filename)

        try:
            uploaded_file.file.seek(0)

            upload_result = await run_in_threadpool(
                self.upload_image_to_cloudinary,
                uploaded_file.file,
                upload_folder=f"{settings.cloudinary_upload_folder}/{folder}",
                public_id=filename,
            )

            return MediaUploadResult(
                provider="cloudinary",
                public_id=upload_result.get("public_id"),
                secure_url=upload_result.get("secure_url"),
                resource_type=upload_result.get("resource_type", "image"),
                folder=upload_result.get("folder"),
                format=upload_result.get("format"),
                bytes=upload_result.get("bytes"),
                width=upload_result.get("width"),
                height=upload_result.get("height"),
                original_filename=filename,
            )

        except Exception as exc:
            logger.warning(f"Cloudinary upload failed: {exc}. Falling back to local.")
            return await self._upload_local(uploaded_file.file, folder, filename)

    async def _upload_local(
        self,
        file_stream: BinaryIO,
        folder: str,
        filename: Optional[str] = None,
    ) -> MediaUploadResult:
        return await run_in_threadpool(
            self._upload_local_sync,
            file_stream,
            folder,
            filename,
        )

    @staticmethod
    def _upload_local_sync(
        file_stream: BinaryIO,
        folder: str,
        filename: Optional[str] = None,
    ) -> MediaUploadResult:
        if not settings.local_media_fallback_enabled:
            raise RuntimeError("Media upload failed and local fallback is disabled.")

        local_dir = os.path.join(settings.local_media_root, folder)
        os.makedirs(local_dir, exist_ok=True)

        stored_filename = filename or f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(local_dir, stored_filename)

        file_stream.seek(0)
        content = file_stream.read()

        with open(file_path, "wb") as output_file:
            output_file.write(content)

        relative_url = f"/static/media/{folder}/{stored_filename}"

        return MediaUploadResult(
            provider="local_dev",
            public_id=None,
            secure_url=relative_url,
            resource_type="image",
            folder=folder,
            original_filename=stored_filename,
            bytes=len(content),
        )

    async def delete_asset(self, public_id: str) -> bool:
        if not self.enabled:
            return False

        try:
            result = await run_in_threadpool(
                cloudinary.uploader.destroy,
                public_id,
            )
            return result.get("result") == "ok"

        except Exception as exc:
            logger.warning(f"Cloudinary delete failed: {exc}")
            return False