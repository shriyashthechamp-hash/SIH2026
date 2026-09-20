import os
import cv2
import pandas as pd
from pathlib import Path
from ultralytics import YOLO

from crop import generate_crop_variants, calculate_quality

def run_cropping(model_path, data_dir, output_dir, conf=0.25):
    print(f"Loading model for cropping: {model_path}")
    model = YOLO(model_path)
    
    image_paths = list(Path(data_dir).glob("*.jpg")) + list(Path(data_dir).glob("*.png"))
    
    crops_dir = Path(output_dir) / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    
    metrics = []
    
    print(f"Processing {len(image_paths)} images for cropping and quality checks...")
    
    # Process only a subset or all
    for img_path in image_paths:
        img_name = img_path.name
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        results = model(img, conf=conf, verbose=False)
        boxes = results[0].boxes
        
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            bbox = (x1, y1, x2, y2)
            
            variants = generate_crop_variants(img, bbox)
            if not variants:
                continue
                
            # We only evaluate quality on the tight crop as baseline
            quality_info = calculate_quality(variants["tight"])
            if quality_info:
                metrics.append({
                    "image": img_name,
                    "crop_idx": i,
                    "detector_conf": round(float(box.conf[0]), 3),
                    **quality_info
                })
                
            # Save crops
            base_name = img_path.stem
            for variant_name, crop_img in variants.items():
                if crop_img is not None and crop_img.size > 0:
                    out_path = crops_dir / f"{base_name}_crop{i}_{variant_name}.jpg"
                    cv2.imwrite(str(out_path), crop_img)

    # Save quality report
    df = pd.DataFrame(metrics)
    report_path = Path(output_dir) / "reports" / "quality_report.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(report_path, index=False)
    
    print(f"\nSaved {len(metrics)} crop quality records to {report_path}")
    print("Quality breakdown:")
    if not df.empty:
        print(df["quality_score"].value_counts())

if __name__ == "__main__":
    import sys
    # Add parent directory to path to allow absolute imports
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from scripts.v3.crop import generate_crop_variants, calculate_quality
    
    MODEL = "models/license-plate-finetune-v2-best.pt"
    DATA = "data/indian_demo"
    OUT = "data/ocr_results_v3"
    run_cropping(MODEL, DATA, OUT)
