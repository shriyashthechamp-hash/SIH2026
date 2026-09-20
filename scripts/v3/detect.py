import os
import cv2
import pandas as pd
from pathlib import Path
from ultralytics import YOLO


def evaluate_detector(model_path, data_dir, output_dir):
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    image_paths = list(Path(data_dir).glob("*.jpg")) + list(Path(data_dir).glob("*.png"))
    total_images = len(image_paths)
    print(f"Found {total_images} images in {data_dir}")
    
    thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    
    # Run once at very low conf to collect all predictions, then filter
    print("Running initial low-confidence inference to collect data...")
    all_preds = {}
    
    # Create debug directory
    debug_dir = Path(output_dir) / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    for img_path in image_paths:
        img_name = img_path.name
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        h, w = img.shape[:2]
        img_area = h * w
        
        # Run inference with conf=0.10 to capture everything
        results = model(img, conf=0.10, verbose=False)
        boxes = results[0].boxes
        
        preds = []
        for box in boxes:
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            box_w = x2 - x1
            box_h = y2 - y1
            box_area = box_w * box_h
            
            preds.append({
                "conf": conf,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "w": box_w, "h": box_h,
                "area_ratio": box_area / img_area
            })
            
        all_preds[img_name] = {
            "path": img_path,
            "img_shape": (h, w),
            "preds": preds
        }
        
    print("Aggregating metrics per threshold...")
    metrics = []
    
    # Analyze per threshold
    for t in thresholds:
        total_detections = 0
        images_with_detections = 0
        duplicate_detections = 0
        images_no_detections = 0
        very_small_crops = 0  # e.g., < 0.1% of image
        suspiciously_large_crops = 0 # e.g., > 30% of image
        conf_sum = 0
        
        for img_name, data in all_preds.items():
            valid_preds = [p for p in data["preds"] if p["conf"] >= t]
            
            num_valid = len(valid_preds)
            if num_valid > 0:
                images_with_detections += 1
                total_detections += num_valid
                
                for p in valid_preds:
                    conf_sum += p["conf"]
                    if p["area_ratio"] < 0.001:
                        very_small_crops += 1
                    if p["area_ratio"] > 0.30:
                        suspiciously_large_crops += 1
                        
                if num_valid > 1:
                    duplicate_detections += 1
            else:
                images_no_detections += 1
                
        avg_conf = conf_sum / total_detections if total_detections > 0 else 0
        
        metrics.append({
            "threshold": t,
            "total_images": total_images,
            "images_with_detections": images_with_detections,
            "images_no_detections": images_no_detections,
            "total_detections": total_detections,
            "duplicate_detections": duplicate_detections,
            "very_small_crops": very_small_crops,
            "suspiciously_large_crops": suspiciously_large_crops,
            "avg_confidence": round(avg_conf, 4)
        })
        
    # Save report
    df = pd.DataFrame(metrics)
    report_path = Path(output_dir) / "reports" / "detection_report.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(report_path, index=False)
    print(f"\nSaved detection report to {report_path}")
    print(df.to_string(index=False))
    
    # Save visual debug samples for conf=0.25
    print("\nSaving visual debug samples (t=0.25)...")
    sample_count = 0
    t_debug = 0.25
    for img_name, data in all_preds.items():
        if sample_count >= 10:
            break
            
        valid_preds = [p for p in data["preds"] if p["conf"] >= t_debug]
        if not valid_preds:
            continue
            
        img = cv2.imread(str(data["path"]))
        for p in valid_preds:
            x1, y1, x2, y2 = int(p["x1"]), int(p["y1"]), int(p["x2"]), int(p["y2"])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{p['conf']:.2f}", (x1, max(10, y1-10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imwrite(str(debug_dir / f"debug_{img_name}"), img)
        sample_count += 1
        
    print(f"Saved {sample_count} debug samples to {debug_dir}")
    
if __name__ == "__main__":
    MODEL = "models/license-plate-finetune-v2-best.pt"
    DATA = "data/indian_demo"
    OUT = "data/ocr_results_v3"
    evaluate_detector(MODEL, DATA, OUT)
