from ultralytics import YOLO
from pathlib import Path

# Load license plate model
model = YOLO("models/license-plate-finetune-v2-best.pt")

# Take some demo images
images = list(Path("data/demo").rglob("*.jpg"))[:20]

for image in images:

    print(f"\nImage: {image}")

    results = model(str(image), conf=0.25)

    found = False

    for result in results:

        for box in result.boxes:

            confidence = float(box.conf[0])

            print(
                f"License plate detected! "
                f"confidence = {confidence:.2f}"
            )

            found = True

    if not found:
        print("No license plate detected")

print("\nPLATE DETECTION TEST COMPLETE 🔥")