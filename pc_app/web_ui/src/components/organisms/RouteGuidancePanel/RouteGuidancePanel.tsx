import { Card } from "../../atoms/Card/Card";
import { HeadingHintIndicator } from "../../molecules/HeadingHintIndicator/HeadingHintIndicator";
import type { RouteGuidanceDecision } from "../../../types/routeSegment";

interface RouteGuidancePanelProps {
  guidance: RouteGuidanceDecision | null;
}

export function RouteGuidancePanel({ guidance }: RouteGuidancePanelProps) {

  if (!guidance) return null; // Don't render until we have guidance data

  return (
    <Card title="Route Guidance">
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Safety Check</div>
            <div style={{ fontWeight: "bold", color: guidance.safety_status === "OK" ? "var(--status-success)" : "var(--status-error)" }}>
              {guidance.safety_status}
            </div>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Confidence</div>
            <div style={{ fontWeight: "bold" }}>{(guidance.confidence * 100).toFixed(0)}%</div>
          </div>
        </div>

        <div>
          <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "uppercase", marginBottom: "4px" }}>Heading Hint</div>
          <HeadingHintIndicator x={guidance.heading_hint_x} y={guidance.heading_hint_y} />
        </div>

        <div style={{ padding: "8px", background: guidance.accepted ? "rgba(40, 167, 69, 0.1)" : "rgba(220, 53, 69, 0.1)", color: guidance.accepted ? "var(--status-success)" : "var(--status-error)", borderRadius: "4px", fontSize: "12px" }}>
          {guidance.reason}
        </div>
        
      </div>
    </Card>
  );
}
