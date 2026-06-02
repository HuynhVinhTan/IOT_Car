import { useState, useEffect } from "react";
import { Card } from "../../atoms/Card/Card";
import { Badge } from "../../atoms/Badge/Badge";
import {
  getAIStatus,
  getCameraStreamStatus,
  type AIStatus,
  type CameraStreamStatus,
} from "../../../services/aiService";

export function AiStatusPanel() {
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [cameraStatus, setCameraStatus] = useState<CameraStreamStatus | null>(null);

  useEffect(() => {
    const refresh = async () => {
      try {
        const [aiData, cameraData] = await Promise.all([
          getAIStatus(),
          getCameraStreamStatus(),
        ]);
        setStatus(aiData);
        setCameraStatus(cameraData);
      } catch (e) {}
    };
    refresh();
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, []);

  const cameraTone: "green" | "red" = cameraStatus?.status === "READY" ? "green" : "red";
  const providerTone = (ready: boolean): "green" | "orange" => (ready ? "green" : "orange");

  return (
    <Card title="AI Ecosystem Status">
      <div className="panel-stack">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Overall AI:</span>
          <Badge tone={status?.status === "READY" ? "green" : "red"}>{status?.status || "UNKNOWN"}</Badge>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Camera Stream:</span>
          <Badge tone={cameraTone}>
            {cameraStatus?.status || (status?.camera_connected ? "READY" : "CAMERA_NOT_READY")}
          </Badge>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Segment Model:</span>
          <Badge tone={providerTone(Boolean(status?.segment_model_loaded))}>
            {status?.segment_model_loaded ? "READY" : "PROVIDER_NOT_READY"}
          </Badge>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Face Embedding:</span>
          <Badge tone={providerTone(Boolean(status?.face_model_loaded))}>
            {status?.face_model_loaded ? "READY" : "PROVIDER_NOT_READY"}
          </Badge>
        </div>
        
        {status?.message && (
          <div style={{ fontSize: "12px", color: "#666", fontStyle: "italic", marginTop: "4px" }}>
            {status.message}
          </div>
        )}
      </div>
    </Card>
  );
}
