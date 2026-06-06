import { Card } from "../../atoms/Card/Card";
import { MetricText } from "../../atoms/MetricText/MetricText";
import "./SystemOverviewPanel.css";

interface SystemOverviewPanelProps {
  carTelemetry: any;
  joystickConnected: boolean;
  carConnected: boolean;
}

export function SystemOverviewPanel({ 
  carTelemetry, 
  joystickConnected, 
  carConnected 
}: SystemOverviewPanelProps) {
  return (
    <Card title="System Performance Overview">
      <div className="telemetry-grid">
        <MetricText 
          label="Car Mode" 
          value={carTelemetry?.mode || "UNKNOWN"} 
        />
        <MetricText 
          label="Battery" 
          value={`${carTelemetry?.battery_voltage?.toFixed(1) || "0.0"}V`} 
        />
        <MetricText 
          label="Link Quality" 
          value={carConnected ? "Stable" : "Disconnected"} 
        />
        <MetricText 
          label="Remote Controller" 
          value={joystickConnected ? "Connected" : "Disconnected"} 
        />
        <MetricText 
          label="Mission Status" 
          value={carTelemetry?.mission_state?.mission_mode || "IDLE"} 
        />
        <MetricText 
          label="Safety Override" 
          value={carTelemetry?.forward_unsafe ? "ACTIVE" : "NONE"} 
        />
      </div>
    </Card>
  );
}
