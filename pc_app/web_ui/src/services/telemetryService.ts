import { apiRequest } from "./apiClient";

export function getLatestTelemetry() {
  return apiRequest("/api/telemetry/latest");
}
