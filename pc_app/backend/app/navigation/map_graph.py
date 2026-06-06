from collections import deque
from typing import Any


class MapGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {
            "HOME": {"id": "HOME", "x": 60, "y": 140, "visited": False, "blocked": False},
            "A": {"id": "A", "x": 60, "y": 140, "visited": False, "blocked": False},
            "B": {"id": "B", "x": 160, "y": 100, "visited": False, "blocked": False},
            "C": {"id": "C", "x": 160, "y": 200, "visited": False, "blocked": False},
            "D": {"id": "D", "x": 280, "y": 60, "visited": False, "blocked": False},
            "E": {"id": "E", "x": 280, "y": 200, "visited": False, "blocked": False},
            "F": {"id": "F", "x": 370, "y": 140, "visited": False, "blocked": False},
            "G": {"id": "G", "x": 460, "y": 140, "visited": False, "blocked": False},
        }
        self.edges: list[dict[str, Any]] = [
            {"from": "HOME", "to": "A", "cost": 0.0},
            {"from": "A", "to": "B", "cost": 1.0},
            {"from": "B", "to": "C", "cost": 1.0},
            {"from": "B", "to": "D", "cost": 1.0},
            {"from": "C", "to": "E", "cost": 1.0},
            {"from": "D", "to": "E", "cost": 1.0},
            {"from": "E", "to": "F", "cost": 1.0},
            {"from": "F", "to": "G", "cost": 1.0},
        ]
        self.segments: list[dict[str, Any]] = [
            {"segment_id": "A_B", "from_node": "A", "to_node": "B", "label": "A → B"},
            {"segment_id": "B_C", "from_node": "B", "to_node": "C", "label": "B → C"},
            {"segment_id": "B_D", "from_node": "B", "to_node": "D", "label": "B → D"},
            {"segment_id": "C_E", "from_node": "C", "to_node": "E", "label": "C → E"},
            {"segment_id": "D_E", "from_node": "D", "to_node": "E", "label": "D → E"},
            {"segment_id": "E_F", "from_node": "E", "to_node": "F", "label": "E → F"},
            {"segment_id": "F_G", "from_node": "F", "to_node": "G", "label": "F → G"},
        ]

    def neighbors(self, node_id: str) -> list[str]:
        neighbors: list[str] = []
        for edge in self.edges:
            if edge["from"] == node_id:
                neighbors.append(edge["to"])
            elif edge["to"] == node_id:
                neighbors.append(edge["from"])
        return [node for node in neighbors if not self.nodes[node]["blocked"]]

    def mark_visited(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.nodes[node_id]["visited"] = True

    def first_unvisited_reachable_node(self, start_node: str) -> str | None:
        if start_node not in self.nodes:
            return None

        visited: set[str] = {start_node}
        queue: deque[str] = deque([start_node])
        while queue:
            current_node = queue.popleft()
            if not self.nodes[current_node]["visited"]:
                return current_node
            for neighbor_node in self.neighbors(current_node):
                if neighbor_node not in visited:
                    visited.add(neighbor_node)
                    queue.append(neighbor_node)
        return None

    def coverage_progress(self) -> float:
        available_nodes = [
            node for node in self.nodes.values() if not node.get("blocked", False)
        ]
        if not available_nodes:
            return 0.0
        visited_count = len([node for node in available_nodes if node["visited"]])
        return visited_count / len(available_nodes)

    def segment_pixel_distance(self, segment_id: str) -> float | None:
        """Return Euclidean pixel distance for a segment, or None if not found."""
        for seg in self.segments:
            if seg["segment_id"] == segment_id:
                a = self.nodes.get(seg["from_node"])
                b = self.nodes.get(seg["to_node"])
                if a and b:
                    return ((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2) ** 0.5
        return None

    def to_dict(self) -> dict[str, Any]:
        return {"nodes": list(self.nodes.values()), "edges": self.edges}

    def get_segments(self) -> list[dict[str, Any]]:
        result = []
        for seg in self.segments:
            from_n = self.nodes.get(seg["from_node"], {})
            to_n = self.nodes.get(seg["to_node"], {})
            is_blocked = from_n.get("blocked", False) or to_n.get("blocked", False)
            is_visited = from_n.get("visited", False) and to_n.get("visited", False)
            result.append({
                "segment_id": seg["segment_id"],
                "from_node": seg["from_node"],
                "to_node": seg["to_node"],
                "label": seg["label"],
                "is_enabled": True,
                "is_blocked": is_blocked,
                "is_visited": is_visited
            })
        return result
