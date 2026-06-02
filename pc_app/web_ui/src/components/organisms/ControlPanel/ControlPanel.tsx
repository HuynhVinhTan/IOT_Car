import { AlertTriangle } from "lucide-react";
import { Button } from "../../atoms/Button/Button";
import { CommandButtonGroup } from "../../molecules/CommandButtonGroup/CommandButtonGroup";
import { useCarCommands } from "../../../hooks/useCarCommands";

export function ControlPanel() {
  const carCommands = useCarCommands();

  return (
    <div className="control-panel">
      <CommandButtonGroup>
        <Button onClick={carCommands.setIdle}>Idle</Button>
        <Button onClick={carCommands.setManualRemote} variant="primary">
          Manual Remote
        </Button>
        <Button onClick={carCommands.startAuto}>Auto</Button>
        <Button onClick={carCommands.resetEmergency}>Reset Emergency</Button>
        <Button onClick={carCommands.emergencyStop} variant="danger">
          <AlertTriangle size={16} /> Emergency Stop
        </Button>
      </CommandButtonGroup>
    </div>
  );
}
