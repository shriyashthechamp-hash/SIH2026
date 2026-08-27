import os
from dotenv import load_dotenv

load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

CAMERA_ID = int(os.getenv("CAMERA_ID", "1"))

VEHICLE_MODEL = os.getenv("VEHICLE_MODEL", "models/yolo11n.pt")
PLATE_MODEL = os.getenv("PLATE_MODEL", "models/license-plate-finetune-v1n.pt")

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.30"))

# Maximum seconds to wait before assuming a detection on a new camera is a new vehicle
MAX_TRANSITION_SECONDS = float(os.getenv("MAX_TRANSITION_SECONDS", "20.0"))
