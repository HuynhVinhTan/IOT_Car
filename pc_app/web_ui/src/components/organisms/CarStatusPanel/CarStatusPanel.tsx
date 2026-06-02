import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { BatteryStatusBadge } from "../../molecules/BatteryStatusBadge/BatteryStatusBadge";
import { ModeBadge } from "../../molecules/ModeBadge/ModeBadge";
import type { CarTelemetry } from "../../../types/carTelemetry";
import { formatDistance, formatNumber } from "../../../utils/formatters";

interface CarStatusPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function CarStatusPanel({ carTelemetry }: CarStatusPanelProps) {
  return (
    <Card title="Car ESP32-WROOM">
      <div className="panel-grid">
        <MetricText label="Board" value={carTelemetry?.board ?? "ESP32_WROOM"} />
        <div className="metric-text">
          <span>Mode</span>
          <ModeBadge mode={carTelemetry?.mode} />
        </div>
        <div className="metric-text">
          <span>Battery</span>
          <BatteryStatusBadge percent={carTelemetry?.battery_percent} />
        </div>
        <MetricText label="Distance" value={formatDistance(carTelemetry?.distance_cm)} />
        <MetricText label="Speed" value={formatNumber(carTelemetry?.speed_value)} />
        <MetricText label="Left motor" value={carTelemetry?.left_motor_speed ?? 0} />
        <MetricText label="Right motor" value={carTelemetry?.right_motor_speed ?? 0} />
        <MetricText label="Path points" value={carTelemetry?.recorded_path_points ?? 0} />
      </div>
    </Card>
  );
}
