const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
    getHealth: async () => {
        try {
            const res = await fetch(`${API_URL}/health`);
            return await res.json();
        } catch (error) {
            console.error('Failed to get health status', error);
            throw error;
        }
    }
};
