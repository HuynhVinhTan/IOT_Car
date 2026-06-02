export function SelectedSegmentBadge({ segmentId }: { segmentId: string | null }) {
  if (!segmentId) {
    return <span style={{ color: "var(--text-secondary)" }}>None</span>;
  }
  return (
    <span
      style={{
        background: "var(--brand-primary)",
        color: "white",
        padding: "2px 8px",
        borderRadius: "12px",
        fontFamily: "var(--font-mono)",
        fontSize: "12px",
        fontWeight: "bold",
      }}
    >
      {segmentId}
    </span>
  );
}
