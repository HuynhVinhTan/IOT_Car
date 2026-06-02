import { Badge } from "../../atoms/Badge/Badge";

interface CliffAlertBadgeProps {
  cliffDetected?: boolean;
}

export function CliffAlertBadge({ cliffDetected = false }: CliffAlertBadgeProps) {
  return (
    <Badge tone={cliffDetected ? "red" : "green"}>
      {cliffDetected ? "Cliff detected" : "Ground safe"}
    </Badge>
  );
}
