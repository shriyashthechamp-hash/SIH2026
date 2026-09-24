import cv2
import time
import base64
import uuid
import re
import numpy as np
import pytesseract
from typing import Optional, Tuple, Dict, Any, List
from ultralytics import YOLO

from core.models import DetectionEvent, BoundingBox
from core.config import VEHICLE_MODEL, PLATE_MODEL, CONFIDENCE_THRESHOLD

def clean_text(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text

def estimate_vehicle_color(crop: np.ndarray) -> str:
    if crop is None or crop.size == 0:
        return "UNKNOWN"
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

def preprocess_variants(crop: np.ndarray) -> Dict[str, np.ndarray]:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    contrast = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(contrast, (3, 3), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
    return {"gray": gray, "contrast": contrast, "otsu": otsu, "adaptive": adaptive}

def run_ocr(images: Dict[str, np.ndarray]) -> List[Tuple[str, str, float]]:
    config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    readings = []
    for name, image in images.items():
        try:
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
        except Exception:
            pass
    return readings

def choose_result(readings: List[Tuple[str, str, float]]) -> Tuple[Optional[str], Optional[float]]:
    if not readings:
        return None, None
    valid_length = [(text, conf) for _, text, conf in readings if 8 <= len(text) <= 12]
    if valid_length:
        return max(valid_length, key=lambda x: len(x[0]))
    return max([(text, conf) for _, text, conf in readings], key=lambda x: len(x[0]))

def encode_image(img: np.ndarray, max_dim: int = 640) -> Optional[str]:
    try:
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    except Exception:
        return None

def decode_image(b64_str: str) -> Optional[np.ndarray]:
    try:
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None

class InferencePipeline:
    def __init__(self):
        self.vehicle_model: Optional[YOLO] = None
        self.plate_model: Optional[YOLO] = None
        self._load_models()

    def _load_models(self):
        try:
            print(f"[INFERENCE] Loading models: {VEHICLE_MODEL}, {PLATE_MODEL}")
            self.vehicle_model = YOLO(VEHICLE_MODEL)
            self.plate_model = YOLO(PLATE_MODEL)
            print("[INFERENCE] Models loaded successfully.")
        except Exception as e:
            print(f"[INFERENCE ERROR] Could not load models: {e}")

    def process_frame(self, frame_b64: str, camera_id: int = 1) -> Tuple[Optional[DetectionEvent], Optional[str], Dict[str, Any]]:
        frame = decode_image(frame_b64)
        if frame is None:
            return None, None, {"error": "Failed to decode image"}

        if self.vehicle_model is None or self.plate_model is None:
            self._load_models()
            if self.vehicle_model is None or self.plate_model is None:
                encoded = encode_image(frame, max_dim=640)
                return None, encoded, {"error": "Models unavailable"}

        annotated_frame = frame.copy()
        detection_event: Optional[DetectionEvent] = None
        meta: Dict[str, Any] = {
            "vehicle_detected": False,
            "plate_detected": False,
            "vehicle_type": None,
            "confidence": None,
            "vehicle_color": None,
            "plate_text": None,
            "ocr_confidence": None
        }

        try:
            results = self.vehicle_model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
            for result in results:
                boxes = result.boxes
                if boxes is None or len(boxes) == 0:
                    continue

                for box in boxes:
                    class_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    v_type = self.vehicle_model.names[class_id]

                    if v_type not in ["car", "motorcycle", "bus", "truck"]:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    h, w = frame.shape[:2]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    vehicle_crop = frame[y1:y2, x1:x2]

                    plate_detected = False
                    plate_conf = None
                    plate_bbox = None
                    plate_text = None
                    ocr_conf = None

                    v_color = estimate_vehicle_color(vehicle_crop)

                    if vehicle_crop.size > 0:
                        plate_results = self.plate_model(vehicle_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
                        for pr in plate_results:
                            if pr.boxes and len(pr.boxes) > 0:
                                plate_detected = True
                                plate_conf = float(pr.boxes[0].conf[0])
                                px1, py1, px2, py2 = map(float, pr.boxes[0].xyxy[0])

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

                                # Draw plate box
                                cv2.rectangle(annotated_frame, (int(px1_full), int(py1_full)), (int(px2_full), int(py2_full)), (255, 0, 0), 2)
                                p_label = f"{plate_text}" if plate_text else "PLATE"
                                cv2.putText(annotated_frame, p_label, (int(px1_full), int(py1_full) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                                break

                    # Draw vehicle box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    v_label = f"{v_color} {v_type.upper()} {int(conf * 100)}%"
                    cv2.putText(annotated_frame, v_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    crop_b64 = encode_image(vehicle_crop, max_dim=200) if vehicle_crop.size > 0 else None

                    detection_event = DetectionEvent(
                        event_id=str(uuid.uuid4()),
                        camera_id=camera_id,
                        timestamp=time.time(),
                        vehicle_type=v_type,
                        confidence=conf,
                        bounding_box=BoundingBox(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2)),
                        plate_detected=plate_detected,
                        plate_confidence=plate_conf,
                        plate_box=plate_bbox,
                        plate_text=plate_text,
                        ocr_confidence=ocr_conf,
                        vehicle_color=v_color,
                        image_base64=crop_b64
                    )

                    meta["vehicle_detected"] = True
                    meta["plate_detected"] = plate_detected
                    meta["vehicle_type"] = v_type
                    meta["confidence"] = conf
                    meta["vehicle_color"] = v_color
                    meta["plate_text"] = plate_text
                    meta["ocr_confidence"] = ocr_conf

                    # For single frame processing, break after primary vehicle
                    break

        except Exception as e:
            print(f"[INFERENCE ERROR] {e}")

        annotated_b64 = encode_image(annotated_frame, max_dim=640)
        return detection_event, annotated_b64, meta
