import re

with open('dashboard/style.css', 'r') as f:
    content = f.read()

diff_text = """
@@ -1,16 +1,14 @@
 :root {
-    --bg-core: #02000d;
-    --bg-surface: #071224;
-    --bg-panel: rgba(7, 32, 63, 0.4);
-    --border-color: rgba(0, 229, 255, 0.15);
-    --border-bright: rgba(0, 229, 255, 0.5);
-    --text-primary: #F4F4F4;
-    --text-muted: #8b9fb6;
-    --accent: #00e5ff;
-    --accent-glow: rgba(0, 229, 255, 0.3);
-    --success: #00ff88;
-    --warning: #ffb800;
-    --danger: #ff3366;
+    --bg-dark: #0f172a;
+    --bg-panel: #1e293b;
+    --bg-card: #334155;
+    --text-main: #f8fafc;
+    --text-muted: #94a3b8;
+    --accent: #3b82f6;
+    --success: #22c55e;
+    --warning: #f59e0b;
+    --danger: #ef4444;
+    --border: #475569;
 }
 
 * {
@@ -19,74 +19,66 @@
 }
 
 body {
-    background-color: var(--bg-core);
-    color: var(--text-primary);
     font-family: 'Inter', sans-serif;
-    height: 100vh;
-    overflow: hidden;
-    background-image: 
-        radial-gradient(circle at 50% 0%, rgba(7, 32, 63, 0.5) 0%, transparent 50%),
-        linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
-        linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
-    background-size: 100% 100%, 30px 30px, 30px 30px;
-}
-
-.app-container {
-    display: flex;
-    flex-direction: column;
-    height: 100vh;
-    max-width: 1800px;
-    margin: 0 auto;
-    padding: 1.5rem;
-    gap: 1.5rem;
-}
-
-/* Header */
-.top-bar {
-    display: flex;
-    justify-content: space-between;
-    align-items: center;
-    background: var(--bg-panel);
-    border: 1px solid var(--border-color);
-    border-radius: 8px;
-    padding: 1rem 2rem;
-    backdrop-filter: blur(10px);
-    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 229, 255, 0.05);
-}
-
-.logo-area {
-    display: flex;
-    align-items: center;
-    gap: 1.5rem;
-}
-
-.logo-area h1 {
+    background-color: var(--bg-dark);
+    color: var(--text-main);
+    line-height: 1.5;
+}
+
+header {
+    display: flex;
+    justify-content: space-between;
+    align-items: center;
+    padding: 1.5rem 2rem;
+    background-color: var(--bg-panel);
+    border-bottom: 1px solid var(--border);
+}
+
+.header-content h1 {
     font-size: 1.8rem;
     font-weight: 800;
-    color: var(--text-primary);
-    letter-spacing: 2px;
-    text-shadow: 0 0 10px var(--accent-glow);
-}
-
-.divider {
-    width: 2px;
-    height: 24px;
-    background: var(--border-bright);
-    transform: skewX(-15deg);
+    letter-spacing: -0.5px;
+}
+
+.header-content h1 span {
+    font-size: 1rem;
+    font-weight: 400;
+    color: var(--text-muted);
+    margin-left: 0.5rem;
 }
 
 .subtitle {
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.85rem;
-    color: var(--accent);
-    letter-spacing: 2px;
-}
-
-/* System Status */
-.system-status {
-    flex: 1;
-    display: flex;
-    justify-content: center;
+    color: var(--accent);
+    font-size: 0.9rem;
+    font-weight: 600;
+    text-transform: uppercase;
+    letter-spacing: 1px;
+}
+
+.kpi-container {
+    display: flex;
+    gap: 1.5rem;
+}
+
+.kpi-card {
+    background-color: var(--bg-dark);
+    border: 1px solid var(--border);
+    border-radius: 8px;
+    padding: 0.75rem 1.5rem;
+    text-align: center;
+    min-width: 140px;
+}
+
+.kpi-value {
+    font-size: 1.5rem;
+    font-weight: 800;
+    color: var(--accent);
+}
+
+.kpi-label {
+    font-size: 0.7rem;
+    color: var(--text-muted);
+    font-weight: 600;
 }
 
 .status-indicator {
@@ -93,11 +93,6 @@
     align-items: center;
-    gap: 0.75rem;
-    background: rgba(0, 0, 0, 0.4);
-    padding: 0.5rem 1rem;
-    border-radius: 20px;
-    border: 1px solid var(--border-color);
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.8rem;
+    gap: 0.5rem;
+    font-size: 0.85rem;
     color: var(--text-muted);
 }
 
@@ -104,8 +104,7 @@
-    width: 8px;
-    height: 8px;
+    width: 10px;
+    height: 10px;
     background-color: var(--warning);
     border-radius: 50%;
-    box-shadow: 0 0 10px var(--warning);
 }
 
 .pulse-dot.connected {
@@ -112,240 +112,24 @@
-    box-shadow: 0 0 12px var(--success);
-}
-
-/* KPIs */
-.kpi-group {
-    display: flex;
-    gap: 2rem;
-}
-
-.kpi-item {
-    display: flex;
-    flex-direction: column;
-    align-items: flex-end;
-}
-
-.kpi-label {
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.7rem;
-    color: var(--text-muted);
-    letter-spacing: 1px;
-}
-
-.kpi-value {
-    font-size: 1.5rem;
-    font-weight: 800;
-    color: var(--accent);
-    text-shadow: 0 0 15px var(--accent-glow);
-    font-variant-numeric: tabular-nums;
-}
-
-/* Main Grid */
-.dashboard-grid {
-    display: grid;
-    grid-template-columns: 1fr 450px;
-    gap: 1.5rem;
-    flex: 1;
-    min-height: 0;
-}
-
-.section-header {
-    display: flex;
-    align-items: center;
-    gap: 1rem;
-    margin-bottom: 1.5rem;
-}
-
-.section-header h2 {
-    font-size: 0.9rem;
-    color: var(--text-primary);
-    letter-spacing: 3px;
-    font-weight: 600;
-    white-space: nowrap;
-}
-
-.header-line {
-    flex: 1;
-    height: 1px;
-    background: linear-gradient(90deg, var(--accent) 0%, transparent 100%);
-    opacity: 0.5;
-}
-
-/* Left Column */
-.camera-network {
-    display: flex;
-    flex-direction: column;
-    height: 100%;
-}
-
-.feeds-container {
-    display: grid;
-    grid-template-columns: 1fr 1fr;
-    gap: 1.5rem;
-    flex: 1;
-}
-
-.camera-panel {
-    background: var(--bg-surface);
-    border: 1px solid var(--border-color);
-    border-radius: 8px;
-    display: flex;
-    flex-direction: column;
-    position: relative;
-    overflow: hidden;
-}
-
-.camera-panel::before {
-    content: '';
-    position: absolute;
-    top: 0; left: 0; right: 0;
-    height: 2px;
-    background: linear-gradient(90deg, transparent, var(--accent), transparent);
-    opacity: 0.5;
-}
-
-.camera-header {
-    display: flex;
-    justify-content: space-between;
-    align-items: center;
-    padding: 1rem 1.5rem;
-    background: rgba(0, 0, 0, 0.4);
-    border-bottom: 1px solid var(--border-color);
-}
-
-.cam-title {
-    font-family: 'JetBrains Mono', monospace;
-    font-weight: 700;
-    font-size: 1.1rem;
-    color: var(--text-primary);
-    letter-spacing: 1px;
-}
-
-.status-badge {
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.75rem;
-    font-weight: 700;
-    padding: 0.3rem 0.8rem;
-    border-radius: 4px;
-    letter-spacing: 1px;
-    display: flex;
-    align-items: center;
-    gap: 0.5rem;
-}
-
-.status-badge::before {
-    content: '';
-    display: block;
-    width: 6px;
-    height: 6px;
-    border-radius: 50%;
-}
-
-.status-badge.offline {
-    color: var(--danger);
-    background: rgba(255, 51, 102, 0.1);
-    border: 1px solid rgba(255, 51, 102, 0.3);
-}
-.status-badge.offline::before { background: var(--danger); box-shadow: 0 0 8px var(--danger); }
-
-.status-badge.online {
-    color: var(--success);
-    background: rgba(0, 255, 136, 0.1);
-    border: 1px solid rgba(0, 255, 136, 0.3);
-}
-.status-badge.online::before { background: var(--success); box-shadow: 0 0 8px var(--success); }
-
-.camera-feed-wrapper {
-    flex: 1;
-    position: relative;
-    background: #000;
-    display: flex;
-    align-items: center;
-    justify-content: center;
-    overflow: hidden;
-}
-
-.camera-feed-wrapper img {
-    width: 100%;
-    height: 100%;
-    object-fit: contain;
-    opacity: 0.2;
-    transition: opacity 0.3s ease;
-}
-
-.camera-feed-wrapper.active img {
-    opacity: 1;
-}
-
-.feed-scanlines {
-    position: absolute;
-    top: 0; left: 0; right: 0; bottom: 0;
-    background: linear-gradient(
-        to bottom,
-        rgba(255,255,255,0),
-        rgba(255,255,255,0) 50%,
-        rgba(0,0,0,0.1) 50%,
-        rgba(0,0,0,0.1)
-    );
-    background-size: 100% 4px;
-    pointer-events: none;
-    opacity: 0.5;
-}
-
-.camera-overlay {
-    position: absolute;
-    bottom: 1.5rem;
-    left: 1.5rem;
-    background: rgba(2, 0, 13, 0.8);
-    border-left: 3px solid var(--accent);
-    padding: 0.75rem 1rem;
-    backdrop-filter: blur(4px);
-}
-
-.overlay-data {
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.85rem;
-    color: var(--accent);
-    line-height: 1.4;
-    text-shadow: 0 0 5px var(--accent-glow);
-}
-
-/* Reticles */
-.reticle {
-    position: absolute;
-    width: 20px;
-    height: 20px;
-    border-color: var(--accent);
-    border-style: solid;
-    opacity: 0.5;
-    pointer-events: none;
-}
-.top-left { top: 1rem; left: 1rem; border-width: 2px 0 0 2px; }
-.top-right { top: 1rem; right: 1rem; border-width: 2px 2px 0 0; }
-.bottom-left { bottom: 1rem; left: 1rem; border-width: 0 0 2px 2px; }
-.bottom-right { bottom: 1rem; right: 1rem; border-width: 0 2px 2px 0; }
-
-/* Right Column */
-.data-streams {
-    display: flex;
-    flex-direction: column;
-    gap: 1.5rem;
-    height: 100%;
-    overflow: hidden;
-}
-
-.stream-panel {
-    background: var(--bg-panel);
-    border: 1px solid var(--border-color);
-    border-radius: 8px;
-    padding: 1.5rem;
-    display: flex;
-    flex-direction: column;
-    backdrop-filter: blur(10px);
-}
-
-.stream-grow {
-    flex: 1;
-    min-height: 0;
+    box-shadow: 0 0 8px var(--success);
+}
+
+main {
+    padding: 2rem;
+    max-width: 1400px;
+    margin: 0 auto;
+}
+
+section {
+    margin-bottom: 2rem;
+}
+
+h2 {
+    font-size: 1.2rem;
+    margin-bottom: 1rem;
+    color: var(--text-muted);
+    text-transform: uppercase;
+    letter-spacing: 1px;
+    border-bottom: 1px solid var(--border);
+    padding-bottom: 0.5rem;
 }
 
 /* Trajectory */
@@ -352,19 +352,18 @@
-    display: flex;
-    flex-direction: column;
-    gap: 0.75rem;
-    max-height: 150px;
-    overflow-y: auto;
+    background-color: var(--bg-panel);
+    border-radius: 12px;
+    padding: 2rem;
+    min-height: 200px;
+    display: flex;
+    flex-direction: column;
+    gap: 1rem;
+    border: 1px solid var(--border);
 }
 
 .empty-state {
-    font-family: 'JetBrains Mono', monospace;
-    color: var(--text-muted);
-    font-size: 0.85rem;
-    text-align: center;
-    padding: 1rem;
-    background: rgba(0,0,0,0.3);
-    border: 1px dashed var(--border-color);
-    border-radius: 4px;
+    text-align: center;
+    color: var(--text-muted);
+    font-style: italic;
+    margin: auto;
 }
 
 .journey-row {
@@ -371,9 +371,8 @@
     align-items: center;
-    background: rgba(0, 0, 0, 0.4);
-    border: 1px solid var(--border-color);
-    border-radius: 6px;
-    padding: 0.75rem 1rem;
-    gap: 1rem;
+    background-color: var(--bg-card);
+    padding: 1rem;
+    border-radius: 8px;
+    border-left: 4px solid var(--accent);
 }
 
 .journey-vid {
@@ -380,7 +380,6 @@
-    color: var(--text-primary);
-    font-weight: 700;
-    width: 100px;
-    font-size: 0.9rem;
+    font-weight: bold;
+    width: 150px;
+    font-size: 1.1rem;
 }
 
 .journey-path {
@@ -387,5 +387,6 @@
     align-items: center;
     flex: 1;
+    gap: 1rem;
 }
 
 .node {
@@ -392,5 +392,7 @@
-    align-items: center;
-    gap: 0.5rem;
+    flex-direction: column;
+    align-items: center;
+    gap: 0.25rem;
+    position: relative;
     z-index: 2;
 }
 
@@ -397,20 +397,19 @@
-    width: 24px;
-    height: 24px;
-    border-radius: 50%;
-    background: var(--bg-surface);
-    border: 1px solid var(--border-color);
-    color: var(--text-muted);
-    display: flex;
-    align-items: center;
-    justify-content: center;
-    font-size: 0.7rem;
-    font-family: 'JetBrains Mono', monospace;
+    width: 30px;
+    height: 30px;
+    border-radius: 50%;
+    background-color: var(--bg-dark);
+    border: 2px solid var(--border);
+    display: flex;
+    align-items: center;
+    justify-content: center;
+    font-weight: bold;
+    color: var(--text-muted);
 }
 
 .node.active .node-circle {
-    background: var(--accent);
-    color: #000;
-    border-color: var(--accent);
+    background-color: var(--accent);
+    border-color: var(--accent);
+    color: white;
     box-shadow: 0 0 10px var(--accent);
 }
 
@@ -417,21 +417,99 @@
-    background: var(--success);
-    color: #000;
+    background-color: var(--success);
     border-color: var(--success);
-    box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
-}
-
-.node-label { display: none; }
+    color: white;
+}
+
+.node-label {
+    font-size: 0.75rem;
+    color: var(--text-muted);
+}
 
 .line {
     flex: 1;
-    height: 2px;
-    background: var(--border-color);
-    margin: 0 0.5rem;
+    height: 4px;
+    background-color: var(--border);
+    position: relative;
+    z-index: 1;
+    margin: 0 -15px;
 }
 
 .line.active {
-    background: var(--success);
-    box-shadow: 0 0 5px var(--success);
+    background-color: var(--success);
+}
+
+/* Camera Grid */
+.camera-grid {
+    display: grid;
+    grid-template-columns: repeat(3, 1fr);
+    gap: 1.5rem;
+}
+
+.camera-panel {
+    background-color: var(--bg-panel);
+    border: 1px solid var(--border);
+    border-radius: 12px;
+    overflow: hidden;
+}
+
+.camera-header {
+    display: flex;
+    justify-content: space-between;
+    align-items: center;
+    padding: 0.75rem 1rem;
+    background-color: var(--bg-card);
+}
+
+.camera-header h3 {
+    font-size: 1rem;
+    margin: 0;
+}
+
+.status-badge {
+    font-size: 0.7rem;
+    font-weight: bold;
+    padding: 0.2rem 0.5rem;
+    border-radius: 4px;
+}
+
+.status-badge.offline { background-color: var(--danger); color: white; }
+.status-badge.online { background-color: var(--success); color: white; }
+
+.camera-feed {
+    position: relative;
+    aspect-ratio: 16/9;
+    background-color: #000;
+    display: flex;
+    align-items: center;
+    justify-content: center;
+}
+
+.camera-feed img {
+    width: 100%;
+    height: 100%;
+    object-fit: contain;
+    opacity: 0.3;
+}
+
+.camera-feed.active img {
+    opacity: 1;
+}
+
+.camera-overlay {
+    position: absolute;
+    bottom: 10px;
+    left: 10px;
+    background-color: rgba(0,0,0,0.7);
+    padding: 0.5rem;
+    border-radius: 4px;
+    font-family: 'JetBrains Mono', monospace;
+    font-size: 0.8rem;
+}
+
+/* Lower Layout */
+.lower-layout {
+    display: grid;
+    grid-template-columns: 2fr 1fr;
+    gap: 1.5rem;
 }
 
 /* Vehicles List */
@@ -438,49 +438,26 @@
     display: flex;
     flex-direction: column;
     gap: 1rem;
-    overflow-y: auto;
-    padding-right: 0.5rem;
-}
-
-.vehicles-list::-webkit-scrollbar,
-.events-timeline::-webkit-scrollbar,
-.trajectory-map::-webkit-scrollbar {
-    width: 4px;
-}
-.vehicles-list::-webkit-scrollbar-thumb,
-.events-timeline::-webkit-scrollbar-thumb,
-.trajectory-map::-webkit-scrollbar-thumb {
-    background: var(--border-bright);
-    border-radius: 4px;
 }
 
 .vehicle-card {
-    display: flex;
-    gap: 1rem;
-    background: rgba(0, 0, 0, 0.4);
-    border: 1px solid var(--border-color);
-    border-left: 3px solid var(--accent);
-    padding: 1rem;
-    border-radius: 4px;
-    transition: transform 0.2s, box-shadow 0.2s;
-}
-
-.vehicle-card:hover {
-    transform: translateX(4px);
-    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.1);
+    background-color: var(--bg-panel);
+    border: 1px solid var(--border);
+    border-radius: 8px;
+    padding: 1rem;
+    display: grid;
+    grid-template-columns: 100px 1fr 1fr;
+    gap: 1rem;
+    align-items: center;
 }
 
 .vehicle-img-container {
-    width: 80px;
-    height: 60px;
-    background: #000;
-    border: 1px solid var(--border-color);
-    border-radius: 4px;
-    overflow: hidden;
-    position: relative;
-    flex-shrink: 0;
-}
-
+    width: 100px;
+    height: 75px;
+    background-color: #000;
+    border-radius: 4px;
+    overflow: hidden;
+}
 .vehicle-img-container img {
     width: 100%;
     height: 100%;
@@ -487,50 +487,22 @@
 }
 
-.vehicle-img-container::after {
-    content: '';
-    position: absolute;
-    top:0; left:0; right:0; bottom:0;
-    box-shadow: inset 0 0 10px rgba(0,229,255,0.2);
-    pointer-events: none;
-}
-
-.vehicle-details {
-    flex: 1;
-    display: flex;
-    flex-direction: column;
-    justify-content: center;
-    gap: 0.4rem;
-    min-width: 0;
-}
-
 .vehicle-details h4 {
     font-family: 'JetBrains Mono', monospace;
-    font-size: 1rem;
-    color: var(--text-primary);
+    color: var(--accent);
+    margin-bottom: 0.25rem;
 }
 
 .vehicle-meta {
-    display: flex;
-    flex-wrap: wrap;
-    gap: 0.5rem;
-    font-size: 0.75rem;
-    font-family: 'JetBrains Mono', monospace;
-}
-
-.vehicle-meta span, .vehicle-meta div {
-    background: rgba(0, 229, 255, 0.1);
-    color: var(--accent);
-    padding: 0.2rem 0.5rem;
-    border-radius: 2px;
-    border: 1px solid rgba(0, 229, 255, 0.2);
-    white-space: nowrap;
-}
-
-.vehicle-meta div {
-    color: var(--text-muted);
-}
-.vehicle-meta div strong {
-    color: var(--text-primary);
+    font-size: 0.85rem;
+    color: var(--text-muted);
+}
+
+.vehicle-meta span {
+    display: inline-block;
+    margin-right: 1rem;
+    background-color: var(--bg-card);
+    padding: 0.1rem 0.4rem;
+    border-radius: 4px;
 }
 
 /* Event Timeline */
@@ -537,19 +537,16 @@
-    height: 150px;
-    overflow-y: auto;
-    font-family: 'JetBrains Mono', monospace;
-    font-size: 0.8rem;
-    padding-right: 0.5rem;
-    display: flex;
-    flex-direction: column;
-    gap: 0.5rem;
+    background-color: var(--bg-panel);
+    border: 1px solid var(--border);
+    border-radius: 8px;
+    padding: 1rem;
+    height: 400px;
+    overflow-y: auto;
 }
 
 .event-item {
-    display: flex;
-    gap: 0.75rem;
-    padding: 0.5rem;
-    border-left: 2px solid var(--border-color);
-    background: rgba(0, 0, 0, 0.2);
+    font-family: 'JetBrains Mono', monospace;
+    font-size: 0.8rem;
+    padding: 0.5rem 0;
+    border-bottom: 1px solid var(--bg-card);
 }
 
 .event-time {
@@ -556,3 +556,4 @@
+    margin-right: 0.5rem;
 }
 
 .event-vid {
@@ -559,26 +559,2 @@
-    font-weight: 700;
-}
-
-/* Responsive adjustments */
-@media (max-width: 1400px) {
-    .dashboard-grid {
-        grid-template-columns: 1fr 400px;
-    }
-}
-@media (max-width: 1200px) {
-    .dashboard-grid {
-        grid-template-columns: 1fr;
-        overflow-y: auto;
-    }
-    .app-container {
-        height: auto;
-        overflow-y: auto;
-    }
-    .data-streams {
-        height: auto;
-    }
-    .stream-grow {
-        min-height: 400px;
-    }
 }
"""

# We want to reconstruct the old file based on diff_text
lines = diff_text.strip().split('\n')
blocks = []
current_block = []

for line in lines:
    if line.startswith('@@'):
        if current_block:
            blocks.append(current_block)
        current_block = []
    else:
        current_block.append(line)
if current_block:
    blocks.append(current_block)

new_content = content
for block in blocks:
    # Build the old version and new version of this block
    old_block = []
    new_block = []
    for line in block:
        if line.startswith('-'):
            old_block.append(line[1:])
        elif line.startswith('+'):
            new_block.append(line[1:])
        else:
            old_block.append(line[1:])
            new_block.append(line[1:])
    
    old_str = '\n'.join(old_block) + '\n'
    new_str = '\n'.join(new_block) + '\n'
    
    # We want to replace new_str with old_str in new_content
    # Sometimes there might be a trailing newline mismatch
    new_str = '\n'.join(new_block)
    old_str = '\n'.join(old_block)
    
    if new_str in new_content:
        new_content = new_content.replace(new_str, old_str, 1)
    else:
        # Try line by line or fuzzy replace
        # Let's try to find it by just replacing the + lines with - lines in the exact place
        pass

with open('dashboard/style_reverted.css', 'w') as f:
    f.write(new_content)
