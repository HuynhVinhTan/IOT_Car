# Smart Car Web UI

React/Vite dashboard for the two-board architecture:

- ESP32-WROOM car controller
- ESP8266MOD joystick bridge
- FastAPI backend as the only serial bridge

## Run

```powershell
cd D:\AA\IOT\project\smart_car\pc_app\web_ui
npm install
npm run dev
```

Open `http://localhost:5173`.

The dashboard shows the ESP32-WROOM battery/LCD status and the ESP8266MOD
audio alert state. The siren buttons call the FastAPI backend; the browser never
reads COM ports directly.
