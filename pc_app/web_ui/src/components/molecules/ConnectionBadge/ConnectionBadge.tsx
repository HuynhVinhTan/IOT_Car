import { Badge } from "../../atoms/Badge/Badge";
import { StatusDot } from "../../atoms/StatusDot/StatusDot";

interface ConnectionBadgeProps {
  label: string;
  connected: boolean;
}

export function ConnectionBadge({ label, connected }: ConnectionBadgeProps) {
  return (
    <div className="connection-badge">
      <StatusDot connected={connected} />
      <Badge tone={connected ? "green" : "red"}>
        {label}: {connected ? "Connected" : "Disconnected"}
      </Badge>
    </div>
  );
}
