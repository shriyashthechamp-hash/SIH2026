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
import re
import numpy as np
import pytesseract
from queue import Queue

def clean_text(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text

def estimate_vehicle_color(crop):
    if crop is None or crop.size == 0:
        return "UNKNOWN"
    # Basic color estimation using mean color
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    avg_h = np.mean(h)
    avg_s = np.mean(s)
    avg_v = np.mean(v)
    
    if avg_v < 50: return "BLACK"
    if avg_s < 30 and avg_v > 200: return "WHITE"
    if avg_s < 30 and avg_v > 50: return "GREY"
    if avg_s < 50 and avg_v > 150: return "SILVER"
    
    if avg_h < 10 or avg_h > 170: return "RED"
    if 10 <= avg_h < 35: return "YELLOW"
    if 35 <= avg_h < 85: return "GREEN"
    if 85 <= avg_h < 130: return "BLUE"
    
    return "UNKNOWN"

def preprocess_variants(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    contrast = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(contrast, (3, 3), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
    return {"gray": gray, "contrast": contrast, "otsu": otsu, "adaptive": adaptive}

def run_ocr(images):
    config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    readings = []
    for name, image in images.items():
        data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
        text = ""
        conf = 0.0
        words = 0
        for i, word in enumerate(data['text']):
            if word.strip():
                text += word
                conf += float(data['conf'][i])
                words += 1
        if words > 0:
            avg_conf = (conf / words) / 100.0
            clean = clean_text(text)
            if clean:
                readings.append((name, clean, avg_conf))
    return readings

def choose_result(readings):
    if not readings:
        return None, None
    valid_length = [(text, conf) for _, text, conf in readings if 8 <= len(text) <= 12]
    if valid_length:
        return max(valid_length, key=lambda x: len(x[0]))
    return max([(text, conf) for _, text, conf in readings], key=lambda x: len(x[0]))

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
                pass # Fail silently to prevent console spam
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

def print_structured_log(camera_id, vehicle_type, vehicle_conf, color, plate_detected, plate_conf, plate_text, ocr_conf):
    print("="*50)
    print(f"ANVAY CAMERA {camera_id:02d}")
    print("="*50)
    print("Status: ONLINE\n")
    print("Vehicle:")
    print(vehicle_type.upper() if vehicle_type else "UNKNOWN")
    print("\nVehicle confidence:")
    print(f"{vehicle_conf:.2f}" if vehicle_conf else "N/A")
    print("\nColour:")
    print(color if color else "UNKNOWN")
    print("\nPlate detected:")
    print("YES" if plate_detected else "NO")
    if plate_detected:
        print("\nPlate detector confidence:")
        print(f"{plate_conf:.2f}" if plate_conf else "N/A")
        print("\nOCR:")
        print(plate_text if plate_text else "NO PLATE")
        print("\nOCR confidence:")
        print(f"{ocr_conf:.2f}" if ocr_conf else "UNAVAILABLE")
    print("\nEvent: SENT")
    print("="*50)

def run_camera_node(camera_id: int, source: str):
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    
    print(f"[CAMERA {camera_id}] Starting node...")
    print(f"[CAMERA {camera_id}] Connecting to server at {server_url}")

    sender_thread = threading.Thread(target=event_sender, args=(server_url, camera_id), daemon=True)
    sender_thread.start()
    print(f"[CAMERA {camera_id}] Connected to server thread started")

    print(f"[CAMERA {camera_id}] Loading models...")
    try:
        vehicle_model = YOLO(VEHICLE_MODEL)
        plate_model = YOLO(PLATE_MODEL)
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")
        return

    try:
        if source.isdigit():
            cap = cv2.VideoCapture(int(source))
        else:
            cap = cv2.VideoCapture(source)
    except Exception as e:
        print(f"[ERROR] Failed to open source {source}: {e}")
        return

    if not cap.isOpened():
        print(f"[ERROR] Failed to open source: {source}")
        return

    print(f"[CAMERA {camera_id}] Camera opened successfully")
    print(f"[CAMERA {camera_id}] Online and capturing.")

    frame_count = 0
    process_every = 5 
    last_log_time = 0

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                if not source.isdigit():
                    # Loop video
                    cap.release()
                    cap = cv2.VideoCapture(source)
                    continue
                else:
                    print(f"[CAMERA {camera_id}] Feed ended.")
                    break

            frame_count += 1
            if frame_count % process_every != 0:
                continue
                
            start_time = time.time()
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
                    # Safe crop
                    h, w = frame.shape[:2]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    vehicle_crop = frame[y1:y2, x1:x2]
                    
                    plate_detected = False
                    plate_conf = None
                    plate_bbox = None
                    plate_text = None
                    ocr_conf = None
                    
                    vehicle_color = estimate_vehicle_color(vehicle_crop)
                    
                    if vehicle_crop.size > 0:
                        plate_results = plate_model(vehicle_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
                        for pr in plate_results:
                            if pr.boxes and len(pr.boxes) > 0:
                                plate_detected = True
                                plate_conf = float(pr.boxes[0].conf[0])
                                px1, py1, px2, py2 = map(float, pr.boxes[0].xyxy[0])
                                
                                # actual plate crop from vehicle crop
                                p_h, p_w = vehicle_crop.shape[:2]
                                px1, py1 = max(0, int(px1)), max(0, int(py1))
                                px2, py2 = min(p_w, int(px2)), min(p_h, int(py2))
                                
                                plate_crop = vehicle_crop[py1:py2, px1:px2]
                                if plate_crop.size > 0:
                                    variants = preprocess_variants(plate_crop)
                                    readings = run_ocr(variants)
                                    pt, oc = choose_result(readings)
                                    if pt:
                                        plate_text = pt
                                        ocr_conf = oc

                                px1_full = x1 + px1
                                py1_full = y1 + py1
                                px2_full = x1 + px2
                                py2_full = y1 + py2
                                
                                plate_bbox = BoundingBox(x1=float(px1_full), y1=float(py1_full), x2=float(px2_full), y2=float(py2_full))
                                
                                # Annotate Plate on frame
                                cv2.rectangle(frame, (px1_full, py1_full), (px2_full, py2_full), (255, 0, 0), 2)
                                label = f"{plate_text}" if plate_text else "PLATE"
                                cv2.putText(frame, label, (px1_full, py1_full - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                                
                                break 

                    # Annotate Vehicle on frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{vehicle_color} {vehicle_type.upper()} {int(confidence*100)}%"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    if time.time() - last_log_time > 2.0:
                        print_structured_log(camera_id, vehicle_type, confidence, vehicle_color, plate_detected, plate_conf, plate_text, ocr_conf)
                        last_log_time = time.time()

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
                        plate_text=plate_text,
                        ocr_confidence=ocr_conf,
                        vehicle_color=vehicle_color,
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
        except Exception as e:
            print(f"[ERROR] Exception in processing loop: {e}")
            time.sleep(1) # Prevent hot loop

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera-id", type=int, required=True, help="ID of this camera (1, 2, or 3)")
    parser.add_argument("--source", type=str, default="0", help="Camera source (0 for webcam, or path to video)")
    args = parser.parse_args()
    
    try:
        run_camera_node(args.camera_id, args.source)
    except KeyboardInterrupt:
        print(f"[CAMERA {args.camera_id}] Shutting down.")
