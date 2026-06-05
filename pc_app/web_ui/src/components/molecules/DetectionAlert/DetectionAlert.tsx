import { UserSearch } from "lucide-react";
import { AlertIcon } from "../../atoms/AlertIcon/AlertIcon";

interface DetectionAlertProps {
  personDetected?: boolean;
  confidence?: number;
  displayName?: string;
}

export function DetectionAlert({
  personDetected = false,
  confidence,
  displayName,
}: DetectionAlertProps) {
  if (!personDetected) {
    return (
      <div className="alert neutral">
        <UserSearch size={16} aria-hidden />
        <span>Chưa phát hiện người</span>
      </div>
    );
  }

  const detail = displayName
    ? `Phát hiện: ${displayName}`
    : confidence != null
      ? `Phát hiện người (độ tin cậy ${(confidence * 100).toFixed(0)}%)`
      : "Phát hiện người!";

  return (
    <div className="alert danger alert-pulse" role="alert">
      <AlertIcon active />
      <span>{detail}</span>
    </div>
  );
}
