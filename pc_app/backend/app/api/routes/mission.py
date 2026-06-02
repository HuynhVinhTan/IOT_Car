from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/mission", tags=["mission"])


@router.get("")
def get_mission_state(request: Request) -> dict:
    return request.app.state.mission_service.snapshot()


@router.post("/auto-search/start")
def start_auto_search(request: Request) -> dict:
    return request.app.state.mission_service.start_auto_search()


@router.post("/stop")
def stop_mission(request: Request) -> dict:
    return request.app.state.mission_service.stop_mission()


@router.post("/return-home")
def return_home(request: Request) -> dict:
    return request.app.state.mission_service.return_home()

from pydantic import BaseModel
class StartSearchBody(BaseModel):
    start_node: str = "A"
    target_node: str = "F"

@router.post("/search/start")
def start_search(request: Request, body: StartSearchBody) -> dict:
    return request.app.state.mission_service.start_search(start_node=body.start_node, target_node=body.target_node)

class MockDetectionBody(BaseModel):
    found: bool

@router.post("/search/mock-detection")
def mock_detection(request: Request, body: MockDetectionBody) -> dict:
    return request.app.state.mission_service.trigger_mock_detection(found=body.found)
