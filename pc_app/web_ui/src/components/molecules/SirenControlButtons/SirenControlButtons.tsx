import { Button } from "../../atoms/Button/Button";

interface SirenControlButtonsProps {
  onTestAlert: () => void;
  onStopAlert: () => void;
  disabled?: boolean;
}

export function SirenControlButtons({
  onTestAlert,
  onStopAlert,
  disabled = false,
  isAlerting = false,
}: SirenControlButtonsProps & { isAlerting?: boolean }) {
  return (
    <div className="command-button-group">
      <Button 
        onClick={onTestAlert} 
        disabled={disabled || isAlerting} 
        variant="primary"
        isActive={isAlerting}
      >
        {isAlerting ? "Alerting..." : "Test Alert"}
      </Button>
      <Button onClick={onStopAlert} disabled={disabled && !isAlerting} variant="danger">
        Stop Siren
      </Button>
    </div>
  );
}
