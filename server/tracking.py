import uuid
import time
from typing import Dict, List, Optional
from core.models import DetectionEvent, VehicleIdentity, JourneyStage, CameraStatus
from core.config import MAX_TRANSITION_SECONDS

class TrackingEngine:
    def __init__(self):
        self.active_vehicles: Dict[str, VehicleIdentity] = {}
        self.completed_vehicles: Dict[str, VehicleIdentity] = {}
        self.camera_statuses: Dict[int, CameraStatus] = {}

    def update_camera_status(self, camera_id: int, status: str, last_frame_base64: Optional[str] = None):
        self.camera_statuses[camera_id] = CameraStatus(
            camera_id=camera_id,
            status=status,
            last_seen=time.time(),
            last_frame_base64=last_frame_base64
        )

    def process_detection(self, event: DetectionEvent) -> VehicleIdentity:
        self.update_camera_status(event.camera_id, "ONLINE", event.image_base64)
        now = time.time()

        matched_vehicle_id = None

        if event.camera_id == 1:
            for vid, v in self.active_vehicles.items():
                if v.current_camera == 1 and (now - v.last_seen) < MAX_TRANSITION_SECONDS:
                    matched_vehicle_id = vid
                    break
        elif event.camera_id == 2:
            for vid, v in self.active_vehicles.items():
                if v.current_camera in [1, 2] and (now - v.last_seen) < MAX_TRANSITION_SECONDS:
                    matched_vehicle_id = vid
                    break
        elif event.camera_id == 3:
            for vid, v in self.active_vehicles.items():
                if v.current_camera in [2, 3] and (now - v.last_seen) < MAX_TRANSITION_SECONDS:
                    matched_vehicle_id = vid
                    break

        if matched_vehicle_id:
            vehicle = self.active_vehicles[matched_vehicle_id]
            if vehicle.current_camera != event.camera_id:
                vehicle.journey.append(JourneyStage(
                    camera_id=event.camera_id,
                    timestamp=now,
                    confidence=event.confidence
                ))
            vehicle.current_camera = event.camera_id
            vehicle.last_seen = now
            vehicle.duration = now - vehicle.first_seen
            if event.plate_detected:
                vehicle.plate_detected = True
            if event.image_base64:
                vehicle.latest_image_base64 = event.image_base64
            
            return vehicle
        else:
            new_vid = f"VEHICLE_{len(self.active_vehicles) + len(self.completed_vehicles) + 1:03d}"
            new_vehicle = VehicleIdentity(
                global_vehicle_id=new_vid,
                vehicle_type=event.vehicle_type,
                confidence=event.confidence,
                plate_detected=event.plate_detected,
                first_seen=now,
                last_seen=now,
                current_camera=event.camera_id,
                journey=[JourneyStage(camera_id=event.camera_id, timestamp=now, confidence=event.confidence)],
                latest_image_base64=event.image_base64
            )
            self.active_vehicles[new_vid] = new_vehicle
            return new_vehicle

    def cleanup_stale_vehicles(self):
        now = time.time()
        stale_ids = []
        completed = []
        for vid, v in self.active_vehicles.items():
            if now - v.last_seen > MAX_TRANSITION_SECONDS:
                v.is_completed = True
                self.completed_vehicles[vid] = v
                stale_ids.append(vid)
                completed.append(v)
        
        for vid in stale_ids:
            del self.active_vehicles[vid]
            
        return completed
