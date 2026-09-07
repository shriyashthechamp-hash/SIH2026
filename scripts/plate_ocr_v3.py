from pathlib import Path
import cv2
import pytesseract
import re
import csv
from collections import Counter
from ultralytics import YOLO


# =========================================================
# ANVAY OCR V3
# Detection + OCR Ensemble + Indian Plate Validation
# + Candidate Consensus
# =========================================================

MODEL_PATH = "models/license-plate-finetune-v2-best.pt"
IMAGE_DIR = Path("data/indian_demo")

OUTPUT_DIR = Path("data/ocr_results_v3")
CROP_DIR = OUTPUT_DIR / "crops"
ENHANCED_DIR = OUTPUT_DIR / "enhanced"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CROP_DIR.mkdir(parents=True, exist_ok=True)
ENHANCED_DIR.mkdir(parents=True, exist_ok=True)

CONFIDENCE = 0.25


# =========================================================
# YOLO
# =========================================================

model = YOLO(MODEL_PATH)


# =========================================================
# INDIAN STATE / UT CODES
# =========================================================

STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "CH", "DL", "DN",
    "GA", "GJ", "HP", "HR", "JH", "JK", "KA", "KL",
    "LA", "LD", "MH", "ML", "MN", "MP", "MZ", "NL",
    "OD", "OR", "PB", "PY", "RJ", "SK", "TN", "TR",
    "TS", "UK", "UP", "WB"
}


# =========================================================
# CLEANING
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
# PREPROCESSING
# =========================================================

def preprocess_variants(crop):

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    contrast = cv2.equalizeHist(gray)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    clahe_img = clahe.apply(gray)

    blur = cv2.GaussianBlur(
        clahe_img,
        (3, 3),
        0
    )

    _, otsu = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    _, otsu_inv = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

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
# OCR
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

            text = clean_text(text)

            if text:

                readings.append({
                    "variant": variant_name,
                    "psm": psm,
                    "text": text
                })

    return readings


# =========================================================
# INDIAN PLATE VALIDATION
# =========================================================

def plate_structure_score(text):

    if not text:
        return 0

    score = 0
    length = len(text)

    # -----------------------------------------------------
    # Length
    # -----------------------------------------------------

    if 8 <= length <= 10:
        score += 30

    elif length == 7:
        score += 10

    elif 11 <= length <= 12:
        score += 5

    else:
        score -= 25

    # -----------------------------------------------------
    # State prefix
    # -----------------------------------------------------

    if length >= 2:

        prefix = text[:2]

        if prefix in STATE_CODES:
            score += 40

    # -----------------------------------------------------
    # Character composition
    # -----------------------------------------------------

    digits = sum(
        c.isdigit()
        for c in text
    )

    letters = sum(
        c.isalpha()
        for c in text
    )

    if digits >= 2:
        score += 15

    if letters >= 2:
        score += 10

    # -----------------------------------------------------
    # Penalize obvious OCR garbage
    # -----------------------------------------------------

    garbage = {
        "REGEL",
        "CELLS",
        "ANOTHAM",
        "ERROR",
        "UNKNOWN",
        "NONE"
    }

    if text in garbage:
        score -= 60

    # Repeated single character
    if len(set(text)) <= 2:
        score -= 30

    return score


# =========================================================
# CHARACTER CONFUSION
# =========================================================

CONFUSIONS = {
    "O": "0",
    "I": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
    "G": "6"
}


def normalized_for_comparison(text):

    """
    Normalize common OCR confusions ONLY for comparing
    candidates.

    We do NOT modify the final plate here.
    """

    result = []

    for char in text:

        if char in CONFUSIONS:
            result.append(
                CONFUSIONS[char]
            )
        else:
            result.append(char)

    return "".join(result)


# =========================================================
# HAMMING-LIKE SIMILARITY
# =========================================================

def similarity(a, b):

    a = normalized_for_comparison(a)
    b = normalized_for_comparison(b)

    if not a or not b:
        return 0

    max_len = max(
        len(a),
        len(b)
    )

    min_len = min(
        len(a),
        len(b)
    )

    matches = sum(
        a[i] == b[i]
        for i in range(min_len)
    )

    return matches / max_len


# =========================================================
# CONSENSUS
# =========================================================

def choose_consensus(readings):

    if not readings:
        return "", 0

    candidates = [
        r["text"]
        for r in readings
        if r["text"]
    ]

    if not candidates:
        return "", 0

    # -----------------------------------------------------
    # Direct frequency
    # -----------------------------------------------------

    counts = Counter(candidates)

    # -----------------------------------------------------
    # Every unique candidate receives a score
    # -----------------------------------------------------

    scored = []

    for candidate in counts:

        structure = plate_structure_score(
            candidate
        )

        frequency = counts[candidate]

        # Repeated observations are valuable.
        frequency_score = min(
            frequency * 8,
            40
        )

        # Similar candidates support each other.
        similarity_support = 0

        for other in counts:

            if other == candidate:
                continue

            sim = similarity(
                candidate,
                other
            )

            if sim >= 0.75:
                similarity_support += 5

        similarity_support = min(
            similarity_support,
            25
        )

        final_score = (
            structure
            + frequency_score
            + similarity_support
        )

        scored.append(
            (
                candidate,
                final_score,
                structure,
                frequency
            )
        )

    scored.sort(
        key=lambda x: x[1],
        reverse=True
    )

    best = scored[0]

    return best[0], best[1]


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
        "candidate_count",
        "all_candidates"
    ])

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
    print("ANVAY OCR V3")
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

    for image_path in images:

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

                # -------------------------------------------------
                # SAVE CROP
                # -------------------------------------------------

                crop_name = (
                    f"{image_path.stem}"
                    f"_plate_{box_number}.jpg"
                )

                cv2.imwrite(
                    str(
                        CROP_DIR / crop_name
                    ),
                    crop
                )

                # -------------------------------------------------
                # PREPROCESS
                # -------------------------------------------------

                variants = preprocess_variants(
                    crop
                )

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

                # -------------------------------------------------
                # OCR
                # -------------------------------------------------

                readings = run_ocr(
                    variants
                )

                plate_text, plate_score = (
                    choose_consensus(
                        readings
                    )
                )

                unique_candidates = Counter(
                    r["text"]
                    for r in readings
                )

                candidate_string = "|".join(
                    f"{text}:{count}"
                    for text, count
                    in unique_candidates.most_common()
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
                    len(unique_candidates),
                    candidate_string
                ])

                print(
                    f"[{detection_count:04d}] "
                    f"{image_path.name:<25} "
                    f"YOLO={confidence:.2f} "
                    f"OCR={plate_text:<15} "
                    f"SCORE={plate_score}"
                )


print()
print("=" * 75)
print("ANVAY OCR V3 COMPLETE 🔥")
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
    f"Crops: {CROP_DIR}"
)

print(
    f"Enhanced: {ENHANCED_DIR}"
)

print()