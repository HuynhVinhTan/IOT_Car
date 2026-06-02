import { Card } from "../../atoms/Card/Card";
import { Badge } from "../../atoms/Badge/Badge";
import { DetectionAlert } from "../../molecules/DetectionAlert/DetectionAlert";
import { useCameraStream } from "../../../hooks/useCameraStream";

interface CameraPanelProps {
  personDetected?: boolean;
}

export function CameraPanel({ personDetected = false }: CameraPanelProps) {
  const cameraStream = useCameraStream();
  const isLive = cameraStream.status === "LIVE";
  const frameSize = cameraStream.metadata.last_frame_size
    ? `${Math.round(cameraStream.metadata.last_frame_size / 1024)} KB`
    : "n/a";
  const fps = cameraStream.metadata.fps_estimate?.toFixed(1) ?? "0.0";

  return (
    <Card title="Camera / AI">
      <div className="camera-live-toolbar">
        <span>{cameraStream.cameraId}</span>
        <Badge tone={isLive ? "green" : cameraStream.connected ? "orange" : "red"}>
          {cameraStream.status}
        </Badge>
      </div>
      <div className="camera-live-toolbar">
        <span>FPS {fps}</span>
        <span>Frame {frameSize}</span>
        <span>Dropped {cameraStream.metadata.dropped_frames ?? 0}</span>
      </div>
      <div className="camera-live-frame">
        {cameraStream.frameUrl ? (
          <img src={cameraStream.frameUrl} alt="Live camera frame" />
        ) : (
          <span>{cameraStream.message || "Waiting for camera publisher"}</span>
        )}
      </div>
      <DetectionAlert personDetected={personDetected} />
    </Card>
  );
}
