from typing import Any

from app.navigation.localization_service import LocalizationService
from app.navigation.map_graph import MapGraph
from app.schemas.route_segment import RouteGuidanceDecision, RouteSelectionState
from app.services.car_control_service import CarControlService
from app.services.telemetry_service import TelemetryService


class RouteSegmentService:
    def __init__(
        self,
        map_graph: MapGraph,
        localization_service: LocalizationService,
        telemetry_service: TelemetryService,
        car_control_service: CarControlService,
    ) -> None:
        self._map_graph = map_graph
        self._localization_service = localization_service
        self._telemetry_service = telemetry_service
        self._car_control_service = car_control_service
        self.selection_state = RouteSelectionState()

    def get_segments(self) -> list[dict[str, Any]]:
        return self._map_graph.get_segments()

    def get_current_selection(self) -> dict[str, Any]:
        state = self.selection_state.model_dump()
        state["current_node"] = self._localization_service.current_node
        state["target_node"] = self._localization_service.target_node
        state["current_segment_id"] = self._localization_service.current_segment
        return state

    def select_segment(
        self, segment_id: str, confirm_on_segment: bool
    ) -> dict[str, Any]:
        segments = {s["segment_id"]: s for s in self.get_segments()}
        if segment_id not in segments:
            self.selection_state.accepted = False
            self.selection_state.reason = "Segment not found"
            return self.get_current_selection()

        segment = segments[segment_id]
        if segment.get("is_blocked"):
            self.selection_state.accepted = False
            self.selection_state.reason = "Segment is blocked"
            return self.get_current_selection()

        self.selection_state.selected_segment_id = segment_id
        if confirm_on_segment:
            self._localization_service.update_location(current_segment=segment_id)

        self.selection_state.accepted = True
        self.selection_state.reason = "Segment selected manually"
        return self.get_current_selection()

    def cancel_segment(self) -> dict[str, Any]:
        if self.selection_state.selected_segment_id:
            try:
                self._car_control_service.send_command({"command": "REMOTE_STOP"})
            except RuntimeError:
                pass

        self.selection_state = RouteSelectionState()
        return self.get_current_selection()

    def heading_hint(
        self, segment_id: str, hint_x: float, hint_y: float
    ) -> dict[str, Any]:
        decision = RouteGuidanceDecision(
            segment_id=segment_id,
            heading_hint_x=max(-1.0, min(1.0, hint_x)),
            heading_hint_y=max(-1.0, min(1.0, hint_y)),
        )

        car_telemetry = self._telemetry_service.latest_car_telemetry or {}
        decision.safety_status = "OK"
        if car_telemetry.get("emergency_reason"):
            decision.safety_status = "EMERGENCY_STOP"
        elif car_telemetry.get("forward_unsafe") or car_telemetry.get(
            "backward_unsafe"
        ):
            decision.safety_status = "UNSAFE_PROXIMITY"

        if decision.safety_status != "OK":
            decision.accepted = False
            decision.reason = f"Rejected by safety checks: {decision.safety_status}"
            return decision.model_dump()

        if (
            self._localization_service.current_node == "UNKNOWN"
            and not self._localization_service.current_segment
        ):
            decision.accepted = False
            decision.reason = "Current location unknown. Confirm segment first."
            return decision.model_dump()

        decision.accepted = True
        decision.reason = "Heading hint recorded as guidance advisory."
        decision.confidence = 0.5
        decision.current_segment_id = self._localization_service.current_segment

        segments = {s["segment_id"]: s for s in self.get_segments()}
        if segment_id in segments:
            decision.target_node = segments[segment_id]["to_node"]

        return decision.model_dump()

    def auto_infer(self) -> dict[str, Any]:
        curr_node = self._localization_service.current_node
        curr_seg = self._localization_service.current_segment

        segments = self.get_segments()
        inferred_segment = None

        if curr_node != "UNKNOWN":
            for seg in segments:
                if (
                    seg["from_node"] == curr_node
                    and not seg["is_blocked"]
                    and not seg["is_visited"]
                ):
                    inferred_segment = seg["segment_id"]
                    break
        elif curr_seg:
            inferred_segment = curr_seg

        if inferred_segment:
            return self.select_segment(inferred_segment, False)

        self.selection_state.accepted = False
        self.selection_state.reason = (
            "Could not infer segment. Please select manually."
        )
        return self.get_current_selection()
