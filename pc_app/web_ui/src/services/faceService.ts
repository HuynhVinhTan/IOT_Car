import { apiRequest } from "./apiClient";

export interface FaceTarget {
  target_person_id: string;
  display_name: string;
  created_at_ms: number;
  is_active: boolean;
}

export function getFaceStatus() {
  return apiRequest<any>("/api/faces/status");
}

export function listFaceTargets() {
  return apiRequest<FaceTarget[]>("/api/faces/targets");
}

export function registerFaceTarget(name: string) {
  return apiRequest<FaceTarget>("/api/faces/targets", {
    method: "POST",
    body: JSON.stringify({ display_name: name }),
  });
}

export function deleteFaceTarget(targetId: string) {
  return apiRequest(`/api/faces/targets/${targetId}`, { method: "DELETE" });
}

export function verifyFaceFrame() {
  return apiRequest("/api/faces/verify-frame", { method: "POST" });
}
