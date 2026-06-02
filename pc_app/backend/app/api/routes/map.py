from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("")
def get_map_state(request: Request) -> dict:
    return request.app.state.localization_service.snapshot()
