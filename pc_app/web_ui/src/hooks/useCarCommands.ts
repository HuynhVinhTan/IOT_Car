import { sendCarCommand, setCarMode } from "../services/carService";

export function useCarCommands() {
  return {
    setIdle: () => setCarMode("IDLE"),
    setManualRemote: () => setCarMode("MANUAL_REMOTE"),
    startAuto: () => sendCarCommand({ command: "START_AUTO_SEARCH" }),
    stopAuto: () => sendCarCommand({ command: "STOP_MISSION" }),
    emergencyStop: () => sendCarCommand({ command: "EMERGENCY_STOP" }),
    resetEmergency: () => sendCarCommand({ command: "RESET_EMERGENCY" }),
  };
}
