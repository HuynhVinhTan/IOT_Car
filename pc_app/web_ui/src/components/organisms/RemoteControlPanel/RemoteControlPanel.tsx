import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { Ads1115StatusBadge } from "../../molecules/Ads1115StatusBadge/Ads1115StatusBadge";
import { RemoteModeButtonStatus } from "../../molecules/RemoteModeButtonStatus/RemoteModeButtonStatus";
import type { JoystickTelemetry } from "../../../types/joystickTelemetry";

interface RemoteControlPanelProps {
  joystickTelemetry: JoystickTelemetry | null;
}

export function RemoteControlPanel({ joystickTelemetry }: RemoteControlPanelProps) {
  return (
    <Card title="Remote Control">
      <div className="panel-stack">
        <Ads1115StatusBadge connected={joystickTelemetry?.ads1115_connected} />
        <RemoteModeButtonStatus
          pressed={joystickTelemetry?.remote_mode_button_pressed}
        />
        <div className="panel-grid">
          <MetricText
            label="Joystick button"
            value={
              joystickTelemetry?.joystick_button_pressed ||
              joystickTelemetry?.button_pressed
                ? "Pressed"
                : "Released"
            }
          />
          <MetricText
            label="Remote mode button"
            value={
              joystickTelemetry?.remote_mode_button_pressed
                ? "Pressed"
                : "Released"
            }
          />
        </div>
      </div>
    </Card>
  );
}
