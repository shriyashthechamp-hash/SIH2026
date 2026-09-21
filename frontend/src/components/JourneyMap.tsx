import React from 'react';
import type { TrackedVehicle } from '../types';

interface JourneyMapProps {
    vehicles: TrackedVehicle[];
}

export const JourneyMap: React.FC<JourneyMapProps> = ({ vehicles }) => {
    return (
        <section className="trajectory-section">
            <h2>Live Journey Map</h2>
            <div className="trajectory-map" id="trajectory-map">
                {vehicles.length === 0 ? (
                    <div className="empty-state">Waiting for vehicle detections...</div>
                ) : (
                    vehicles.map(v => {
                        const hasCam1 = v.journey.some(j => j.camera_id === 1) || v.current_camera === 1;
                        const hasCam2 = v.journey.some(j => j.camera_id === 2) || v.current_camera === 2;
                        const hasCam3 = v.journey.some(j => j.camera_id === 3) || v.current_camera === 3;
                        
                        return (
                            <div key={v.global_vehicle_id} className="journey-row">
                                <div className="journey-vid">{v.global_vehicle_id}</div>
                                <div className="journey-path">
                                    <div className={`node ${hasCam1 ? 'passed' : ''} ${v.current_camera === 1 ? 'active' : ''}`}>
                                        <div className="node-circle">1</div>
                                        <span className="node-label">Camera 1</span>
                                    </div>
                                    <div className={`line ${hasCam1 && (hasCam2 || hasCam3) ? 'active' : ''}`}></div>
                                    <div className={`node ${hasCam2 ? 'passed' : ''} ${v.current_camera === 2 ? 'active' : ''}`}>
                                        <div className="node-circle">2</div>
                                        <span className="node-label">Camera 2</span>
                                    </div>
                                    <div className={`line ${hasCam2 && hasCam3 ? 'active' : ''}`}></div>
                                    <div className={`node ${hasCam3 ? 'passed' : ''} ${v.current_camera === 3 ? 'active' : ''}`}>
                                        <div className="node-circle">3</div>
                                        <span className="node-label">Camera 3</span>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </section>
    );
};
