import os
import zipfile
import random
import shutil
import xml.etree.ElementTree as ET


# -----------------------------
# Paths
# -----------------------------

ZIP_PATH = "data/demo/archive (2).zip"

OUTPUT_DIR = "data/license_plate"

TEMP_DIR = "data/temp_plate_dataset"


# -----------------------------
# Create folders
# -----------------------------

os.makedirs("data/license_plate/images/train", exist_ok=True)
os.makedirs("data/license_plate/images/val", exist_ok=True)

os.makedirs("data/license_plate/labels/train", exist_ok=True)
os.makedirs("data/license_plate/labels/val", exist_ok=True)

os.makedirs(TEMP_DIR, exist_ok=True)


# -----------------------------
# Extract ZIP
# -----------------------------

print("Extracting dataset...")

with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
    zip_ref.extractall(TEMP_DIR)

print("Dataset extracted!")


# -----------------------------
# Find XML files
# -----------------------------

xml_files = []

for root, dirs, files in os.walk(TEMP_DIR):

    for file in files:

        if file.lower().endswith(".xml"):

            xml_files.append(
                os.path.join(root, file)
            )


print("XML files found:", len(xml_files))


# -----------------------------
# Shuffle dataset
# -----------------------------

random.seed(42)

random.shuffle(xml_files)


# 80% training
# 20% validation

split_index = int(len(xml_files) * 0.8)

train_files = xml_files[:split_index]

val_files = xml_files[split_index:]


print("Training images:", len(train_files))
print("Validation images:", len(val_files))


# -----------------------------
# Convert XML → YOLO
# -----------------------------

def convert_dataset(xml_list, split):

    for xml_path in xml_list:

        tree = ET.parse(xml_path)

        root = tree.getroot()


        # Get image size

        size = root.find("size")

        width = int(size.find("width").text)

        height = int(size.find("height").text)


        # Get image filename

        filename = root.find("filename").text


        # Find image

        image_path = os.path.join(
            os.path.dirname(xml_path),
            filename
        )


        if not os.path.exists(image_path):

            print("Image not found:", image_path)

            continue


        # Create a unique filename

        base_name = os.path.splitext(filename)[0]

        new_name = base_name + ".jpg"


        # Destination image

        destination_image = os.path.join(
            "data/license_plate/images",
            split,
            new_name
        )


        # Destination label

        destination_label = os.path.join(
            "data/license_plate/labels",
            split,
            base_name + ".txt"
        )


        # Copy image

        shutil.copy2(
            image_path,
            destination_image
        )


        # Create YOLO label

        label_lines = []


        objects = root.findall("object")


        for obj in objects:

            # Class 0 = license plate

            class_id = 0


            bbox = obj.find("bndbox")


            xmin = float(bbox.find("xmin").text)

            ymin = float(bbox.find("ymin").text)

            xmax = float(bbox.find("xmax").text)

            ymax = float(bbox.find("ymax").text)


            # Convert to YOLO format

            center_x = ((xmin + xmax) / 2) / width

            center_y = ((ymin + ymax) / 2) / height

            box_width = (xmax - xmin) / width

            box_height = (ymax - ymin) / height


            label_lines.append(
                f"{class_id} "
                f"{center_x:.6f} "
                f"{center_y:.6f} "
                f"{box_width:.6f} "
                f"{box_height:.6f}"
            )


        # Write label file

        with open(destination_label, "w") as f:

            f.write("\n".join(label_lines))


# -----------------------------
# Run conversion
# -----------------------------

print("\nConverting training dataset...")

convert_dataset(train_files, "train")


print("Converting validation dataset...")

convert_dataset(val_files, "val")


print("\n================================")
print("DATASET CONVERSION COMPLETE 🔥")
print("================================")

print("Train:", len(train_files))
print("Val:", len(val_files))
print()
print("Dataset location:")
print("data/license_plate/")