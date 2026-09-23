import React, { useEffect, useRef } from 'react';
import type { CameraStatus, TrackedVehicle } from '../types';

interface CameraCardProps {
    cameraId: number;
    camera?: CameraStatus;
    vehicle?: TrackedVehicle;
}

export const CameraCard: React.FC<CameraCardProps> = ({ cameraId, camera, vehicle }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const isOnline = camera && (Date.now() / 1000 - camera.last_seen) < 10;
    const hasFrame = isOnline && camera.last_frame_base64 && camera.last_frame_base64.length > 20000;

    useEffect(() => {
        if (!hasFrame || !camera.last_frame_base64) return;
        
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        const img = new Image();
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        };
        img.src = `data:image/jpeg;base64,${camera.last_frame_base64}`;
    }, [camera?.last_frame_base64, hasFrame]);

    return (
        <div className="camera-panel" id={`camera-${cameraId}`}>
            <div className="camera-header">
                <h3>CAMERA {cameraId.toString().padStart(2, '0')}</h3>
                <span className={`status-badge ${isOnline ? 'online' : 'offline'}`}>
                    {isOnline ? 'ONLINE' : 'OFFLINE'}
                </span>
            </div>
            <div className={`camera-feed ${hasFrame ? 'active' : ''}`}>
                <canvas ref={canvasRef} id={`feed-cam-${cameraId}`} className="camera-canvas"></canvas>
                <div className="camera-overlay">
                    <div className="overlay-text">
                        {isOnline ? (
                            vehicle ? (
                                <>
                                    {vehicle.vehicle_type.toUpperCase()}<br/>
                                    {(vehicle.confidence * 100).toFixed(0)}%<br/><br/>
                                    {vehicle.vehicle_color || 'UNKNOWN'}<br/><br/>
                                    {vehicle.plate_text ? vehicle.plate_text : 'NO PLATE'}
                                </>
                            ) : (
                                'SCANNING...'
                            )
                        ) : (
                            'NO SIGNAL'
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
