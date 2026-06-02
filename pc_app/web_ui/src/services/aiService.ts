import { apiRequest } from "./apiClient";

export interface AIStatus {
  status: string;
  camera_connected: boolean;
  segment_model_loaded: boolean;
  face_model_loaded: boolean;
  dataset_ready: boolean;
  message: string;
}

export interface CameraStreamStatus {
  camera_id: string;
  status: string;
  publisher_connected: boolean;
  viewer_count: number;
  last_frame_at: string | null;
  last_seen_at: string | null;
  last_frame_size: number;
  frame_count: number;
  fps_estimate: number;
  dropped_frames: number;
  last_drop_reason: string | null;
  last_error: string | null;
}

export function getAIStatus() {
  return apiRequest<AIStatus>("/api/ai/status");
}

export function getCameraStreamStatus(
  cameraId: string = import.meta.env.VITE_DEFAULT_CAMERA_ID ?? "car_front_camera",
) {
  return apiRequest<CameraStreamStatus>(`/api/cameras/${cameraId}/status`);
}

export function getSegmentAIStatus() {
  return apiRequest<any>("/api/ai/map-segment/status");
}

export function predictSegment() {
  return apiRequest("/api/ai/map-segment/predict", { method: "POST" });
}
