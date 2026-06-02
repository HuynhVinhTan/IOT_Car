import { Siren } from "lucide-react";

interface AlertIconProps {
  active?: boolean;
}

export function AlertIcon({ active = false }: AlertIconProps) {
  return (
    <Siren
      size={18}
      aria-label={active ? "Siren active" : "Siren inactive"}
      className={active ? "alert-icon-active" : undefined}
    />
  );
}
