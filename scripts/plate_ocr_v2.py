from pathlib import Path
import cv2
import pytesseract
import re
import csv
from collections import Counter
from ultralytics import YOLO


# =========================================================
# ANVAY OCR V2
# Multi-preprocessing + multi-PSM + plate-format scoring
# =========================================================

MODEL_PATH = "models/license-plate-finetune-v2-best.pt"
IMAGE_DIR = Path("data/indian_demo")
OUTPUT_DIR = Path("data/ocr_results_v2")

CROP_DIR = OUTPUT_DIR / "crops"
ENHANCED_DIR = OUTPUT_DIR / "enhanced"

CROP_DIR.mkdir(parents=True, exist_ok=True)
ENHANCED_DIR.mkdir(parents=True, exist_ok=True)

CONFIDENCE = 0.25


# =========================================================
# MODEL
# =========================================================

model = YOLO(MODEL_PATH)


# =========================================================
# COMMON INDIAN STATE / UT CODES
# =========================================================

STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "CH", "DL", "DN", "GA",
    "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD",
    "MH", "ML", "MN", "MP", "MZ", "NL", "OD", "OR", "PB",
    "PY", "RJ", "SK", "TN", "TR", "TS", "UK", "UP", "WB"
}


# =========================================================
# CLEAN OCR
# =========================================================

def clean_text(text):
    text = text.upper()

    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# =========================================================
# CHARACTER NORMALIZATION
# Conservative OCR corrections
# =========================================================

def normalize_ocr(text):

    text = clean_text(text)

    if not text:
        return ""

    # Remove extremely unlikely leading/trailing noise
    text = text.strip()

    return text


# =========================================================
# PREPROCESSING VARIANTS
# =========================================================

def preprocess_variants(crop):

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # Large upscale
    gray = cv2.resize(
        gray,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # Contrast
    contrast = cv2.equalizeHist(gray)

    # CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    clahe_img = clahe.apply(gray)

    # Light denoise
    blur = cv2.GaussianBlur(
        clahe_img,
        (3, 3),
        0
    )

    # OTSU
    _, otsu = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Inverted OTSU
    _, otsu_inv = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Adaptive
    adaptive = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return {
        "gray": gray,
        "contrast": contrast,
        "clahe": clahe_img,
        "otsu": otsu,
        "otsu_inv": otsu_inv,
        "adaptive": adaptive
    }


# =========================================================
# OCR CONFIGURATIONS
# =========================================================

PSM_MODES = [6, 7, 8, 13]


def run_ocr(variants):

    readings = []

    whitelist = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    for variant_name, image in variants.items():

        for psm in PSM_MODES:

            config = (
                f"--psm {psm} "
                f"-c tessedit_char_whitelist={whitelist}"
            )

            text = pytesseract.image_to_string(
                image,
                config=config
            )

            text = normalize_ocr(text)

            if text:

                readings.append({
                    "variant": variant_name,
                    "psm": psm,
                    "text": text
                })

    return readings


# =========================================================
# PLATE FORMAT SCORING
# =========================================================

def plate_format_score(text):

    if not text:
        return 0

    score = 0

    length = len(text)

    # -----------------------------------------------------
    # Length
    # -----------------------------------------------------

    if 8 <= length <= 10:
        score += 35

    elif length == 7:
        score += 15

    elif 11 <= length <= 12:
        score += 10

    else:
        score -= 20

    # -----------------------------------------------------
    # State code
    # -----------------------------------------------------

    if length >= 2:

        prefix = text[:2]

        if prefix in STATE_CODES:
            score += 35

    # -----------------------------------------------------
    # Registration number usually contains digits
    # -----------------------------------------------------

    digit_count = sum(
        char.isdigit()
        for char in text
    )

    letter_count = sum(
        char.isalpha()
        for char in text
    )

    if digit_count >= 2:
        score += 15

    if letter_count >= 2:
        score += 10

    # -----------------------------------------------------
    # Penalize obvious word-like garbage
    # -----------------------------------------------------

    garbage_words = {
        "REGEL",
        "CELLS",
        "ANOTHAM",
        "CBRELI",
        "SUP",
        "ERROR",
        "NONE",
        "UNKNOWN"
    }

    if text in garbage_words:
        score -= 50

    return score


# =========================================================
# CONSENSUS + SCORING
# =========================================================

def choose_best_result(readings):

    if not readings:
        return "", 0

    candidates = []

    for item in readings:

        text = item["text"]

        format_score = plate_format_score(text)

        candidates.append(
            (
                text,
                format_score
            )
        )

    # -----------------------------------------------------
    # Count repeated OCR outputs
    # -----------------------------------------------------

    counts = Counter(
        text
        for text, _ in candidates
    )

    # -----------------------------------------------------
    # Final score
    # -----------------------------------------------------

    scored = []

    for text, format_score in candidates:

        frequency_bonus = min(
            counts[text] * 8,
            24
        )

        length_bonus = min(
            len(text),
            10
        )

        final_score = (
            format_score
            + frequency_bonus
            + length_bonus
        )

        scored.append(
            (
                text,
                final_score
            )
        )

    scored.sort(
        key=lambda x: x[1],
        reverse=True
    )

    best_text, best_score = scored[0]

    return best_text, best_score


# =========================================================
# CSV
# =========================================================

csv_path = OUTPUT_DIR / "results.csv"

with open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.writer(csv_file)

    writer.writerow([
        "image",
        "confidence",
        "x1",
        "y1",
        "x2",
        "y2",
        "ocr",
        "ocr_score",
        "ocr_readings"
    ])

    # -----------------------------------------------------
    # Load images
    # -----------------------------------------------------

    images = sorted(
        [
            p for p in IMAGE_DIR.iterdir()
            if p.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            }
        ]
    )

    print()
    print("=" * 75)
    print("ANVAY OCR V2")
    print("=" * 75)
    print()

    print(
        f"Images available: {len(images)}"
    )

    print()

    detection_count = 0

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for index, image_path in enumerate(
        images,
        start=1
    ):

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            continue

        results = model(
            image,
            conf=CONFIDENCE,
            verbose=False
        )

        for result in results:

            for box_number, box in enumerate(
                result.boxes,
                start=1
            ):

                detection_count += 1

                confidence = float(
                    box.conf[0]
                )

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                h, w = image.shape[:2]

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                crop = image[
                    y1:y2,
                    x1:x2
                ]

                if crop.size == 0:
                    continue

                # -----------------------------------------
                # SAVE CROP
                # -----------------------------------------

                crop_name = (
                    f"{image_path.stem}"
                    f"_plate_{box_number}.jpg"
                )

                cv2.imwrite(
                    str(CROP_DIR / crop_name),
                    crop
                )

                # -----------------------------------------
                # PREPROCESSING
                # -----------------------------------------

                variants = preprocess_variants(
                    crop
                )

                # -----------------------------------------
                # SAVE BEST VISUAL ENHANCEMENT
                # -----------------------------------------

                enhanced_name = (
                    f"{image_path.stem}"
                    f"_enhanced_{box_number}.jpg"
                )

                cv2.imwrite(
                    str(
                        ENHANCED_DIR
                        / enhanced_name
                    ),
                    variants["clahe"]
                )

                # -----------------------------------------
                # OCR
                # -----------------------------------------

                readings = run_ocr(
                    variants
                )

                plate_text, plate_score = (
                    choose_best_result(
                        readings
                    )
                )

                # -----------------------------------------
                # STORE ALL READINGS
                # -----------------------------------------

                reading_string = "|".join(
                    f"{r['variant']}:{r['psm']}:{r['text']}"
                    for r in readings
                )

                writer.writerow([
                    image_path.name,
                    f"{confidence:.4f}",
                    x1,
                    y1,
                    x2,
                    y2,
                    plate_text,
                    plate_score,
                    reading_string
                ])

                # -----------------------------------------
                # TERMINAL OUTPUT
                # -----------------------------------------

                print(
                    f"[{detection_count:04d}] "
                    f"{image_path.name:<25} "
                    f"YOLO={confidence:.2f} "
                    f"OCR={plate_text:<15} "
                    f"SCORE={plate_score}"
                )


# =========================================================
# COMPLETE
# =========================================================

print()

print("=" * 75)
print("ANVAY OCR V2 COMPLETE 🔥")
print("=" * 75)

print()

print(
    f"Total plate detections: "
    f"{detection_count}"
)

print(
    f"Results: {csv_path}"
)

print(
    f"Crops  : {CROP_DIR}"
)

print(
    f"Enhanced: {ENHANCED_DIR}"
)

print()