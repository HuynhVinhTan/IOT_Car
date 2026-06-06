import { useEffect, useMemo, useState } from "react";
import type { CarTelemetry } from "../types/carTelemetry";
import type { DetectionState } from "../services/detectionService";

interface WebSocketDetectionEvent {
  type: "detection_event";
  event?: "person_detected" | "person_lost";
  object_found?: boolean;
  confidence?: number;
  display_name?: string;
}

export interface PersonDetectionInfo {
  detected: boolean;
  confidence?: number;
  displayName?: string;
}

function isDetectionEvent(event: unknown): event is WebSocketDetectionEvent {
  return (
    typeof event === "object" &&
    event !== null &&
    (event as WebSocketDetectionEvent).type === "detection_event"
  );
}

export function usePersonDetection(
  carTelemetry: CarTelemetry | null,
  detectionState: DetectionState | null,
  events: unknown[]
): PersonDetectionInfo {
  const [eventDetected, setEventDetected] = useState<boolean | null>(null);
  const [eventMeta, setEventMeta] = useState<{
    confidence?: number;
    displayName?: string;
  }>({});

  const latestDetectionEvent = useMemo(
    () => events.find(isDetectionEvent) ?? null,
    [events]
  );

  useEffect(() => {
    if (!latestDetectionEvent) {
      return;
    }

    if (
      latestDetectionEvent.event === "person_detected" ||
      latestDetectionEvent.object_found === true
    ) {
      setEventDetected(true);
      setEventMeta({
        confidence: latestDetectionEvent.confidence,
        displayName: latestDetectionEvent.display_name,
      });
      return;
    }

    if (
      latestDetectionEvent.event === "person_lost" ||
      latestDetectionEvent.object_found === false
    ) {
      setEventDetected(false);
      setEventMeta({});
    }
  }, [latestDetectionEvent]);

  const polledDetected =
    detectionState?.object_found ||
    carTelemetry?.person_detected ||
    carTelemetry?.mission_state?.detection_state?.object_found ||
    false;

  const detected = eventDetected ?? polledDetected;

  const confidence =
    eventMeta.confidence ??
    detectionState?.confidence ??
    carTelemetry?.mission_state?.detection_state?.confidence;

  const displayName =
    eventMeta.displayName ??
    (detectionState as { display_name?: string | null })?.display_name ??
    undefined;

  return {
    detected,
    confidence,
    displayName: displayName ?? undefined,
  };
}
