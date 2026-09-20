from pydantic import BaseModel
from typing import Optional, List
import uuid

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class DetectionEvent(BaseModel):
    event_id: str
    camera_id: int
    timestamp: float
    vehicle_type: str
    confidence: float
    bounding_box: BoundingBox
    plate_detected: bool
    plate_confidence: Optional[float] = None
    plate_box: Optional[BoundingBox] = None
    plate_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    vehicle_color: Optional[str] = None
    image_base64: Optional[str] = None 

class CameraStatusUpdate(BaseModel):
    camera_id: int
    status: str
    frame_base64: Optional[str] = None

class CameraStatus(BaseModel):
    camera_id: int
    status: str
    last_seen: float
    last_frame_base64: Optional[str] = None

class JourneyStage(BaseModel):
    camera_id: int
    timestamp: float
    confidence: float

class VehicleIdentity(BaseModel):
    global_vehicle_id: str
    vehicle_type: str
    confidence: float
    plate_detected: bool
    first_seen: float
    last_seen: float
    current_camera: int
    journey: List[JourneyStage] = []
    is_completed: bool = False
    duration: float = 0.0
    plate_confidence: Optional[float] = None
    plate_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    vehicle_color: Optional[str] = None
    latest_image_base64: Optional[str] = None
