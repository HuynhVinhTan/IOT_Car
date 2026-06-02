import { useEffect, useMemo, useRef, useState } from "react";

const DEFAULT_CAMERA_ID = import.meta.env.VITE_DEFAULT_CAMERA_ID ?? "car_front_camera";

function getCameraWsUrl(cameraId: string) {
  const explicitBase = import.meta.env.VITE_CAMERA_WS_BASE_URL;
  if (explicitBase) {
    return `${explicitBase.replace(/\/$/, "")}/ws/cameras/${cameraId}/view`;
  }

  const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  const url = new URL(apiBase);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = `/ws/cameras/${cameraId}/view`;
  url.search = "";
  return url.toString();
}

interface CameraStatusMessage {
  type?: string;
  status?: string;
  publisher_connected?: boolean;
  viewer_count?: number;
  fps_estimate?: number;
  last_frame_size?: number;
  dropped_frames?: number;
  last_drop_reason?: string | null;
  last_error?: string | null;
  message?: string;
}

export function useCameraStream(cameraId = DEFAULT_CAMERA_ID) {
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("CONNECTING");
  const [message, setMessage] = useState("");
  const [metadata, setMetadata] = useState<CameraStatusMessage>({});
  const objectUrlRef = useRef<string | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptRef = useRef(0);

  const wsUrl = useMemo(() => getCameraWsUrl(cameraId), [cameraId]);

  useEffect(() => {
    let closed = false;
    let websocket: WebSocket | null = null;

    const cleanupFrameUrl = () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };

    const connect = () => {
      if (closed) return;
      setStatus(reconnectAttemptRef.current > 0 ? "RECONNECTING" : "CONNECTING");
      websocket = new WebSocket(wsUrl);
      websocket.binaryType = "blob";

      websocket.onopen = () => {
        if (closed) return;
        reconnectAttemptRef.current = 0;
        setConnected(true);
        setStatus("VIEWER_CONNECTED");
        setMessage("");
      };

      websocket.onmessage = (event) => {
        if (closed) return;

        if (event.data instanceof Blob) {
          const nextUrl = URL.createObjectURL(event.data);
          const previousUrl = objectUrlRef.current;
          objectUrlRef.current = nextUrl;
          setFrameUrl(nextUrl);
          setStatus("LIVE");
          setMessage("");
          if (previousUrl) URL.revokeObjectURL(previousUrl);
          return;
        }

        if (typeof event.data === "string") {
          try {
            const payload = JSON.parse(event.data) as CameraStatusMessage;
            if (payload.type === "camera_status" || payload.status) {
              setMetadata(payload);
              setStatus(payload.status ?? "UNKNOWN");
              setMessage(payload.message ?? payload.last_error ?? payload.last_drop_reason ?? "");
            }
          } catch {
            setMessage(event.data);
          }
        }
      };

      websocket.onerror = () => {
        if (closed) return;
        setStatus("ERROR");
        setMessage("Camera stream websocket error");
      };

      websocket.onclose = () => {
        if (closed) return;
        setConnected(false);
        setStatus("RECONNECTING");
        reconnectAttemptRef.current += 1;
        const delayMs = Math.min(1000 * 2 ** (reconnectAttemptRef.current - 1), 10000);
        reconnectTimerRef.current = window.setTimeout(connect, delayMs);
      };
    };

    connect();

    return () => {
      closed = true;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      if (websocket?.readyState === WebSocket.OPEN) {
        websocket.close(1000, "component unmounted");
      }
      if (websocket?.readyState === WebSocket.CONNECTING) {
        const connectingSocket = websocket;
        websocket.addEventListener(
          "open",
          () => connectingSocket.close(1000, "component unmounted"),
          { once: true },
        );
      }
      cleanupFrameUrl();
    };
  }, [wsUrl]);

  return {
    cameraId,
    connected,
    frameUrl,
    metadata,
    message,
    status,
  };
}
