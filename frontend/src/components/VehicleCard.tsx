import React from 'react';
import type { TrackedVehicle } from '../types';

interface VehicleCardProps {
    vehicle: TrackedVehicle;
}

export const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle: v }) => {
    return (
        <div className="vehicle-card">
            <div className="vehicle-img-container">
                {v.latest_image_base64 && (
                    <img src={`data:image/jpeg;base64,${v.latest_image_base64}`} alt="Vehicle" />
                )}
            </div>
            <div className="vehicle-details">
                <h4>{v.global_vehicle_id}</h4>
                <div className="vehicle-meta">
                    <span>{v.vehicle_type.toUpperCase()}</span>
                    <span>{(v.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="vehicle-meta" style={{ marginTop: '5px' }}>
                    <span>COLOR</span>
                    <strong>{v.vehicle_color || 'UNKNOWN'}</strong>
                </div>
                <div className="vehicle-meta" style={{ marginTop: '5px' }}>
                    <span>LICENSE PLATE</span>
                    <strong>{v.plate_text ? v.plate_text : 'NO PLATE'}</strong>
                </div>
                <div className="vehicle-meta" style={{ marginTop: '5px' }}>
                    <span>PLATE DETECTOR</span>
                    <strong>{v.plate_confidence ? (v.plate_confidence * 100).toFixed(0) + '%' : 'N/A'}</strong>
                </div>
                <div className="vehicle-meta" style={{ marginTop: '5px' }}>
                    <span>OCR CONFIDENCE</span>
                    <strong>{v.ocr_confidence ? (v.ocr_confidence * 100).toFixed(0) + '%' : 'UNAVAILABLE'}</strong>
                </div>
            </div>
            <div className="vehicle-details" style={{ borderTop: '1px solid rgba(255,255,255,0.1)', marginTop: '10px', paddingTop: '10px' }}>
                <div className="vehicle-meta">
                    <div>Current: <strong>Camera {v.current_camera}</strong></div>
                    <div>Duration: <strong>{v.duration.toFixed(1)}s</strong></div>
                </div>
            </div>
        </div>
    );
};
