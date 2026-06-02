import { useState, useEffect } from "react";
import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { Badge } from "../../atoms/Badge/Badge";
import { 
  getDetectionState, 
  triggerMockFound, 
  triggerMockLost, 
  clearDetection 
} from "../../../services/detectionService";

const ENABLE_MOCK_CONTROLS = import.meta.env.VITE_ENABLE_MOCK_CONTROLS === "true";

export function DetectionStatusPanel() {
  const [state, setState] = useState<any>(null);

  const refresh = async () => {
    try {
      const data = await getDetectionState();
      setState(data);
    } catch (e) {}
  };

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 2000);
    return () => clearInterval(timer);
  }, []);

  const getStatusTone = (status: string) => {
    switch (status) {
      case "TARGET_FOUND": return "green";
      case "PERSON_CANDIDATE":
      case "FACE_VISIBLE": return "blue";
      case "UNKNOWN_PERSON":
      case "FACE_NOT_CLEAR": return "orange";
      case "PROVIDER_NOT_READY":
      case "CAMERA_NOT_READY": return "red";
      default: return "neutral";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "TARGET_FOUND": return "Target Found";
      case "PERSON_CANDIDATE": return "Person Candidate";
      case "FACE_VISIBLE": return "Face Visible";
      case "UNKNOWN_PERSON": return "Unknown Person";
      case "FACE_NOT_CLEAR": return "Face Not Clear";
      case "PROVIDER_NOT_READY": return "AI Not Ready";
      case "CAMERA_NOT_READY": return "Camera Error";
      case "NO_PERSON": return "No Person";
      case "TARGET_LOST": return "Target Lost";
      default: return status || "Idle";
    }
  };

  return (
    <Card title="AI Vision & Detection">
      <div className="panel-stack">
        <div className="sensor-metric-card" style={{ 
          background: state?.status === "TARGET_FOUND" ? "#e8f5e9" : (state?.object_found ? "#e3f2fd" : "#f7f9fb"),
          transition: "all 0.3s ease"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Status:</span>
            <Badge tone={getStatusTone(state?.status)}>{getStatusLabel(state?.status)}</Badge>
          </div>
          
          {state?.object_found && (
            <div style={{ marginTop: "12px", fontSize: "14px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <div>Type: <strong>{state.object_type}</strong></div>
              <div>Conf: <strong>{(state.confidence * 100).toFixed(1)}%</strong></div>
              {state.display_name && (
                <div style={{ gridColumn: "span 2", borderTop: "1px dashed #ccc", paddingTop: "4px", marginTop: "4px" }}>
                   Identity: <strong style={{ color: "#2e7d32" }}>{state.display_name}</strong>
                </div>
              )}
            </div>
          )}
          
          {state?.message && state.message !== "Waiting" && (
            <div style={{ marginTop: "8px", fontSize: "12px", fontStyle: "italic", color: "#666" }}>
              {state.message}
            </div>
          )}
        </div>

        {ENABLE_MOCK_CONTROLS && (
          <div style={{ borderTop: "1px solid #eee", paddingTop: "12px" }}>
            <div style={{ fontSize: "12px", marginBottom: "8px", color: "#666" }}>Mock Controls (Testing Only)</div>
            <div className="command-button-group">
              <Button onClick={() => triggerMockFound("person")} disabled={state?.object_found}>
                Mock Person Found
              </Button>
              <Button onClick={() => triggerMockLost()} disabled={!state?.object_found}>
                Mock Lost
              </Button>
              <Button onClick={() => clearDetection()}>
                Clear
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
