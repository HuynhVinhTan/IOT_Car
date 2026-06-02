import { useEffect, useState } from "react";
import { getMapState } from "../services/mapService";

export function useMapState() {
  const [mapState, setMapState] = useState<unknown>(null);

  useEffect(() => {
    getMapState().then(setMapState).catch(() => setMapState(null));
  }, []);

  return { mapState };
}
