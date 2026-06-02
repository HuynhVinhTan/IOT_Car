import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { MetricText } from "../../atoms/MetricText/MetricText";
import { ModeBadge } from "../../molecules/ModeBadge/ModeBadge";
import type { CarTelemetry, DriveMode } from "../../../types/carTelemetry";
import {
  returnHomeMission,
  startSearchMission,
  stopMission,
  triggerMockDetection,
} from "../../../services/missionService";

const ENABLE_MOCK_CONTROLS = import.meta.env.VITE_ENABLE_MOCK_CONTROLS === "true";

interface MissionControlPanelProps {
  carTelemetry: CarTelemetry | null;
}

export function MissionControlPanel({ carTelemetry }: MissionControlPanelProps) {
  const missionMode = carTelemetry?.mission_state?.mission_mode || "IDLE";
  const isOutbound = missionMode === "SEARCH_OUTBOUND";
  const isReturning = missionMode === "SEARCH_RETURNING";
  const isFollowing = missionMode === "FOLLOWING_OBJECT";
  const isEmergency = missionMode === "EMERGENCY_STOP";
  const isMissionActive = missionMode !== "IDLE" && missionMode !== "COMPLETED";

  return (
    <Card title="Autonomous Mission Control">
      <div className="panel-grid">
        <div className="metric-text">
          <span>Mode</span>
          <ModeBadge mode={missionMode as any} />
        </div>
        <MetricText
          label="Origin"
          value={carTelemetry?.mission_state?.home_node || "A"}
        />
        <MetricText label="Target" value={carTelemetry?.mission_state?.target_node || "F"} />
        <MetricText
          label="AI Detection"
          value={carTelemetry?.mission_state?.detection_state?.message || "IDLE"}
        />
      </div>
      <div className="command-button-group mission-actions" style={{ marginBottom: "1rem" }}>
        <Button 
          onClick={() => void startSearchMission("A", "F")} 
          variant="primary"
          disabled={isMissionActive}
          isActive={isOutbound}
        >
          {isOutbound ? "Searching Out..." : "Start (A → F)"}
        </Button>
        <Button 
          onClick={() => void returnHomeMission()}
          disabled={isMissionActive && !isOutbound}
          isActive={isReturning}
        >
          {isReturning ? "Returning..." : "Return (F → A)"}
        </Button>
        <Button onClick={() => void stopMission()} variant="danger" disabled={!isMissionActive}>
          Stop Mission
        </Button>
      </div>
      {ENABLE_MOCK_CONTROLS && (
        <div className="command-button-group mission-actions">
          <Button 
            onClick={() => void triggerMockDetection(true)} 
            variant="secondary"
            disabled={!isMissionActive || isFollowing}
            isActive={isFollowing}
          >
            Mock: Found
          </Button>
          <Button 
            onClick={() => void triggerMockDetection(false)} 
            variant="secondary"
            disabled={!isFollowing}
          >
            Mock: Lost
          </Button>
        </div>
      )}
    </Card>
  );
}
