export interface RemoteRouteEvent {
  type: "remote_route_event";
  event: string;
  timestamp_ms: number;
  segment_index?: number;
  segment_id?: string;
  heading_hint_x?: number;
  heading_hint_y?: number;
}
