import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { AudioAlertBadge } from "../../molecules/AudioAlertBadge/AudioAlertBadge";
import { SirenControlButtons } from "../../molecules/SirenControlButtons/SirenControlButtons";
import type { JoystickTelemetry } from "../../../types/joystickTelemetry";

interface JoystickAlertPanelProps {
  joystickTelemetry: JoystickTelemetry | null;
  onTestAlert: () => void;
  onStopAlert: () => void;
}

export function JoystickAlertPanel({
  joystickTelemetry,
  onTestAlert,
  onStopAlert,
}: JoystickAlertPanelProps) {
  const alertActive = joystickTelemetry?.alert_siren_active ?? false;
  const alertEnabled = joystickTelemetry?.alert_enabled ?? true;

  return (
    <Card title="Joystick Audio Alert">
      <div className="panel-stack">
        <AudioAlertBadge active={alertActive} enabled={alertEnabled} />
        <SirenControlButtons
          onTestAlert={onTestAlert}
          onStopAlert={onStopAlert}
          disabled={!alertEnabled && !alertActive}
          isAlerting={alertActive}
        />
        <div className="panel-grid">
          <MetricText label="Siren active" value={alertActive ? "Yes" : "No"} />
          <MetricText label="Alert enabled" value={alertEnabled ? "Yes" : "No"} />
        </div>
        <p className="warning-text">
          Passive buzzer uses tone sweep. Real speaker output needs a driver or amplifier.
        </p>
      </div>
    </Card>
  );
}
