import { useState, useEffect } from "react";
import { Card } from "../../atoms/Card/Card";
import { Button } from "../../atoms/Button/Button";
import { Badge } from "../../atoms/Badge/Badge";
import { 
  getTrainingStatus, 
  startTrainingSession, 
  stopTrainingSession,
  exportDataset,
  recordTrainingSample 
} from "../../../services/trainingService";

export function TrainingPanel() {
  const [status, setStatus] = useState<any>(null);
  const [sessionName, setSessionName] = useState("session_001");
  const [loading, setLoading] = useState(false);

  const refreshStatus = async () => {
    try {
      const data = await getTrainingStatus();
      setStatus(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    refreshStatus();
    const timer = setInterval(refreshStatus, 3000);
    return () => clearInterval(timer);
  }, []);

  const handleStart = async () => {
    setLoading(true);
    try {
      await startTrainingSession({
        session_name: sessionName,
        segment_id: "A_B", // Hardcode for now, ideally selected from map
        direction: "A_to_B",
        start_node: "A",
        target_node: "B"
      });
      refreshStatus();
    } catch (e) {
      alert("Failed to start session");
    }
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopTrainingSession();
      refreshStatus();
    } catch (e) {
      alert("Failed to stop session");
    }
    setLoading(false);
  };

  const handleExport = async () => {
    if (!status?.current_session_id) return;
    setLoading(true);
    try {
      await exportDataset(status.current_session_id);
      alert("Dataset exported successfully");
    } catch (e) {
      alert("Export failed");
    }
    setLoading(false);
  };

  const handleSample = async () => {
    try {
      await recordTrainingSample();
      refreshStatus();
    } catch (e) {}
  };

  const isRecording = status?.status === "RECORDING";

  return (
    <Card title="Training & Recording">
      <div className="panel-stack">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Status:</span>
          <Badge tone={isRecording ? "orange" : "blue"}>{status?.status || "IDLE"}</Badge>
        </div>

        {isRecording && (
          <div className="sensor-metric-card">
            <div>Samples: <strong>{status?.sample_count || 0}</strong></div>
            <Button onClick={handleSample} variant="primary" style={{ marginTop: "8px" }}>
              Manual Tag Sample
            </Button>
          </div>
        )}

        <div className="panel-stack" style={{ gap: "8px" }}>
          {!isRecording ? (
            <>
              <input 
                type="text" 
                value={sessionName} 
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="Session Name"
                className="button"
                style={{ textAlign: "left" }}
              />
              <Button onClick={handleStart} variant="primary" disabled={loading}>
                Start Recording Session
              </Button>
            </>
          ) : (
            <Button onClick={handleStop} variant="danger" disabled={loading}>
              Stop Recording Session
            </Button>
          )}

          <Button onClick={handleExport} disabled={loading || isRecording || !status?.current_session_id}>
            Export Latest Dataset
          </Button>
        </div>

        {!status?.dataset_ready && (
          <div className="warning-text">
            ⚠️ Camera or specific AI sensors might not be ready.
          </div>
        )}
      </div>
    </Card>
  );
}
