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
    if crop.size == 0:
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
                            plate_crop = vehicle_crop[int(py1):int(py2), int(px1):int(px2)]
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
                            
                            plate_bbox = BoundingBox(x1=px1_full, y1=py1_full, x2=px2_full, y2=py2_full)
                            
                            # Annotate Plate on frame
                            cv2.rectangle(frame, (int(px1_full), int(py1_full)), (int(px2_full), int(py2_full)), (255, 0, 0), 2)
                            label = f"{plate_text}" if plate_text else "PLATE"
                            cv2.putText(frame, label, (int(px1_full), int(py1_full) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            
                            break 

                # Annotate Vehicle on frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{vehicle_color} {vehicle_type.upper()} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                print(f"[CAMERA {camera_id}] Vehicle: {vehicle_type.upper()}")
                print(f"[CAMERA {camera_id}] Vehicle Confidence: {confidence:.2f}")
                print(f"[CAMERA {camera_id}] Color: {vehicle_color}")
                if plate_detected:
                    print(f"[CAMERA {camera_id}] Plate Detected: YES")
                    print(f"[CAMERA {camera_id}] Plate Detector Confidence: {plate_conf:.2f}")
                    print(f"[CAMERA {camera_id}] Plate OCR: {plate_text if plate_text else 'NO PLATE'}")
                    if ocr_conf:
                        print(f"[CAMERA {camera_id}] OCR Confidence: {ocr_conf:.2f}")
                print("-" * 30)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera-id", type=int, required=True, help="ID of this camera (1, 2, or 3)")
    parser.add_argument("--source", type=str, default="0", help="Camera source (0 for webcam, or path to video)")
    args = parser.parse_args()
    
    run_camera_node(args.camera_id, args.source)
