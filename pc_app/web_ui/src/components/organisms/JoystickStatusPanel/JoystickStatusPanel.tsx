import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { AudioAlertBadge } from "../../molecules/AudioAlertBadge/AudioAlertBadge";
import { Ads1115StatusBadge } from "../../molecules/Ads1115StatusBadge/Ads1115StatusBadge";
import { JoystickPreview } from "../../molecules/JoystickPreview/JoystickPreview";
import type { JoystickTelemetry } from "../../../types/joystickTelemetry";
import { formatNumber } from "../../../utils/formatters";

interface JoystickStatusPanelProps {
  joystickTelemetry: JoystickTelemetry | null;
}

export function JoystickStatusPanel({ joystickTelemetry }: JoystickStatusPanelProps) {
  return (
    <Card title="Joystick ESP8266MOD">
      <JoystickPreview joystickTelemetry={joystickTelemetry} />
      <div className="panel-grid">
        <div className="metric-text">
          <span>ADC</span>
          <Ads1115StatusBadge connected={joystickTelemetry?.ads1115_connected} />
        </div>
        <MetricText label="Raw X" value={joystickTelemetry?.raw_x ?? "N/A"} />
        <MetricText label="Raw Y" value={joystickTelemetry?.raw_y ?? "N/A"} />
        <MetricText label="Norm X" value={formatNumber(joystickTelemetry?.normalized_x)} />
        <MetricText label="Norm Y" value={formatNumber(joystickTelemetry?.normalized_y)} />
        <div className="metric-text">
          <span>Audio alert</span>
          <AudioAlertBadge
            active={joystickTelemetry?.alert_siren_active}
            enabled={joystickTelemetry?.alert_enabled}
          />
        </div>
        <MetricText
          label="Button"
          value={
            joystickTelemetry?.joystick_button_pressed ||
            joystickTelemetry?.button_pressed
              ? "Pressed"
              : "Released"
          }
        />
        <MetricText
          label="Remote mode"
          value={joystickTelemetry?.remote_mode_button_pressed ? "Pressed" : "Released"}
        />
        <MetricText label="Deadzone" value={joystickTelemetry?.deadzone_applied ? "Yes" : "No"} />
      </div>
      {joystickTelemetry?.warning ? (
        <p className="warning-text">{joystickTelemetry.warning}</p>
      ) : null}
    </Card>
  );
}
