import { useState } from "react";
import { Card } from "../../atoms/Card/Card";
import { RouteSegmentButton } from "../../molecules/RouteSegmentButton/RouteSegmentButton";
import { SelectedSegmentBadge } from "../../molecules/SelectedSegmentBadge/SelectedSegmentBadge";
import type { RouteSegment, RouteSelectionState } from "../../../types/routeSegment";
import "./LocalizationAssistPanel.css";

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
      <div className="localization-assist-panel">
        <div className="localization-header">
          <p className="localization-description">
            Use this panel to help the backend re-locate the robot when current node is UNKNOWN or lost.
          </p>
          <button onClick={refreshData} disabled={loading} className="localization-refresh-btn">Refresh</button>
        </div>

        <div className="localization-status-grid">
          <div className="localization-status-item">
            <div className="localization-status-label">Current Node</div>
            <div className={`localization-status-value ${selection?.current_node === "UNKNOWN" ? "unknown" : ""}`}>
              {selection?.current_node || "UNKNOWN"}
            </div>
          </div>
          <div className="localization-status-item">
            <div className="localization-status-label">Selected Segment</div>
            <SelectedSegmentBadge segmentId={selection?.selected_segment_id || null} />
          </div>
        </div>

        <div>
          <div className="localization-segments-header">
            <h4 className="localization-segments-title">Available Segments</h4>
            <button onClick={autoInfer} disabled={loading} className="localization-auto-infer-btn">
              Auto Infer
            </button>
          </div>
          <div className="localization-segments-container">
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
            {segments.length === 0 && <span className="localization-no-segments">No segments found.</span>}
          </div>
        </div>

        {selection?.selected_segment_id && (
          <div className="localization-action-buttons">
            <button
              onClick={() => select(selection.selected_segment_id!, true)}
              disabled={loading || selection.current_segment_id === selection.selected_segment_id}
              className="localization-confirm-btn"
            >
              I am on this segment
            </button>
            <button
              onClick={cancel}
              disabled={loading}
              className="localization-cancel-btn"
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
          <div className={`localization-result-message ${selection.accepted ? "success" : "error"}`}>
            {selection.reason}
          </div>
        )}
      </div>
    </Card>
  );
}
