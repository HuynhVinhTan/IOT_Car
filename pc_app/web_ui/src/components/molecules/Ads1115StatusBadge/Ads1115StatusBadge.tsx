import { Badge } from "../../atoms/Badge/Badge";

interface Ads1115StatusBadgeProps {
  connected?: boolean;
}

export function Ads1115StatusBadge({ connected = false }: Ads1115StatusBadgeProps) {
  return (
    <Badge tone={connected ? "green" : "red"}>
      {connected ? "ADS1115 OK" : "ADS1115 offline"}
    </Badge>
  );
}
