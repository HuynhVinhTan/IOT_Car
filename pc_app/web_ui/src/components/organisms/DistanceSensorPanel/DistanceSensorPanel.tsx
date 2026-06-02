import { Card } from "../../atoms/Card/Card";
import { SensorMetricCard } from "../../molecules/SensorMetricCard/SensorMetricCard";
import type { CarTelemetry } from "../../../types/carTelemetry";

interface DistanceSensorPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function DistanceSensorPanel({ carTelemetry }: DistanceSensorPanelProps) {
  return (
    <Card title="Distance Sensors">
      <div className="sensor-grid">
        <SensorMetricCard
          label="Front"
          distanceCm={carTelemetry?.front_distance_cm ?? carTelemetry?.distance_cm}
          danger={carTelemetry?.obstacle_front}
        />
        <SensorMetricCard
          label="Left"
          distanceCm={carTelemetry?.left_distance_cm}
          danger={carTelemetry?.obstacle_left}
        />
        <SensorMetricCard
          label="Right"
          distanceCm={carTelemetry?.right_distance_cm}
          danger={carTelemetry?.obstacle_right}
        />
        <SensorMetricCard
          label="Rear"
          distanceCm={carTelemetry?.rear_distance_cm}
          danger={carTelemetry?.obstacle_rear}
        />
      </div>
    </Card>
  );
}
