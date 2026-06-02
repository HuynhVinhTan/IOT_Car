import { apiRequest } from "./apiClient";

export interface TrainingSession {
  session_id: string;
  session_name: string;
  map_id: string;
  segment_id: string;
  direction: string;
  start_node: string;
  target_node: string;
  status: string;
  sample_count: number;
  created_at_ms: number;
  output_dir: string;
}

export function getTrainingStatus() {
  return apiRequest<any>("/api/training/status");
}

export function startTrainingSession(data: {
  session_name: string;
  segment_id: string;
  direction: string;
  start_node: string;
  target_node: string;
}) {
  return apiRequest<TrainingSession>("/api/training/sessions/start", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function stopTrainingSession() {
  return apiRequest<TrainingSession>("/api/training/sessions/stop", { method: "POST" });
}

export function getCurrentTrainingSession() {
  return apiRequest<TrainingSession>("/api/training/sessions/current");
}

export function listTrainingSessions() {
  return apiRequest<TrainingSession[]>("/api/training/sessions");
}

export function recordTrainingSample() {
  return apiRequest("/api/training/samples", { method: "POST" });
}

export function exportDataset(sessionId: string) {
  return apiRequest("/api/training/export", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}
