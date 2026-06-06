import pytest
from fastapi import UploadFile, HTTPException
from io import BytesIO
from app.utils.upload_file_utils import read_upload_file_bytes

@pytest.mark.asyncio
async def test_upload_valid_image():
    content = b"fake_jpeg_content"
    file = BytesIO(content)
    upload = UploadFile(filename="test.jpg", file=file)
    upload.headers = {"content-type": "image/jpeg"}
    
    result = await read_upload_file_bytes(upload)
    assert result.content == content
    assert result.filename == "test.jpg"
    assert result.content_type == "image/jpeg"
    assert result.size == len(content)

@pytest.mark.asyncio
async def test_upload_empty_file():
    upload = UploadFile(filename="empty.jpg", file=BytesIO(b""))
    upload.headers = {"content-type": "image/jpeg"}
    
    with pytest.raises(HTTPException) as exc:
        await read_upload_file_bytes(upload)
    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_upload_invalid_content_type():
    upload = UploadFile(filename="test.txt", file=BytesIO(b"hello"))
    upload.headers = {"content-type": "text/plain"}
    
    with pytest.raises(HTTPException) as exc:
        await read_upload_file_bytes(upload)
    assert exc.value.status_code == 400
    assert "Invalid content type" in exc.value.detail

@pytest.mark.asyncio
async def test_upload_file_too_large():
    content = b"0" * (5 * 1024 * 1024 + 1) # > 5MB
    upload = UploadFile(filename="big.jpg", file=BytesIO(content))
    upload.headers = {"content-type": "image/jpeg"}
    
    with pytest.raises(HTTPException) as exc:
        await read_upload_file_bytes(upload)
    assert exc.value.status_code == 400
    assert "too large" in exc.value.detail.lower() or "exceeds" in exc.value.detail.lower()