import type { DashboardMode } from "../OperationModeSwitcher/OperationModeSwitcher";
import { SystemOverviewPanel } from "../SystemOverviewPanel/SystemOverviewPanel";
import { RemoteControlPanel } from "../RemoteControlPanel/RemoteControlPanel";
import { JoystickStatusPanel } from "../JoystickStatusPanel/JoystickStatusPanel";
import { MissionControlPanel } from "../MissionControlPanel/MissionControlPanel";
import { DetectionStatusPanel } from "../DetectionStatusPanel/DetectionStatusPanel";
import { LocalizationAssistPanel } from "../LocalizationAssistPanel/LocalizationAssistPanel";
import { RouteGuidancePanel } from "../RouteGuidancePanel/RouteGuidancePanel";
import { TrainingPanel } from "../TrainingPanel/TrainingPanel";
import { FaceTargetPanel } from "../FaceTargetPanel/FaceTargetPanel";
import { AiStatusPanel } from "../AiStatusPanel/AiStatusPanel";
import { ApiStatusPanel } from "../ApiStatusPanel/ApiStatusPanel";
import { TelemetryPanel } from "../TelemetryPanel/TelemetryPanel";
import { DetectionEventsPanel } from "../DetectionEventsPanel/DetectionEventsPanel";
import { JoystickAlertPanel } from "../JoystickAlertPanel/JoystickAlertPanel";
import { RobotLocationPanel } from "../RobotLocationPanel/RobotLocationPanel";
import { BatteryStatusPanel } from "../BatteryStatusPanel/BatteryStatusPanel";

interface ModePanelSwitcherProps {
  activeMode: DashboardMode;
  carTelemetry: any;
  joystickTelemetry: any;
  joystickConnected: boolean;
  carConnected: boolean;
  segments: any[];
  selection: any;
  guidance: any;
  events: any[];
  onStopSiren: () => void;
  selectSegment: (id: string, confirm: boolean) => void;
  cancelSegment: () => void;
  autoInfer: () => void;
  refreshSegments: () => void;
}

export function ModePanelSwitcher({
  activeMode,
  carTelemetry,
  joystickTelemetry,
  joystickConnected,
  carConnected,
  segments,
  selection,
  guidance,
  events,
  onStopSiren,
  selectSegment,
  cancelSegment,
  autoInfer,
  refreshSegments
}: ModePanelSwitcherProps) {
  switch (activeMode) {
    case "overview":
      return (
        <>
          <SystemOverviewPanel 
            carTelemetry={carTelemetry} 
            carConnected={carConnected}
            joystickConnected={joystickConnected}
          />
          <BatteryStatusPanel carTelemetry={carTelemetry} />
          <DetectionStatusPanel />
          <AiStatusPanel />
        </>
      );
    case "manual_remote":
      return (
        <>
          <RemoteControlPanel joystickTelemetry={joystickTelemetry} />
          <JoystickStatusPanel joystickTelemetry={joystickTelemetry} /> 
          <JoystickAlertPanel 
            onStopAlert={onStopSiren}
            onTestAlert={() => {}} // Not needed here if we only want stop
            joystickTelemetry={joystickTelemetry}
          />
        </>
      );
    case "auto_search":
      return (
        <>
          <MissionControlPanel carTelemetry={carTelemetry} />
          <DetectionStatusPanel />
        </>
      );
    case "localization_assist":
      return (
        <>
          <LocalizationAssistPanel 
            segments={segments}
            selection={selection}
            loading={false}
            select={selectSegment}
            cancel={cancelSegment}
            autoInfer={autoInfer}
            refreshData={refreshSegments}
          />
          <RouteGuidancePanel guidance={guidance} />
        </>
      );
    case "training_recording":
      return (
        <>
          <TrainingPanel />
          <JoystickStatusPanel joystickTelemetry={joystickTelemetry} />
        </>
      );
    case "face_recognition":
      return (
        <>
          <FaceTargetPanel />
          <DetectionStatusPanel />
          <AiStatusPanel />
        </>
      );
    case "diagnostics":
      return (
        <>
          <ApiStatusPanel />
          <BatteryStatusPanel carTelemetry={carTelemetry} />
          <RobotLocationPanel carTelemetry={carTelemetry} />
          <TelemetryPanel carTelemetry={carTelemetry} />
          <DetectionEventsPanel 
            events={events} 
            detectionState={carTelemetry?.mission_state?.detection_state}
            onStopSiren={onStopSiren}
          />
        </>
      );
    default:
      return null;
  }
}
