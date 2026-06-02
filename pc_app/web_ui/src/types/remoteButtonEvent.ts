export interface RemoteButtonEvent {
  type: "remote_button_event";
  event: "mode_button_short_press" | "mode_button_long_press";
  timestamp_ms: number;
}
