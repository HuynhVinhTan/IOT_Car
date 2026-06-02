import { Badge } from "../../atoms/Badge/Badge";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { formatDistance } from "../../../utils/formatters";

interface SensorMetricCardProps {
  label: string;
  distanceCm?: number | null;
  danger?: boolean;
}

export function SensorMetricCard({
  label,
  distanceCm,
  danger = false,
}: SensorMetricCardProps) {
  return (
    <div className="sensor-metric-card">
      <MetricText label={label} value={formatDistance(distanceCm)} />
      <Badge tone={danger ? "red" : "green"}>{danger ? "Blocked" : "Clear"}</Badge>
    </div>
  );
}
