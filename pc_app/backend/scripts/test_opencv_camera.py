from pathlib import Path
import cv2

from app.core.loggers import logger


def main() -> None:
    output_dir = Path("storage/tmp_uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    camera_index = 0
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        logger(f"Không mở được camera index={camera_index}")
        logger("Thử đổi camera_index = 1 hoặc kiểm tra webcam có đang bị app khác chiếm không.")
        return

    ok, frame = camera.read()
    camera.release()

    if not ok or frame is None:
        logger("Mở được camera nhưng không đọc được frame.")
        return

    output_path = output_dir / "opencv_test_frame.jpg"
    cv2.imwrite(str(output_path), frame)

    height, width = frame.shape[:2]
    logger("Camera OK")
    logger(f"Frame size: {width}x{height}")
    logger(f"Saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()