import { Battery, BatteryLow, BatteryWarning } from "lucide-react";

interface BatteryIconProps {
  percent?: number | null;
}

export function BatteryIcon({ percent }: BatteryIconProps) {
  const iconSize = 18;

  if (percent == null) {
    return <BatteryWarning size={iconSize} aria-label="Battery unknown" />;
  }

  if (percent <= 15) {
    return <BatteryWarning size={iconSize} aria-label="Battery critical" />;
  }

  if (percent <= 35) {
    return <BatteryLow size={iconSize} aria-label="Battery low" />;
  }

  return <Battery size={iconSize} aria-label="Battery" />;
}
