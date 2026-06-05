import { useState, useEffect, useRef } from "react";
import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { Badge } from "../../atoms/Badge/Badge";
import {
  listFaceTargets,
  registerFaceTarget,
  deleteFaceTarget,
  getFaceStatus,
} from "../../../services/faceService";

export function FaceTargetPanel() {
  const [targets, setTargets] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [newName, setNewName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refresh = async () => {
    try {
      const [tList, fStatus] = await Promise.all([
        listFaceTargets(),
        getFaceStatus(),
      ]);
      setTargets(tList);
      setStatus(fStatus);
    } catch (e) {}
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleRegister = async () => {
    if (!newName || !selectedFile) {
      alert("Please provide both a name and an image file.");
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("display_name", newName);
      formData.append("image", selectedFile);

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
      // Using fetch directly for multipart/form-data as our apiClient might need adjustment
      const response = await fetch(`${API_BASE_URL}/api/faces/targets`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${response.status} - ${errorText}`);
      }

      setNewName("");
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      refresh();
    } catch (e) {
      alert("Failed to register target");
    }
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this target?")) return;
    try {
      await deleteFaceTarget(id);
      refresh();
    } catch (e) {}
  };

  return (
    <Card title="Face Recognition Targets">
      <div className="panel-stack">
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            marginBottom: "16px",
          }}
        >
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Person Name"
            style={{ padding: "8px" }}
          />
         {/* Ẩn input gốc, giữ nguyên ref và logic */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          style={{ display: "none" }}
        />

        {/* Button thay thế */}
        <label
          onClick={() => fileInputRef.current?.click()}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            padding: "7px 14px",
            border: "0.5px solid #b7c2cd",
            borderRadius: "8px",
            background: "#ffffff",
            color: "#172026",
            fontSize: "13px",
            fontWeight: 500,
            cursor: "pointer",
            transition: "background 0.15s",
          }}
          onMouseEnter={e => (e.currentTarget.style.background = "#f4f7fa")}
          onMouseLeave={e => (e.currentTarget.style.background = "#ffffff")}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          {selectedFile ? selectedFile.name : "Chọn ảnh..."}
        </label>
          <Button variant="primary" onClick={handleRegister} disabled={loading}>
            {loading ? "Uploading..." : "Add Target"}
          </Button>
        </div>

        <div
          className="events-list"
          style={{ maxHeight: "200px", overflowY: "auto" }}
        >
          {targets.length === 0 && (
            <div style={{ textAlign: "center", color: "#888" }}>
              No targets registered.
            </div>
          )}
          {targets.map((t) => (
            <div
              key={t.target_person_id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "8px",
                background: "#f7f9fb",
                borderRadius: "6px",
                marginBottom: "4px",
              }}
            >
              <span>{t.display_name}</span>
              <Button
                variant="danger"
                onClick={() => handleDelete(t.target_person_id)}
                style={{
                  minHeight: "24px",
                  fontSize: "11px",
                  padding: "0 6px",
                }}
              >
                Delete
              </Button>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: "12px",
            borderTop: "1px solid #eee",
            paddingTop: "8px",
          }}
        >
          <div style={{ fontSize: "12px", color: "#5d6b78" }}>
            Provider:{" "}
            <Badge tone={status?.embedding_provider_ready ? "green" : "red"}>
              {status?.embedding_provider_ready ? "READY" : "NOT CONFIGURED"}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  );
}
