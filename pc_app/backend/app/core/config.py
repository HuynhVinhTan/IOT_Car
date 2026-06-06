from pathlib import Path
from typing import Optional
from urllib.parse import quote

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    logger_format: str = Field(default="%(asctime)s - %(module)s - %(levelname)s - %(message)s", validation_alias="LOGGER_FORMAT")
    logger_level: str = Field(default="WARN", validation_alias="LOGGER_LEVEL")
    sqlalchemy_log_level: str = Field(default="WARN", validation_alias="SQLALCHEMY_LOG_LEVEL")


    # Serial Ports
    car_esp32_serial_port: str = Field(default="COM3", validation_alias="CAR_ESP32_SERIAL_PORT")
    joystick_esp8266_serial_port: str = Field(default="COM4", validation_alias="JOYSTICK_ESP8266_SERIAL_PORT")
    serial_baud_rate: int = Field(default=115200, validation_alias="SERIAL_BAUD_RATE")

    # Policy & Timeout
    enable_robot_control: bool = Field(default=True, validation_alias="ENABLE_ROBOT_CONTROL")
    remote_drive_max_motor_speed: int = Field(default=255, validation_alias="REMOTE_DRIVE_MAX_MOTOR_SPEED")
    joystick_offline_timeout_seconds: float = Field(default=1.0, validation_alias="JOYSTICK_OFFLINE_TIMEOUT_SECONDS")
    car_offline_timeout_seconds: float = Field(default=2.0, validation_alias="CAR_OFFLINE_TIMEOUT_SECONDS")
    robot_telemetry_stale_ms: int = Field(default=1500, validation_alias="ROBOT_TELEMETRY_STALE_MS")
    stop_on_person_detected: bool = Field(default=False, validation_alias="STOP_ON_PERSON_DETECTED")
    enable_person_detection: bool = Field(default=True, validation_alias="ENABLE_PERSON_DETECTED")
    enable_joystick_audio_alert: bool = Field(default=True, validation_alias="ENABLE_JOYSTICK_AUDIO_ALERT")
    auto_stop_car_on_person_detected: bool = Field(default=False, validation_alias="AUTO_STOP_CAR_ON_PERSON_DETECTED")
    remote_short_press_mode_policy: str = Field(default="cycle_safe_modes", validation_alias="REMOTE_SHORT_PRESS_MODE_POLICY")
    remote_long_press_action: str = Field(default="stop_and_idle", validation_alias="REMOTE_LONG_PRESS_ACTION")

    # Database
    database_driver: str = Field(default="postgresql+asyncpg", validation_alias="DATABASE_DRIVER")
    database_host: str = Field(default="localhost", validation_alias="DATABASE_HOST")
    database_port: int = Field(default=5432, validation_alias="DATABASE_PORT")
    database_name: str = Field(default="smart_car_ai", validation_alias="DATABASE_NAME")
    database_user: str = Field(default="postgres", validation_alias="DATABASE_USER")
    database_password: str = Field(default="postgres", validation_alias="DATABASE_PASSWORD")

    @computed_field
    @property
    def database_url(self) -> str:
        user = quote(self.database_user, safe="")
        password = quote(self.database_password, safe="")

        return (
            f"{self.database_driver}://"
            f"{user}:{password}@"
            f"{self.database_host}:{self.database_port}/"
            f"{self.database_name}"
        )

    # Cloudinary
    cloudinary_enabled: bool = Field(default=True, validation_alias="CLOUDINARY_ENABLED")
    cloudinary_cloud_name: Optional[str] = Field(default=None, validation_alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: Optional[str] = Field(default=None, validation_alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = Field(default=None, validation_alias="CLOUDINARY_API_SECRET")
    cloudinary_upload_folder: str = Field(default="smart-car-ai", validation_alias="CLOUDINARY_UPLOAD_FOLDER")

    # Local Media
    local_media_fallback_enabled: bool = Field(default=True, validation_alias="LOCAL_MEDIA_FALLBACK_ENABLED")
    local_media_root: str = Field(default="storage/local_media", validation_alias="LOCAL_MEDIA_ROOT")

    # Camera
    esp32_cam_stream_url: Optional[str] = Field(default=None, validation_alias="ESP32_CAM_STREAM_URL")
    default_camera_id: str = Field(default="car_front_camera", validation_alias="DEFAULT_CAMERA_ID")
    camera_publish_token: str = Field(default="dev-camera-token", validation_alias="CAMERA_PUBLISH_TOKEN")
    max_camera_frame_bytes: int = Field(default=200_000, validation_alias="MAX_CAMERA_FRAME_BYTES")
    camera_publish_max_fps: float = Field(default=8.0, validation_alias="CAMERA_PUBLISH_MAX_FPS")
    camera_offline_timeout_seconds: float = Field(default=5.0, validation_alias="CAMERA_OFFLINE_TIMEOUT_SECONDS")
    max_camera_viewers_per_camera: int = Field(default=4, validation_alias="MAX_CAMERA_VIEWERS_PER_CAMERA")
    camera_viewer_send_timeout_seconds: float = Field(default=0.25, validation_alias="CAMERA_VIEWER_SEND_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
