import type { DriveMode } from "./carTelemetry";

export interface CarCommand {
  command: string;
  mode?: DriveMode;
  left_motor_speed?: number;
  right_motor_speed?: number;
  detected?: boolean;
}
