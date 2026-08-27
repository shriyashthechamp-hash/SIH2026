from PIL import Image, ImageDraw
import os
import random

# Dataset folders
image_folder = "data/license_plate/images/train"
label_folder = "data/license_plate/labels/train"

# Pick a random image
images = [
    f for f in os.listdir(image_folder)
    if f.endswith(".jpg")
]

image_name = random.choice(images)

image_path = os.path.join(image_folder, image_name)

# Corresponding label
label_name = os.path.splitext(image_name)[0] + ".txt"
label_path = os.path.join(label_folder, label_name)

# Open image
image = Image.open(image_path)
draw = ImageDraw.Draw(image)

width, height = image.size

print("Image:", image_path)
print("Size:", width, "x", height)
print("Label:", label_path)

# Read YOLO label
with open(label_path, "r") as file:
    lines = file.readlines()

for line in lines:

    values = line.strip().split()

    class_id = int(values[0])

    x_center = float(values[1])
    y_center = float(values[2])
    box_width = float(values[3])
    box_height = float(values[4])

    # Convert YOLO coordinates to pixels
    x_center = x_center * width
    y_center = y_center * height

    box_width = box_width * width
    box_height = box_height * height

    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)

    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)

    # Draw bounding box
    draw.rectangle(
        [x1, y1, x2, y2],
        outline="red",
        width=3
    )

    print("License plate box:")
    print(x1, y1, x2, y2)

# Save result
output_path = "data/license_plate_check.jpg"

image.save(output_path)

print("\nSaved result to:")
print(output_path)