import { AlertIcon } from "../../atoms/AlertIcon/AlertIcon";
import { Badge } from "../../atoms/Badge/Badge";

interface AudioAlertBadgeProps {
  active?: boolean;
  enabled?: boolean;
}

export function AudioAlertBadge({ active = false, enabled = false }: AudioAlertBadgeProps) {
  const tone = active ? "red" : enabled ? "green" : "neutral";
  const label = active ? "Siren active" : enabled ? "Siren armed" : "Siren disabled";

  return (
    <Badge tone={tone}>
      <span className="inline-badge-content">
        <AlertIcon active={active} />
        {label}
      </span>
    </Badge>
  );
}
