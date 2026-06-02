import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { BatteryStatusBadge } from "../../molecules/BatteryStatusBadge/BatteryStatusBadge";
import type { CarTelemetry } from "../../../types/carTelemetry";
import { formatNumber } from "../../../utils/formatters";

interface BatteryStatusPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function BatteryStatusPanel({ carTelemetry }: BatteryStatusPanelProps) {
  const batteryPercent = carTelemetry?.battery_percent;

  return (
    <Card title="Battery + LCD">
      <div className="panel-stack">
        <BatteryStatusBadge percent={batteryPercent} />
        <div className="panel-grid">
          <MetricText
            label="Battery voltage"
            value={`${formatNumber(carTelemetry?.battery_voltage)} V`}
          />
          <MetricText label="Battery percent" value={batteryPercent ?? "N/A"} />
          <MetricText label="LCD status" value={carTelemetry?.lcd_status ?? "N/A"} />
          <MetricText
            label="LCD enabled"
            value={carTelemetry?.lcd_enabled ? "Yes" : "No"}
          />
          <MetricText
            label="Low battery"
            value={batteryPercent != null && batteryPercent <= 20 ? "Yes" : "No"}
          />
        </div>
      </div>
    </Card>
  );
}
