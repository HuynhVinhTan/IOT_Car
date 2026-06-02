import { useEffect, useState } from "react";
import { getMissionState } from "../services/missionService";

export function useMission() {
  const [missionState, setMissionState] = useState<unknown>(null);

  useEffect(() => {
    getMissionState().then(setMissionState).catch(() => setMissionState(null));
  }, []);

  return { missionState };
}
