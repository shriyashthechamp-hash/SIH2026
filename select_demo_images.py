from pathlib import Path
import shutil
from collections import defaultdict

# Dataset locations
dataset = Path("data/veri/VeRi")
query_file = dataset / "name_query.txt"
image_folder = dataset / "image_query"

# Where our small demo dataset will live
demo_folder = Path("data/demo")
demo_folder.mkdir(parents=True, exist_ok=True)

# Read query image names
with open(query_file, "r") as file:
    image_names = [line.strip() for line in file if line.strip()]

# Store images by vehicle ID
vehicles = defaultdict(list)

for image_name in image_names:

    # Example:
    # 0002_c002_00030600_0.jpg

    parts = image_name.split("_")

    vehicle_id = parts[0]
    camera_id = parts[1]

    vehicles[vehicle_id].append(
        (camera_id, image_name)
    )

# Find vehicles that appear in at least 3 cameras
selected = []

for vehicle_id, images in vehicles.items():

    cameras = set(camera for camera, _ in images)

    if len(cameras) >= 3:
        selected.append(
            (vehicle_id, images)
        )

# Take first 5 suitable vehicles
selected = selected[:5]

print("\nSelected vehicles:\n")

for vehicle_id, images in selected:

    print(
        vehicle_id,
        "->",
        len(images),
        "images from",
        len(set(camera for camera, _ in images)),
        "cameras"
    )

    # Take at most 3 images per vehicle
    chosen = images[:3]

    vehicle_folder = demo_folder / f"vehicle_{vehicle_id}"
    vehicle_folder.mkdir(parents=True, exist_ok=True)

    for camera_id, image_name in chosen:

        source = image_folder / image_name
        destination = vehicle_folder / f"{camera_id}_{image_name}"

        if source.exists():
            shutil.copy2(source, destination)

print("\nDONE!")
print("Demo images saved inside:", demo_folder)
