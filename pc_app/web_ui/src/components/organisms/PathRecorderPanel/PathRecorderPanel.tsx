import { Button } from "../../atoms/Button/Button";
import { Card } from "../../atoms/Card/Card";
import { sendCarCommand } from "../../../services/carService";

export function PathRecorderPanel() {
  return (
    <Card title="Path Recorder">
      <div className="command-button-group">
        <Button onClick={() => sendCarCommand({ command: "START_RECORD" })}>Start Record</Button>
        <Button onClick={() => sendCarCommand({ command: "STOP_RECORD" })}>Stop Record</Button>
        <Button onClick={() => sendCarCommand({ command: "CLEAR_PATH" })}>Clear Path</Button>
      </div>
    </Card>
  );
}
