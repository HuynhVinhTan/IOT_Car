import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { MetricText } from "../../atoms/MetricText/MetricText";

interface DetectionEventsPanelProps {
  events: unknown[];
  detectionState?: any;
  onStopSiren?: () => void;
}

export function DetectionEventsPanel({ events, detectionState, onStopSiren }: DetectionEventsPanelProps) {
  return (
    <Card title="Events">
      {onStopSiren ? (
        <div className="events-toolbar">
          <Button onClick={onStopSiren} variant="secondary">
            Stop Siren
          </Button>
        </div>
      ) : null}
      {detectionState && (
        <div className="panel-grid" style={{ marginBottom: "1rem" }}>
          <MetricText label="Object found" value={detectionState.object_found ? "YES" : "NO"} />
          <MetricText label="Type" value={detectionState.object_type.toUpperCase()} />
          <MetricText label="Confidence" value={`${(detectionState.confidence * 100).toFixed(1)}%`} />
          <MetricText label="Track status" value={detectionState.follow_state.toUpperCase()} />
        </div>
      )}
      <div className="events-list">
        {events.length === 0 ? <p>No events yet</p> : null}
        {events.slice(0, 3).map((eventEntry, index) => (
          <pre key={index}>{JSON.stringify(eventEntry, null, 2)}</pre>
        ))}
      </div>
    </Card>
  );
}
