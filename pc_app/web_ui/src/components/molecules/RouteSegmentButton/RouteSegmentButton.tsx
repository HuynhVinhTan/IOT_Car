import type { RouteSegment } from "../../../types/routeSegment";
import "./RouteSegmentButton.css";

interface RouteSegmentButtonProps {
  segment: RouteSegment;
  isSelected?: boolean;
  isCurrent?: boolean;
  onClick: (id: string) => void;
  disabled?: boolean;
}

export function RouteSegmentButton({ segment, isSelected, isCurrent, onClick, disabled }: RouteSegmentButtonProps) {
  let className = "route-segment-button";
  if (isSelected) className += " selected";
  if (isCurrent) className += " current";
  if (segment.is_blocked) className += " blocked";
  if (segment.is_visited) className += " visited";

  return (
    <button
      className={className}
      onClick={() => onClick(segment.segment_id)}
      disabled={disabled || segment.is_blocked || !segment.is_enabled}
      title={segment.is_blocked ? "Segment Blocked" : ""}
    >
      <span className="segment-label">{segment.label}</span>
      {isCurrent && <span className="segment-badge current-badge">Here</span>}
      {segment.is_blocked && <span className="segment-badge blocked-badge">Blocked</span>}
    </button>
  );
}
