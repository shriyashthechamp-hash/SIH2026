export interface BoundingBox {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface JourneyStage {
    camera_id: number;
    timestamp: number;
    confidence: number;
}

export interface TrackedVehicle {
    global_vehicle_id: string;
    vehicle_type: string;
    confidence: number;
    plate_detected: boolean;
    first_seen: number;
    last_seen: number;
    current_camera: number;
    journey: JourneyStage[];
    is_completed: boolean;
    duration: number;
    plate_confidence?: number | null;
    plate_text?: string | null;
    ocr_confidence?: number | null;
    vehicle_color?: string | null;
    latest_image_base64?: string | null;
}

export interface CameraStatus {
    camera_id: number;
    status: string;
    last_seen: number;
    last_frame_base64?: string | null;
}

export type WebSocketMessage = 
    | { type: 'initial_state'; active_vehicles: TrackedVehicle[]; cameras: CameraStatus[] }
    | { type: 'vehicle_update'; vehicle: TrackedVehicle; event_camera?: number }
    | { type: 'camera_update'; camera: CameraStatus }
    | { type: 'vehicle_completed'; vehicle: TrackedVehicle };

export interface TimelineEvent {
    id: string;
    time: string;
    message: string;
}
