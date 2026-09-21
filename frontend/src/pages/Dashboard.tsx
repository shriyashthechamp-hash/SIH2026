import React from 'react';
import { Header } from '../components/Header';
import { JourneyMap } from '../components/JourneyMap';
import { CameraGrid } from '../components/CameraGrid';
import { TrackedVehicles } from '../components/TrackedVehicles';
import { EventTimeline } from '../components/EventTimeline';
import { useAnvayWebSocket } from '../hooks/useAnvayWebSocket';

export const Dashboard: React.FC = () => {
    const { activeVehicles, completedCount, cameras, connectionStatus, events } = useAnvayWebSocket();

    const activeCamerasCount = Object.values(cameras).filter(c => (Date.now() / 1000 - c.last_seen) < 10).length;

    return (
        <>
            <Header 
                activeVehiclesCount={activeVehicles.length}
                completedJourneysCount={completedCount}
                camerasOnlineCount={activeCamerasCount}
                connectionStatus={connectionStatus}
            />
            <main>
                <JourneyMap vehicles={activeVehicles} />
                <CameraGrid cameras={cameras} activeVehicles={activeVehicles} />
                
                <div className="lower-layout">
                    <TrackedVehicles vehicles={activeVehicles} />
                    <EventTimeline events={events} />
                </div>
            </main>
        </>
    );
};
