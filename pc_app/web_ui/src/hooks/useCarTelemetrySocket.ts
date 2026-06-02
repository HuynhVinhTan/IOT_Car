import { useEffect, useState } from "react";
import type { CarTelemetry } from "../types/carTelemetry";

const WS_URL =
  import.meta.env.VITE_TELEMETRY_WS_URL ?? "ws://localhost:8000/ws/telemetry";

export function useCarTelemetrySocket() {
  const [carTelemetry, setCarTelemetry] = useState<CarTelemetry | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<unknown[]>([]);

  useEffect(() => {
    const websocket = new WebSocket(WS_URL);
    websocket.onopen = () => setConnected(true);
    websocket.onclose = () => setConnected(false);
    websocket.onmessage = (event) => {
      const websocketMessage = JSON.parse(event.data);
      if (websocketMessage.type === "car_telemetry") {
        setCarTelemetry(websocketMessage as CarTelemetry);
      }
      const eventTypes = new Set([
        "backend_event",
        "car_event",
        "command_ack",
        "detection_event",
        "joystick_command_ack",
        "remote_button_event",
        "serial_error",
      ]);

      if (eventTypes.has(websocketMessage.type)) {
        setEvents((currentEvents) => [websocketMessage, ...currentEvents].slice(0, 50));
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

  return { connected, carTelemetry, events };
}
