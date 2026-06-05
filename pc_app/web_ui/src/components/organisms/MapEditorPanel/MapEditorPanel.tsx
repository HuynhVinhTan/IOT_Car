import { useState, useEffect, useRef } from "react";
import { Card } from "../../atoms/Card/Card";
import * as mapService from "../../../services/mapService";
import type { MapNode, MapEdge, Map } from "../../../services/mapService";

export function MapEditorPanel() {
  const [maps, setMaps] = useState<Map[]>([]);
  const [currentMap, setCurrentMap] = useState<Map | null>(null);
  const [activeMap, setActiveMap] = useState<string | null>(null);
  const [nodes, setNodes] = useState<MapNode[]>([]);
  const [edges, setEdges] = useState<MapEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null);
  const [edgeFrom, setEdgeFrom] = useState<string | null>(null);
  const [dragging, setDragging] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("");
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    loadMaps();
    loadActiveMap();
  }, []);

  const loadMaps = async () => {
    try {
      const data = await mapService.listMaps();
      setMaps(data);
    } catch (e) {
      setMessage(`Load failed: ${e}`);
    }
  };

  const loadActiveMap = async () => {
    try {
      const active = await mapService.getActiveMap();
      setActiveMap(active.id);
    } catch (e) {
      setActiveMap(null);
    }
  };

  const loadMap = async (mapId: string) => {
    try {
      const data = await mapService.getMap(mapId);
      setCurrentMap(data);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      setMessage(`Loaded: ${data.name || mapId}`);
    } catch (e) {
      setMessage(`Load failed: ${e}`);
    }
  };

  const newMap = () => {
    const id = `map_${Date.now()}`;
    setCurrentMap({ id, name: "New Map", nodes: [], edges: [] });
    setNodes([]);
    setEdges([]);
    setMessage("New map created");
  };

  const saveMap = async () => {
    if (!currentMap) return;
    try {
      await mapService.saveMap({ ...currentMap, nodes, edges });
      setMessage("Map saved!");
      await loadMaps();
    } catch (e) {
      setMessage(`Save failed: ${e}`);
    }
  };

  const activateMap = async () => {
    if (!currentMap) return;
    try {
      await mapService.activateMap(currentMap.id);
      setActiveMap(currentMap.id);
      setMessage(`Map "${currentMap.name || currentMap.id}" set as active!`);
    } catch (e) {
      setMessage(`Activate failed: ${e}`);
    }
  };

  const addNodeAt = (x: number, y: number) => {
    const id = `node_${Date.now()}`;
    const label = String.fromCharCode(65 + (nodes.length % 26));
    setNodes([...nodes, { id, x, y, type: "normal", label }]);
  };

  const handleCanvasClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return;
    if (e.target !== svgRef.current) return; // Don't add node if clicking on existing node/edge
    const rect = svgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    addNodeAt(x, y);
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  const handleNodeClick = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setSelectedEdge(null);
    if (edgeFrom === null) {
      setEdgeFrom(nodeId);
      setSelectedNode(nodeId);
    } else if (edgeFrom !== nodeId) {
      const edgeId = `edge_${Date.now()}`;
      const from = nodes.find((n) => n.id === edgeFrom);
      const to = nodes.find((n) => n.id === nodeId);
      const distance =
        from && to
          ? Math.sqrt(Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2))
          : 0;
      setEdges([
        ...edges,
        {
          id: edgeId,
          from: edgeFrom,
          to: nodeId,
          distance: Math.round(distance),
          bidirectional: true,
        },
      ]);
      setEdgeFrom(null);
      setSelectedNode(nodeId);
      setSelectedEdge(edgeId);
    } else {
      setEdgeFrom(null);
      setSelectedNode(nodeId);
    }
  };

  const handleEdgeClick = (e: React.MouseEvent, edgeId: string) => {
    e.stopPropagation();
    setSelectedEdge(edgeId);
    setSelectedNode(null);
    setEdgeFrom(null);
  };

  const handleNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setDragging(nodeId);
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!dragging || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setNodes(nodes.map((n) => (n.id === dragging ? { ...n, x, y } : n)));
  };

  const handleMouseUp = () => {
    setDragging(null);
  };

  const deleteNode = (nodeId: string) => {
    setNodes(nodes.filter((n) => n.id !== nodeId));
    setEdges(edges.filter((e) => e.from !== nodeId && e.to !== nodeId));
    if (selectedNode === nodeId) setSelectedNode(null);
    if (edgeFrom === nodeId) setEdgeFrom(null);
  };

  const deleteEdge = (edgeId: string) => {
    setEdges(edges.filter((e) => e.id !== edgeId));
    if (selectedEdge === edgeId) setSelectedEdge(null);
  };

  const changeNodeType = (nodeId: string, type: MapNode["type"]) => {
    setNodes(nodes.map((n) => (n.id === nodeId ? { ...n, type } : n)));
  };

  const changeNodeLabel = (nodeId: string, label: string) => {
    setNodes(nodes.map((n) => (n.id === nodeId ? { ...n, label } : n)));
  };

  const updateEdgeDistance = (edgeId: string, distance: number) => {
    setEdges(edges.map((e) => (e.id === edgeId ? { ...e, distance } : e)));
  };

  const updateEdgeBidirectional = (edgeId: string, bidirectional: boolean) => {
    setEdges(edges.map((e) => (e.id === edgeId ? { ...e, bidirectional } : e)));
  };

  const getNodeColor = (type: MapNode["type"]) => {
    switch (type) {
      case "home":
        return "green";
      case "target":
        return "red";
      case "checkpoint":
        return "orange";
      default:
        return "blue";
    }
  };

  return (
    <Card title="Map Editor">
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "10px",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <button onClick={newMap}>New Map</button>
        <button onClick={saveMap} disabled={!currentMap}>
          Save Map
        </button>
        <button
          onClick={activateMap}
          disabled={!currentMap}
          style={{
            background: activeMap === currentMap?.id ? "#28a745" : "#007bff",
            color: "white",
          }}
        >
          {activeMap === currentMap?.id ? "✓ Active Map" : "Set Active Map"}
        </button>
        <button onClick={loadMaps}>Refresh List</button>
        <select
          onChange={(e) => e.target.value && loadMap(e.target.value)}
          value={currentMap?.id || ""}
        >
          <option value="">Select a map to edit...</option>
          {maps.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name || m.id} {activeMap === m.id ? "(ACTIVE)" : ""}
            </option>
          ))}
        </select>
      </div>

      {currentMap && (
        <div style={{ marginBottom: "10px" }}>
          <input
            placeholder="Map Name"
            value={currentMap.name || ""}
            onChange={(e) =>
              setCurrentMap({ ...currentMap, name: e.target.value })
            }
            style={{ marginRight: "10px", padding: "5px" }}
          />
          <input
            placeholder="Map ID"
            value={currentMap.id}
            onChange={(e) =>
              setCurrentMap({ ...currentMap, id: e.target.value })
            }
            style={{ padding: "5px" }}
          />
          {activeMap === currentMap.id && (
            <span
              style={{ marginLeft: "10px", color: "green", fontWeight: "bold" }}
            >
              [ACTIVE MAP]
            </span>
          )}
        </div>
      )}

      <div
        style={{
          color: message.includes("failed") ? "red" : "green",
          marginBottom: "10px",
        }}
      >
        {message}
      </div>

      {currentMap && (
        <div style={{ marginBottom: "10px" }}>
          <button
            onClick={() => {}}
            style={{
              background: activeMap === currentMap.id ? "#e8f5e9" : "#f0f0f0",
              border: "1px solid #ccc",
              padding: "5px 10px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
          >
            {activeMap === currentMap.id ? "🔒" : "🔓"} Lock Zoom
          </button>
        </div>
      )}

      <svg
        ref={svgRef}
        width="100%"
        height="400"
        viewBox="0 0 600 400"
        style={{
          border: "1px solid #ccc",
          background: "#f9f9f9",
          cursor: "crosshair",
          display: "block",
        }}
        onClick={handleCanvasClick}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        {edges.map((edge) => {
          const from = nodes.find((n) => n.id === edge.from);
          const to = nodes.find((n) => n.id === edge.to);
          if (!from || !to) return null;
          return (
            <line
              key={edge.id}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke={selectedEdge === edge.id ? "blue" : "gray"}
              strokeWidth={selectedEdge === edge.id ? "4" : "2"}
              onClick={(e) => handleEdgeClick(e, edge.id)}
              style={{ cursor: "pointer" }}
            />
          );
        })}
        {nodes.map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={15}
              fill={getNodeColor(node.type)}
              stroke={selectedNode === node.id ? "black" : "none"}
              strokeWidth="3"
              onClick={(e) => handleNodeClick(e, node.id)}
              onMouseDown={(e) => handleNodeMouseDown(e, node.id)}
              style={{ cursor: "pointer" }}
            />
            <text
              x={node.x}
              y={node.y + 5}
              textAnchor="middle"
              fill="white"
              fontSize="12"
              pointerEvents="none"
            >
              {node.label || node.id}
            </text>
          </g>
        ))}
      </svg>

      {selectedEdge && (
        <div
          style={{
            marginTop: "10px",
            padding: "10px",
            border: "1px solid #ccc",
          }}
        >
          <h4>Edge: {selectedEdge}</h4>
          <div>
            <label style={{ marginRight: "10px" }}>
              Distance:
              <input
                type="number"
                value={edges.find((e) => e.id === selectedEdge)?.distance || 0}
                onChange={(e) =>
                  updateEdgeDistance(selectedEdge, Number(e.target.value))
                }
                style={{ marginLeft: "5px", padding: "5px", width: "80px" }}
              />
            </label>
            <label style={{ marginRight: "10px" }}>
              Bidirectional:
              <input
                type="checkbox"
                checked={
                  edges.find((e) => e.id === selectedEdge)?.bidirectional ||
                  false
                }
                onChange={(e) =>
                  updateEdgeBidirectional(selectedEdge, e.target.checked)
                }
                style={{ marginLeft: "5px" }}
              />
            </label>
            <button onClick={() => deleteEdge(selectedEdge)}>
              Delete Edge
            </button>
          </div>
        </div>
      )}

      {selectedNode && (
        <div
          style={{
            marginTop: "10px",
            padding: "10px",
            border: "1px solid #ccc",
          }}
        >
          <h4>Node: {selectedNode}</h4>
          <input
            placeholder="Label"
            value={nodes.find((n) => n.id === selectedNode)?.label || ""}
            onChange={(e) => changeNodeLabel(selectedNode, e.target.value)}
            style={{ marginRight: "5px", padding: "5px" }}
          />
          <select
            value={nodes.find((n) => n.id === selectedNode)?.type || "normal"}
            onChange={(e) =>
              changeNodeType(selectedNode, e.target.value as MapNode["type"])
            }
            style={{ marginRight: "5px", padding: "5px" }}
          >
            <option value="normal">Normal</option>
            <option value="home">Home</option>
            <option value="target">Target</option>
            <option value="checkpoint">Checkpoint</option>
          </select>
          <button onClick={() => deleteNode(selectedNode)}>Delete Node</button>
        </div>
      )}

      <div
        style={{
          marginTop: "10px",
          maxHeight: "200px",
          overflow: "auto",
          border: "1px solid #ccc",
          padding: "10px",
        }}
      >
        <h4>Debug Info</h4>
        <div>
          <strong>Nodes ({nodes.length}):</strong>
        </div>
        {nodes.map((n) => (
          <div key={n.id} style={{ fontSize: "12px" }}>
            {n.id}: ({n.x.toFixed(0)}, {n.y.toFixed(0)}) - {n.type}
          </div>
        ))}
        <div style={{ marginTop: "10px" }}>
          <strong>Edges ({edges.length}):</strong>
        </div>
        {edges.map((e) => (
          <div key={e.id} style={{ fontSize: "12px" }}>
            {e.id}: {e.from} → {e.to} ({e.distance?.toFixed(1)}px)
            <button
              onClick={() => deleteEdge(e.id)}
              style={{ marginLeft: "5px", fontSize: "10px" }}
            >
              X
            </button>
          </div>
        ))}
        <div style={{ marginTop: "10px" }}>
          <strong>JSON Preview:</strong>
        </div>
        <pre style={{ fontSize: "10px", maxHeight: "100px", overflow: "auto" }}>
          {JSON.stringify({ id: currentMap?.id, nodes, edges }, null, 2)}
        </pre>
      </div>
    </Card>
  );
}
