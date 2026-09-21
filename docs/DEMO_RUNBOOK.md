# ANVAY Demo Runbook

This guide contains the exact steps to launch the ANVAY Distributed ANPR system across multiple machines for a live demonstration.

## Prerequisites
1. All laptops/machines must be on the **same Wi-Fi network**.
2. Python 3.9+ installed on all machines.
3. Dependencies installed: `pip install -r requirements.txt`
4. `.env` file copied and configured.

## Step 1: Start Central Server (Machine 1)

This machine acts as the Command Center and hosts the Dashboard.

1. Open terminal on Machine 1:
```bash
python server/main.py
```
2. Find Machine 1's IP address:
- Mac: `ipconfig getifaddr en0`
- Windows: `ipconfig` (Look for IPv4 Address)
*(e.g., 192.168.1.100)*

3. Open the dashboard in a browser:
http://localhost:8000 (or `http://<MACHINE_1_IP>:8000`)

## Step 2: Configure Camera Nodes

On Machine 2 and Machine 3, edit the `.env` file and set the `SERVER_HOST` to Machine 1's IP.

```env
SERVER_HOST=192.168.1.100
SERVER_PORT=8000
```

## Step 3: Start Camera Nodes

### Camera 1 (Local to Server / Webcam)
On Machine 1, open a new terminal:
```bash
python camera_node/main.py --camera-id 1 --source 0
```

### Camera 2 (Machine 2 / Video feed)
On Machine 2, launch a video feed:
```bash
python camera_node/main.py --camera-id 2 --source data/demo_cam2.mp4
```

### Camera 3 (Machine 3 / Webcam)
On Machine 3, launch using the webcam:
```bash
python camera_node/main.py --camera-id 3 --source 0
```

## Step 4: Verification

1. Verify all terminals say `[CAMERA X] Online and capturing.`
2. Verify the Server terminal shows event receipts.
3. Check the Dashboard (Machine 1).
   - "CAMERAS ONLINE" should equal 3.
   - All three feeds should stream live onto the canvas.
   - Tracked vehicles should appear in the lower pane.
   - Trajectory mapping should draw the live paths of detected vehicles.
