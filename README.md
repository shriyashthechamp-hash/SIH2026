# ANVAY - Distributed Multi-Camera Vehicle Intelligence

This project implements a distributed ANPR and vehicle tracking system designed for a 3-Mac physical hackathon demo.

## Features
- **Central Dashboard**: A real-time web interface built with FastAPI and WebSockets, visualizing vehicle trajectories across cameras.
- **Camera Nodes**: Independent nodes that run YOLO11 for vehicle detection and a custom YOLO for license plate detection.
- **Identity Association**: A temporal and sequence-based tracking engine to identify the same vehicle as it moves from Camera 1 to 2 to 3.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
```

## HOW TO RUN THE 3-MAC DEMO (EXACT SETUP)

### Mac 1 (Server + Dashboard + Camera 1)
This Mac will host the central brain and run the first camera.

1. Ensure the Mac is connected to the same Wi-Fi/LAN as Mac 2 and Mac 3.
2. Find the local IP address of Mac 1 (e.g., `192.168.1.100`).
3. Start the server:
   ```bash
   export SERVER_HOST=0.0.0.0
   python server/main.py
   ```
4. Open the dashboard in a browser: `http://localhost:8000/dashboard`
5. In a new terminal, start Camera 1:
   ```bash
   export SERVER_HOST=127.0.0.1
   python camera_node/main.py --camera-id 1
   ```

### Mac 2 (Camera 2)
1. On Mac 2, pull the repository.
2. Edit `.env` and set `SERVER_HOST` to Mac 1's IP address (e.g., `192.168.1.100`).
3. Start Camera 2:
   ```bash
   python camera_node/main.py --camera-id 2
   ```

### Mac 3 (Camera 3)
1. On Mac 3, pull the repository.
2. Edit `.env` and set `SERVER_HOST` to Mac 1's IP address (e.g., `192.168.1.100`).
3. Start Camera 3:
   ```bash
   python camera_node/main.py --camera-id 3
   ```

## Physical Demo Setup Guide

1. **Positioning**: Place Mac 1, Mac 2, and Mac 3 in a straight line on a table.
2. **Camera Angles**: Angle the webcams down slightly towards the table surface so they have distinct, non-overlapping fields of view.
3. **Execution**: Start the server and all three camera nodes. Ensure the Dashboard shows "3 CAMERAS ONLINE".
4. **The Demo**: Take the toy car and slowly slide it across the table from Mac 1, to Mac 2, to Mac 3. The dashboard will track the journey live.

## Simulation Mode (Development)

If you don't have 3 Macs available, you can simulate the demo using the provided script and demo images.

1. Start the server:
   ```bash
   python server/main.py
   ```
2. Open the dashboard: `http://localhost:8000/dashboard`
3. Run the simulation script:
   ```bash
   python scripts/simulate_demo.py
   ```
