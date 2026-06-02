interface StatusDotProps {
  connected: boolean;
}

export function StatusDot({ connected }: StatusDotProps) {
  return <span className={`status-dot ${connected ? "online" : "offline"}`} />;
}
