import { apiRequest } from "./apiClient";

export interface DetectionState {
  object_found: boolean;
  object_type: string;
  confidence: number;
  detected_at_ms: number;
  detected_node: string | null;
  detected_segment_id: string | null;
  follow_state: string;
  message: string;
  source: string;
}

export function getDetections() {
  return apiRequest<any[]>("/api/detection/events");
}

export function getDetectionState() {
  return apiRequest<DetectionState>("/api/detection/state");
}

export function triggerMockFound(objectType: string = "person") {
  return apiRequest("/api/detection/mock-found", {
    method: "POST",
    body: JSON.stringify({ object_type: objectType }),
  });
}

export function triggerMockLost() {
  return apiRequest("/api/detection/mock-lost", { method: "POST" });
}

export function clearDetection() {
  return apiRequest("/api/detection/clear", { method: "POST" });
}
