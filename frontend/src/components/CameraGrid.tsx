import React from 'react';
import { CameraCard } from './CameraCard';
import type { CameraStatus, TrackedVehicle } from '../types';

interface CameraGridProps {
    cameras: Record<number, CameraStatus>;
    activeVehicles: TrackedVehicle[];
}

export const CameraGrid: React.FC<CameraGridProps> = ({ cameras, activeVehicles }) => {
    return (
        <section className="cameras-section">
            <h2>Live Camera Nodes</h2>
            <div className="camera-grid">
                {[1, 2, 3].map(cameraId => {
                    const camera = cameras[cameraId];
                    const vehicleAtCamera = activeVehicles.find(v => v.current_camera === cameraId);
                    
                    return (
                        <CameraCard 
                            key={cameraId} 
                            cameraId={cameraId} 
                            camera={camera} 
                            vehicle={vehicleAtCamera} 
                        />
                    );
                })}
            </div>
        </section>
    );
};
