import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";

interface TelemetryMetricCardProps {
  label: string;
  value: string | number;
}

export function TelemetryMetricCard({ label, value }: TelemetryMetricCardProps) {
  return (
    <Card>
      <MetricText label={label} value={value} />
    </Card>
  );
}
