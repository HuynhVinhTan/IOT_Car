from dataclasses import dataclass
from fastapi import HTTPException, UploadFile, status

MAX_IMAGE_BYTES = 5 * 1024 * 1024

@dataclass(frozen=True)
class UploadedBinary:
    content: bytes
    filename: str | None
    content_type: str | None
    size: int

async def read_upload_file_bytes(
    upload: UploadFile,
    *,
    allowed_content_prefixes: tuple[str, ...] = ("image/",),
    max_bytes: int = MAX_IMAGE_BYTES,
) -> UploadedBinary:
    if not upload.content_type or not upload.content_type.startswith(allowed_content_prefixes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {upload.content_type}. Allowed: {allowed_content_prefixes}"
        )
    
    content = await upload.read()
    size = len(content)
    
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded image is empty."
        )
        
    if size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {max_bytes} bytes"
        )
        
    await upload.seek(0)
    
    return UploadedBinary(
        content=content,
        filename=upload.filename,
        content_type=upload.content_type,
        size=size
    )