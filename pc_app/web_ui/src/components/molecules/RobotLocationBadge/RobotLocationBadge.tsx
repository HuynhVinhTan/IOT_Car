import { MapPin } from "lucide-react";
import { Badge } from "../../atoms/Badge/Badge";

interface RobotLocationBadgeProps {
  currentNode?: string | null;
}

export function RobotLocationBadge({ currentNode }: RobotLocationBadgeProps) {
  return (
    <Badge tone={currentNode && currentNode !== "UNKNOWN" ? "blue" : "orange"}>
      <span className="inline-badge-content">
        <MapPin size={16} />
        {currentNode && currentNode !== "" ? currentNode : "UNKNOWN"}
      </span>
    </Badge>
  );
}
