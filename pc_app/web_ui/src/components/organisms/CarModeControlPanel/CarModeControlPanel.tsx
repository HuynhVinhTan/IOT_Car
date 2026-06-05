import { useState } from "react";
import { Card } from "../../atoms/Card/Card";
import { setCarMode, getCarStatus } from "../../../services/carService";
import { apiRequest } from "../../../services/apiClient";
import type { DriveMode } from "../../../types/carTelemetry";
import "./CarModeControlPanel.css";

interface CarModeControlPanelProps {
  carConnected: boolean;
  currentMode: string;
  onRefreshStatus?: () => void;
}

export function CarModeControlPanel({
  carConnected,
  currentMode,
  onRefreshStatus,
}: CarModeControlPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = async (mode: DriveMode | "RESET_EMERGENCY") => {
    setLoading(true);
    setError(null);
    try {
      if (mode === "RESET_EMERGENCY") {
        const res: any = await apiRequest("/api/car/reset-emergency", {
          method: "POST",
        });
        if (res && res.ok === false) {
          throw new Error(res.reason || "Failed to reset emergency");
        }
      } else {
        const modeMap: Record<string, string> = {
          MANUAL_REMOTE: "server_control",
          AUTO_SEARCH: "autonomous",
          IDLE: "idle",
          EMERGENCY_STOP: "emergency_stop",
        };
        const mappedMode = modeMap[mode] || mode;
        await setCarMode(mappedMode);
      }

      // Refresh status after a short delay to allow car to apply mode
      setTimeout(async () => {
        if (onRefreshStatus) {
          onRefreshStatus();
        } else {
          try {
            await getCarStatus();
          } catch (e) {}
        }
      }, 500);
    } catch (err: any) {
      setError(err.message || "Failed to change mode");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Car Mode Control">
      <div className="car-mode-control">
        <div className="status-indicators">
          <div
            className={`status-badge ${carConnected ? "connected" : "offline"}`}
          >
            {carConnected ? "Connected" : "Offline"}
          </div>
          <div className="mode-badge">
            Current: <strong>{currentMode}</strong>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {!carConnected && (
          <div className="offline-warning">
            Car offline, cannot change mode locally (Backend will reject)
          </div>
        )}

        <div className="control-buttons">
          <button
            className="btn btn-primary"
            disabled={loading}
            onClick={() => handleModeChange("MANUAL_REMOTE")}
          >
            Server Control
          </button>

          <button
            className="btn btn-success"
            disabled={loading}
            onClick={() => handleModeChange("AUTO_SEARCH")}
          >
            Autonomous
          </button>

          <button
            className="btn btn-secondary"
            disabled={loading}
            onClick={() => handleModeChange("IDLE")}
          >
            Idle / Stop
          </button>

          <button
            className="btn btn-danger"
            disabled={loading}
            onClick={() => handleModeChange("EMERGENCY_STOP")}
          >
            Emergency Stop
          </button>

          <button
            className="btn btn-warning"
            disabled={loading}
            onClick={() => handleModeChange("RESET_EMERGENCY")}
          >
            Reset Emergency
          </button>
        </div>
      </div>
    </Card>
  );
}
