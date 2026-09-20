from pathlib import Path
import cv2
import pytesseract
import re
import csv
from ultralytics import YOLO


MODEL_PATH = "models/license-plate-finetune-v2-best.pt"
IMAGE_DIR = Path("data/indian_demo")

OUTPUT_DIR = Path("data/ocr_results")
CROP_DIR = OUTPUT_DIR / "crops"
ENHANCED_DIR = OUTPUT_DIR / "enhanced"

CROP_DIR.mkdir(parents=True, exist_ok=True)
ENHANCED_DIR.mkdir(parents=True, exist_ok=True)

CONFIDENCE = 0.25


model = YOLO(MODEL_PATH)


# ---------------------------------------------------------
# Clean OCR
# ---------------------------------------------------------

def clean_text(text):

    text = text.upper()

    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# ---------------------------------------------------------
# OCR variants
# ---------------------------------------------------------

def preprocess_variants(crop):

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # Large upscale for small plates
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Contrast
    contrast = cv2.equalizeHist(gray)

    # Light denoise
    blur = cv2.GaussianBlur(
        contrast,
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

    # Adaptive threshold
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
        "otsu": otsu,
        "adaptive": adaptive
    }


# ---------------------------------------------------------
# Run multiple OCR configurations
# ---------------------------------------------------------

def run_ocr(images):

    config = (
        "--psm 7 "
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    readings = []

    for name, image in images.items():

        text = pytesseract.image_to_string(
            image,
            config=config
        )

        text = clean_text(text)

        if text:

            readings.append(
                (name, text)
            )

    return readings


# ---------------------------------------------------------
# Pick best OCR result
# ---------------------------------------------------------

def choose_result(readings):

    if not readings:
        return ""

    # Prefer strings with reasonable plate length
    valid_length = [
        text
        for _, text in readings
        if 8 <= len(text) <= 12
    ]

    if valid_length:

        # Longest reasonable result
        return max(
            valid_length,
            key=len
        )

    return max(
        (text for _, text in readings),
        key=len
    )


# ---------------------------------------------------------
# CSV
# ---------------------------------------------------------

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
    print("=" * 70)
    print("ANVAY OCR EVALUATION")
    print("=" * 70)
    print()

    print(
        f"Images available: {len(images)}"
    )

    print()


    detection_count = 0


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


        for detection_number, result in enumerate(
            results,
            start=1
        ):

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
                # Save original plate crop
                # -----------------------------------------

                crop_name = (
                    f"{image_path.stem}"
                    f"_plate_{box_number}.jpg"
                )

                crop_path = (
                    CROP_DIR / crop_name
                )

                cv2.imwrite(
                    str(crop_path),
                    crop
                )


                # -----------------------------------------
                # Preprocessing
                # -----------------------------------------

                variants = preprocess_variants(
                    crop
                )


                # Save enhanced version
                enhanced_name = (
                    f"{image_path.stem}"
                    f"_enhanced_{box_number}.jpg"
                )

                cv2.imwrite(
                    str(
                        ENHANCED_DIR
                        / enhanced_name
                    ),
                    variants["adaptive"]
                )


                # -----------------------------------------
                # OCR
                # -----------------------------------------

                readings = run_ocr(
                    variants
                )

                plate_text = choose_result(
                    readings
                )


                # -----------------------------------------
                # Save CSV
                # -----------------------------------------

                writer.writerow([
                    image_path.name,
                    f"{confidence:.4f}",
                    x1,
                    y1,
                    x2,
                    y2,
                    plate_text
                ])


                print(
                    f"[{detection_count:03d}] "
                    f"{image_path.name:<25} "
                    f"{confidence:.2f}  "
                    f"{plate_text}"
                )


print()
print("=" * 70)
print("OCR EVALUATION COMPLETE 🔥")
print("=" * 70)
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

print()