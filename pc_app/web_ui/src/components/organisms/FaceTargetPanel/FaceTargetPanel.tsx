import { useState, useEffect } from "react";
import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { Badge } from "../../atoms/Badge/Badge";
import { 
  listFaceTargets, 
  registerFaceTarget, 
  deleteFaceTarget,
  getFaceStatus 
} from "../../../services/faceService";

export function FaceTargetPanel() {
  const [targets, setTargets] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    try {
      const [tList, fStatus] = await Promise.all([
        listFaceTargets(),
        getFaceStatus()
      ]);
      setTargets(tList);
      setStatus(fStatus);
    } catch (e) {}
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleRegister = async () => {
    if (!newName) return;
    setLoading(true);
    try {
      await registerFaceTarget(newName);
      setNewName("");
      refresh();
    } catch (e) {
      alert("Failed to register");
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
        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
          <input 
            type="text" 
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Person Name"
            className="button"
            style={{ flex: 1, textAlign: "left" }}
          />
          <Button variant="primary" onClick={handleRegister} disabled={loading}>
            Add
          </Button>
        </div>

        <div className="events-list" style={{ maxHeight: "200px" }}>
          {targets.length === 0 && <div style={{ textAlign: "center", color: "#888" }}>No targets registered.</div>}
          {targets.map(t => (
            <div key={t.target_person_id} style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center",
              padding: "8px",
              background: "#f7f9fb",
              borderRadius: "6px"
            }}>
              <span>{t.display_name}</span>
              <Button variant="danger" onClick={() => handleDelete(t.target_person_id)} style={{ minHeight: "24px", fontSize: "11px", padding: "0 6px" }}>
                Delete
              </Button>
            </div>
          ))}
        </div>

        <div style={{ marginTop: "12px", borderTop: "1px solid #eee", paddingTop: "8px" }}>
          <div style={{ fontSize: "12px", color: "#5d6b78" }}>
            Provider: <Badge tone={status?.embedding_provider_ready ? "green" : "red"}>
              {status?.embedding_provider_ready ? "READY" : "NOT CONFIGURED"}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  );
}
