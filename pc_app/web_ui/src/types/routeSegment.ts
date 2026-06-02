export interface RouteSegment {
  segment_id: string;
  from_node: string;
  to_node: string;
  label: string;
  is_enabled: boolean;
  is_visited: boolean;
  is_blocked: boolean;
}

export interface RouteSelectionState {
  selected_segment_id: string | null;
  current_segment_id: string | null;
  current_node: string | null;
  target_node: string | null;
  localization_source: string;
  localization_confidence: string;
  heading_hint_x: number | null;
  heading_hint_y: number | null;
  accepted: boolean;
  reason: string;
}

export interface RouteGuidanceDecision {
  accepted: boolean;
  reason: string;
  segment_id: string | null;
  current_segment_id: string | null;
  target_node: string | null;
  confidence: number;
  heading_hint_x: number | null;
  heading_hint_y: number | null;
  safety_status: string;
}
