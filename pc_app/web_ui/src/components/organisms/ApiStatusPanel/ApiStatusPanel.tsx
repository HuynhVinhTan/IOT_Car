import { useState, useEffect } from "react";
import { Card } from "../../atoms/Card/Card";
import { StatusDot } from "../../atoms/StatusDot/StatusDot";
import { apiRequest } from "../../../services/apiClient";

export function ApiStatusPanel() {
  const [endpoints, setEndpoints] = useState<any>({
    routes: false,
    training: false,
    ai: false,
    faces: false,
    detection: false
  });

  const check = async () => {
    const checks = [
      { key: "routes", path: "/api/routes/segments" },
      { key: "training", path: "/api/training/status" },
      { key: "ai", path: "/api/ai/status" },
      { key: "faces", path: "/api/faces/status" },
      { key: "detection", path: "/api/detection/state" }
    ];

    const results: any = {};
    for (const c of checks) {
      try {
        await apiRequest(c.path);
        results[c.key] = true;
      } catch (e) {
        results[c.key] = false;
      }
    }
    setEndpoints(results);
  };

  useEffect(() => {
    check();
    const timer = setInterval(check, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <Card title="API Endpoint Connectivity">
      <div className="panel-stack">
        {Object.keys(endpoints).map(key => (
          <div key={key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ textTransform: "capitalize" }}>{key} API</span>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "12px", color: endpoints[key] ? "green" : "red" }}>
                {endpoints[key] ? "REACHABLE" : "UNREACHABLE"}
              </span>
              <StatusDot connected={endpoints[key]} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
