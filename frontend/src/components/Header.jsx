// frontend/src/components/Header.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Header() {
    const navigate = useNavigate();
    const isSuperuser = localStorage.getItem('is_superuser') === 'true';
    const isLoggedIn = localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('is_superuser');
        navigate('/login');
    };

    return (
        <header className="header">
            <nav className="header-nav">
                <Link to="/" className="header-link">Dashboard</Link>
                <Link to="/clients" className="header-link">Clients</Link>
                {isSuperuser && (
                    <Link to="/admin-dashboard" className="header-link">Admin</Link>
                )}
            </nav>
            {isLoggedIn ? (
                <button onClick={handleLogout} className="btn-logout">Logout</button>
            ) : (
                <Link to="/login" className="header-link">Login</Link>
            )}
        </header>
    );
}
export default Header;