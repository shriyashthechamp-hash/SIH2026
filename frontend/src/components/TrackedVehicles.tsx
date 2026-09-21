import React from 'react';
import { VehicleCard } from './VehicleCard';
import type { TrackedVehicle } from '../types';

interface TrackedVehiclesProps {
    vehicles: TrackedVehicle[];
}

export const TrackedVehicles: React.FC<TrackedVehiclesProps> = ({ vehicles }) => {
    return (
        <section className="active-vehicles-section">
            <h2>Tracked Vehicles</h2>
            <div className="vehicles-list" id="vehicles-list">
                {vehicles.map(v => (
                    <VehicleCard key={v.global_vehicle_id} vehicle={v} />
                ))}
            </div>
        </section>
    );
};
