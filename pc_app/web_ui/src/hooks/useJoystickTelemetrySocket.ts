import { useEffect, useState } from "react";
import type { JoystickTelemetry } from "../types/joystickTelemetry";

const WS_URL =
  import.meta.env.VITE_TELEMETRY_WS_URL ?? "ws://localhost:8000/ws/telemetry";

export function useJoystickTelemetrySocket() {
  const [joystickTelemetry, setJoystickTelemetry] =
    useState<JoystickTelemetry | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(WS_URL);
    websocket.onopen = () => setConnected(true);
    websocket.onclose = () => setConnected(false);
    websocket.onmessage = (event) => {
      const websocketMessage = JSON.parse(event.data);
      if (websocketMessage.type === "joystick_telemetry") {
        setJoystickTelemetry(websocketMessage as JoystickTelemetry);
      }
    };

   return () => {
                  if (websocket.readyState === WebSocket.OPEN) {
                    websocket.close(1000, "component unmounted");
                  }

                  if (websocket.readyState === WebSocket.CONNECTING) {
                    websocket.addEventListener(
                      "open",
                      () => websocket.close(1000, "component unmounted"),
                      { once: true }
                    );
                  }
                };
  }, []);

  return { connected, joystickTelemetry };
}
