import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { CliffAlertBadge } from "../../molecules/CliffAlertBadge/CliffAlertBadge";
import type { CarTelemetry } from "../../../types/carTelemetry";
import { formatDistance } from "../../../utils/formatters";

interface CliffSafetyPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function CliffSafetyPanel({ carTelemetry }: CliffSafetyPanelProps) {
  return (
    <Card title="Cliff Safety">
      <div className="panel-stack">
        <CliffAlertBadge cliffDetected={carTelemetry?.cliff_detected} />
        <div className="panel-grid">
          <MetricText
            label="Front left ground"
            value={formatDistance(carTelemetry?.front_left_ground_cm)}
          />
          <MetricText
            label="Front right ground"
            value={formatDistance(carTelemetry?.front_right_ground_cm)}
          />
          <MetricText
            label="Rear left ground"
            value={formatDistance(carTelemetry?.rear_left_ground_cm)}
          />
          <MetricText
            label="Rear right ground"
            value={formatDistance(carTelemetry?.rear_right_ground_cm)}
          />
          <MetricText
            label="Forward unsafe"
            value={carTelemetry?.forward_unsafe ? "Yes" : "No"}
          />
          <MetricText
            label="Backward unsafe"
            value={carTelemetry?.backward_unsafe ? "Yes" : "No"}
          />
        </div>
      </div>
    </Card>
  );
}
