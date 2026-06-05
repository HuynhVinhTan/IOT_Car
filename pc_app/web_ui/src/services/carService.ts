import { apiRequest } from "./apiClient";
import type { CarCommand } from "../types/command";
import type { DriveMode } from "../types/carTelemetry";

export async function getCarStatus() {
  const res: any = await apiRequest("/api/car/status", {
    method: "GET",
  });
  if (res && res.ok === false) {
    throw new Error(res.reason || "Failed to get car status");
  }
  return res;
}

export async function sendCarCommand(command: CarCommand) {
  const res: any = await apiRequest("/api/car/command", {
    method: "POST",
    body: JSON.stringify(command),
  });
  if (res && res.ok === false) {
    throw new Error(res.reason || "Failed to send command");
  }
  return res;
}

export async function setCarMode(mode: DriveMode | string) {
  const res: any = await apiRequest("/api/car/mode", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
  if (res && res.ok === false) {
    throw new Error(res.reason || "Failed to set mode");
  }
  return res;
}
