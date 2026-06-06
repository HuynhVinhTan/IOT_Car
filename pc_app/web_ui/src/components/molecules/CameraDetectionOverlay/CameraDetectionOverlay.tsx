import { AlertIcon } from "../../atoms/AlertIcon/AlertIcon";

interface CameraDetectionOverlayProps {
  confidence?: number;
  displayName?: string;
}

export function CameraDetectionOverlay({
  confidence,
  displayName,
}: CameraDetectionOverlayProps) {
  const label = displayName
    ? `Phát hiện: ${displayName}`
    : confidence != null
      ? `Phát hiện người (${(confidence * 100).toFixed(0)}%)`
      : "Phát hiện người!";

  return (
    <div className="camera-detection-overlay" role="alert" aria-live="assertive">
      <div className="camera-detection-ring alert-ring-pulse" />
      <span className="camera-detection-chip">
        <AlertIcon active />
        {label}
      </span>
    </div>
  );
}
