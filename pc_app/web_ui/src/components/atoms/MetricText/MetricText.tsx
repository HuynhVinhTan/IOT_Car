interface MetricTextProps {
  label: string;
  value: string | number;
}

export function MetricText({ label, value }: MetricTextProps) {
  return (
    <div className="metric-text">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
