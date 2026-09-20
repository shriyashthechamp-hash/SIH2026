import os
import cv2
import numpy as np
import argparse
from pathlib import Path

def preprocess_image(img):
    """
    Applies multiple preprocessing techniques to an image for OCR.
    Returns a dictionary of preprocessed image variants.
    """
    variants = {}
    
    # Base: Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variants["gray"] = gray
    
    # 1. Contrast Enhancement (Linear)
    alpha = 1.5 # Contrast control
    beta = 10 # Brightness control
    contrast = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    variants["contrast"] = contrast
    
    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe = clahe_obj.apply(gray)
    variants["clahe"] = clahe
    
    # 3. OTSU Thresholding (requires blur to reduce noise)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants["otsu"] = otsu
    
    # 4. Adaptive Thresholding
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    variants["adaptive"] = adaptive
    
    # Upscaled variants (2x) using cubic interpolation (good for text)
    h, w = gray.shape
    upscaled_variants = {}
    for name, variant_img in variants.items():
        upscaled = cv2.resize(variant_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        upscaled_variants[f"{name}_2x"] = upscaled
        
    variants.update(upscaled_variants)
    
    return variants

def main():
    parser = argparse.ArgumentParser(description="ANVAY V3 Preprocessing Module")
    parser.add_argument("--input", type=str, required=True, help="Input directory containing plate crops")
    parser.add_argument("--output", type=str, required=True, help="Output directory for preprocessed images")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist.")
        return
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    image_paths = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
    total_images = len(image_paths)
    
    if total_images == 0:
        print(f"No images found in {input_dir}.")
        return
        
    print(f"Starting preprocessing for {total_images} crops...")
    
    generated_count = 0
    
    for i, img_path in enumerate(image_paths, 1):
        if i % 500 == 0 or i == 1:
            print(f"Processing {i}/{total_images}...")
            
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        base_name = img_path.stem
        variants = preprocess_image(img)
        
        for variant_name, processed_img in variants.items():
            out_filename = f"{base_name}_{variant_name}.jpg"
            out_path = output_dir / out_filename
            cv2.imwrite(str(out_path), processed_img)
            generated_count += 1
            
    print("\nPREPROCESSING COMPLETE")
    print(f"Input crops: {total_images}")
    print(f"Output images: {generated_count}")

if __name__ == "__main__":
    main()
