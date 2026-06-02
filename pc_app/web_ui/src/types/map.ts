export interface MapNode {
  id: string;
  x: number;
  y: number;
}

export interface MapEdge {
  from: string;
  to: string;
  id?: string;
}

export interface RobotMap {
  nodes: MapNode[];
  edges: MapEdge[];
}
