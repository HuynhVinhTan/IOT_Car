from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.schemas.ai import AIStatus, SegmentAIStatus, SegmentPrediction

router = APIRouter(prefix="/api/ai", tags=["AI Inference"])


def _call_service_status(service: Any) -> Any | None:
    if service is None:
        return None

    get_status = getattr(service, "get_status", None)
    if callable(get_status):
        return get_status()

    status = getattr(service, "status", None)
    if callable(status):
        return status()

    return None


def _status_to_dict(status: Any) -> dict[str, Any]:
    if status is None:
        return {}

    if isinstance(status, dict):
        return status

    model_dump = getattr(status, "model_dump", None)
    if callable(model_dump):
        return model_dump()

    dict_method = getattr(status, "dict", None)
    if callable(dict_method):
        return dict_method()

    return {
        key: value
        for key, value in vars(status).items()
        if not key.startswith("_")
    }


def _is_service_ready(service: Any) -> bool:
    if service is None:
        return False

    is_ready = getattr(service, "is_ready", None)
    if callable(is_ready):
        return bool(is_ready())

    status_payload = _status_to_dict(_call_service_status(service))
    return bool(
        status_payload.get("model_loaded")
        or status_payload.get("ready")
        or status_payload.get("is_ready")
        or status_payload.get("status") == "READY"
    )


def _get_camera_connected(camera_service: Any) -> bool:
    if camera_service is None:
        return False

    get_status = getattr(camera_service, "get_status", None)
    if not callable(get_status):
        return False

    camera_status = get_status()
    if not isinstance(camera_status, dict):
        return False

    return bool(
        camera_status.get("connected")
        or camera_status.get("camera_connected")
    )


def _get_remote_camera_connected(state: Any) -> bool:
    hub = getattr(state, "camera_frame_hub", None)
    if hub is None:
        return False
    
    # Check all cameras in the hub
    for cid, state_obj in hub._states.items():
        status_payload = hub.get_status(cid)
        if status_payload.get("publisher_connected") and status_payload.get("status") == "READY":
            return True
    return False


def _fallback_segment_status() -> SegmentAIStatus:
    return SegmentAIStatus(
        status="NOT_READY",
        model_loaded=False,
        message="Map segment AI service is not initialized or no segment model is trained.",
    )


def _coerce_segment_status(raw_status: Any) -> SegmentAIStatus:
    if isinstance(raw_status, SegmentAIStatus):
        return raw_status

    payload = _status_to_dict(raw_status)

    if not payload:
        return _fallback_segment_status()

    payload.setdefault("status", "READY" if payload.get("model_loaded") else "NOT_READY")
    payload.setdefault("model_loaded", False)
    payload.setdefault("message", "Map segment AI status inquiry successful.")

    return SegmentAIStatus(**payload)


@router.get("/status", response_model=AIStatus)
async def get_ai_status(request: Request) -> AIStatus:
    state = request.app.state

    camera_service = getattr(state, "camera_service", None)
    segment_ai_service = getattr(state, "map_segment_ai_service", None)
    face_recognition_service = getattr(state, "face_recognition_service", None)
    person_detection_service = getattr(state, "person_detection_service", None)

    segment_status = _coerce_segment_status(
        _call_service_status(segment_ai_service)
    )

    segment_model_loaded = bool(segment_status.model_loaded)
    face_model_loaded = _is_service_ready(face_recognition_service)
    person_detector_loaded = _is_service_ready(person_detection_service)

    any_ai_ready = (
        segment_model_loaded
        or face_model_loaded
        or person_detector_loaded
    )

    return AIStatus(
        status="READY" if any_ai_ready else "NOT_READY",
        camera_connected=_get_remote_camera_connected(state) or _get_camera_connected(camera_service),
        segment_model_loaded=segment_model_loaded,
        face_model_loaded=face_model_loaded,
        dataset_ready=segment_model_loaded,
        message=(
            "AI services are available."
            if any_ai_ready
            else "AI services are initialized, but no real model/provider is ready yet."
        ),
    )


@router.get("/map-segment/status", response_model=SegmentAIStatus)
async def get_segment_status(request: Request) -> SegmentAIStatus:
    service = getattr(request.app.state, "map_segment_ai_service", None)

    if service is None:
        return _fallback_segment_status()

    return _coerce_segment_status(_call_service_status(service))


@router.post("/map-segment/predict", response_model=SegmentPrediction)
async def predict_segment(request: Request) -> SegmentPrediction:
    service = getattr(request.app.state, "map_segment_ai_service", None)

    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Map segment AI service is not initialized.",
        )

    is_ready = getattr(service, "is_ready", None)
    if callable(is_ready) and not is_ready():
        raise HTTPException(
            status_code=503,
            detail="Map segment model is not ready. Please train/load a model first.",
        )

    predict = getattr(service, "predict", None)
    if not callable(predict):
        raise HTTPException(
            status_code=503,
            detail="Map segment prediction is not available.",
        )

    return predict()
