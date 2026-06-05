import { useState, useEffect, useCallback, useRef } from "react";
import { Card } from "../../atoms/Card/Card";
import {
  sendCarCommand,
  getCarStatus,
  setCarMode,
} from "../../../services/carService";
import * as mapService from "../../../services/mapService";
import type { Map } from "../../../services/mapService";

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

      // Don't block keyboard when user is typing
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
      <div
        style={{
          marginBottom: "15px",
          padding: "10px",
          background: "#f0f0f0",
          borderRadius: "5px",
          fontSize: "13px",
        }}
      >
        <strong>Status: </strong>
        {isConnected ? (
          <span style={{ color: "green" }}>Connected</span>
        ) : (
          <span style={{ color: "red" }}>Offline</span>
        )}
        {carStatus && (
          <div style={{ marginTop: "5px" }}>
            <div>Car ID: {carStatus.car_id || "N/A"}</div>
            <div>Mode: {carStatus.mode || "Unknown"}</div>
            <div>
              Last seen:{" "}
              {carStatus.last_seen_ms
                ? new Date(carStatus.last_seen_ms).toLocaleTimeString()
                : "Never"}
            </div>
            {carStatus.latest_telemetry?.remote_command_timed_out && (
              <div style={{ color: "orange" }}>⚠️ Remote command timed out</div>
            )}
            {carStatus.latest_telemetry?.safety_override_active && (
              <div style={{ color: "orange" }}>⚠️ Safety override active</div>
            )}
            {(carStatus.latest_telemetry?.obstacle_front ||
              carStatus.latest_telemetry?.forward_unsafe) && (
              <div style={{ color: "red", fontWeight: "bold" }}>
                ⚠️ Obstacle Front!
              </div>
            )}
          </div>
        )}
        {statusError && (
          <div style={{ color: "red", fontSize: "11px" }}>{statusError}</div>
        )}
        {commandError && (
          <div style={{ color: "red", fontSize: "11px" }}>{commandError}</div>
        )}
      </div>

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "15px",
          flexWrap: "wrap",
        }}
      >
        <button className="btn"
          onClick={(e) => {
            setKeyboardEnabled(!keyboardEnabled);
            e.currentTarget.blur();
          }}
          disabled={!canControl}
          style={{ fontWeight: keyboardEnabled ? "bold" : "normal" }}
        >
          {keyboardEnabled ? "Disable Keyboard" : "Enable Keyboard"}
        </button>

        {!isManualMode && isConnected && (
          <button className="btn"
            onClick={switchToManualMode}
            style={{ background: "#ffc107", color: "black" }}
          >
            Switch to Manual Remote
          </button>
        )}

        <button className="btn"
          onClick={startAutonomous}
          disabled={!isConnected || !activeMapId}
          style={{
            background: activeMapId ? "#17a2b8" : "#ccc",
            color: "white",
          }}
        >
          Start Autonomous
        </button>
      </div>

      {autonomousError && (
        <div
          style={{
            color: "red",
            marginBottom: "10px",
            fontSize: "12px",
            padding: "8px",
            border: "1px solid red",
            borderRadius: "4px",
          }}
        >
          {autonomousError}
        </div>
      )}

      {!canControl && (
        <div
          style={{
            color: "red",
            marginBottom: "10px",
            fontSize: "13px",
            fontWeight: "bold",
          }}
        >
          {!isConnected
            ? "Car controller offline"
            : "Switch to Manual Remote mode first"}
        </div>
      )}

      <div
        style={{
          marginBottom: "15px",
          padding: "10px",
          background: "#f9f9f9",
          borderRadius: "5px",
        }}
      >
        <h4 style={{ margin: "0 0 10px 0" }}>Autonomous Control</h4>
        <div style={{ marginBottom: "8px" }}>
          <strong>Active Map:</strong>
          {activeMapId ? (
            <span style={{ color: "green", marginLeft: "5px" }}>
              ✓ {maps.find((m) => m.id === activeMapId)?.name || activeMapId}
            </span>
          ) : (
            <span style={{ color: "red", marginLeft: "5px" }}>
              No active map selected
            </span>
          )}
        </div>
        <div style={{ marginBottom: "8px" }}>
          <label style={{ marginRight: "10px" }}>
            Select Map to Activate:
            <select
              value={selectedMapId}
              onChange={(e) => setSelectedMapId(e.target.value)}
              style={{ marginLeft: "5px", padding: "5px" }}
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
          <button className="button-activate"
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

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "5px",
          width: "150px",
          opacity: canControl ? 1 : 0.5,
          pointerEvents: canControl ? "auto" : "none",
        }}
      >
        <div />
        <button
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
        <button onMouseDown={stop}>STOP</button>
        <button
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
    </Card>
  );
}
