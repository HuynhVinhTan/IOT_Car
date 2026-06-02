from typing import Any

from app.navigation.map_graph import MapGraph


class LocalizationService:
    def __init__(self, map_graph: MapGraph | None = None) -> None:
        self._map_graph = map_graph or MapGraph()
        self.current_node = "UNKNOWN"
        self.current_segment = ""
        self.home_node = "HOME"
        self.target_node = ""
        self.visited_nodes: list[str] = []
        self.progress_ratio: float = 0.0
        self.direction: str = "unknown"
        self.position_source: str = "backend_estimate"

    def update_location(
        self,
        current_node: str | None = None,
        current_segment: str | None = None,
        home_node: str | None = None,
        target_node: str | None = None,
    ) -> dict[str, Any]:
        if current_node:
            self.current_node = current_node
            if current_node not in self.visited_nodes:
                self.visited_nodes.append(current_node)
            self._map_graph.mark_visited(current_node)
        if current_segment is not None:
            self.current_segment = current_segment
        if home_node:
            self.home_node = home_node
        if target_node is not None:
            self.target_node = target_node
        
        # Determine direction based on current_node vs current_segment
        if self.current_node != "UNKNOWN" and self.current_segment:
            segments = self._map_graph.get_segments()
            for s in segments:
                if s["segment_id"] == self.current_segment:
                    if s["from_node"] == self.current_node:
                        self.direction = "forward"
                    elif s["to_node"] == self.current_node:
                        self.direction = "backward"
                    break
                    
        return self.snapshot()

    def get_robot_position(self) -> dict[str, Any]:
        import time
        return {
            "current_node": self.current_node if self.current_node != "UNKNOWN" else None,
            "current_segment_id": self.current_segment if self.current_segment else None,
            "target_node": self.target_node if self.target_node else None,
            "direction": self.direction,
            "progress_ratio": self.progress_ratio,
            "position_source": self.position_source,
            "updated_at_ms": int(time.time() * 1000)
        }

    def enrich_car_telemetry(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        enriched_telemetry = dict(telemetry)
        incoming_node = enriched_telemetry.get("current_node")
        if incoming_node and incoming_node != "UNKNOWN":
            self.update_location(str(incoming_node))
        else:
            enriched_telemetry["current_node"] = self.current_node

        enriched_telemetry.setdefault("home_node", self.home_node)
        enriched_telemetry.setdefault("target_node", self.target_node)
        enriched_telemetry["current_segment"] = self.current_segment
        enriched_telemetry["visited_nodes"] = list(self.visited_nodes)
        enriched_telemetry["coverage_progress"] = self.coverage_progress()
        enriched_telemetry["robot_position"] = self.get_robot_position()
        return enriched_telemetry

    def coverage_progress(self) -> float:
        return self._map_graph.coverage_progress()

    def snapshot(self) -> dict[str, Any]:
        return {
            "current_node": self.current_node,
            "current_segment": self.current_segment,
            "home_node": self.home_node,
            "target_node": self.target_node,
            "visited_nodes": self.visited_nodes,
            "coverage_progress": self.coverage_progress(),
            "map": self._map_graph.to_dict(),
        }
