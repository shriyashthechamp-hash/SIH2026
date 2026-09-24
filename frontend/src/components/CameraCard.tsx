import React, { useEffect, useRef, useState, useCallback } from 'react';
import type { CameraStatus, TrackedVehicle } from '../types';
import { api } from '../services/api';

interface CameraCardProps {
    cameraId: number;
    camera?: CameraStatus;
    vehicle?: TrackedVehicle;
}

export const CameraCard: React.FC<CameraCardProps> = ({ cameraId, camera, vehicle }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const captureCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const inFlightRef = useRef<boolean>(false);

    const [hasPermission, setHasPermission] = useState<boolean>(false);
    const [isRequesting, setIsRequesting] = useState<boolean>(false);
    const [permissionError, setPermissionError] = useState<string | null>(null);
    const [localDetection, setLocalDetection] = useState<{
        vehicle_type?: string;
        confidence?: number;
        vehicle_color?: string;
        plate_text?: string;
        plate_detected?: boolean;
    } | null>(null);

    const isOnline = Boolean(camera && (Date.now() / 1000 - camera.last_seen) < 10);
    const hasFrame = Boolean(isOnline && camera?.last_frame_base64 && camera.last_frame_base64.length > 20000);

    const isCamera1 = cameraId === 1;
    const showOnboarding = isCamera1 && !hasPermission && !hasFrame && !isOnline;

    // Callback ref for the video element to guarantee immediate attachment of the stream
    const setVideoElement = useCallback((node: HTMLVideoElement | null) => {
        videoRef.current = node;
        if (node && streamRef.current) {
            if (node.srcObject !== streamRef.current) {
                node.srcObject = streamRef.current;
            }
            node.play().catch(e => console.error("Error playing video:", e));
        }
    }, []);

    // Draw backend frame on canvas if received and not in local webcam mode
    useEffect(() => {
        if (hasPermission || !hasFrame || !camera?.last_frame_base64) return;
        
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
    }, [camera?.last_frame_base64, hasFrame, hasPermission]);

    // Handle Enable Camera button click with real getUserMedia
    const handleEnableCamera = async () => {
        setIsRequesting(true);
        setPermissionError(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            streamRef.current = stream;
            setHasPermission(true);
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play().catch(e => console.error("Error playing video:", e));
            }
        } catch (err: any) {
            console.error("Camera permission error:", err);
            const msg = err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError'
                ? "Permission denied. Please allow camera access in your browser."
                : (err?.message || "Failed to access camera. Please check browser permissions.");
            setPermissionError(msg);
        } finally {
            setIsRequesting(false);
        }
    };

    // Clean up tracks on unmount
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Frame capture and transmission loop for Camera 01
    useEffect(() => {
        if (!hasPermission || !isCamera1) return;

        if (!captureCanvasRef.current) {
            captureCanvasRef.current = document.createElement('canvas');
        }

        const interval = setInterval(async () => {
            const video = videoRef.current;
            if (!video || video.readyState < 2 || inFlightRef.current) return;

            const canvas = captureCanvasRef.current;
            if (!canvas) return;

            const maxDim = 640;
            let w = video.videoWidth || 640;
            let h = video.videoHeight || 480;
            if (Math.max(w, h) > maxDim) {
                const scale = maxDim / Math.max(w, h);
                w = Math.round(w * scale);
                h = Math.round(h * scale);
            }

            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            ctx.drawImage(video, 0, 0, w, h);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);

            inFlightRef.current = true;
            try {
                const result = await api.sendFrame(1, dataUrl);
                if (result && result.meta) {
                    if (result.meta.vehicle_detected) {
                        setLocalDetection({
                            vehicle_type: result.meta.vehicle_type,
                            confidence: result.meta.confidence,
                            vehicle_color: result.meta.vehicle_color,
                            plate_text: result.meta.plate_text,
                            plate_detected: result.meta.plate_detected
                        });
                    }
                }
            } catch (e) {
                console.error("Frame transmission error:", e);
            } finally {
                inFlightRef.current = false;
            }
        }, 280); // ~3.5 fps

        return () => clearInterval(interval);
    }, [hasPermission, isCamera1]);

    const statusText = showOnboarding
        ? (isRequesting ? 'REQUESTING...' : 'AWAITING PERMISSION')
        : (isCamera1 && hasPermission ? 'LIVE' : (isOnline ? 'ONLINE' : 'OFFLINE'));

    const statusClass = showOnboarding
        ? 'awaiting'
        : (isCamera1 && hasPermission ? 'online' : (isOnline ? 'online' : 'offline'));

    // Determine displayed vehicle detection (either from central WebSocket state or immediate local detection)
    const currentVehicle = vehicle || (localDetection?.vehicle_type ? {
        vehicle_type: localDetection.vehicle_type,
        confidence: localDetection.confidence || 0,
        vehicle_color: localDetection.vehicle_color || 'UNKNOWN',
        plate_text: localDetection.plate_text || null
    } : null);

    return (
        <div className="camera-panel" id={`camera-${cameraId}`}>
            <div className="camera-header">
                <h3>CAMERA {cameraId.toString().padStart(2, '0')}</h3>
                <span className={`status-badge ${statusClass}`}>
                    {statusText}
                </span>
            </div>
            
            {showOnboarding ? (
                <div className="camera-feed onboarding-feed">
                    <div className="camera-onboarding">
                        <div className="onboarding-left">
                            <div className="onboarding-header-group">
                                <h2 className="onboarding-title">
                                    Let’s get<br />Camera Access
                                </h2>
                                <p className="onboarding-subtitle">
                                    We need access to your camera<br />to detect vehicles in real time.
                                </p>
                            </div>

                            <div className="onboarding-steps">
                                <div className="onboarding-step">
                                    <div className="step-num">1</div>
                                    <p className="step-text">Click 'Allow' when prompted</p>
                                </div>
                                <div className="onboarding-step">
                                    <div className="step-num">2</div>
                                    <p className="step-text">
                                        Show a vehicle (e.g. a car image on your phone)<br />
                                        in front of the camera
                                    </p>
                                </div>
                                <div className="onboarding-step">
                                    <div className="step-num">3</div>
                                    <p className="step-text">See live detection in action!</p>
                                </div>
                            </div>

                            <div className="onboarding-action">
                                <button 
                                    className="btn-enable-camera" 
                                    onClick={handleEnableCamera}
                                    disabled={isRequesting}
                                >
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                                        <circle cx="12" cy="13" r="4"/>
                                    </svg>
                                    <span>{isRequesting ? 'Requesting...' : 'Enable Camera'}</span>
                                </button>
                                {permissionError && (
                                    <div className="onboarding-error">{permissionError}</div>
                                )}
                            </div>
                        </div>

                        <div className="onboarding-right">
                            <svg className="onboarding-illustration" viewBox="0 0 240 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#42c99b" stopOpacity="0.35"/>
                                        <stop offset="100%" stopColor="#ffe66b" stopOpacity="0.05"/>
                                    </linearGradient>
                                    <linearGradient id="phoneScreenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stopColor="#1e293b"/>
                                        <stop offset="100%" stopColor="#0f172a"/>
                                    </linearGradient>
                                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#ffe66b" />
                                    </marker>
                                </defs>

                                {/* Laptop & Webcam */}
                                <g id="laptop" transform="translate(10, 30)">
                                    <rect x="15" y="25" width="70" height="75" rx="5" fill="#14151f" stroke="#3b3e52" strokeWidth="1.5" />
                                    <rect x="19" y="32" width="62" height="63" rx="2" fill="#1e202e" />
                                    <circle cx="50" cy="28.5" r="2" fill="#42c99b" />
                                    <circle cx="50" cy="28.5" r="3.5" stroke="#42c99b" strokeWidth="0.75" strokeOpacity="0.6" />
                                    <path d="M5 100 L95 100 L105 108 L-5 108 Z" fill="#282a38" stroke="#3b3e52" strokeWidth="1.5" />
                                    <rect x="35" y="102" width="30" height="3" rx="1.5" fill="#1a1c26" />
                                </g>

                                {/* Vision Rays */}
                                <polygon points="60,58.5 130,45 130,120" fill="url(#beamGrad)" />
                                <line x1="60" y1="58.5" x2="132" y2="52" stroke="#42c99b" strokeWidth="1" strokeDasharray="3 3" opacity="0.8" />
                                <line x1="60" y1="58.5" x2="132" y2="115" stroke="#ffe66b" strokeWidth="1" strokeDasharray="3 3" opacity="0.8" />

                                {/* Phone & Hand */}
                                <g id="phone-and-hand" transform="translate(130, 35)">
                                    <rect x="8" y="10" width="56" height="88" rx="8" fill="#12131a" stroke="#ffffff" strokeWidth="1.8" />
                                    <line x1="28" y1="15" x2="44" y2="15" stroke="#4a4d60" strokeWidth="1.5" strokeLinecap="round" />
                                    <rect x="12" y="20" width="48" height="70" rx="4" fill="url(#phoneScreenGrad)" />
                                    
                                    <g transform="translate(14, 34)">
                                        <ellipse cx="22" cy="38" rx="18" ry="3" fill="#ffe66b" fillOpacity="0.15" />
                                        <path d="M5 28 C6 24 10 22 14 20 L28 20 C32 22 36 24 38 28 L41 30 C42 31 42 34 40 34 L4 34 C2 34 2 31 3 30 Z" fill="#ffad4a" stroke="#ffffff" strokeWidth="0.8"/>
                                        <path d="M14 21 L18 15 L26 15 L30 21 Z" fill="#38bdf8" fillOpacity="0.9" stroke="#ffffff" strokeWidth="0.6"/>
                                        <circle cx="11" cy="34" r="3.5" fill="#0f172a" stroke="#ffffff" strokeWidth="0.8" />
                                        <circle cx="11" cy="34" r="1.5" fill="#ffe66b" />
                                        <circle cx="32" cy="34" r="3.5" fill="#0f172a" stroke="#ffffff" strokeWidth="0.8" />
                                        <circle cx="32" cy="34" r="1.5" fill="#ffe66b" />
                                        <path d="M40 30 L45 28 L45 33 Z" fill="#ffe66b" opacity="0.8" />
                                    </g>

                                    <path d="M4 64 C2 58 8 58 9 64 C9 68 5 70 3 68 Z" fill="#fcd34d" stroke="#050505" strokeWidth="1.2" />
                                    <path d="M64 42 C68 42 68 50 64 50 M64 53 C68 53 68 61 64 61 M64 64 C68 64 68 72 64 72" fill="none" stroke="#050505" strokeWidth="2.5" strokeLinecap="round" />
                                    <path d="M64 42 C67.5 42 67.5 50 64 50 M64 53 C67.5 53 67.5 61 64 61 M64 64 C67.5 64 67.5 72 64 72" fill="none" stroke="#fcd34d" strokeWidth="1.5" strokeLinecap="round" />
                                    <path d="M26 98 L24 130 L46 130 L44 98 Z" fill="#fcd34d" stroke="#050505" strokeWidth="1.2" />
                                </g>

                                {/* Callout note */}
                                <g id="callout" transform="translate(135, 5)">
                                    <text x="40" y="10" fill="#ffffff" fontSize="7.5" fontWeight="700" fontFamily="system-ui, sans-serif" textAnchor="middle">
                                        Show a car image
                                    </text>
                                    <text x="40" y="19" fill="#a0aec0" fontSize="6.5" fontWeight="500" fontFamily="system-ui, sans-serif" textAnchor="middle">
                                        in front of your camera!
                                    </text>
                                    <path d="M 40 22 C 38 27 34 32 30 36" fill="none" stroke="#ffe66b" strokeWidth="1.2" strokeDasharray="2.5 2" markerEnd="url(#arrow)" />
                                </g>
                            </svg>
                        </div>
                    </div>
                </div>
            ) : (
                <div className={`camera-feed ${hasFrame || hasPermission ? 'active' : ''}`}>
                    {hasPermission ? (
                        <video 
                            ref={setVideoElement} 
                            autoPlay 
                            playsInline 
                            muted 
                            className="camera-video"
                        />
                    ) : (
                        <canvas ref={canvasRef} id={`feed-cam-${cameraId}`} className="camera-canvas"></canvas>
                    )}
                    <div className="camera-overlay">
                        <div className="overlay-text">
                            {currentVehicle ? (
                                <>
                                    {currentVehicle.vehicle_type.toUpperCase()}<br/>
                                    {(currentVehicle.confidence * 100).toFixed(0)}%<br/><br/>
                                    {currentVehicle.vehicle_color || 'UNKNOWN'}<br/><br/>
                                    {currentVehicle.plate_text ? currentVehicle.plate_text : 'NO PLATE'}
                                </>
                            ) : (isOnline || hasPermission) ? (
                                'SCANNING...'
                            ) : (
                                'NO SIGNAL'
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};



