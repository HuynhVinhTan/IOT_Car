import { apiRequest } from "./apiClient";

export function getMapState() {
  return apiRequest("/api/map");
}

export function setRobotLocation(payload: {
  current_node?: string;
  home_node?: string;
  target_node?: string;
}) {
  return apiRequest("/api/navigation/location", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
