import { useEffect, useState } from "react";
import { Card } from "../../atoms/Card/Card";
import { Badge } from "../../atoms/Badge/Badge";
import { apiRequest } from "../../../services/apiClient";

interface StatusState {
  aiStatus: any;
  cameraStatus: any;
  detectionState: any;
  faceStatus: any;
  carStatus: any;
  error: string | null;
}

export function StatusPanel() {
  const [state, setState] = useState<StatusState>({
    aiStatus: null,
    cameraStatus: null,
    detectionState: null,
    faceStatus: null,
    carStatus: null,
    error: null,
  });

  const fetchStatuses = async () => {
    try {
      const [aiRes, camRes, detRes, faceRes, carRes] = await Promise.allSettled(
        [
          apiRequest("/api/ai/status"),
          apiRequest("/api/camera/status"),
          apiRequest("/api/detection/state"),
          apiRequest("/api/faces/status"),
          apiRequest("/api/car/status"),
        ],
      );

      const aiStatus = aiRes.status === "fulfilled" ? aiRes.value : null;
      const cameraStatus = camRes.status === "fulfilled" ? camRes.value : null;
      const detectionState =
        detRes.status === "fulfilled" ? detRes.value : null;
      const faceStatus = faceRes.status === "fulfilled" ? faceRes.value : null;
      const carStatus = carRes.status === "fulfilled" ? carRes.value : null;
      const error =
        aiRes.status === "rejected" ||
        camRes.status === "rejected" ||
        detRes.status === "rejected" ||
        faceRes.status === "rejected" ||
        carRes.status === "rejected"
          ? "Some status endpoints failed"
          : null;

      setState({
        aiStatus,
        cameraStatus,
        detectionState,
        faceStatus,
        carStatus,
        error,
      });
    } catch {
      setState((prev) => ({ ...prev, error: "Failed to fetch status" }));
    }
  };

  useEffect(() => {
    fetchStatuses();
    const interval = setInterval(fetchStatuses, 3000);
    return () => clearInterval(interval);
  }, []);

  if (state.error) {
    return (
      <Card title="Camera & AI Status">
        <div style={{ color: "#b91c1c", padding: "8px" }}>{state.error}</div>
      </Card>
    );
  }

  const cameraConnected =
    state.aiStatus?.camera_connected ||
    state.cameraStatus?.connected ||
    state.carStatus?.camera_connected;
  const lastFrameAge = state.cameraStatus?.last_frame_age ?? "N/A";
  const cameraId =
    state.cameraStatus?.camera_id || state.carStatus?.camera_id || "N/A";

  const insightfaceLoaded =
    state.aiStatus?.face_model_loaded ||
    state.faceStatus?.embedding_provider_ready;
  const personDetectionEnabled =
    state.aiStatus?.person_detection_enabled ??
    state.detectionState?.person_detection_enabled ??
    false;
  const personDetectionReady =
    state.aiStatus?.person_detection_ready ??
    state.detectionState?.person_detection_ready ??
    false;
  const activeTargetSet = state.faceStatus?.active_target_exists ?? false;

  return (
    <Card title="Camera & AI Status">
      <div className="panel-stack">
        {/* Camera */}
        <div className="status-row">
          <span className="status-label">Camera:</span>
          <Badge tone={cameraConnected ? "green" : "red"}>
            {cameraConnected ? "Connected" : "Offline"}
          </Badge>
        </div>
        {cameraConnected && (
          <>
            <div className="status-row">
              <span className="status-label">Camera ID:</span>
              <span style={{ fontSize: "12px", color: "#5d6b78" }}>
                {cameraId}
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">Last Frame Age:</span>
              <span style={{ fontSize: "12px", color: "#5d6b78" }}>
                {typeof lastFrameAge === "number"
                  ? `${lastFrameAge.toFixed(1)}s`
                  : String(lastFrameAge)}
              </span>
            </div>
          </>
        )}

        {/* AI Engine */}
        <div className="status-row">
          <span className="status-label">AI Engine:</span>
          <Badge tone={state.aiStatus?.status === "READY" ? "green" : "red"}>
            {state.aiStatus?.status === "READY" ? "Ready" : "Not Ready"}
          </Badge>
        </div>
        <div className="status-row">
          <span className="status-label">Face Recognition:</span>
          <Badge tone={insightfaceLoaded ? "green" : "red"}>
            {insightfaceLoaded ? "Ready" : "Not Ready"}
          </Badge>
        </div>
        <div className="status-row">
          <span className="status-label">Person Detection:</span>
          <Badge
            tone={
              personDetectionEnabled && personDetectionReady
                ? "green"
                : personDetectionEnabled
                  ? "orange"
                  : "neutral"
            }
          >
            {personDetectionEnabled
              ? personDetectionReady
                ? "Ready"
                : "Not Ready"
              : "Disabled"}
          </Badge>
        </div>
        <div className="status-row">
          <span className="status-label">Active Target:</span>
          <Badge tone={activeTargetSet ? "green" : "red"}>
            {activeTargetSet ? "Set" : "Missing"}
          </Badge>
        </div>

        {/* Detection State */}
        <div className="status-row">
          <span className="status-label">Detection State:</span>
          <span style={{ fontSize: "12px", color: "#5d6b78" }}>
            {state.detectionState?.state || "Idle"}
          </span>
        </div>
        <div className="status-row">
          <span className="status-label">Object Found:</span>
          <Badge
            tone={state.detectionState?.object_found ? "green" : "neutral"}
          >
            {state.detectionState?.object_found ? "True" : "False"}
          </Badge>
        </div>
        {state.detectionState?.confidence !== undefined && (
          <div className="status-row">
            <span className="status-label">Confidence:</span>
            <span style={{ fontSize: "12px", color: "#5d6b78" }}>
              {(state.detectionState.confidence * 100).toFixed(1)}%
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
