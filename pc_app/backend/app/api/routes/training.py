from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.training import (
    TrainingSession, 
    TrainingSessionStartRequest, 
    TrainingSample,
    TrainingExportRequest,
    TrainingStatus
)
from app.services.training_session_service import TrainingSessionService
from app.services.training_sample_service import TrainingSampleService

router = APIRouter(prefix="/api/training", tags=["AI Training"])


def _session_to_schema(session) -> TrainingSession:
    return TrainingSession(
        session_id=str(session.id),
        session_name=session.session_name,
        map_id=session.map_id,
        segment_id=session.segment_id,
        direction=session.direction,
        start_node=session.start_node,
        target_node=session.target_node,
        status=session.status,
        record_camera=session.record_camera,
        sample_count=session.sample_count,
        created_at_ms=int(session.created_at.timestamp() * 1000),
        stopped_at_ms=(
            int(session.stopped_at.timestamp() * 1000)
            if getattr(session, "stopped_at", None)
            else None
        ),
        output_dir=getattr(session, "output_dir", "") or "",
        notes=session.notes,
    )


@router.post("/sessions/start", response_model=TrainingSession)
async def start_session(req: TrainingSessionStartRequest, db: AsyncSession = Depends(get_db)):
    service = TrainingSessionService(db)
    try:
        session = await service.start_session(req)
        return _session_to_schema(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/stop", response_model=TrainingSession)
async def stop_session(db: AsyncSession = Depends(get_db)):
    service = TrainingSessionService(db)
    session = await service.stop_session()
    if not session:
        raise HTTPException(status_code=404, detail="No active recording session")
    
    return _session_to_schema(session)

@router.get("/sessions/current", response_model=TrainingSession)
async def get_current_session(db: AsyncSession = Depends(get_db)):
    service = TrainingSessionService(db)
    session = await service.get_current_session()
    if not session:
        raise HTTPException(status_code=404, detail="No active session")
    return _session_to_schema(session)

@router.post("/samples", response_model=TrainingSample)
async def record_sample(request: Request, db: AsyncSession = Depends(get_db)):
    state = request.app.state
    telemetry_service = getattr(state, "telemetry_service", None)
    joystick_service = getattr(state, "joystick_service", None)
    camera_service = getattr(state, "camera_service", None)

    if telemetry_service is None or joystick_service is None or camera_service is None:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "NOT_READY",
                "message": "Training dependencies are not initialized",
            },
        )

    session_service = TrainingSessionService(db)
    sample_service = TrainingSampleService(
        db, session_service, telemetry_service, joystick_service, camera_service
    )
    
    sample = await sample_service.record_sample()
    if not sample:
        raise HTTPException(status_code=400, detail="No active session to record sample")
    
    return TrainingSample(
        sample_id=str(sample.id),
        session_id=str(sample.session_id),
        timestamp_ms=sample.timestamp_ms,
        segment_id=sample.segment_id,
        direction=sample.direction,
        current_node=sample.current_node,
        target_node=sample.target_node,
        joystick_x=sample.joystick_x,
        joystick_y=sample.joystick_y,
        left_motor_speed=sample.left_motor_speed,
        right_motor_speed=sample.right_motor_speed,
        front_distance_cm=sample.front_distance_cm,
        left_distance_cm=sample.left_distance_cm,
        right_distance_cm=sample.right_distance_cm,
        rear_distance_cm=sample.rear_distance_cm,
        forward_unsafe=sample.forward_unsafe,
        backward_unsafe=sample.backward_unsafe,
        object_found=sample.object_found,
        notes=sample.notes,
    )

@router.get("/status", response_model=TrainingStatus)
async def get_status(db: AsyncSession = Depends(get_db)):
    service = TrainingSessionService(db)
    try:
        session = await service.get_current_session()
    except SQLAlchemyError as exc:
        return TrainingStatus(
            status="NOT_READY",
            current_session_id=None,
            sample_count=0,
            dataset_ready=False,
            message=f"Training database is not ready: {exc.__class__.__name__}",
        )

    return TrainingStatus(
        status=session.status if session else "IDLE",
        current_session_id=str(session.id) if session else None,
        sample_count=session.sample_count if session else 0,
        dataset_ready=bool(session and session.sample_count > 0),
        message="Database recording is active" if session else "No active recording session"
    )
