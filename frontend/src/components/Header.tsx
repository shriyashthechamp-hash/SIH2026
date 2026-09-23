import React from 'react';
import { Link } from 'react-router-dom';

interface HeaderProps {
    activeVehiclesCount: number;
    completedJourneysCount: number;
    camerasOnlineCount: number;
    connectionStatus: 'Connecting...' | 'Connected' | 'Disconnected. Reconnecting...';
}

export const Header: React.FC<HeaderProps> = ({
    activeVehiclesCount,
    completedJourneysCount,
    camerasOnlineCount,
    connectionStatus
}) => {
    const isConnected = connectionStatus === 'Connected';

    return (
        <header>
            <div className="header-content">
                <Link to="/" style={{ textDecoration: 'none', color: '#888', fontSize: '12px', marginBottom: '8px', display: 'inline-block' }}>← BACK TO ANVAY</Link>
                <h1>ANVAY <span>Multi-Camera Vehicle Intelligence</span></h1>
                <p className="subtitle">Distributed Vehicle Tracking & ANPR Command Center</p>
            </div>
            
            <div className="kpi-container">
                <div className="kpi-card">
                    <div className="kpi-value">{activeVehiclesCount}</div>
                    <div className="kpi-label">ACTIVE VEHICLES</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value">{completedJourneysCount}</div>
                    <div className="kpi-label">TOTAL JOURNEYS</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value">{camerasOnlineCount}</div>
                    <div className="kpi-label">CAMERAS ONLINE</div>
                </div>
            </div>
            
            <div className="status-indicator">
                <div className={`pulse-dot ${isConnected ? 'connected' : ''}`}></div>
                <span>{connectionStatus}</span>
            </div>
        </header>
    );
};
