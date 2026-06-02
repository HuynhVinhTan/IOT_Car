from typing import Any

from app.navigation.coverage_planner import CoveragePlanner
from app.navigation.localization_service import LocalizationService
from app.navigation.path_planner import PathPlanner
from app.services.car_control_service import CarControlService


class MissionService:
    def __init__(
        self,
        localization_service: LocalizationService,
        path_planner: PathPlanner,
        coverage_planner: CoveragePlanner,
        car_control_service: CarControlService,
    ) -> None:
        self._localization_service = localization_service
        self._path_planner = path_planner
        self._coverage_planner = coverage_planner
        self._car_control_service = car_control_service
        self.mission_mode = "IDLE"
        self.planned_path: list[str] = []
        self.detection_state = {
            "object_found": False,
            "object_type": "unknown",
            "confidence": 0.0,
            "detected_at_ms": 0,
            "detected_node": None,
            "detected_segment_id": None,
            "follow_state": "idle",
            "message": "Waiting"
        }

    def start_auto_search(self) -> dict[str, Any]:
        current_node = self._localization_service.current_node
        if current_node == "UNKNOWN":
            return {
                "success": False,
                "message": "Set current_node before starting AutoSearch",
            }

        self._localization_service.update_location(home_node=current_node)
        next_target = self._coverage_planner.choose_next_target(current_node)
        if next_target is None:
            return {"success": False, "message": "No reachable unvisited node"}

        self.planned_path = self._path_planner.find_path(current_node, next_target)
        self._localization_service.update_location(target_node=next_target)
        self.mission_mode = "AutoSearch"
        self._car_control_service.set_mode("AUTO_SEARCH")
        return self.snapshot(success=True, message="AutoSearch started")

    def return_home(self) -> dict[str, Any]:
        current_node = self._localization_service.current_node
        home_node = self._localization_service.home_node
        if current_node == "UNKNOWN":
            return {"success": False, "message": "Current node is unknown"}
        self.planned_path = self._path_planner.find_path(current_node, home_node)
        self._localization_service.update_location(target_node=home_node)
        self.mission_mode = "ReturnHome"
        self._car_control_service.set_mode("RETURN_HOME")
        return self.snapshot(success=True, message="ReturnHome started")

    def start_search(self, start_node: str = "A", target_node: str = "F") -> dict[str, Any]:
        self._localization_service.update_location(home_node=start_node, target_node=target_node, current_node=start_node)
        self.planned_path = self._path_planner.find_path(start_node, target_node)
        self.mission_mode = "SEARCH_OUTBOUND"
        self.detection_state["message"] = f"Searching from {start_node} to {target_node}"
        self.detection_state["follow_state"] = "searching"
        self._car_control_service.set_mode("SEARCH")
        return self.snapshot(success=True, message=self.detection_state["message"])

    def handle_search_progress(self) -> None:
        """Called periodically or when telemetry updates to check if we reached targets."""
        # Simple mock logic: if we reached target_node, we transition.
        if self.mission_mode == "SEARCH_OUTBOUND" and self._localization_service.current_node == "F":
            self.mission_mode = "SEARCH_RETURNING"
            self._localization_service.update_location(target_node="A")
            self.planned_path = self._path_planner.find_path("F", "A")
            self.detection_state["message"] = "Reached F. Object not found. Returning to A."
        elif self.mission_mode == "SEARCH_RETURNING" and self._localization_service.current_node == "A":
            self.mission_mode = "COMPLETED"
            self.detection_state["message"] = "Search completed. Object not found."
            self.detection_state["follow_state"] = "idle"

    def trigger_mock_detection(self, found: bool) -> dict[str, Any]:
        import time
        if found:
            self.detection_state["object_found"] = True
            self.detection_state["object_type"] = "person"
            self.detection_state["confidence"] = 0.95
            self.detection_state["detected_at_ms"] = int(time.time() * 1000)
            self.detection_state["detected_node"] = self._localization_service.current_node if self._localization_service.current_node != "UNKNOWN" else None
            self.detection_state["detected_segment_id"] = self._localization_service.current_segment if self._localization_service.current_segment else None
            
            # Transition mission
            if self.mission_mode in ["SEARCH_OUTBOUND", "SEARCH_RETURNING"]:
                self.mission_mode = "FOLLOWING_OBJECT"
                self.detection_state["follow_state"] = "following"
                self.detection_state["message"] = "Object found! Initiating follow."
                
                try:
                    self._car_control_service.send_command({"command": "PERSON_DETECTED", "detected": True})
                except RuntimeError:
                    pass
        else:
            self.detection_state["object_found"] = False
            self.detection_state["follow_state"] = "lost"
            self.mission_mode = "OBJECT_LOST"
            self.detection_state["message"] = "Object lost."
            try:
                self._car_control_service.send_command({"command": "PERSON_LOST"})
            except RuntimeError:
                pass
                
        return self.snapshot(success=True, message=self.detection_state["message"])

    def stop_mission(self) -> dict[str, Any]:
        self.mission_mode = "IDLE"
        self.planned_path = []
        self.detection_state["follow_state"] = "idle"
        self.detection_state["message"] = "Mission stopped."
        try:
            self._car_control_service.send_command({"command": "STOP_MISSION"})
        except RuntimeError:
            pass
        return self.snapshot(success=True, message="Mission stopped")

    def snapshot(self, success: bool = True, message: str = "") -> dict[str, Any]:
        localization_snapshot = self._localization_service.snapshot()
        return {
            "success": success,
            "message": message,
            "mission_mode": self.mission_mode,
            "planned_path": self.planned_path,
            "detection_state": self.detection_state,
            **localization_snapshot,
        }
