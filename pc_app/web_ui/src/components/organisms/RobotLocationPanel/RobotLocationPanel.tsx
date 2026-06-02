import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { RobotLocationBadge } from "../../molecules/RobotLocationBadge/RobotLocationBadge";
import type { CarTelemetry } from "../../../types/carTelemetry";
import { formatNumber } from "../../../utils/formatters";

interface RobotLocationPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function RobotLocationPanel({ carTelemetry }: RobotLocationPanelProps) {
  const currentPose = carTelemetry?.current_pose;

  return (
    <Card title="Robot Location">
      <div className="panel-stack">
        <RobotLocationBadge currentNode={carTelemetry?.current_node} />
        <div className="panel-grid">
          <MetricText label="Home node" value={carTelemetry?.home_node ?? "HOME"} />
          <MetricText label="Target node" value={carTelemetry?.target_node || "N/A"} />
          <MetricText label="Pose X" value={formatNumber(currentPose?.x)} />
          <MetricText label="Pose Y" value={formatNumber(currentPose?.y)} />
          <MetricText
            label="Heading"
            value={
              currentPose ? `${formatNumber(currentPose.heading_deg, 0)} deg` : "N/A"
            }
          />
          <MetricText
            label="Coverage"
            value={`${Math.round((carTelemetry?.coverage_progress ?? 0) * 100)}%`}
          />
        </div>
      </div>
    </Card>
  );
}
