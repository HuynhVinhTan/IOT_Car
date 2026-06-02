# Smart Car Backend

FastAPI bridge between:

- Car ESP32 on `CAR_ESP32_SERIAL_PORT`
- ESP8266MOD joystick bridge on `JOYSTICK_ESP8266_SERIAL_PORT`
- Web dashboard over HTTP/WebSocket

## Run

```powershell
cd D:\AA\IOT\project\smart_car\pc_app\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:CAR_ESP32_SERIAL_PORT="COM3"
$env:JOYSTICK_ESP8266_SERIAL_PORT="COM4"
$env:ENABLE_JOYSTICK_AUDIO_ALERT="true"
$env:AUTO_STOP_CAR_ON_PERSON_DETECTED="false"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Alert endpoints

- `POST /api/joystick-alert/start`
- `POST /api/joystick-alert/stop`
- `POST /api/joystick-alert/test`
- `GET /api/joystick-alert/status`

When `POST /api/detection/person-detected` is called and
`ENABLE_JOYSTICK_AUDIO_ALERT=true`, the backend sends
`START_PERSON_FOUND_ALERT` to the ESP8266MOD joystick bridge.
