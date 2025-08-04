// src/components/Clients.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Clients() {
    const [clients, setClients] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchClients = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://127.0.0.1:8000/api/clients/', {
                    headers: { Authorization: `Token ${token}` },
                });
                setClients(response.data);
                setIsLoading(false);
            } catch (error) {
                console.error('Failed to fetch clients:', error);
                setIsLoading(false);
                if (error.response && error.response.status === 401) {
                    navigate('/login');
                }
            }
        };
        fetchClients();
    }, [navigate]);

    const filteredClients = clients.filter(client =>
        (client.name && client.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (client.company && client.company.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (client.email && client.email.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div>
            <h2 style={{ marginBottom: '1rem' }}>Approved Clients</h2>

            <div style={{ marginBottom: '1rem' }}>
                <input
                    type="text"
                    placeholder="Search clients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{ padding: '0.5rem', width: '300px' }}
                />
            </div>

            {isLoading ? (
                <p>Loading clients...</p>
            ) : (
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {filteredClients.length > 0 ? (
                        filteredClients.map(client => (
                            <li key={client.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eee' }}>
                                <strong>{client.name}</strong> - {client.company} ({client.email})
                            </li>
                        ))
                    ) : (
                        <p>No clients found.</p>
                    )}
                </ul>
            )}
        </div>
    );
}

export default Clients;