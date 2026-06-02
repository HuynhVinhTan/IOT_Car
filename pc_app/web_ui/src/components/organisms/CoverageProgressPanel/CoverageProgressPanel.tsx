import { Card } from "../../atoms/Card/Card";
import type { CarTelemetry } from "../../../types/carTelemetry";

interface CoverageProgressPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function CoverageProgressPanel({
  carTelemetry,
}: CoverageProgressPanelProps) {
  const progressPercent = Math.round((carTelemetry?.coverage_progress ?? 0) * 100);

  return (
    <Card title="Coverage">
      <div className="coverage-track">
        <div
          className="coverage-fill"
          style={{ width: `${Math.min(progressPercent, 100)}%` }}
        />
      </div>
      <strong>{progressPercent}%</strong>
    </Card>
  );
}
