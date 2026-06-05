import { useState } from "react";
import { Card } from "../../atoms/Card/Card";
import { RouteSegmentButton } from "../../molecules/RouteSegmentButton/RouteSegmentButton";
import { SelectedSegmentBadge } from "../../molecules/SelectedSegmentBadge/SelectedSegmentBadge";
import type { RouteSegment, RouteSelectionState } from "../../../types/routeSegment";

interface LocalizationAssistPanelProps {
  segments: RouteSegment[];
  selection: RouteSelectionState | null;
  loading: boolean;
  select: (id: string, confirm: boolean) => void;
  cancel: () => void;
  autoInfer: () => void;
  refreshData: () => void;
  setStartPosition?: (segmentId: string, offsetPct: number) => void;
}

export function LocalizationAssistPanel({
  segments,
  selection,
  loading,
  select,
  cancel,
  autoInfer,
  refreshData,
  setStartPosition,
}: LocalizationAssistPanelProps) {
  const [offsetPct, setOffsetPct] = useState(0);

  return (
    <Card title="Localization Assist">
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
            Use this panel to help the backend re-locate the robot when current node is UNKNOWN or lost.
          </p>
          <button onClick={refreshData} disabled={loading} style={{fontSize: "12px", border: "1px solid var(--border-color)", background: "transparent", color: "var(--text-primary)", cursor: "pointer", borderRadius: "4px", padding: "2px 8px"}}>Refresh</button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", background: "var(--bg-surface-hover)", padding: "12px", borderRadius: "4px" }}>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "uppercase", marginBottom: "4px" }}>Current Node</div>
            <div style={{ fontWeight: "bold", color: selection?.current_node === "UNKNOWN" ? "var(--status-warning)" : "var(--text-primary)" }}>
              {selection?.current_node || "UNKNOWN"}
            </div>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "uppercase", marginBottom: "4px" }}>Selected Segment</div>
            <SelectedSegmentBadge segmentId={selection?.selected_segment_id || null} />
          </div>
        </div>

        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <h4 style={{ margin: 0, fontSize: "14px" }}>Available Segments</h4>
            <button onClick={autoInfer} disabled={loading} style={{ fontSize: "11px", padding: "4px 8px", background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border-color)", borderRadius: "4px", cursor: "pointer" }}>
              Auto Infer
            </button>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {segments.map(seg => (
              <RouteSegmentButton
                key={seg.segment_id}
                segment={seg}
                isSelected={selection?.selected_segment_id === seg.segment_id}
                isCurrent={selection?.current_segment_id === seg.segment_id}
                onClick={(id) => select(id, false)}
                disabled={loading}
              />
            ))}
            {segments.length === 0 && <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>No segments found.</span>}
          </div>
        </div>

        {selection?.selected_segment_id && (
          <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
            <button
              onClick={() => select(selection.selected_segment_id!, true)}
              disabled={loading || selection.current_segment_id === selection.selected_segment_id}
              style={{ flex: 1, padding: "8px", background: "var(--brand-primary)", border: "none", color: "white", borderRadius: "4px", cursor: "pointer", opacity: loading || (selection.current_segment_id === selection.selected_segment_id) ? 0.5 : 1 }}
            >
              I am on this segment
            </button>
            <button
              onClick={cancel}
              disabled={loading}
              style={{ padding: "8px 16px", background: "var(--bg-surface)", color: "var(--status-error)", border: "1px solid var(--status-error)", borderRadius: "4px", cursor: "pointer" }}
            >
              Cancel
            </button>
          </div>
        )}

        {/* ── Start-position block: shown when a segment is selected ── */}
        {selection?.selected_segment_id && setStartPosition && (
          <div style={{ marginTop: "8px", padding: "12px", background: "var(--bg-surface-hover)", borderRadius: "4px", display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              Tôi đã đi được <strong>{offsetPct}%</strong> của đoạn <strong>{selection.selected_segment_id}</strong>
              &nbsp;— còn lại <strong>{100 - offsetPct}%</strong> đến điểm tiếp theo.
            </div>
            <input
              type="range"
              min={0}
              max={99}
              value={offsetPct}
              onChange={(e) => setOffsetPct(Number(e.target.value))}
              style={{ width: "100%", cursor: "pointer" }}
            />
            <button
              onClick={() => setStartPosition(selection.selected_segment_id!, offsetPct / 100)}
              disabled={loading}
              style={{ padding: "8px", background: "var(--status-success, #28a745)", border: "none", color: "white", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", opacity: loading ? 0.5 : 1 }}
            >
              ▶ Bắt đầu chạy từ đây
            </button>
          </div>
        )}

        {selection && selection.reason && (
          <div style={{ padding: "8px", background: selection.accepted ? "rgba(40, 167, 69, 0.1)" : "rgba(220, 53, 69, 0.1)", color: selection.accepted ? "var(--status-success)" : "var(--status-error)", borderRadius: "4px", fontSize: "12px" }}>
            {selection.reason}
          </div>
        )}
      </div>
    </Card>
  );
}
