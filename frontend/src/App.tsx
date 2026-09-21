import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Demo } from './pages/Demo';

export const App: React.FC = () => {
    return (
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/demo" element={<Demo />} />
        </Routes>
    );
};

export default App;
