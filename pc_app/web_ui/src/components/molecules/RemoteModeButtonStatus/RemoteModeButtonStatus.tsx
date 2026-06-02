import { Badge } from "../../atoms/Badge/Badge";

interface RemoteModeButtonStatusProps {
  pressed?: boolean;
}

export function RemoteModeButtonStatus({
  pressed = false,
}: RemoteModeButtonStatusProps) {
  return (
    <Badge tone={pressed ? "blue" : "neutral"}>
      {pressed ? "Remote button pressed" : "Remote button released"}
    </Badge>
  );
}
