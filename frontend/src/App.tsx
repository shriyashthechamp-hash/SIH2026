import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { Dashboard } from './pages/Dashboard';

export const App: React.FC = () => {
    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/demo" element={<Dashboard />} />
        </Routes>
    );
};

export default App;
