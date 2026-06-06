import { Button } from "../../atoms/Button/Button";
import {
  LayoutDashboard,
  Gamepad2,
  Bot,
  MapPin,
  Video,
  ScanFace,
  Map,
  Stethoscope,
} from "lucide-react";
export type DashboardMode =
  | "overview"
  | "manual_remote"
  | "auto_search"
  | "localization_assist"
  | "training_recording"
  | "face_recognition"
  | "map_editor"
  | "diagnostics";

interface OperationModeSwitcherProps {
  activeMode: DashboardMode;
  onModeChange: (mode: DashboardMode) => void;
}

export function OperationModeSwitcher({
  activeMode,
  onModeChange,
}: OperationModeSwitcherProps) {
  const modes: { id: DashboardMode; label: string; icon: React.ReactNode }[] = [
    { id: "overview",            label: "Overview",            icon: <LayoutDashboard size={14} /> },
    { id: "manual_remote",       label: "Manual Remote",       icon: <Gamepad2 size={14} /> },
    { id: "auto_search",         label: "Auto Search",         icon: <Bot size={14} /> },
    { id: "localization_assist", label: "Localization Assist", icon: <MapPin size={14} /> },
    { id: "training_recording",  label: "Training",            icon: <Video size={14} /> },
    { id: "face_recognition",    label: "Face Recognition",    icon: <ScanFace size={14} /> },
    { id: "map_editor",          label: "Map Editor",          icon: <Map size={14} /> },
    { id: "diagnostics",         label: "Diagnostics",         icon: <Stethoscope size={14} /> },
  ];
  
  return (
    <div className="mode-switcher">
      {modes.map((mode) => (
        <Button
          key={mode.id}
          isActive={activeMode === mode.id}
          onClick={() => onModeChange(mode.id)}
        >
          {mode.icon}
          {mode.label}
        </Button>
      ))}
    </div>
  );
}
