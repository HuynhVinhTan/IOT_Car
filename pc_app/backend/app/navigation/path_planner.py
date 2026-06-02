from collections import deque

from app.navigation.map_graph import MapGraph


class PathPlanner:
    def __init__(self, map_graph: MapGraph) -> None:
        self._map_graph = map_graph

    def find_path(self, start_node: str, target_node: str) -> list[str]:
        if start_node == target_node:
            return [start_node]
        if start_node not in self._map_graph.nodes or target_node not in self._map_graph.nodes:
            return []

        queue: deque[list[str]] = deque([[start_node]])
        visited = {start_node}
        while queue:
            current_path = queue.popleft()
            current_node = current_path[-1]
            for neighbor_node in self._map_graph.neighbors(current_node):
                if neighbor_node in visited:
                    continue
                candidate_path = [*current_path, neighbor_node]
                if neighbor_node == target_node:
                    return candidate_path
                visited.add(neighbor_node)
                queue.append(candidate_path)
        return []
