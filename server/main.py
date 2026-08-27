import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from typing import List

from core.models import DetectionEvent
from core.config import SERVER_HOST, SERVER_PORT
from server.tracking import TrackingEngine

app = FastAPI(title="ANVAY Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TrackingEngine()

# Mount dashboard
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

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

@app.post("/api/events")
async def receive_event(event: DetectionEvent):
    vehicle = engine.process_detection(event)
    
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def cleanup_task():
    while True:
        completed = engine.cleanup_stale_vehicles()
        for v in completed:
            await manager.broadcast({
                "type": "vehicle_completed",
                "vehicle": v.model_dump()
            })
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_task())

if __name__ == "__main__":
    uvicorn.run("server.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
