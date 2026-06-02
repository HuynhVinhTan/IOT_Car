import { BatteryIcon } from "../../atoms/BatteryIcon/BatteryIcon";
import { Badge } from "../../atoms/Badge/Badge";

interface BatteryStatusBadgeProps {
  percent?: number | null;
}

export function BatteryStatusBadge({ percent }: BatteryStatusBadgeProps) {
  const tone = percent == null ? "orange" : percent <= 20 ? "red" : "green";
  const label = percent == null ? "Battery N/A" : `Battery ${percent}%`;

  return (
    <Badge tone={tone}>
      <span className="inline-badge-content">
        <BatteryIcon percent={percent} />
        {label}
      </span>
    </Badge>
  );
}
