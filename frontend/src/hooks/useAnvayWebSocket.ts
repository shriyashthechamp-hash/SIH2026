import { useState, useEffect, useCallback, useRef } from 'react';
import type { TrackedVehicle, CameraStatus, WebSocketMessage, TimelineEvent } from '../types';

export function useAnvayWebSocket() {
    const [activeVehicles, setActiveVehicles] = useState<Record<string, TrackedVehicle>>({});
    const [completedCount, setCompletedCount] = useState(0);
    const [cameras, setCameras] = useState<Record<number, CameraStatus>>({});
    const [connectionStatus, setConnectionStatus] = useState<'Connecting...' | 'Connected' | 'Disconnected. Reconnecting...'>('Connecting...');
    const [events, setEvents] = useState<TimelineEvent[]>([]);

    const wsRef = useRef<WebSocket | null>(null);

    const logEvent = useCallback((message: string) => {
        setEvents((prev) => {
            const newEvent: TimelineEvent = {
                id: Math.random().toString(36).substring(2, 9),
                time: new Date().toLocaleTimeString(),
                message
            };
            const newEvents = [newEvent, ...prev];
            if (newEvents.length > 50) return newEvents.slice(0, 50);
            return newEvents;
        });
    }, []);

    const connect = useCallback(() => {
        setConnectionStatus('Connecting...');
        
        let wsUrl = import.meta.env.VITE_WS_URL;
        if (!wsUrl || import.meta.env.PROD) {
            // Fallback for local development or infer from location in production
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = (import.meta.env.PROD || !import.meta.env.VITE_API_URL)
                ? window.location.host 
                : import.meta.env.VITE_API_URL.replace(/^https?:\/\//, '');
            wsUrl = `${protocol}//${host}/ws`;
        }

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            setConnectionStatus('Connected');
        };

        ws.onclose = () => {
            setConnectionStatus('Disconnected. Reconnecting...');
            // Attempt to reconnect
            setTimeout(connect, 2000);
        };

        ws.onmessage = (event) => {
            try {
                const data: WebSocketMessage = JSON.parse(event.data);
                
                if (data.type === 'initial_state') {
                    const vehiclesMap: Record<string, TrackedVehicle> = {};
                    data.active_vehicles.forEach(v => vehiclesMap[v.global_vehicle_id] = v);
                    setActiveVehicles(vehiclesMap);

                    const camerasMap: Record<number, CameraStatus> = {};
                    data.cameras.forEach(c => camerasMap[c.camera_id] = c);
                    setCameras(camerasMap);
                } else if (data.type === 'vehicle_update') {
                    setActiveVehicles(prev => {
                        const v = data.vehicle;
                        const isNew = !prev[v.global_vehicle_id];
                        
                        if (isNew) {
                            logEvent(`Vehicle detected at Camera ${v.current_camera}`);
                            if (v.plate_detected) {
                                setTimeout(() => logEvent(`Plate recognized`), 1000);
                            }
                        } else {
                            // Using the logic from original app.js:
                            const lastJourney = v.journey[v.journey.length - 2];
                            if (lastJourney && v.current_camera !== lastJourney.camera_id) {
                                logEvent(`Camera transition`);
                                setTimeout(() => logEvent(`Vehicle detected at Camera ${v.current_camera}`), 1000);
                            }
                        }

                        return { ...prev, [v.global_vehicle_id]: v };
                    });
                } else if (data.type === 'camera_update') {
                    setCameras(prev => ({
                        ...prev,
                        [data.camera.camera_id]: data.camera
                    }));
                } else if (data.type === 'vehicle_completed') {
                    setActiveVehicles(prev => {
                        const next = { ...prev };
                        delete next[data.vehicle.global_vehicle_id];
                        return next;
                    });
                    setCompletedCount(prev => prev + 1);
                    logEvent(`Journey completed (${data.vehicle.duration.toFixed(1)}s)`);
                }
            } catch (err) {
                console.error("Failed to parse WebSocket message", err);
            }
        };
    }, [logEvent]);

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null; // Prevent reconnect on unmount
                wsRef.current.close();
            }
        };
    }, [connect]);

    return {
        activeVehicles: Object.values(activeVehicles),
        completedCount,
        cameras,
        connectionStatus,
        events
    };
}
