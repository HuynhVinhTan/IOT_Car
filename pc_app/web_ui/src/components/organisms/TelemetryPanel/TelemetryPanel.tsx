import { TelemetryMetricCard } from "../../molecules/TelemetryMetricCard/TelemetryMetricCard";
import type { CarTelemetry } from "../../../types/carTelemetry";

interface TelemetryPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function TelemetryPanel({ carTelemetry }: TelemetryPanelProps) {
  return (
    <div className="telemetry-grid">
      <TelemetryMetricCard label="Obstacle" value={carTelemetry?.obstacle_detected ? "Yes" : "No"} />
      <TelemetryMetricCard label="Recording" value={carTelemetry?.is_recording ? "Yes" : "No"} />
      <TelemetryMetricCard label="Auto running" value={carTelemetry?.is_auto_running ? "Yes" : "No"} />
      <TelemetryMetricCard label="Control source" value={carTelemetry?.control_source ?? "NONE"} />
    </div>
  );
}
