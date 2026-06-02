import { Card } from "../../atoms/Card/Card";
import type { CarTelemetry } from "../../../types/carTelemetry";
import type { RouteSegment, RouteSelectionState } from "../../../types/routeSegment";

// UI Layout coordinates only. 
// Truth about which segments exist comes from Backend via props.
const NODE_LAYOUT: Record<string, { x: number, y: number }> = {
  "A": { x: 60, y: 140 },
  "B": { x: 160, y: 100 },
  "C": { x: 160, y: 200 },
  "D": { x: 280, y: 60 },
  "E": { x: 280, y: 200 },
  "F": { x: 370, y: 140 },
  "G": { x: 460, y: 140 },
};

interface MapPanelProps {
  carTelemetry: CarTelemetry | null;
  segments: RouteSegment[];
  selection: RouteSelectionState | null;
  loading?: boolean;
  error?: string | null;
}

export function MapPanel({ carTelemetry, segments, selection, loading, error }: MapPanelProps) {
  const currentNode = selection?.current_node || carTelemetry?.current_node || "UNKNOWN";
  const homeNode = carTelemetry?.home_node || "HOME";
  const targetNode = selection?.target_node || carTelemetry?.target_node || "";
  const visitedNodes = new Set(carTelemetry?.visited_nodes || []);

  const edgeById = new Map(segments.map(s => [s.segment_id, s]));

  const robotPos = carTelemetry?.robot_position;
  const detectionState = carTelemetry?.mission_state?.detection_state;

  let rx = 0, ry = 0;
  let showRobot = false;
  
  if (robotPos?.current_node && robotPos.current_node !== "UNKNOWN" && NODE_LAYOUT[robotPos.current_node]) {
    const n = NODE_LAYOUT[robotPos.current_node];
    rx = n.x; ry = n.y; showRobot = true;
  } else if (robotPos?.current_segment_id && edgeById.has(robotPos.current_segment_id)) {
    const e = edgeById.get(robotPos.current_segment_id)!;
    const fn = NODE_LAYOUT[e.from_node];
    const tn = NODE_LAYOUT[e.to_node];
    if (fn && tn) {
      const p = robotPos.progress_ratio || 0.5;
      if (robotPos.direction === "backward") {
        rx = tn.x + (fn.x - tn.x) * p;
        ry = tn.y + (fn.y - tn.y) * p;
      } else {
        rx = fn.x + (tn.x - fn.x) * p;
        ry = fn.y + (tn.y - fn.y) * p;
      }
      showRobot = true;
    }
  }

  let ox = 0, oy = 0, showObject = false;
  if (detectionState?.object_found) {
    if (detectionState.detected_node && NODE_LAYOUT[detectionState.detected_node]) {
      const n = NODE_LAYOUT[detectionState.detected_node];
      ox = n.x; oy = n.y; showObject = true;
    } else if (detectionState.detected_segment_id && edgeById.has(detectionState.detected_segment_id)) {
      const e = edgeById.get(detectionState.detected_segment_id)!;
      const fn = NODE_LAYOUT[e.from_node];
      const tn = NODE_LAYOUT[e.to_node];
      if (fn && tn) {
        ox = fn.x + (tn.x - fn.x) * 0.5;
        oy = fn.y + (tn.y - fn.y) * 0.5;
        showObject = true;
      }
    }
  }

  // Get all unique nodes from segments
  const activeNodes = new Set<string>();
  segments.forEach(s => {
    activeNodes.add(s.from_node);
    activeNodes.add(s.to_node);
  });
  const nodesToRender = Array.from(activeNodes).filter(id => !!NODE_LAYOUT[id]);

  return (
    <Card title="Map">
      {loading && (
        <div style={{ height: "200px", display: "flex", justifyContent: "center", alignItems: "center", color: "var(--text-secondary)" }}>
          Loading map from backend...
        </div>
      )}
      {error && (
        <div style={{ height: "200px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", color: "var(--status-error)", textAlign: "center", padding: "0 20px" }}>
          <p style={{ fontWeight: "bold" }}>Backend disconnected</p>
          <p style={{ fontSize: "12px" }}>{error}</p>
        </div>
      )}
      {!loading && !error && segments.length === 0 && (
        <div style={{ height: "200px", display: "flex", justifyContent: "center", alignItems: "center", color: "var(--text-secondary)" }}>
          No route segments configured.
        </div>
      )}
      {!loading && !error && segments.length > 0 && (
        <svg className="map-canvas" viewBox="20 20 480 220" role="img" style={{ width: "100%", height: "auto" }}>
          {segments.map((edge) => {
            const fromNode = NODE_LAYOUT[edge.from_node];
            const toNode = NODE_LAYOUT[edge.to_node];
            if (!fromNode || !toNode) {
              return null;
            }
            const isSelected = selection?.selected_segment_id === edge.segment_id;
            const isCurrent = selection?.current_segment_id === edge.segment_id;
            return (
              <line
                key={edge.segment_id}
                x1={fromNode.x}
                y1={fromNode.y}
                x2={toNode.x}
                y2={toNode.y}
                className={["map-edge", isSelected ? "selected" : "", isCurrent ? "current" : "", edge.is_blocked ? "blocked" : ""].join(" ")}
              />
            );
          })}
          {nodesToRender.map((nodeId) => {
            const node = NODE_LAYOUT[nodeId];
            const isCurrent = nodeId === currentNode;
            const isHome = nodeId === homeNode || (homeNode === "HOME" && nodeId === "A");
            const isTarget = nodeId === targetNode;
            const isVisited = visitedNodes.has(nodeId);
            return (
              <g key={nodeId}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isCurrent ? 17 : 13}
                  className={[
                    "map-node",
                    isCurrent ? "current" : "",
                    isHome ? "home" : "",
                    isTarget ? "target" : "",
                    isVisited ? "visited" : "",
                  ].join(" ")}
                />
                <text x={node.x} y={node.y + 4} textAnchor="middle" style={{ fontSize: "12px", fontFamily: "var(--font-mono)", fill: "var(--text-primary)" }}>
                  {nodeId}
                </text>
                {isHome && (
                  <text x={node.x - 20} y={node.y - 20} textAnchor="middle" style={{ fontSize: "10px", fill: "var(--brand-primary)", fontWeight: "bold" }}>
                    HOME
                  </text>
                )}
              </g>
            );
          })}
          {showRobot && (
            <g>
              <circle cx={rx} cy={ry} r={8} fill="var(--brand-primary)" stroke="white" strokeWidth={2} />
              {robotPos?.position_source !== "telemetry" && (
                <text x={rx} y={ry - 12} textAnchor="middle" style={{ fontSize: "9px", fill: "var(--brand-primary)" }}>EST</text>
              )}
            </g>
          )}
          {showObject && (
            <g>
              <circle cx={ox} cy={oy} r={10} fill="var(--status-error)" opacity={0.6} />
              <circle cx={ox} cy={oy} r={5} fill="var(--status-error)" />
              <text x={ox} y={oy - 15} textAnchor="middle" style={{ fontSize: "10px", fill: "var(--status-error)", fontWeight: "bold" }}>
                {detectionState?.object_type.toUpperCase()}
              </text>
            </g>
          )}
        </svg>
      )}
    </Card>
  );
}
