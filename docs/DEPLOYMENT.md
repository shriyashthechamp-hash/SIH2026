# ANVAY Deployment Guide

This guide describes how to deploy the ANVAY Central Server to a production environment. Camera nodes remain running at the edge.

## Architecture

The system is split into two deployment units:
1. **Central Server:** FastAPI + WebSockets. Highly scalable.
2. **Camera Nodes:** Heavy YOLO AI Edge nodes. Run on physical hardware locally.

## Deploying the Central Server

The server is built with FastAPI and binds to the `PORT` environment variable by default, making it instantly compatible with PaaS providers like Heroku, Render, Railway, or AWS App Runner.

### 1. Preparing the Environment
Ensure your PaaS environment has Python 3.9+ installed.
Define the start command in your platform (or a `Procfile`):
```bash
python server/main.py
```

### 2. Environment Variables
Configure the following in your hosting dashboard:
- `SERVER_PORT`: Default port to bind to if `$PORT` isn't set.
- `PORT`: (Injected automatically by Heroku/Render)

### 3. Health Checks
PaaS systems require a health endpoint to verify the deployment is alive.
Configure your load balancer or deployment platform to ping:
`GET /health`

Expected response: `HTTP 200 OK`
```json
{"status": "ok", "service": "ANVAY"}
```

### 4. Edge Node Configuration
Once the server is deployed (e.g., `https://anvay-server.herokuapp.com`), configure your local physical edge nodes (Camera Nodes) to point to the server:

**Edge Node `.env`:**
```env
SERVER_HOST=anvay-server.herokuapp.com
SERVER_PORT=443
```
*(Note: If using HTTPS, modify the `camera_node/main.py` protocol string from `http://` to `https://` if needed.)*

## Running Camera Nodes in Production

Camera nodes must run on physical hardware with GPU or TPU acceleration (e.g., Jetson Nano, Edge TPU, or local workstation).

Install requirements and run as a systemd service:

`/etc/systemd/system/anvay-camera.service`
```ini
[Unit]
Description=ANVAY Camera Node
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/ANVAY/camera_node/main.py --camera-id 1 --source 0
WorkingDirectory=/path/to/ANVAY
Restart=always

[Install]
WantedBy=multi-user.target
```
