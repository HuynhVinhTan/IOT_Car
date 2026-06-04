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
    map,
    mission,
    navigation,
    path_record,
    robot,
    route_segments,
    telemetry,
)
from app.core.config import settings
from app.core.loggers import logger
from app.core.database import AsyncSessionLocal
from app.services.camera_service import CameraService
from app.services.camera_frame_hub import CameraFrameHub
from app.services.face.face_recognition_service import FaceRecognitionService
from app.services.robot.robot_mode_service import RobotModeService
from app.services.robot.telemetry_service import TelemetryService
from app.websocket.connection_manager import ConnectionManager
from app.services.robot.safety_gate_service import SafetyGateService
from app.services.robot.car_control_service import CarControlService


# Shared singleton services: hardware, navigation, telemetry, AI state
connection_manager = ConnectionManager()
telemetry_service = TelemetryService()
robot_mode_service = RobotModeService()
camera_service = CameraService(settings)
camera_frame_hub = CameraFrameHub(
    max_frame_bytes=settings.max_camera_frame_bytes,
    max_fps=settings.camera_publish_max_fps,
    offline_timeout_seconds=settings.camera_offline_timeout_seconds,
    max_viewers_per_camera=settings.max_camera_viewers_per_camera,
    viewer_send_timeout_seconds=settings.camera_viewer_send_timeout_seconds,
)
safety_gate_service = SafetyGateService(telemetry_service, settings)

# Lazy-loaded services
face_recognition_service = FaceRecognitionService(None)

# Optional/Deferred services
map_segment_ai_service = None
map_graph = None
localization_service = None
path_planner = None
coverage_planner = None
car_serial_client = None
joystick_serial_client = None
car_control_service = None
remote_control_service = None
route_segment_service = None
joystick_service = None
mission_service = None
detection_service = None
person_detection_service = None
robot_decision_service = None
vision_pipeline_service = None

if settings.enable_robot_control:
    from app.navigation.map_graph import MapGraph
    from app.navigation.localization_service import LocalizationService
    from app.navigation.path_planner import PathPlanner
    from app.navigation.coverage_planner import CoveragePlanner
    from app.serial_comm.car_serial_client import CarSerialClient
    from app.serial_comm.joystick_serial_client import JoystickSerialClient
    from app.services.route_segment_service import RouteSegmentService
    from app.services.robot.joystick_service import JoystickService
    from app.services.robot.remote_control_service import RemoteControlService
    from app.navigation.mission_service import MissionService
    from app.services.vision.detection_service import DetectionService
    from app.services.robot.robot_decision_service import RobotDecisionService
    from app.services.vision.vision_pipeline_service import VisionPipelineService
    from app.services.map_segment_ai_service import MapSegmentAIService

    map_graph = MapGraph()
    localization_service = LocalizationService(map_graph)
    path_planner = PathPlanner(map_graph)
    coverage_planner = CoveragePlanner(map_graph)
    map_segment_ai_service = MapSegmentAIService()
    car_serial_client = CarSerialClient(settings.car_esp32_serial_port, settings.serial_baud_rate)
    joystick_serial_client = JoystickSerialClient(settings.joystick_esp8266_serial_port, settings.serial_baud_rate)
    car_control_service = CarControlService(car_serial_client, telemetry_service, safety_gate_service, settings)
    remote_control_service = RemoteControlService(car_control_service, telemetry_service, settings)
    route_segment_service = RouteSegmentService(map_graph, localization_service, telemetry_service, car_control_service)
    joystick_service = JoystickService(telemetry_service, car_control_service, joystick_serial_client, remote_control_service, route_segment_service)
    mission_service = MissionService(localization_service, path_planner, coverage_planner, car_control_service)
    detection_service = DetectionService(car_control_service, joystick_service, settings)
    detection_service.set_mission_service(mission_service)
    robot_decision_service = RobotDecisionService(car_control_service, settings)

if getattr(settings, "enable_person_detection", False):
    from app.services.vision.person_detection_service import PersonDetectionService
    person_detection_service = PersonDetectionService()
    if robot_decision_service:
        vision_pipeline_service = VisionPipelineService(person_detection_service, face_recognition_service, detection_service, robot_decision_service)


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
    # 1. Build Face Recognition Cache
    try:
        async with AsyncSessionLocal() as session:
            logger("Building face recognition cache...")
            await face_recognition_service.build_cache(session)
            logger("Face recognition cache built successfully.")
    except Exception as e:
        logger(f"Error building face cache: {e}")
    
    # 2. Initialize Person Detection (Lazy Load)
    if settings.enable_person_detection and person_detection_service:
        try:
            logger("Initializing YOLO model...")
            await asyncio.to_thread(person_detection_service.initialize)
            logger("YOLO model initialized.")
        except Exception as e:
            logger(f"Error initializing YOLO: {e}")

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

    # 2. Start Vision Worker Loop
    async def vision_worker():
        while True:
            try:
                frame = camera_frame_hub.get_latest_frame("default")
                if frame:
                    result = await vision_pipeline_service.analyze_frame(
                        db=None, image_bytes=frame
                    )
                    await connection_manager.broadcast_json({
                        "type": "target_tracking_result",
                        **result.dict()
                    })
            except Exception as e:
                logger(f"Vision worker error: {e}")
            await asyncio.sleep(0.2) # 5 FPS

    vision_task = asyncio.create_task(vision_worker())

    # 3. Start Robot Hardware (Conditional)
    watchdog_task = None
    if settings.enable_robot_control:
        await asyncio.to_thread(car_serial_client.start, on_car_message)
        await asyncio.to_thread(joystick_serial_client.start, on_joystick_message)
        watchdog_task = asyncio.create_task(remote_safety_watchdog())
        app.state.remote_safety_watchdog_task = watchdog_task
    else:
        logger("Robot control disabled. Skipping serial clients and watchdog.")

    try:
        yield
    finally:
        if watchdog_task:
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
app.state.robot_mode_service = robot_mode_service
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
app.include_router(ai.router)
app.include_router(faces.router)
app.include_router(robot.router)


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
