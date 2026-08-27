import time
import requests
import cv2
import uuid
import sys
import os
from pathlib import Path

# Add project root to sys.path so we can import core
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.models import DetectionEvent, BoundingBox
import base64
from ultralytics import YOLO

SERVER_URL = "http://127.0.0.1:8000"
VEHICLE_MODEL = "models/yolo11n.pt"

def encode_image(img):
    try:
        h, w = img.shape[:2]
        max_dim = 400
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    except Exception:
        return None

def simulate():
    print("Loading model for simulation...")
    model = YOLO(VEHICLE_MODEL)
    
    demo_dir = Path("data/demo")
    
    vehicle_ids = set()
    for img in demo_dir.rglob("*.jpg"):
        if img.name.startswith("vehicle_"):
            parts = img.name.split("_")
            if len(parts) >= 2:
                vehicle_ids.add(parts[1])
                
    if not vehicle_ids:
        print("No demo images found. Run scripts/select_demo.py first.")
        return
                
    for vid in sorted(list(vehicle_ids)):
        print(f"\nSimulating journey for Vehicle {vid}")
        
        for cam_id in [1, 2, 3]:
            # The naming from select_demo.py is: vehicle_X_camera_Y.jpg
            # where Y was the real camera ID, but it's placed in the camera_N folder.
            # Let's just find ANY image in the camera_N folder for this vehicle.
            cam_dir = demo_dir / f"camera_{cam_id}"
            
            img_path = None
            if cam_dir.exists():
                for f in cam_dir.glob(f"vehicle_{vid}_*.jpg"):
                    img_path = f
                    break
                    
            if img_path and img_path.exists():
                print(f"  -> Camera {cam_id} sees vehicle...")
                img = cv2.imread(str(img_path))
                
                results = model(img, verbose=False)
                
                for r in results:
                    for b in r.boxes:
                        cls_id = int(b.cls[0])
                        if model.names[cls_id] in ["car", "truck", "bus", "motorcycle"]:
                            x1, y1, x2, y2 = map(int, b.xyxy[0])
                            crop = img[y1:y2, x1:x2]
                            
                            event = DetectionEvent(
                                event_id=str(uuid.uuid4()),
                                camera_id=cam_id,
                                timestamp=time.time(),
                                vehicle_type=model.names[cls_id],
                                confidence=float(b.conf[0]),
                                bounding_box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                                plate_detected=True, 
                                plate_confidence=0.85,
                                image_base64=encode_image(crop) if crop.size > 0 else None
                            )
                            
                            try:
                                requests.post(f"{SERVER_URL}/api/events", json=event.model_dump())
                            except Exception as e:
                                print(f"Error sending event: {e}")
                            break # Just one per image
                            
                time.sleep(3) # 3 seconds between cameras to simulate travel time

    print("\nSimulation complete!")

if __name__ == "__main__":
    simulate()
