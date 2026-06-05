/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_TELEMETRY_WS_URL?: string;
  readonly VITE_CAMERA_WS_BASE_URL?: string;
  readonly VITE_DEFAULT_CAMERA_ID?: string;
  readonly VITE_ENABLE_MOCK_CONTROLS?: string;
  readonly VITE_STANDALONE_UI?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
