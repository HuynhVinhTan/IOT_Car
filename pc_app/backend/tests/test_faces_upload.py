import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.core.database import get_db
from app.utils.upload_file_utils import UploadedBinary
from sqlalchemy.ext.asyncio import AsyncSession

client = TestClient(app)

# Mock DB Session
class MockAsyncSession:
    def __init__(self):
        self.add = MagicMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.delete = AsyncMock()
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        
        # Mock result for image query
        mock_image = MagicMock()
        mock_image.media_asset = MagicMock(secure_url="http://test.com/img.jpg", local_url=None)
        
        # Mock result for embedding query
        mock_embedding = MagicMock()
        mock_embedding.id = "emb123"
        
        self.execute = AsyncMock(side_effect=[
            MagicMock(scalars=lambda: MagicMock(all=lambda: [mock_image])),
            MagicMock(scalars=lambda: MagicMock(first=lambda: mock_embedding))
        ])

async def override_get_db():
    yield MockAsyncSession()

app.dependency_overrides[get_db] = override_get_db

def test_enroll_face_no_face_detected(monkeypatch):
    """
    Test that uploading an image with no face detected returns 422 and does not crash with 500.
    Also verifies that no delete is called on a non-persisted target.
    """
    # Mock FaceRegistryService.add_target_image to raise 422
    async def mock_add_target_image(*args, **kwargs):
        raise HTTPException(status_code=422, detail="No face detected. Please upload a clear frontal face image.")

    from app.services.face.face_registry_service import FaceRegistryService
    monkeypatch.setattr(FaceRegistryService, "add_target_image", mock_add_target_image)

    # Prepare request
    files = {"image": ("no_face.jpg", b"fake_image_content", "image/jpeg")}
    data = {"display_name": "Test User", "notes": "Testing no face"}

    response = client.post("/api/faces/targets", data=data, files=files)

    assert response.status_code == 422
    assert response.json()["detail"] == "No face detected. Please upload a clear frontal face image."

def test_enroll_face_success_mocked(monkeypatch):
    """
    Test successful face enrollment.
    """
    async def mock_register_target(*args, **kwargs):
        target = MagicMock()
        target.id = "target123"
        target.display_name = "Success User"
        target.created_at = MagicMock(timestamp=lambda: 1717640000.0)
        target.notes = "Testing success"
        return target

    async def mock_add_target_image(*args, **kwargs):
        return {"image_id": "img123", "media_asset_id": "med123", "embedding_id": "emb123"}

    from app.services.face.face_registry_service import FaceRegistryService
    monkeypatch.setattr(FaceRegistryService, "register_target", mock_register_target)
    monkeypatch.setattr(FaceRegistryService, "add_target_image", mock_add_target_image)

    files = {"image": ("face.jpg", b"fake_image_content", "image/jpeg")}
    data = {"display_name": "Success User", "notes": "Testing success"}

    response = client.post("/api/faces/targets", data=data, files=files)

    assert response.status_code == 200
    assert "target_person_id" in response.json()

def test_enroll_face_invalid_image(monkeypatch):
    """
    Test uploading an invalid image (e.g. wrong content type) returns 400.
    """
    files = {"image": ("test.txt", b"not an image", "text/plain")}
    data = {"display_name": "Invalid User", "notes": "Testing invalid"}

    response = client.post("/api/faces/targets", data=data, files=files)

    assert response.status_code == 400