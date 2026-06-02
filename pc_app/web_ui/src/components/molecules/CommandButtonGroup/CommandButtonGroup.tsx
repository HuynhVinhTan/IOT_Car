import type { ReactNode } from "react";

interface CommandButtonGroupProps {
  children: ReactNode;
}

export function CommandButtonGroup({ children }: CommandButtonGroupProps) {
  return <div className="command-button-group">{children}</div>;
}
