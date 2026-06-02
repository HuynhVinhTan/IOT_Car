from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/navigation", tags=["navigation"])


class LocationRequest(BaseModel):
    current_node: str | None = None
    home_node: str | None = None
    target_node: str | None = None


@router.get("/map")
def get_map(request: Request) -> dict:
    return request.app.state.localization_service.snapshot()


@router.post("/location")
def set_location(request: Request, location_request: LocationRequest) -> dict:
    return request.app.state.localization_service.update_location(
        current_node=location_request.current_node,
        home_node=location_request.home_node,
        target_node=location_request.target_node,
    )
