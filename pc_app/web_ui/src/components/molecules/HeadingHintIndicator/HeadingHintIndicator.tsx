interface HeadingHintIndicatorProps {
  x: number | null;
  y: number | null;
}

export function HeadingHintIndicator({ x, y }: HeadingHintIndicatorProps) {
  if (x === null || y === null || (x === 0 && y === 0)) {
    return <span style={{ color: "var(--text-secondary)" }}>No hint provided</span>;
  }

  // Calculate angle for visual arrow
  const angle = Math.atan2(y, x) * (180 / Math.PI);
  // Using an upward arrow by default (which points top, 0 deg)
  // atan2(y, x) gives 0 directly right. We need to map it visually or just show values.
  
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <div 
        style={{
          width: "24px", 
          height: "24px", 
          borderRadius: "50%", 
          background: "var(--bg-surface-hover)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "1px solid var(--border-color)",
          transform: `rotate(${angle + 90}deg)` // Adjust depending on standard SVG icon orientation
        }}
      >
        ↑
      </div>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>
        (x: {x.toFixed(2)}, y: {y.toFixed(2)})
      </span>
    </div>
  );
}
