import { Button } from "../../atoms/Button/Button";
import { Card } from "../../atoms/Card/Card";
import { sendCarCommand } from "../../../services/carService";

export function AutoModePanel() {
  return (
    <Card title="Auto Search">
      <div className="command-button-group">
        <Button onClick={() => sendCarCommand({ command: "START_AUTO_SEARCH" })}>
          Start Auto Search
        </Button>
        <Button onClick={() => sendCarCommand({ command: "STOP_MISSION" })}>
          Stop Mission
        </Button>
      </div>
    </Card>
  );
}
