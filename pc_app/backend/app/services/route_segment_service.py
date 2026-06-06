import asyncio
from typing import Any

from app.navigation.localization_service import LocalizationService
from app.navigation.map_graph import MapGraph
from app.schemas.route_segment import RouteGuidanceDecision, RouteSelectionState
from app.services.robot.car_control_service import CarControlService
from app.services.robot.telemetry_service import TelemetryService

# Pixels-per-cm scale: 1 pixel on the canvas = PIXEL_TO_CM real-world centimetres.
# Tune this constant once you've measured your real track.
PIXEL_TO_CM: float = 2.0

# Fixed drive speed for auto-navigation segments (0–255).
DRIVE_SPEED: int = 160

# How fast the robot moves in cm/s at DRIVE_SPEED.  Measure on the real car.
SPEED_CM_PER_S: float = 20.0


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

    # ------------------------------------------------------------------
    # Start-position API
    # ------------------------------------------------------------------

    def set_start_position(
        self, segment_id: str, offset_pct: float
    ) -> dict[str, Any]:
        """
        User tells us: "robot is on segment_id, already travelled offset_pct of it."
        We update localization and kick off an async mission task.
        """
        position_info = self._localization_service.set_start_position(
            segment_id, offset_pct
        )
        if not position_info.get("ok"):
            return {"ok": False, "reason": position_info.get("reason", "Unknown error")}

        # Fire-and-forget async mission
        asyncio.create_task(self._run_mission_from_segment(segment_id, offset_pct))

        return {
            "ok": True,
            "message": f"Mission started from {segment_id} at {int(offset_pct * 100)}%",
            **position_info,
        }

    async def _run_mission_from_segment(
        self, start_segment_id: str, offset_pct: float
    ) -> None:
        """
        Core mission orchestrator:
          1. Drive remaining part of start_segment to its to_node
          2. Then walk every subsequent segment in order until the map is done
        """
        all_segments = self.get_segments()
        seg_map = {s["segment_id"]: s for s in all_segments}

        # --- Step 1: finish the partial start segment ---
        start_seg = seg_map.get(start_segment_id)
        if not start_seg:
            return

        remaining_pct = 1.0 - offset_pct
        pixel_dist = self._map_graph.segment_pixel_distance(start_segment_id)
        if pixel_dist and remaining_pct > 0:
            remaining_cm = pixel_dist * PIXEL_TO_CM * remaining_pct
            duration_ms = int((remaining_cm / SPEED_CM_PER_S) * 1000)
            await self._car_control_service.drive_timed(
                duration_ms, DRIVE_SPEED, DRIVE_SPEED
            )

        # Mark arrival at to_node of the start segment
        arrived_node = start_seg["to_node"]
        self._localization_service.update_location(
            current_node=arrived_node, current_segment=start_segment_id
        )

        # --- Step 2: run remaining segments in order ---
        await self._continue_mission_from_node(arrived_node, seg_map)

    async def _continue_mission_from_node(
        self,
        current_node: str,
        seg_map: dict[str, Any],
    ) -> None:
        """
        Greedily traverse segments from current_node until no unvisited
        unblocked segment starts from the current node.
        """
        while True:
            # Find the next segment that starts at current_node and is not blocked/visited
            next_seg = None
            for seg in seg_map.values():
                if (
                    seg["from_node"] == current_node
                    and not seg.get("is_blocked")
                    and not seg.get("is_visited")
                ):
                    next_seg = seg
                    break

            if next_seg is None:
                # Mission complete — no more segments to visit
                self._localization_service.update_location(
                    current_node=current_node
                )
                return

            seg_id = next_seg["segment_id"]
            pixel_dist = self._map_graph.segment_pixel_distance(seg_id)
            if pixel_dist:
                duration_ms = int((pixel_dist * PIXEL_TO_CM / SPEED_CM_PER_S) * 1000)
                self._localization_service.update_location(current_segment=seg_id)
                await self._car_control_service.drive_timed(
                    duration_ms, DRIVE_SPEED, DRIVE_SPEED
                )

            # Mark arrival
            current_node = next_seg["to_node"]
            self._localization_service.update_location(
                current_node=current_node, current_segment=seg_id
            )
            # Mark segment visited so we don't loop
            next_seg["is_visited"] = True


    async def continue_from_node(self, node: str) -> None:
       
        self._localization_service.update_location(current_node=node)
        
        next_segment = self._find_next_segment(from_node=node)
        
        if next_segment is None:
            await self._car_control_service.send_command({"command": "STOP_MISSION"})
            return
            
        seg_id = next_segment["segment_id"]
        pixel_dist = self._map_graph.segment_pixel_distance(seg_id)
        
        if pixel_dist:
            duration_ms = int((pixel_dist * PIXEL_TO_CM / SPEED_CM_PER_S) * 1000)
            
            self._localization_service.update_location(current_segment=seg_id)
            
            # Ra lệnh cho xe chạy ngầm
            await self._car_control_service.drive_timed(
                duration_ms, DRIVE_SPEED, DRIVE_SPEED
            )
            
        next_segment["is_visited"] = True

    def _find_next_segment(self, from_node: str) -> dict[str, Any] | None:
        for seg in self.get_segments():
            if seg["from_node"] == from_node and not seg.get("is_visited", False):
                return seg
        return None