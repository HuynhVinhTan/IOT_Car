import { useState, useRef } from "react";
import { Card } from "../../atoms/Card/Card";
import type { CarTelemetry } from "../../../types/carTelemetry";
import type {
  RouteSegment,
  RouteSelectionState,
} from "../../../types/routeSegment";
import { useMapState } from "../../../hooks/useMapState";
import type { MapNode, MapEdge } from "../../../services/mapService";

// UI Layout coordinates only.
// Truth about which segments exist comes from Backend via props.
const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  A: { x: 60, y: 140 },
  B: { x: 160, y: 100 },
  C: { x: 160, y: 200 },
  D: { x: 280, y: 60 },
  E: { x: 280, y: 200 },
  F: { x: 370, y: 140 },
  G: { x: 460, y: 140 },
};

interface MapPanelProps {
  carTelemetry: CarTelemetry | null;
  segments: RouteSegment[];
  selection: RouteSelectionState | null;
  loading?: boolean;
  error?: string | null;
}

export function MapPanel({
  carTelemetry,
  segments,
  selection,
  loading,
  error,
}: MapPanelProps) {
  const { mapState } = useMapState();
  const svgRef = useRef<SVGSVGElement>(null);

  // Zoom and Pan state
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });

  const currentNode =
    selection?.current_node || carTelemetry?.current_node || "UNKNOWN";
  const homeNode = carTelemetry?.home_node || "HOME";
  const targetNode = selection?.target_node || carTelemetry?.target_node || "";
  const visitedNodes = new Set(carTelemetry?.visited_nodes || []);

  // Use active map if available, otherwise fall back to route segments
  const useActiveMap = mapState && mapState.nodes && mapState.nodes.length > 0;

  // Build layout and node data from active map nodes if available
  const mapLayout: Record<string, { x: number; y: number }> = {};
  const nodeLabels: Record<string, string> = {};

  if (useActiveMap && mapState?.nodes) {
    mapState.nodes.forEach((node: MapNode) => {
      mapLayout[node.id] = { x: node.x, y: node.y };
      nodeLabels[node.id] = node.label || node.id;
    });
  } else {
    // Fallback to the original NODE_LAYOUT
    Object.assign(mapLayout, NODE_LAYOUT);
    // Default labels are node IDs
    Object.keys(NODE_LAYOUT).forEach((id) => {
      nodeLabels[id] = id;
    });
  }

  const edgeById = new Map(segments.map((s) => [s.segment_id, s]));

  const robotPos = carTelemetry?.robot_position;
  const detectionState = carTelemetry?.mission_state?.detection_state;

  let rx = 0,
    ry = 0;
  let showRobot = false;

  if (
    robotPos?.current_node &&
    robotPos.current_node !== "UNKNOWN" &&
    mapLayout[robotPos.current_node]
  ) {
    const n = mapLayout[robotPos.current_node];
    rx = n.x;
    ry = n.y;
    showRobot = true;
  } else if (
    robotPos?.current_segment_id &&
    edgeById.has(robotPos.current_segment_id)
  ) {
    const e = edgeById.get(robotPos.current_segment_id)!;
    const fn = mapLayout[e.from_node];
    const tn = mapLayout[e.to_node];
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

  let ox = 0,
    oy = 0,
    showObject = false;
  if (detectionState?.object_found) {
    if (
      detectionState.detected_node &&
      mapLayout[detectionState.detected_node]
    ) {
      const n = mapLayout[detectionState.detected_node];
      ox = n.x;
      oy = n.y;
      showObject = true;
    } else if (
      detectionState.detected_segment_id &&
      edgeById.has(detectionState.detected_segment_id)
    ) {
      const e = edgeById.get(detectionState.detected_segment_id)!;
      const fn = mapLayout[e.from_node];
      const tn = mapLayout[e.to_node];
      if (fn && tn) {
        ox = fn.x + (tn.x - fn.x) * 0.5;
        oy = fn.y + (tn.y - fn.y) * 0.5;
        showObject = true;
      }
    }
  }

  // Get all unique nodes to render (from active map or segments)
  const activeNodes = new Set<string>();
  if (useActiveMap && mapState?.nodes) {
    mapState.nodes.forEach((node: MapNode) => {
      activeNodes.add(node.id);
    });
  } else {
    segments.forEach((s) => {
      activeNodes.add(s.from_node);
      activeNodes.add(s.to_node);
    });
  }
  const nodesToRender = Array.from(activeNodes).filter((id) => !!mapLayout[id]);

  // Get edges to render
  const edgesToRender = useActiveMap && mapState?.edges ? mapState.edges : [];

  // Calculate dynamic viewBox based on node positions
  const calculateViewBox = () => {
    if (!useActiveMap || !mapState?.nodes || mapState.nodes.length === 0) {
      return "20 20 480 220"; // Default viewBox
    }

    const padding = 50;
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity;

    mapState.nodes.forEach((node: MapNode) => {
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x);
      maxY = Math.max(maxY, node.y);
    });

    if (!isFinite(minX)) return "20 20 480 220";

    const width = maxX - minX + padding * 2;
    const height = maxY - minY + padding * 2;

    return `${minX - padding} ${minY - padding} ${width} ${height}`;
  };

  const viewBox = calculateViewBox();

  // Zoom/Pan handlers
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom((prev) => Math.max(0.5, Math.min(5, prev * delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsPanning(true);
      setStartPan({ x: e.clientX - panX, y: e.clientY - panY });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPanX(e.clientX - startPan.x);
      setPanY(e.clientY - startPan.y);
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(5, prev * 1.2));
  const handleZoomOut = () => setZoom((prev) => Math.max(0.5, prev / 1.2));
  const handleResetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  return (
    <Card title="Map">
      {loading && (
        <div
          style={{
            height: "200px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            color: "var(--text-secondary)",
          }}
        >
          Loading map from backend...
        </div>
      )}
      {error && (
        <div
          style={{
            height: "200px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            color: "var(--status-error)",
            textAlign: "center",
            padding: "0 20px",
          }}
        >
          <p style={{ fontWeight: "bold" }}>Backend disconnected</p>
          <p style={{ fontSize: "12px" }}>{error}</p>
        </div>
      )}
      {!loading && !error && !useActiveMap && segments.length === 0 && (
        <div
          style={{
            height: "200px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            color: "var(--text-secondary)",
          }}
        >
          No active map or route segments configured.
        </div>
      )}
      {!loading && !error && (segments.length > 0 || useActiveMap) && (
        <div style={{ position: "relative", overflow: "hidden" }}>
          <div
            style={{
              position: "absolute",
              top: 8,
              left: 8,
              zIndex: 2,
              background: "rgba(0,0,0,0.65)",
              color: "white",
              padding: "4px 8px",
              borderRadius: "4px",
              fontSize: "11px",
              maxWidth: "70%",
            }}
          >
            {useActiveMap
              ? `Active: ${mapState?.name || mapState?.id}`
              : "Route segments fallback"}
          </div>
          <div
            style={{
              position: "absolute",
              top: 8,
              right: 8,
              zIndex: 2,
              display: "flex",
              gap: "4px",
            }}
          >
            <button onClick={handleZoomIn} title="Zoom in">
              +
            </button>
            <button onClick={handleZoomOut} title="Zoom out">
              −
            </button>
            <button onClick={handleResetView} title="Reset view">
              Reset
            </button>
          </div>
          <svg
            ref={svgRef}
            className="map-canvas"
            viewBox={viewBox}
            role="img"
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{
              width: "100%",
              height: "280px",
              cursor: isPanning ? "grabbing" : "grab",
              touchAction: "none",
              userSelect: "none",
            }}
          >
            <g transform={`translate(${panX} ${panY}) scale(${zoom})`}>
              {useActiveMap &&
                edgesToRender.map((edge: MapEdge) => {
                  const fromNode = mapLayout[edge.from];
                  const toNode = mapLayout[edge.to];
                  if (!fromNode || !toNode) {
                    return null;
                  }
                  return (
                    <line
                      key={edge.id}
                      x1={fromNode.x}
                      y1={fromNode.y}
                      x2={toNode.x}
                      y2={toNode.y}
                      stroke="gray"
                      strokeWidth={2}
                      style={{ cursor: "pointer" }}
                    />
                  );
                })}
              {!useActiveMap &&
                segments.map((edge) => {
                  const fromNode = mapLayout[edge.from_node];
                  const toNode = mapLayout[edge.to_node];
                  if (!fromNode || !toNode) {
                    return null;
                  }
                  const isSelected =
                    selection?.selected_segment_id === edge.segment_id;
                  const isCurrent =
                    selection?.current_segment_id === edge.segment_id;
                  return (
                    <line
                      key={edge.segment_id}
                      x1={fromNode.x}
                      y1={fromNode.y}
                      x2={toNode.x}
                      y2={toNode.y}
                      className={[
                        "map-edge",
                        isSelected ? "selected" : "",
                        isCurrent ? "current" : "",
                        edge.is_blocked ? "blocked" : "",
                      ].join(" ")}
                    />
                  );
                })}
              {nodesToRender.map((nodeId) => {
                const node = mapLayout[nodeId];
                const isCurrent = nodeId === currentNode;
                const isHome =
                  nodeId === homeNode ||
                  (homeNode === "HOME" && nodeId === "A");
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
                    <text
                      x={node.x}
                      y={node.y + 4}
                      textAnchor="middle"
                      style={{
                        fontSize: "12px",
                        fontFamily: "var(--font-mono)",
                        fill: "var(--text-primary)",
                      }}
                    >
                      {nodeLabels[nodeId] || nodeId}
                    </text>
                    {isHome && (
                      <text
                        x={node.x - 20}
                        y={node.y - 20}
                        textAnchor="middle"
                        style={{
                          fontSize: "10px",
                          fill: "var(--brand-primary)",
                          fontWeight: "bold",
                        }}
                      >
                        HOME
                      </text>
                    )}
                  </g>
                );
              })}
              {showRobot && (
                <g>
                  <circle
                    cx={rx}
                    cy={ry}
                    r={8}
                    fill="var(--brand-primary)"
                    stroke="white"
                    strokeWidth={2}
                  />
                  {robotPos?.position_source !== "telemetry" && (
                    <text
                      x={rx}
                      y={ry - 12}
                      textAnchor="middle"
                      style={{ fontSize: "9px", fill: "var(--brand-primary)" }}
                    >
                      EST
                    </text>
                  )}
                </g>
              )}
              {showObject && (
                <g>
                  <circle
                    cx={ox}
                    cy={oy}
                    r={10}
                    fill="var(--status-error)"
                    opacity={0.6}
                  />
                  <circle cx={ox} cy={oy} r={5} fill="var(--status-error)" />
                  <text
                    x={ox}
                    y={oy - 15}
                    textAnchor="middle"
                    style={{
                      fontSize: "10px",
                      fill: "var(--status-error)",
                      fontWeight: "bold",
                    }}
                  >
                    {detectionState?.object_type.toUpperCase()}
                  </text>
                </g>
              )}
            </g>
          </svg>
        </div>
      )}
    </Card>
  );
}
