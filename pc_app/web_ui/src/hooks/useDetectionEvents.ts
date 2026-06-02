import { useEffect, useState } from "react";
import { getDetections } from "../services/detectionService";
import type { DetectionEvent } from "../types/detection";

export function useDetectionEvents() {
  const [events, setEvents] = useState<DetectionEvent[]>([]);

  useEffect(() => {
    getDetections().then((response) => setEvents(response as DetectionEvent[]));
  }, []);

  return events;
}
