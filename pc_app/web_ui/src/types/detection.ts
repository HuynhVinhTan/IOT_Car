export interface DetectionEvent {
  id: string;
  type: "detection_event";
  event: "person_detected" | "person_lost";
  detected_at: string;
  confidence?: number | null;
}
