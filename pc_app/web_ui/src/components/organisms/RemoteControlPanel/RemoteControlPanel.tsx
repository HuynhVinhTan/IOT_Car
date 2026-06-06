import { useState, useEffect, useCallback, useRef } from "react";
import { Card } from "../../atoms/Card/Card";
import {
  sendCarCommand,
  getCarStatus,
  setCarMode,
} from "../../../services/carService";
import * as mapService from "../../../services/mapService";
import type { Map } from "../../../services/mapService";
import "./RemoteControlPanel.css";

export function RemoteControlPanel() {
  const [keyboardEnabled, setKeyboardEnabled] = useState(false);
  const [carStatus, setCarStatus] = useState<any>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [maps, setMaps] = useState<Map[]>([]);
  const [selectedMapId, setSelectedMapId] = useState<string>("");
  const [activeMapId, setActiveMapId] = useState<string | null>(null);
  const [autonomousError, setAutonomousError] = useState<string | null>(null);
  const [commandError, setCommandError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const status = await getCarStatus();
      setCarStatus(status);
      setStatusError(null);
    } catch (e: any) {
      setStatusError(e.message);
      setCarStatus(null);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    loadMaps();
    loadActiveMap();
    const timer = setInterval(fetchStatus, 2000);
    return () => clearInterval(timer);
  }, [fetchStatus]);

  const loadMaps = async () => {
    try {
      const data = await mapService.listMaps();
      setMaps(data);
    } catch (e) {
      console.error("Failed to load maps:", e);
    }
  };

  const loadActiveMap = async () => {
    try {
      const active = await mapService.getActiveMap();
      setActiveMapId(active.id);
    } catch (e) {
      setActiveMapId(null);
    }
  };

  const sendDrive = useCallback(async (left: number, right: number) => {
    try {
      const res = await sendCarCommand({
        command: "REMOTE_DRIVE",
        left_motor_speed: left,
        right_motor_speed: right,
      });
      if (res && res.ok === false)
        setCommandError("Command failed: " + (res.detail || "Unknown error"));
      else setCommandError(null);
    } catch (e: any) {
      console.error("Drive command failed:", e);
      setCommandError(e.message || "Failed to send command");
    }
  }, []);

  const stop = useCallback(async () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    try {
      const res = await sendCarCommand({ command: "REMOTE_STOP" });
      if (res && res.ok === false)
        setCommandError("Command failed: " + (res.detail || "Unknown error"));
      else setCommandError(null);
    } catch (e: any) {
      console.error("Stop command failed:", e);
      setCommandError(e.message || "Failed to stop");
    }
  }, []);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!keyboardEnabled) return;

      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }

      const speed = 150;
      let handled = false;

      if (e.key === "w" || e.key === "ArrowUp") {
        e.preventDefault();
        e.stopPropagation();
        handled = true;
        if (!intervalRef.current) {
          sendDrive(speed, speed);
          intervalRef.current = window.setInterval(
            () => sendDrive(speed, speed),
            150,
          );
        }
      } else if (e.key === "s" || e.key === "ArrowDown") {
        e.preventDefault();
        e.stopPropagation();
        handled = true;
        if (!intervalRef.current) {
          sendDrive(-speed, -speed);
          intervalRef.current = window.setInterval(
            () => sendDrive(-speed, -speed),
            150,
          );
        }
      } else if (e.key === "a" || e.key === "ArrowLeft") {
        e.preventDefault();
        e.stopPropagation();
        handled = true;
        if (!intervalRef.current) {
          sendDrive(-speed, speed);
          intervalRef.current = window.setInterval(
            () => sendDrive(-speed, speed),
            150,
          );
        }
      } else if (e.key === "d" || e.key === "ArrowRight") {
        e.preventDefault();
        e.stopPropagation();
        handled = true;
        if (!intervalRef.current) {
          sendDrive(speed, -speed);
          intervalRef.current = window.setInterval(
            () => sendDrive(speed, -speed),
            150,
          );
        }
      } else if (e.key === " ") {
        e.preventDefault();
        e.stopPropagation();
        handled = true;
        stop();
      }
    },
    [keyboardEnabled, sendDrive, stop],
  );

  const handleKeyUp = useCallback(
    (e: KeyboardEvent) => {
      if (!keyboardEnabled) return;
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }
      if (
        [
          "w",
          "s",
          "a",
          "d",
          "ArrowUp",
          "ArrowDown",
          "ArrowLeft",
          "ArrowRight",
          " ",
        ].includes(e.key)
      ) {
        e.preventDefault();
        e.stopPropagation();
        stop();
      }
    },
    [keyboardEnabled, stop],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    window.addEventListener("blur", stop);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      window.removeEventListener("blur", stop);
    };
  }, [handleKeyDown, handleKeyUp, stop]);

  const switchToManualMode = async () => {
    try {
      await setCarMode("MANUAL_REMOTE");
      await fetchStatus();
    } catch (e: any) {
      alert(`Failed to switch mode: ${e.message}`);
    }
  };

  const startAutonomous = async () => {
    setAutonomousError(null);

    if (!activeMapId) {
      setAutonomousError(
        "No active map selected. Please set a map active in Map Editor first.",
      );
      return;
    }

    try {
      const result = await setCarMode("autonomous");
      if (!result.ok) {
        setAutonomousError(`Failed: ${result.detail || result.reason}`);
      } else {
        setAutonomousError(null);
        await fetchStatus();
      }
    } catch (e: any) {
      setAutonomousError(`Error: ${e.message}`);
    }
  };

  const isConnected = carStatus?.connected === true;
  const isManualMode = carStatus?.mode === "MANUAL_REMOTE";
  const canControl = isConnected && isManualMode;

  return (
    <Card title="Remote Control">
      <div className="remote-control-panel">
        {/* Status Box */}
        <div className="remote-status-box">
          <div className="remote-status-label">
            Status:{" "}
            <span className={isConnected ? "remote-status-connected" : "remote-status-offline"}>
              {isConnected ? "Connected" : "Offline"}
            </span>
          </div>
          {carStatus && (
            <div>
              <div className="remote-status-item">Car ID: {carStatus.car_id || "N/A"}</div>
              <div className="remote-status-item">Mode: {carStatus.mode || "Unknown"}</div>
              <div className="remote-status-item">
                Last seen:{" "}
                {carStatus.last_seen_ms
                  ? new Date(carStatus.last_seen_ms).toLocaleTimeString()
                  : "Never"}
              </div>
              {carStatus.latest_telemetry?.remote_command_timed_out && (
                <div className="remote-status-item remote-status-warning">
                  ⚠️ Remote command timed out
                </div>
              )}
              {carStatus.latest_telemetry?.safety_override_active && (
                <div className="remote-status-item remote-status-warning">
                  ⚠️ Safety override active
                </div>
              )}
              {(carStatus.latest_telemetry?.obstacle_front ||
                carStatus.latest_telemetry?.forward_unsafe) && (
                <div className="remote-status-item remote-status-warning" style={{ fontWeight: "bold" }}>
                  ⚠️ Obstacle Front!
                </div>
              )}
            </div>
          )}
          {statusError && <div className="remote-status-error">{statusError}</div>}
          {commandError && <div className="remote-status-error">{commandError}</div>}
        </div>

        {/* Button Group */}
        <div className="remote-button-group">
          <button
            className={`remote-btn ${keyboardEnabled ? "active" : ""}`}
            onClick={(e) => {
              setKeyboardEnabled(!keyboardEnabled);
              e.currentTarget.blur();
            }}
            disabled={!canControl}
          >
            {keyboardEnabled ? "Disable Keyboard" : "Enable Keyboard"}
          </button>

          {!isManualMode && isConnected && (
            <button className="remote-btn warning" onClick={switchToManualMode}>
              Switch to Manual Remote
            </button>
          )}

          <button
            className={`remote-btn info`}
            onClick={startAutonomous}
            disabled={!isConnected || !activeMapId}
          >
            Start Autonomous
          </button>
        </div>

        {/* Error Messages */}
        {autonomousError && <div className="remote-error-message">{autonomousError}</div>}

        {!canControl && (
          <div className="remote-control-disabled">
            {!isConnected
              ? "Car controller offline"
              : "Switch to Manual Remote mode first"}
          </div>
        )}

        {/* Autonomous Section */}
        <div className="remote-autonomous-section">
          <h4 className="remote-autonomous-title">Autonomous Control</h4>
          <div className="remote-autonomous-item">
            <span className="remote-autonomous-label">Active Map:</span>
            {activeMapId ? (
              <span className="remote-autonomous-active">
                ✓ {maps.find((m) => m.id === activeMapId)?.name || activeMapId}
              </span>
            ) : (
              <span className="remote-autonomous-inactive">No active map selected</span>
            )}
          </div>
          <div className="remote-autonomous-item">
            <label style={{ marginRight: "10px" }}>
              Select Map to Activate:
              <select
                value={selectedMapId}
                onChange={(e) => setSelectedMapId(e.target.value)}
                className="remote-map-select"
                disabled={!isConnected}
              >
                <option value="">-- Choose a map --</option>
                {maps.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name || m.id}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="remote-activate-btn"
              onClick={async () => {
                if (selectedMapId) {
                  try {
                    await mapService.activateMap(selectedMapId);
                    setActiveMapId(selectedMapId);
                    setSelectedMapId("");
                    await loadActiveMap();
                  } catch (e) {
                    setAutonomousError(`Failed to activate map: ${e}`);
                  }
                }
              }}
              disabled={!selectedMapId || !isConnected}
            >
              Activate
            </button>
          </div>
        </div>

        {/* Control Grid */}
        <div className={`remote-control-grid ${!canControl ? "disabled" : ""}`}>
          <div />
          <button
            className="remote-control-btn"
            onMouseDown={() => {
              if (!intervalRef.current) {
                sendDrive(150, 150);
                intervalRef.current = window.setInterval(
                  () => sendDrive(150, 150),
                  150,
                );
              }
            }}
            onMouseUp={stop}
            onMouseLeave={stop}
          >
            ↑
          </button>
          <div />
          <button
            className="remote-control-btn"
            onMouseDown={() => {
              if (!intervalRef.current) {
                sendDrive(-150, 150);
                intervalRef.current = window.setInterval(
                  () => sendDrive(-150, 150),
                  150,
                );
              }
            }}
            onMouseUp={stop}
            onMouseLeave={stop}
          >
            ←
          </button>
          <button
            className="remote-control-btn remote-control-stop"
            onMouseDown={stop}
          >
            STOP
          </button>
          <button
            className="remote-control-btn"
            onMouseDown={() => {
              if (!intervalRef.current) {
                sendDrive(150, -150);
                intervalRef.current = window.setInterval(
                  () => sendDrive(150, -150),
                  150,
                );
              }
            }}
            onMouseUp={stop}
            onMouseLeave={stop}
          >
            →
          </button>
          <div />
          <button
            className="remote-control-btn"
            onMouseDown={() => {
              if (!intervalRef.current) {
                sendDrive(-150, -150);
                intervalRef.current = window.setInterval(
                  () => sendDrive(-150, -150),
                  150,
                );
              }
            }}
            onMouseUp={stop}
            onMouseLeave={stop}
          >
            ↓
          </button>
          <div />
        </div>
      </div>
    </Card>
  );
}
