const wsUrl = `ws://${window.location.host}/ws`;
let ws;

const state = {
    active_vehicles: {},
    completed: 0,
    cameras: {}
};

function connectWebSocket() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('connection-status').textContent = 'Connected';
        document.querySelector('.pulse-dot').classList.add('connected');
    };

    ws.onclose = () => {
        document.getElementById('connection-status').textContent = 'Disconnected. Reconnecting...';
        document.querySelector('.pulse-dot').classList.remove('connected');
        setTimeout(connectWebSocket, 2000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

function handleMessage(data) {
    if (data.type === 'initial_state') {
        data.active_vehicles.forEach(v => {
            state.active_vehicles[v.global_vehicle_id] = v;
        });
        data.cameras.forEach(c => {
            state.cameras[c.camera_id] = c;
        });
        updateUI();
    } else if (data.type === 'vehicle_update') {
        const v = data.vehicle;
        const isNew = !state.active_vehicles[v.global_vehicle_id];
        state.active_vehicles[v.global_vehicle_id] = v;
        
        if (isNew) {
            logEvent(`Vehicle detected at Camera ${v.current_camera}`);
            if (v.plate_detected) {
                setTimeout(() => logEvent(`Plate recognized`), 1000);
            }
        } else if (v.current_camera !== v.journey[v.journey.length - 2]?.camera_id) {
            logEvent(`Camera transition`);
            setTimeout(() => logEvent(`Vehicle detected at Camera ${v.current_camera}`), 1000);
        }
        
        updateUI();
    } else if (data.type === 'camera_update') {
        state.cameras[data.camera.camera_id] = data.camera;
        if (data.camera.last_frame_base64 && data.camera.last_frame_base64.length > 20000) {
            renderCameraFeed(data.camera.camera_id, data.camera.last_frame_base64);
        }
        updateUI();
    } else if (data.type === 'vehicle_completed') {
        delete state.active_vehicles[data.vehicle.global_vehicle_id];
        state.completed++;
        logEvent(`Journey completed (${data.vehicle.duration.toFixed(1)}s)`, data.vehicle.global_vehicle_id);
        updateUI();
    }
}

function logEvent(message, vid) {
    const timeline = document.getElementById('events-timeline');
    const time = new Date().toLocaleTimeString();
    
    const el = document.createElement('div');
    el.className = 'event-item';
    el.style.marginBottom = '15px';
    el.innerHTML = `
        <div style="font-size: 12px; color: #888; font-family: 'JetBrains Mono', monospace;">${time}</div>
        <div style="font-weight: 600; margin-top: 4px; color: #fff;">${message}</div>
    `;
    
    timeline.prepend(el);
    if (timeline.children.length > 50) {
        timeline.lastChild.remove();
    }
}

function renderCameraFeed(cameraId, base64Str) {
    if (!base64Str) return;
    const canvas = document.getElementById(`feed-cam-${cameraId}`);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${base64Str}`;
}

function updateUI() {
    // Update KPIs
    document.getElementById('kpi-active').textContent = Object.keys(state.active_vehicles).length;
    document.getElementById('kpi-completed').textContent = state.completed;
    document.getElementById('kpi-cameras').textContent = Object.keys(state.cameras).length;

    // Update Cameras
    for (let i = 1; i <= 3; i++) {
        const cam = state.cameras[i];
        const statusEl = document.getElementById(`status-cam-${i}`);
        const feedEl = document.getElementById(`feed-cam-${i}`);
        const overlayEl = document.getElementById(`overlay-cam-${i}`);
        const feedContainer = feedEl.parentElement;

        if (cam && (Date.now()/1000 - cam.last_seen) < 10) {
            statusEl.textContent = 'ONLINE';
            statusEl.className = 'status-badge online';
            
            // Note: feed is rendered separately via renderCameraFeed()
            if (cam.last_frame_base64 && cam.last_frame_base64.length > 20000) {
                feedContainer.classList.add('active');
            }
            
            // Find what vehicle is currently here
            const v = Object.values(state.active_vehicles).find(v => v.current_camera === i);
            if (v) {
                overlayEl.innerHTML = `${v.vehicle_type.toUpperCase()}<br>${(v.confidence*100).toFixed(0)}%<br><br>${v.vehicle_color || 'UNKNOWN'}<br><br>${v.plate_text ? v.plate_text : (v.plate_detected ? 'NO PLATE' : 'NO PLATE')}`;
            } else {
                overlayEl.textContent = 'SCANNING...';
            }
        } else {
            statusEl.textContent = 'OFFLINE';
            statusEl.className = 'status-badge offline';
            feedContainer.classList.remove('active');
            overlayEl.textContent = 'NO SIGNAL';
        }
    }

    // Update Trajectory
    const mapEl = document.getElementById('trajectory-map');
    const vehicles = Object.values(state.active_vehicles);
    
    if (vehicles.length === 0) {
        mapEl.innerHTML = '<div class="empty-state">Waiting for vehicle detections...</div>';
    } else {
        mapEl.innerHTML = '';
        vehicles.forEach(v => {
            const hasCam1 = v.journey.some(j => j.camera_id === 1) || v.current_camera === 1;
            const hasCam2 = v.journey.some(j => j.camera_id === 2) || v.current_camera === 2;
            const hasCam3 = v.journey.some(j => j.camera_id === 3) || v.current_camera === 3;
            
            const row = document.createElement('div');
            row.className = 'journey-row';
            row.innerHTML = `
                <div class="journey-vid">${v.global_vehicle_id}</div>
                <div class="journey-path">
                    <div class="node ${hasCam1 ? 'passed' : ''} ${v.current_camera === 1 ? 'active' : ''}">
                        <div class="node-circle">1</div>
                        <span class="node-label">Camera 1</span>
                    </div>
                    <div class="line ${hasCam1 && (hasCam2 || hasCam3) ? 'active' : ''}"></div>
                    <div class="node ${hasCam2 ? 'passed' : ''} ${v.current_camera === 2 ? 'active' : ''}">
                        <div class="node-circle">2</div>
                        <span class="node-label">Camera 2</span>
                    </div>
                    <div class="line ${hasCam2 && hasCam3 ? 'active' : ''}"></div>
                    <div class="node ${hasCam3 ? 'passed' : ''} ${v.current_camera === 3 ? 'active' : ''}">
                        <div class="node-circle">3</div>
                        <span class="node-label">Camera 3</span>
                    </div>
                </div>
            `;
            mapEl.appendChild(row);
        });
    }

    // Update Vehicles List
    const listEl = document.getElementById('vehicles-list');
    listEl.innerHTML = '';
    vehicles.forEach(v => {
        const card = document.createElement('div');
        card.className = 'vehicle-card';
        card.innerHTML = `
            <div class="vehicle-img-container">
                ${v.latest_image_base64 ? `<img src="data:image/jpeg;base64,${v.latest_image_base64}">` : ''}
            </div>
            <div class="vehicle-details">
                <h4>${v.global_vehicle_id}</h4>
                <div class="vehicle-meta">
                    <span>${v.vehicle_type.toUpperCase()}</span>
                    <span>${(v.confidence*100).toFixed(0)}%</span>
                </div>
                <div class="vehicle-meta" style="margin-top: 5px;">
                    <span>COLOR</span>
                    <strong>${v.vehicle_color || 'UNKNOWN'}</strong>
                </div>
                <div class="vehicle-meta" style="margin-top: 5px;">
                    <span>LICENSE PLATE</span>
                    <strong>${v.plate_text ? v.plate_text : 'NO PLATE'}</strong>
                </div>
                <div class="vehicle-meta" style="margin-top: 5px;">
                    <span>PLATE DETECTOR</span>
                    <strong>${v.plate_confidence ? (v.plate_confidence*100).toFixed(0) + '%' : 'N/A'}</strong>
                </div>
                <div class="vehicle-meta" style="margin-top: 5px;">
                    <span>OCR CONFIDENCE</span>
                    <strong>${v.ocr_confidence ? (v.ocr_confidence*100).toFixed(0) + '%' : 'UNAVAILABLE'}</strong>
                </div>
            </div>
            <div class="vehicle-details" style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 10px; padding-top: 10px;">
                <div class="vehicle-meta">
                    <div>Current: <strong>Camera ${v.current_camera}</strong></div>
                    <div>Duration: <strong>${v.duration.toFixed(1)}s</strong></div>
                </div>
            </div>
        `;
        listEl.appendChild(card);
    });
}

connectWebSocket();
