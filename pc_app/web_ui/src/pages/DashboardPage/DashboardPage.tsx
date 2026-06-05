import { useState, useEffect } from "react";
import { ConnectionBadge } from "../../components/molecules/ConnectionBadge/ConnectionBadge";
import { ModeBadge } from "../../components/molecules/ModeBadge/ModeBadge";
import { CameraPanel } from "../../components/organisms/CameraPanel/CameraPanel";
import { MapPanel } from "../../components/organisms/MapPanel/MapPanel";
import { DashboardLayout } from "../../components/templates/DashboardLayout/DashboardLayout";
import {
  OperationModeSwitcher,
  type DashboardMode,
} from "../../components/organisms/OperationModeSwitcher/OperationModeSwitcher";
import { DashboardStatusStrip } from "../../components/organisms/DashboardStatusStrip/DashboardStatusStrip";
import { ModePanelSwitcher } from "../../components/organisms/ModePanelSwitcher/ModePanelSwitcher";
import { CarModeControlPanel } from "../../components/organisms/CarModeControlPanel/CarModeControlPanel";
import { useCarTelemetrySocket } from "../../hooks/useCarTelemetrySocket";
import { useJoystickTelemetrySocket } from "../../hooks/useJoystickTelemetrySocket";
import { useRouteSegments } from "../../hooks/useRouteSegments";
import { stopJoystickAlert } from "../../services/joystickService";
import { getAIStatus, type AIStatus } from "../../services/aiService";
import { getTrainingStatus } from "../../services/trainingService";
import { getDetectionState } from "../../services/detectionService";
import { getCarStatus } from "../../services/carService";

export function DashboardPage() {
  const [activeMode, setActiveMode] = useState<DashboardMode>("overview");
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [trainingStatus, setTrainingStatus] = useState<any>(null);
  const [detectionState, setDetectionState] = useState<any>(null);
  const [carStatus, setCarStatus] = useState<{
    connected: boolean;
    mode: string;
  } | null>(null);

  const {
    connected: carSocketConnected,
    carTelemetry,
    events,
  } = useCarTelemetrySocket();
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
    refreshData,
    setStartPosition,
  } = useRouteSegments();

  const fetchStatus = async () => {
    try {
      const results = await Promise.allSettled([
        getAIStatus(),
        getTrainingStatus(),
        getDetectionState(),
        getCarStatus(),
      ]);

      const [aiRes, trainRes, detectRes, carRes] = results;

      if (aiRes.status === "fulfilled") setAiStatus(aiRes.value);
      if (trainRes.status === "fulfilled") setTrainingStatus(trainRes.value);
      if (detectRes.status === "fulfilled") setDetectionState(detectRes.value);
      if (carRes.status === "fulfilled") {
        setCarStatus({
          connected: (carRes.value as any).connected,
          mode: (carRes.value as any).mode,
        });
      }

      // Backend is considered connected if at least the core car status API responds
      setBackendConnected(carRes.status === "fulfilled");
    } catch (e) {
      setBackendConnected(false);
    }
  };

  useEffect(() => {
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
            <ConnectionBadge
              label="Remote ESP8266"
              connected={joystickSocketConnected}
            />
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
          backendConnected={backendConnected}
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
          carConnected={carStatus?.connected ?? carSocketConnected}
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
          setStartPosition={setStartPosition}
          onRefreshStatus={fetchStatus}
        />
      }
      bottom={
        <div style={{ fontSize: "11px", color: "#888", textAlign: "center" }}>
          UI Preview Mode: <strong>{activeMode.toUpperCase()}</strong> | Real
          Car Mode: <strong>{carTelemetry?.mode || "UNKNOWN"}</strong>
        </div>
      }
    />
  );
}
