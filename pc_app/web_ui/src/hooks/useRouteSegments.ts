import { useState, useEffect, useCallback } from "react";
import type { RouteSegment, RouteSelectionState, RouteGuidanceDecision } from "../types/routeSegment";
import { routeSegmentService } from "../services/routeSegmentService";

export function useRouteSegments() {
  const [segments, setSegments] = useState<RouteSegment[]>([]);
  const [selection, setSelection] = useState<RouteSelectionState | null>(null);
  const [guidance, setGuidance] = useState<RouteGuidanceDecision | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [segs, sel] = await Promise.all([
        routeSegmentService.getSegments(),
        routeSegmentService.getCurrentSelection()
      ]);
      setSegments(segs);
      setSelection(sel);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Backend disconnected or API error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const select = async (id: string, confirm: boolean) => {
    setLoading(true);
    try {
      const res = await routeSegmentService.selectSegment(id, confirm);
      setSelection(res);
    } finally {
      setLoading(false);
    }
  };

  const cancel = async () => {
    setLoading(true);
    try {
      const res = await routeSegmentService.cancelSegment();
      setSelection(res);
      setGuidance(null);
    } finally {
      setLoading(false);
    }
  };

  const autoInfer = async () => {
    setLoading(true);
    try {
      const res = await routeSegmentService.autoInfer();
      setSelection(res);
    } finally {
      setLoading(false);
    }
  };

  const setHint = async (id: string, x: number, y: number) => {
    setLoading(true);
    try {
      const res = await routeSegmentService.headingHint(id, x, y);
      setGuidance(res);
    } finally {
      setLoading(false);
    }
  };

  return {
    segments,
    selection,
    guidance,
    loading,
    error,
    refreshData,
    select,
    cancel,
    autoInfer,
    setHint
  };
}
