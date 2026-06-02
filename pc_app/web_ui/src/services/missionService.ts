import { apiRequest } from "./apiClient";

export function getMissionState() {
  return apiRequest("/api/mission");
}

export function startAutoSearchMission() {
  return apiRequest("/api/mission/auto-search/start", { method: "POST" });
}

export function stopMission() {
  return apiRequest("/api/mission/stop", { method: "POST" });
}

export function returnHomeMission() {
  return apiRequest("/api/mission/return-home", { method: "POST" });
}

export function startSearchMission(startNode: string, targetNode: string) {
  return apiRequest("/api/mission/search/start", {
    method: "POST",
    body: JSON.stringify({ start_node: startNode, target_node: targetNode })
  });
}

export function triggerMockDetection(found: boolean) {
  return apiRequest("/api/mission/search/mock-detection", {
    method: "POST",
    body: JSON.stringify({ found })
  });
}
