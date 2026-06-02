import { StatusDot } from "../../atoms/StatusDot/StatusDot";
import { Badge } from "../../atoms/Badge/Badge";

interface DashboardStatusStripProps {
  backendConnected: boolean;
  carConnected: boolean;
  remoteConnected: boolean;
  cameraReady: boolean;
  aiReady: boolean;
  isRecording: boolean;
  personFound: boolean;
}

export function DashboardStatusStrip({
  backendConnected,
  carConnected,
  remoteConnected,
  cameraReady,
  aiReady,
  isRecording,
  personFound,
}: DashboardStatusStripProps) {
  return (
    <div className="status-strip">
      <div className="status-item">
        <StatusDot connected={backendConnected} />
        <span>Backend</span>
      </div>
      <div className="status-item">
        <StatusDot connected={carConnected} />
        <span>Car ESP32</span>
      </div>
      <div className="status-item">
        <StatusDot connected={remoteConnected} />
        <span>Remote ESP8266</span>
      </div>
      <div className="status-item">
        <Badge tone={cameraReady ? "green" : "red"}>
          Camera: {cameraReady ? "READY" : "NOT READY"}
        </Badge>
      </div>
      <div className="status-item">
        <Badge tone={aiReady ? "green" : "red"}>
          AI: {aiReady ? "READY" : "NOT READY"}
        </Badge>
      </div>
      {isRecording && (
        <div className="status-item">
          <Badge tone="orange">RECORDING</Badge>
        </div>
      )}
      {personFound && (
        <div className="status-item">
          <Badge tone="green">PERSON FOUND</Badge>
        </div>
      )}
    </div>
  );
}
