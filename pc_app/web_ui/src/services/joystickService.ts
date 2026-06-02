import { apiRequest } from "./apiClient";

export function startJoystickAlert() {
  return apiRequest("/api/joystick-alert/start", { method: "POST" });
}

export function stopJoystickAlert() {
  return apiRequest("/api/joystick-alert/stop", { method: "POST" });
}

export function testJoystickAlert() {
  return apiRequest("/api/joystick-alert/test", { method: "POST" });
}

export function setJoystickAlertEnabled(enabled: boolean) {
  return apiRequest("/api/joystick-alert/enabled", {
    method: "POST",
    body: JSON.stringify({ enabled }),
  });
}

export function getJoystickAlertStatus() {
  return apiRequest("/api/joystick-alert/status");
}
