import { Button } from "../../atoms/Button/Button";

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
  const modes: { id: DashboardMode; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "manual_remote", label: "Manual Remote" },
    { id: "auto_search", label: "Auto Search" },
    { id: "localization_assist", label: "Localization Assist" },
    { id: "training_recording", label: "Training" },
    { id: "face_recognition", label: "Face Recognition" },
    { id: "map_editor", label: "Map Editor" },
    { id: "diagnostics", label: "Diagnostics" },
  ];

  return (
    <div className="mode-switcher">
      {modes.map((mode) => (
        <Button
          key={mode.id}
          isActive={activeMode === mode.id}
          onClick={() => onModeChange(mode.id)}
        >
          {mode.label}
        </Button>
      ))}
    </div>
  );
}
