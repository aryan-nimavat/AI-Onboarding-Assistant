// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Clients from './components/Clients'; // <-- Import new component

function App() {
    const isAuthenticated = () => {
        return !!localStorage.getItem('token');
    };

    const ProtectedRoute = ({ children }) => {
        if (!isAuthenticated()) {
            return <Navigate to="/login" replace />;
        }
        return children;
    };

    return (
        <Router>
            <div className="app-container">
                <Header />
                <main style={{ minHeight: '80vh', padding: '2rem' }}>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                        <Route path="/clients" element={<ProtectedRoute><Clients /></ProtectedRoute>} /> {/* <-- Add new route */}
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
}

export default App;