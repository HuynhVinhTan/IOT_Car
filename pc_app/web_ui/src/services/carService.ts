import { apiRequest } from "./apiClient";
import type { CarCommand } from "../types/command";
import type { DriveMode } from "../types/carTelemetry";

export function sendCarCommand(command: CarCommand) {
  return apiRequest("/api/car/command", {
    method: "POST",
    body: JSON.stringify(command),
  });
}

export function setCarMode(mode: DriveMode) {
  return apiRequest("/api/car/mode", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}
