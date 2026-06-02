from fastapi import APIRouter, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.vision import VisionAnalysisResult
from app.services.camera_frame_hub import CameraFrameHub

router = APIRouter(tags=["camera-stream"])


def _get_hub(request_or_websocket: Request | WebSocket) -> CameraFrameHub:
    hub = getattr(request_or_websocket.app.state, "camera_frame_hub", None)
    if hub is None:
        raise RuntimeError("Camera frame hub is not initialized")
    return hub


@router.websocket("/ws/cameras/{camera_id}/publish")
async def publish_camera_frames(
    websocket: WebSocket,
    camera_id: str,
    token: str | None = None,
) -> None:
    settings = websocket.app.state.settings
    if token != settings.camera_publish_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="invalid camera token")
        return

    hub = _get_hub(websocket)
    await websocket.accept()
    await hub.register_publisher(camera_id, websocket)
    await hub.broadcast_status(camera_id, "Camera publisher connected")

    try:
        while True:
            message = await websocket.receive()
            frame_bytes = message.get("bytes")
            text_message = message.get("text")

            if frame_bytes is not None:
                result = await hub.handle_frame(camera_id, frame_bytes)
                if not result["accepted"] and result["reason"] == "FRAME_TOO_LARGE":
                    await websocket.close(code=1009, reason="camera frame too large")
                    return
                continue

            if text_message is not None:
                await hub.handle_heartbeat(camera_id)
    except WebSocketDisconnect:
        pass
    except RuntimeError:
        pass
    finally:
        await hub.unregister_publisher(camera_id, websocket)


@router.websocket("/ws/cameras/{camera_id}/view")
async def view_camera_frames(websocket: WebSocket, camera_id: str) -> None:
    hub = _get_hub(websocket)
    await websocket.accept()
    registered = await hub.register_viewer(camera_id, websocket)
    if not registered:
        await websocket.send_json(
            {
                "type": "camera_status",
                "camera_id": camera_id,
                "status": "VIEWER_LIMIT_REACHED",
                "message": "Too many camera viewers are connected",
            }
        )
        await websocket.close(code=1013, reason="too many camera viewers")
        return

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.unregister_viewer(camera_id, websocket)
    except RuntimeError:
        hub.unregister_viewer(camera_id, websocket)


@router.get("/api/cameras/{camera_id}/status")
async def camera_stream_status(request: Request, camera_id: str) -> dict:
    try:
        hub = _get_hub(request)
    except RuntimeError:
        return {
            "camera_id": camera_id,
            "status": "NOT_READY",
            "publisher_connected": False,
            "viewer_count": 0,
            "message": "Camera frame hub is not initialized",
        }
    return hub.get_status(camera_id)


@router.get("/api/cameras/{camera_id}/latest-frame")
async def latest_camera_frame(request: Request, camera_id: str) -> Response:
    try:
        hub = _get_hub(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    frame = hub.get_latest_frame(camera_id)
    if frame is None:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "CAMERA_NOT_READY",
                "message": "No camera frame is available yet",
            },
        )

    return Response(content=frame, media_type="image/jpeg")


@router.post("/api/cameras/{camera_id}/analyze-latest", response_model=VisionAnalysisResult)
async def analyze_latest_camera_frame(
    request: Request,
    camera_id: str,
    db: AsyncSession = Depends(get_db),
) -> VisionAnalysisResult:
    hub = _get_hub(request)
    frame = hub.get_latest_frame(camera_id)
    if frame is None:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "CAMERA_NOT_READY",
                "message": "No camera frame is available yet",
            },
        )

    pipeline = getattr(request.app.state, "vision_pipeline_service", None)
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "NOT_READY",
                "message": "Vision pipeline service is not initialized",
            },
        )

    return await pipeline.analyze_frame(
        db=db,
        image_bytes=frame,
        source=f"camera_ws:{camera_id}",
    )
