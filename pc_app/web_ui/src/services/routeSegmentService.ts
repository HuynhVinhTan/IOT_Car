import { apiRequest } from "./apiClient";
import type { RouteSegment, RouteSelectionState, RouteGuidanceDecision } from "../types/routeSegment";

export const routeSegmentService = {
  getSegments: (): Promise<RouteSegment[]> => {
    return apiRequest<RouteSegment[]>("/api/routes/segments");
  },

  getCurrentSelection: (): Promise<RouteSelectionState> => {
    return apiRequest<RouteSelectionState>("/api/routes/current-selection");
  },

  selectSegment: (segmentId: string, confirmOnSegment: boolean): Promise<RouteSelectionState> => {
    return apiRequest<RouteSelectionState>("/api/routes/select-segment", {
      method: "POST",
      body: JSON.stringify({ segment_id: segmentId, confirm_on_segment: confirmOnSegment }),
    });
  },

  headingHint: (segmentId: string, hintX: number, hintY: number): Promise<RouteGuidanceDecision> => {
    return apiRequest<RouteGuidanceDecision>("/api/routes/heading-hint", {
      method: "POST",
      body: JSON.stringify({ segment_id: segmentId, heading_hint_x: hintX, heading_hint_y: hintY }),
    });
  },

  cancelSegment: (): Promise<RouteSelectionState> => {
    return apiRequest<RouteSelectionState>("/api/routes/cancel-segment", { method: "POST" });
  },

  setStartPosition: (segmentId: string, offsetPct: number): Promise<Record<string, unknown>> => {
    return apiRequest<Record<string, unknown>>("/api/routes/set-start-position", {
      method: "POST",
      body: JSON.stringify({ segment_id: segmentId, offset_pct: offsetPct }),
    });
  },

  autoInfer: (): Promise<RouteSelectionState> => {
    return apiRequest<RouteSelectionState>("/api/routes/auto-infer", { method: "POST" });
  },
};
