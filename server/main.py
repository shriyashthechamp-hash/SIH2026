import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from core.models import DetectionEvent
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from typing import List

from core.models import DetectionEvent
from core.config import SERVER_HOST, SERVER_PORT
from server.tracking import TrackingEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[SERVER] Listening on 0.0.0.0:{os.environ.get('PORT', SERVER_PORT)}")
    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()

app = FastAPI(title="ANVAY Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TrackingEngine()

# Dashboard will be mounted at the end

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "active_vehicles": [v.model_dump() for v in engine.active_vehicles.values()],
            "cameras": [c.model_dump() for c in engine.camera_statuses.values()]
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ANVAY"}

@app.post("/api/events")
async def receive_event(event: DetectionEvent):
    try:
        vehicle = engine.process_detection(event)
    except Exception as e:
        print(f"[ERROR] Error processing event: {e}")
        raise HTTPException(status_code=500, detail="Error processing event")
    
    # Broadcast event
    await manager.broadcast({
        "type": "vehicle_update",
        "vehicle": vehicle.model_dump(),
        "event_camera": event.camera_id
    })
    
    # Broadcast camera status update
    await manager.broadcast({
        "type": "camera_update",
        "camera": engine.camera_statuses[event.camera_id].model_dump()
    })
    return {"status": "success", "vehicle_id": vehicle.global_vehicle_id}

@app.post("/api/camera/status")
async def receive_camera_status(update: dict):
    try:
        camera_id = update.get("camera_id")
        status = update.get("status")
        frame_base64 = update.get("frame_base64")
        
        if camera_id is not None:
            engine.update_camera_status(camera_id, status, frame_base64)
    except Exception as e:
        print(f"[ERROR] Error processing camera status: {e}")
        raise HTTPException(status_code=500, detail="Error processing camera status")
    
    await manager.broadcast({
        "type": "camera_update",
        "camera": engine.camera_statuses[camera_id].model_dump()
    })
    return {"status": "success"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def cleanup_task():
    try:
        while True:
            completed = engine.cleanup_stale_vehicles()
            for v in completed:
                await manager.broadcast({
                    "type": "vehicle_completed",
                    "vehicle": v.model_dump()
                })
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        pass

# Mount dashboard at the very end to avoid intercepting API routes (fixes 405 error)
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", SERVER_PORT))
    uvicorn.run("server.main:app", host="0.0.0.0", port=port, reload=True)
