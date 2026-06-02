from app.navigation.map_graph import MapGraph


class CoveragePlanner:
    def __init__(self, map_graph: MapGraph) -> None:
        self._map_graph = map_graph

    def choose_next_target(self, current_node: str) -> str | None:
        return self._map_graph.first_unvisited_reachable_node(current_node)
