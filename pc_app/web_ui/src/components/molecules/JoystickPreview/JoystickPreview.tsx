import type { JoystickTelemetry } from "../../../types/joystickTelemetry";
import { formatNumber } from "../../../utils/formatters";

interface JoystickPreviewProps {
  joystickTelemetry: JoystickTelemetry | null;
}

export function JoystickPreview({ joystickTelemetry }: JoystickPreviewProps) {
  const normalizedX = joystickTelemetry?.normalized_x ?? 0;
  const normalizedY = joystickTelemetry?.normalized_y ?? 0;

  return (
    <div className="joystick-preview">
      <div className="joystick-pad">
        <span
          className="joystick-dot"
          style={{
            left: `${50 + normalizedX * 42}%`,
            top: `${50 - normalizedY * 42}%`,
          }}
        />
      </div>
      <div>
        <p>X: {formatNumber(normalizedX)}</p>
        <p>Y: {formatNumber(normalizedY)}</p>
      </div>
    </div>
  );
}
