import { Badge } from "../../atoms/Badge/Badge";
import type { DriveMode } from "../../../types/carTelemetry";
import { modeTone } from "../../../utils/statusColors";

interface ModeBadgeProps {
  mode?: DriveMode;
}

export function ModeBadge({ mode = "IDLE" }: ModeBadgeProps) {
  return <Badge tone={modeTone(mode)}>{mode}</Badge>;
}
