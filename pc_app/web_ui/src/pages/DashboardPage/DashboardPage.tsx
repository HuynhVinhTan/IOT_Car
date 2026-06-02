import { useState, useEffect } from "react";
import { ConnectionBadge } from "../../components/molecules/ConnectionBadge/ConnectionBadge";
import { ModeBadge } from "../../components/molecules/ModeBadge/ModeBadge";
import { CameraPanel } from "../../components/organisms/CameraPanel/CameraPanel";
import { MapPanel } from "../../components/organisms/MapPanel/MapPanel";
import { DashboardLayout } from "../../components/templates/DashboardLayout/DashboardLayout";
import { OperationModeSwitcher, type DashboardMode } from "../../components/organisms/OperationModeSwitcher/OperationModeSwitcher";
import { DashboardStatusStrip } from "../../components/organisms/DashboardStatusStrip/DashboardStatusStrip";
import { ModePanelSwitcher } from "../../components/organisms/ModePanelSwitcher/ModePanelSwitcher";
import { useCarTelemetrySocket } from "../../hooks/useCarTelemetrySocket";
import { useJoystickTelemetrySocket } from "../../hooks/useJoystickTelemetrySocket";
import { useRouteSegments } from "../../hooks/useRouteSegments";
import { stopJoystickAlert } from "../../services/joystickService";
import { getAIStatus, type AIStatus } from "../../services/aiService";
import { getTrainingStatus } from "../../services/trainingService";
import { getDetectionState } from "../../services/detectionService";

export function DashboardPage() {
  const [activeMode, setActiveMode] = useState<DashboardMode>("overview");
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [trainingStatus, setTrainingStatus] = useState<any>(null);
  const [detectionState, setDetectionState] = useState<any>(null);

  const { connected: carSocketConnected, carTelemetry, events } =
    useCarTelemetrySocket();
  const { connected: joystickSocketConnected, joystickTelemetry } =
    useJoystickTelemetrySocket();
    
  const { 
    segments, 
    selection, 
    guidance,
    loading: routeLoading, 
    error: routeError,
    select,
    cancel,
    autoInfer,
    refreshData
  } = useRouteSegments();

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [a, t, d] = await Promise.all([
          getAIStatus(),
          getTrainingStatus(),
          getDetectionState()
        ]);
        setAiStatus(a);
        setTrainingStatus(t);
        setDetectionState(d);
      } catch (e) {}
    };
    fetchStatus();
    const timer = setInterval(fetchStatus, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <DashboardLayout
      header={
        <>
          <div>
            <h1>Smart Car Console</h1>
            <p>Robotics AI Platform v2.0</p>
          </div>
          <div className="header-status">
            <ConnectionBadge label="Car ESP32" connected={carSocketConnected} />
            <ConnectionBadge label="Remote ESP8266" connected={joystickSocketConnected} />
            <ModeBadge mode={carTelemetry?.mode} />
          </div>
        </>
      }
      toolbar={
        <OperationModeSwitcher 
          activeMode={activeMode} 
          onModeChange={setActiveMode} 
        />
      }
      subHeader={
        <DashboardStatusStrip 
          backendConnected={true} // If API calls succeed
          carConnected={carSocketConnected}
          remoteConnected={joystickSocketConnected}
          cameraReady={aiStatus?.camera_connected || false}
          aiReady={aiStatus?.status === "READY"}
          isRecording={trainingStatus?.status === "RECORDING"}
          personFound={detectionState?.object_found || false}
        />
      }
      left={
        <>
          <CameraPanel personDetected={carTelemetry?.person_detected} />
          <MapPanel 
            carTelemetry={carTelemetry} 
            segments={segments}
            selection={selection}
            loading={routeLoading}
            error={routeError}
          />
        </>
      }
      right={
        <ModePanelSwitcher 
          activeMode={activeMode}
          carTelemetry={carTelemetry}
          joystickTelemetry={joystickTelemetry}
          carConnected={carSocketConnected}
          joystickConnected={joystickSocketConnected}
          segments={segments}
          selection={selection}
          guidance={guidance}
          events={events}
          onStopSiren={() => void stopJoystickAlert()}
          selectSegment={select}
          cancelSegment={cancel}
          autoInfer={autoInfer}
          refreshSegments={refreshData}
        />
      }
      bottom={
        <div style={{ fontSize: "11px", color: "#888", textAlign: "center" }}>
          UI Preview Mode: <strong>{activeMode.toUpperCase()}</strong> | Real Car Mode: <strong>{carTelemetry?.mode || "UNKNOWN"}</strong>
        </div>
      }
    />
  );
}
