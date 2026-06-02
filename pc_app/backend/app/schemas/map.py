from pydantic import BaseModel


class MapNode(BaseModel):
    id: str
    x: float = 0.0
    y: float = 0.0
    visited: bool = False
    blocked: bool = False


class MapEdge(BaseModel):
    source: str
    target: str
    cost: float = 1.0


class MapGraphSchema(BaseModel):
    nodes: list[MapNode]
    edges: list[MapEdge]
