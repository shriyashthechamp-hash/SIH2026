from pathlib import Path
from collections import defaultdict
import re
import shutil

# Full VeRi dataset
SOURCE = Path("data/veri/VeRi/image_train")

# Our demo dataset
DEMO = Path("data/demo")

# Create camera folders
for camera in range(1, 4):
    (DEMO / f"camera_{camera}").mkdir(parents=True, exist_ok=True)


# Store:
# vehicle_id -> camera_id -> images
vehicles = defaultdict(lambda: defaultdict(list))

# Example VeRi filename:
# 0002_c001_00030600_0.jpg
pattern = re.compile(r"^(\d+)_c(\d+)_")


# Read all training images
for image in SOURCE.glob("*.jpg"):

    match = pattern.match(image.name)

    if not match:
        continue

    vehicle_id = int(match.group(1))
    camera_id = int(match.group(2))

    vehicles[vehicle_id][camera_id].append(image)


# Find vehicles appearing in at least 3 cameras
candidates = []

for vehicle_id, cameras in vehicles.items():

    if len(cameras) >= 3:
        candidates.append(vehicle_id)


# Keep the result consistent
candidates.sort()

# Select first 6 suitable vehicles
selected_vehicles = candidates[:6]

print("\nSelected vehicles:")
print(selected_vehicles)

print("\nCreating demo dataset...\n")


# Put each vehicle into 3 simulated cameras
for vehicle_id in selected_vehicles:

    cameras = sorted(vehicles[vehicle_id].keys())

    selected_cameras = cameras[:3]

    for demo_camera, real_camera in enumerate(selected_cameras, start=1):

        image = vehicles[vehicle_id][real_camera][0]

        destination = (
            DEMO
            / f"camera_{demo_camera}"
            / f"vehicle_{vehicle_id}_camera_{real_camera}.jpg"
        )

        shutil.copy2(image, destination)

        print(
            f"Vehicle {vehicle_id} | "
            f"Real Camera {real_camera} -> "
            f"Demo Camera {demo_camera}"
        )


print("\n================================")
print("DEMO DATASET CREATED SUCCESSFULLY")
print("================================")