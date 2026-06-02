import type { DriveMode } from "../types/carTelemetry";

export function modeTone(mode: DriveMode) {
  if (mode === "MANUAL_REMOTE") {
    return "blue";
  }
  if (mode === "AUTO_SEARCH" || mode === "RETURN_HOME") {
    return "green";
  }
  if (mode === "STATUS_DISPLAY" || mode === "LEARNING_MAP") {
    return "orange";
  }
  if (mode === "EMERGENCY_STOP") {
    return "red";
  }
  return "neutral";
}
