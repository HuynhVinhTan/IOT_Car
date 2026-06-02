import { useEffect, useState } from "react";

const WS_URL = import.meta.env.VITE_TELEMETRY_WS_URL ?? "ws://localhost:8000/ws/telemetry";

export function useTelemetrySocket() {
  const [latestMessage, setLatestMessage] = useState<unknown>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(WS_URL);
    websocket.onopen = () => setConnected(true);
    websocket.onclose = () => setConnected(false);
    websocket.onmessage = (event) => setLatestMessage(JSON.parse(event.data));

    return () => websocket.close();
  }, []);

  return { connected, latestMessage };
}
