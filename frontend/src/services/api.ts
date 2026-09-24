const API_URL = import.meta.env.PROD 
    ? (import.meta.env.VITE_API_URL || '') 
    : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

export const api = {
    getHealth: async () => {
        try {
            const res = await fetch(`${API_URL}/health`);
            return await res.json();
        } catch (error) {
            console.error('Failed to get health status', error);
            throw error;
        }
    },
    sendFrame: async (cameraId: number, frameBase64: string) => {
        try {
            const res = await fetch(`${API_URL}/api/camera/frame`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    camera_id: cameraId,
                    frame_base64: frameBase64
                })
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (error) {
            console.error('Failed to send camera frame', error);
            return null;
        }
    }
};

