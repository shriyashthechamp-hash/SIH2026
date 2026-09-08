import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import cv2
import time
import requests
import argparse
import base64
import uuid
import threading
import sys
import os
from queue import Queue

# Ensure core is importable even if run as a script directly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from ultralytics import YOLO
from core.models import DetectionEvent, BoundingBox, CameraStatusUpdate
from core.config import SERVER_HOST, SERVER_PORT, VEHICLE_MODEL, PLATE_MODEL, CONFIDENCE_THRESHOLD

event_queue = Queue()

def event_sender(server_url: str, camera_id: int):
    while True:
        msg_type, data = event_queue.get()
        try:
            endpoint = "/api/events" if msg_type == "event" else "/api/camera/status"
            response = requests.post(
                f"{server_url}{endpoint}",
                json=data,
                timeout=2
            )
            if response.status_code != 200:
                print(f"[ERROR] Server responded with {response.status_code} for {endpoint}")
            elif msg_type == "event":
                print(f"[CAMERA {camera_id}] Event sent successfully")
        except requests.exceptions.RequestException:
            pass # Silently drop for hackathon demo to avoid spamming logs when server is down
        finally:
            event_queue.task_done()

def encode_image(img, max_dim=640) -> str:
    try:
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    except Exception:
        return None

def run_camera_node(camera_id: int, source: str):
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    
    print(f"[CAMERA {camera_id}] Starting node...")
    print(f"[CAMERA {camera_id}] Connecting to server at {server_url}")

    sender_thread = threading.Thread(target=event_sender, args=(server_url, camera_id), daemon=True)
    sender_thread.start()
    print(f"[CAMERA {camera_id}] Connected to server thread started")

    print(f"[CAMERA {camera_id}] Loading models...")
    vehicle_model = YOLO(VEHICLE_MODEL)
    plate_model = YOLO(PLATE_MODEL)

    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)

    if not cap.isOpened():
        print(f"[ERROR] Failed to open source: {source}")
        return

    print(f"[CAMERA {camera_id}] Camera opened successfully")
    print(f"[CAMERA {camera_id}] Online and capturing.")

    frame_count = 0
    process_every = 5 

    while True:
        ret, frame = cap.read()
        if not ret:
            if not source.isdigit():
                cap.release()
                cap = cv2.VideoCapture(source)
                continue
            break

        frame_count += 1
        if frame_count % process_every != 0:
            continue

        results = vehicle_model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                vehicle_type = vehicle_model.names[class_id]
                
                if vehicle_type not in ["car", "motorcycle", "bus", "truck"]:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                vehicle_crop = frame[y1:y2, x1:x2]
                
                plate_detected = False
                plate_conf = None
                plate_bbox = None
                
                if vehicle_crop.size > 0:
                    plate_results = plate_model(vehicle_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
                    for pr in plate_results:
                        if pr.boxes and len(pr.boxes) > 0:
                            plate_detected = True
                            plate_conf = float(pr.boxes[0].conf[0])
                            px1, py1, px2, py2 = map(float, pr.boxes[0].xyxy[0])
                            plate_bbox = BoundingBox(x1=px1, y1=py1, x2=px2, y2=py2)
                            
                            # Annotate Plate on frame
                            cv2.rectangle(frame, (x1 + int(px1), y1 + int(py1)), (x1 + int(px2), y1 + int(py2)), (255, 0, 0), 2)
                            cv2.putText(frame, "PLATE", (x1 + int(px1), y1 + int(py1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            print(f"[CAMERA {camera_id}] Plate detected")
                            break 

                # Annotate Vehicle on frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{vehicle_type.upper()} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                print(f"[CAMERA {camera_id}] Vehicle detected: {vehicle_type}")

                # Encode small crop for vehicle list in UI
                img_base64 = encode_image(vehicle_crop, max_dim=200) if vehicle_crop.size > 0 else None

                event = DetectionEvent(
                    event_id=str(uuid.uuid4()),
                    camera_id=camera_id,
                    timestamp=time.time(),
                    vehicle_type=vehicle_type,
                    confidence=confidence,
                    bounding_box=BoundingBox(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2)),
                    plate_detected=plate_detected,
                    plate_confidence=plate_conf,
                    plate_box=plate_bbox,
                    image_base64=img_base64
                )
                
                event_queue.put(("event", event.model_dump()))
                
        # Send full annotated frame to dashboard as a heartbeat/status update
        full_frame_base64 = encode_image(frame, max_dim=640)
        status_update = CameraStatusUpdate(
            camera_id=camera_id,
            status="ONLINE",
            frame_base64=full_frame_base64
        )
        event_queue.put(("status", status_update.model_dump()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera-id", type=int, required=True, help="ID of this camera (1, 2, or 3)")
    parser.add_argument("--source", type=str, default="0", help="Camera source (0 for webcam, or path to video)")
    args = parser.parse_args()
    
    run_camera_node(args.camera_id, args.source)
