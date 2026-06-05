import { useEffect, useState } from "react";
import { getActiveMap } from "../services/mapService";
import type { Map } from "../services/mapService";

export function useMapState() {
  const [mapState, setMapState] = useState<Map | null>(null);

  const refreshMapState = async () => {
    try {
      const map = await getActiveMap();
      setMapState(map);
    } catch (e) {
      setMapState(null);
    }
  };

  useEffect(() => {
    refreshMapState();
    // Poll for active map changes every 2 seconds
    const interval = setInterval(refreshMapState, 2000);
    return () => clearInterval(interval);
  }, []);

  return { mapState, refreshMapState };
}
