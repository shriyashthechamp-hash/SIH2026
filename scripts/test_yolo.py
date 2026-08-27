from ultralytics import YOLO
from pathlib import Path

# Load YOLO model
model = YOLO("yolo11n.pt")

# Folder containing demo images
images = list(Path("data/demo").rglob("*.jpg"))

print("Total images:", len(images))

# Test first 20 images
images = images[:20]

for image in images:

    print("\nImage:", image)

    results = model(
        str(image),
        conf=0.4
    )

    for result in results:

        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            print("No vehicle detected")
            continue

        for box in boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            print(
                "Detected:",
                model.names[class_id],
                "confidence =",
                round(confidence, 2)
            )

        # Save image with bounding boxes
        result.save(
            filename=f"data/demo/result_{image.name}"
        )

print("\nYOLO TEST COMPLETE 🔥")