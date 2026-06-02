import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    ai,
    auto,
    camera,
    camera_ws,
    car,
    detection,
    faces,
    health,
    joystick,
    joystick_alert,
    map,
    mission,
    navigation,
    path_record,
    route_segments,
    telemetry,
    training,
)
from app.core.config import settings
from app.core.loggers import logger
from app.navigation.coverage_planner import CoveragePlanner
from app.navigation.localization_service import LocalizationService
from app.navigation.map_graph import MapGraph
from app.navigation.mission_service import MissionService
from app.navigation.path_planner import PathPlanner
from app.serial_comm.car_serial_client import CarSerialClient
from app.serial_comm.joystick_serial_client import JoystickSerialClient
from app.services.camera_service import CameraService
from app.services.camera_frame_hub import CameraFrameHub
from app.services.car_control_service import CarControlService
from app.services.detection_service import DetectionService
from app.services.face_recognition_service import FaceRecognitionService
from app.services.joystick_service import JoystickService
from app.services.map_segment_ai_service import MapSegmentAIService
from app.services.person_detection_service import PersonDetectionService
from app.services.remote_control_service import RemoteControlService
from app.services.route_segment_service import RouteSegmentService
from app.services.telemetry_service import TelemetryService
from app.services.vision_pipeline_service import VisionPipelineService
from app.websocket.connection_manager import ConnectionManager
from app.services.safety_gate_service import SafetyGateService


# Shared singleton services: hardware, navigation, telemetry, AI state
connection_manager = ConnectionManager()
telemetry_service = TelemetryService()
camera_service = CameraService(settings)
camera_frame_hub = CameraFrameHub(
    max_frame_bytes=settings.max_camera_frame_bytes,
    max_fps=settings.camera_publish_max_fps,
    offline_timeout_seconds=settings.camera_offline_timeout_seconds,
    max_viewers_per_camera=settings.max_camera_viewers_per_camera,
    viewer_send_timeout_seconds=settings.camera_viewer_send_timeout_seconds,
)
safety_gate_service = SafetyGateService(telemetry_service, settings)
map_segment_ai_service = MapSegmentAIService()

map_graph = MapGraph()
localization_service = LocalizationService(map_graph)
path_planner = PathPlanner(map_graph)
coverage_planner = CoveragePlanner(map_graph)

car_serial_client = CarSerialClient(
    settings.car_esp32_serial_port,
    settings.serial_baud_rate,
)
joystick_serial_client = JoystickSerialClient(
    settings.joystick_esp8266_serial_port,
    settings.serial_baud_rate,
)

car_control_service = CarControlService(
    car_serial_client,
    telemetry_service,
    safety_gate_service,
    settings,
)
remote_control_service = RemoteControlService(
    car_control_service,
    telemetry_service,
    settings,
)
route_segment_service = RouteSegmentService(
    map_graph,
    localization_service,
    telemetry_service,
    car_control_service,
)
joystick_service = JoystickService(
    telemetry_service,
    car_control_service,
    joystick_serial_client,
    remote_control_service,
    route_segment_service,
)
mission_service = MissionService(
    localization_service,
    path_planner,
    coverage_planner,
    car_control_service,
)

# AI & detection services
# DB-related work should still receive sessions from route dependencies when needed.
detection_service = DetectionService(
    car_control_service,
    joystick_service,
    settings,
)
detection_service.set_mission_service(mission_service)

person_detection_service = PersonDetectionService()
face_recognition_service = FaceRecognitionService(None)

from app.services.robot_decision_service import RobotDecisionService

robot_decision_service = RobotDecisionService(
    car_control_service,
    settings
)

vision_pipeline_service = VisionPipelineService(
    person_detection_service,
    face_recognition_service,
    detection_service,
    robot_decision_service
)


async def remote_safety_watchdog() -> None:
    while True:
        joystick_online = telemetry_service.joystick_connected(
            settings.joystick_offline_timeout_seconds
        )

        latest_car_telemetry = telemetry_service.latest_car_telemetry
        is_manual_remote_mode = (
            latest_car_telemetry is not None
            and latest_car_telemetry.get("mode") == "MANUAL_REMOTE"
        )

        if not joystick_online and is_manual_remote_mode:
            try:
                car_control_service.send_command({"command": "REMOTE_STOP"})
            except Exception:
                # Keep watchdog alive even if the serial command fails.
                pass

        await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    event_loop = asyncio.get_running_loop()

    def on_car_message(message: dict[str, Any]) -> None:
        if message.get("type") == "car_telemetry":
            mission_service.handle_search_progress()
            message = localization_service.enrich_car_telemetry(message)
            message["mission_state"] = mission_service.snapshot()

        telemetry_service.update_car_message(message)

        asyncio.run_coroutine_threadsafe(
            connection_manager.broadcast_json(message),
            event_loop,
        )

    def on_joystick_message(message: dict[str, Any]) -> None:
        joystick_service.handle_joystick_message(message)

        asyncio.run_coroutine_threadsafe(
            connection_manager.broadcast_json(message),
            event_loop,
        )

    await asyncio.to_thread(car_serial_client.start, on_car_message)
    await asyncio.to_thread(joystick_serial_client.start, on_joystick_message)

    watchdog_task = asyncio.create_task(remote_safety_watchdog())
    app.state.remote_safety_watchdog_task = watchdog_task

    try:
        yield
    finally:
        watchdog_task.cancel()

        with suppress(asyncio.CancelledError):
            await watchdog_task

        car_stop = getattr(car_serial_client, "stop", None)
        if callable(car_stop):
            await asyncio.to_thread(car_stop)

        joystick_stop = getattr(joystick_serial_client, "stop", None)
        if callable(joystick_stop):
            await asyncio.to_thread(joystick_stop)


app = FastAPI(
    title="Smart Car Backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Export singletons for routes to access through request.app.state
app.state.settings = settings
app.state.telemetry_service = telemetry_service
app.state.localization_service = localization_service
app.state.car_control_service = car_control_service
app.state.remote_control_service = remote_control_service
app.state.joystick_service = joystick_service
app.state.camera_service = camera_service
app.state.camera_frame_hub = camera_frame_hub
app.state.mission_service = mission_service
app.state.route_segment_service = route_segment_service
app.state.connection_manager = connection_manager
app.state.face_recognition_service = face_recognition_service
app.state.person_detection_service = person_detection_service
app.state.detection_service = detection_service
app.state.vision_pipeline_service = vision_pipeline_service
app.state.robot_decision_service = robot_decision_service
app.state.safety_gate_service = safety_gate_service
app.state.map_segment_ai_service = map_segment_ai_service


app.include_router(health.router)
app.include_router(car.router)
app.include_router(joystick.router)
app.include_router(joystick_alert.router)
app.include_router(map.router)
app.include_router(mission.router)
app.include_router(navigation.router)
app.include_router(telemetry.router)
app.include_router(detection.router)
app.include_router(camera.router)
app.include_router(camera_ws.router)
app.include_router(path_record.router)
app.include_router(auto.router)
app.include_router(route_segments.router)
app.include_router(training.router)
app.include_router(ai.router)
app.include_router(faces.router)


@app.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket) -> None:
    await connection_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

@app.websocket("/ws/car")
async def websocket_car_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger("Car connected via WebSocket")
    
    # Setup command push
    async def send_to_car(payload: dict):
        try:
            await websocket.send_json(payload)
        except Exception:
            pass
            
    # Link car control service to this websocket
    # Note: For simplicity in MVP, we assume only one car connects
    app.state.car_control_service.set_command_callback(
        lambda p: asyncio.create_task(send_to_car(p))
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming telemetry/events from car
            if data.get("type") == "car_telemetry":
                app.state.telemetry_service.update_telemetry(data)
                # Broadcast to dashboard
                await app.state.connection_manager.broadcast_json(data)
            elif data.get("type") == "car_event":
                # Log or handle events
                await app.state.connection_manager.broadcast_json(data)
    except WebSocketDisconnect:
        logger("Car disconnected")
        app.state.car_control_service.set_command_callback(None)
    except Exception as e:
        logger(f"Car WS Error: {e}")
        app.state.car_control_service.set_command_callback(None)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
