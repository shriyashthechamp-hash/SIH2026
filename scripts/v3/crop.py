import cv2
import numpy as np

def clamp_box(x1, y1, x2, y2, img_w, img_h):
    """Clamps bounding box coordinates to image dimensions."""
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(img_w, int(x2))
    y2 = min(img_h, int(y2))
    return x1, y1, x2, y2

def generate_crop_variants(img, box):
    """
    Generates multiple crop variants given the image and bounding box.
    Returns: dictionary of {'tight': img, 'margin_5': img, 'margin_10': img}
    """
    h, w = img.shape[:2]
    x1, y1, x2, y2 = box
    
    # Tight crop
    cx1, cy1, cx2, cy2 = clamp_box(x1, y1, x2, y2, w, h)
    tight_crop = img[cy1:cy2, cx1:cx2]
    
    # If invalid crop, return empty
    if tight_crop.size == 0:
        return None
        
    box_w = x2 - x1
    box_h = y2 - y1
    
    # Reject microscopic crops
    if box_w < 10 or box_h < 5:
        return None
        
    variants = {"tight": tight_crop}
    
    # 5% margin
    m5_x = int(box_w * 0.05)
    m5_y = int(box_h * 0.05)
    m5_x1, m5_y1, m5_x2, m5_y2 = clamp_box(x1 - m5_x, y1 - m5_y, x2 + m5_x, y2 + m5_y, w, h)
    variants["margin_5"] = img[m5_y1:m5_y2, m5_x1:m5_x2]
    
    # 10% margin
    m10_x = int(box_w * 0.10)
    m10_y = int(box_h * 0.10)
    m10_x1, m10_y1, m10_x2, m10_y2 = clamp_box(x1 - m10_x, y1 - m10_y, x2 + m10_x, y2 + m10_y, w, h)
    variants["margin_10"] = img[m10_y1:m10_y2, m10_x1:m10_x2]
    
    return variants

def calculate_quality(crop_img):
    """
    Calculates image quality metrics for a given crop.
    Returns: dict of metrics.
    """
    if crop_img is None or crop_img.size == 0:
        return None
        
    h, w = crop_img.shape[:2]
    area = w * h
    aspect_ratio = w / h if h > 0 else 0
    
    # Grayscale for brightness/contrast/sharpness
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    
    brightness = np.mean(gray)
    contrast = np.std(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Categorize quality roughly
    if sharpness > 300 and contrast > 40 and 1.5 < aspect_ratio < 6.0 and area > 1000:
        quality_score = "GOOD"
    elif sharpness < 50 or contrast < 15 or area < 200:
        quality_score = "POOR"
    else:
        quality_score = "MEDIUM"
        
    return {
        "width": w,
        "height": h,
        "aspect_ratio": round(aspect_ratio, 2),
        "area": area,
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
        "sharpness": round(float(sharpness), 2),
        "quality_score": quality_score
    }

if __name__ == "__main__":
    # Simple test
    print("crop.py loaded successfully.")
