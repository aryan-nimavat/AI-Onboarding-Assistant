// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
    const [file, setFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [calls, setCalls] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedCallDetails, setSelectedCallDetails] = useState(null);
    const [extractedData, setExtractedData] = useState({});
    
    const navigate = useNavigate();

    // Polling function to fetch all call recordings from the backend
    const fetchCalls = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://127.0.0.1:8000/api/call-recordings/', {
                headers: { Authorization: `Token ${token}` },
            });
            setCalls(response.data);
            setIsLoading(false);
        } catch (error) {
            console.error('Failed to fetch call recordings:', error);
            setIsLoading(false);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
        }
    };

    useEffect(() => {
        fetchCalls();
        const interval = setInterval(() => {
            fetchCalls();
        }, 5000); 

        return () => clearInterval(interval);
    }, []);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setUploadStatus('');
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploadStatus('Uploading...');
        const formData = new FormData();
        formData.append('audio_file', file);
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://127.0.0.1:8000/api/call-recordings/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Token ${token}`,
                },
            });
            setUploadStatus('Upload successful! Processing...');
            setFile(null);
            fetchCalls();
        } catch (error) {
            setUploadStatus(`Upload failed: ${error.message}`);
            console.error('Upload error:', error);
        }
    };
    
    const handleSelectCall = async (callId) => {
        try {
            const token = localStorage.getItem('token');
            const [callResponse, extractedResponse] = await Promise.all([
                axios.get(`http://127.0.0.1:8000/api/call-recordings/${callId}/`, {
                    headers: { Authorization: `Token ${token}` },
                }),
                axios.get(`http://127.0.0.1:8000/api/extracted-info/${callId}/`, {
                    headers: { Authorization: `Token ${token}` },
                }),
            ]);
            
            setSelectedCallDetails(callResponse.data);
            setExtractedData(extractedResponse.data);
        } catch (error) {
            console.error('Failed to fetch call details:', error);
            setSelectedCallDetails(null);
            setExtractedData({});
        }
    };

    const handleExtractedDataChange = (e) => {
        const { name, value } = e.target;
        setExtractedData(prevData => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleReviewAction = async (action) => {
        if (!selectedCallDetails || !extractedData) return;

        try {
            const token = localStorage.getItem('token');
            const url = `http://127.0.0.1:8000/api/extracted-info/${extractedData.id}/${action}/`;
            const payload = {
                ...extractedData,
                review_notes: extractedData.review_notes || 'No notes provided.'
            };

            const response = await axios.post(url, payload, {
                headers: { Authorization: `Token ${token}` },
            });
            
            setCalls(prevCalls =>
                prevCalls.map(call =>
                    call.id === selectedCallDetails.id ? { ...call, status: response.data.status || action.toUpperCase() } : call
                )
            );
            
            setSelectedCallDetails(null);
            setExtractedData({});
            alert(`Action '${action}' successful!`);

        } catch (error) {
            console.error(`Action '${action}' failed:`, error);
            alert(`Error during '${action}': ${error.response?.data?.detail || error.message}`);
        }
    };
    
    const isReadyForReview = selectedCallDetails?.status === 'READY_FOR_REVIEW';
    const isProcessed = selectedCallDetails?.status === 'APPROVED' || selectedCallDetails?.status === 'REJECTED';

    return (
        <div className="container dashboard-layout">
            {/* Left Column: Call List and Upload */}
            <div className="dashboard-list-panel">
                <h1 style={{ marginBottom: '1rem' }}>Dashboard</h1>

                {/* File Upload Section */}
                <div style={{ marginBottom: '2rem' }}>
                    <h3>Upload New Call Recording</h3>
                    <input type="file" onChange={handleFileChange} accept="audio/*" />
                    <button onClick={handleUpload} disabled={!file} className="btn btn-upload">
                        Upload
                    </button>
                    {uploadStatus && <p>{uploadStatus}</p>}
                </div>

                <hr style={{ margin: '1rem 0' }} />

                {/* Call List Section */}
                <div>
                    <h3>Call Recordings</h3>
                    {isLoading ? (
                        <p>Loading calls...</p>
                    ) : (
                        <ul style={{ listStyleType: 'none', padding: 0 }}>
                            {calls.length > 0 ? (
                                calls.map(call => (
                                    <li 
                                        key={call.id} 
                                        onClick={() => handleSelectCall(call.id)} 
                                        className={`list-item ${selectedCallDetails?.id === call.id ? 'selected' : ''}`}
                                    >
                                        <p>Call ID: {call.id} - Status: {call.status}</p>
                                    </li>
                                ))
                            ) : (
                                <p>No calls found. Upload one to get started!</p>
                            )}
                        </ul>
                    )}
                </div>
            </div>

            {/* Right Column: Call Details */}
            <div className="dashboard-details-panel">
                {selectedCallDetails && extractedData ? (
                    <div>
                        <h2>Details for Call ID: {selectedCallDetails.id}</h2>
                        
                        <div style={{ marginBottom: '2rem' }}>
                            <h3>Transcript</h3>
                            <div style={{ border: '1px solid #ccc', padding: '1rem', whiteSpace: 'pre-wrap' }}>
                                {selectedCallDetails.transcript_text || 'Transcript is not yet available.'}
                            </div>
                        </div>

                        <h3>Extracted Information</h3>
                        <form>
                            <div>
                                <label>Client Name:</label>
                                <input
                                    type="text"
                                    name="client_name"
                                    value={extractedData.client_name || ''}
                                    onChange={handleExtractedDataChange}
                                    className="input-field"
                                />
                            </div>
                            <div>
                                <label>Company Name:</label>
                                <input
                                    type="text"
                                    name="company_name"
                                    value={extractedData.company_name || ''}
                                    onChange={handleExtractedDataChange}
                                    className="input-field"
                                />
                            </div>
                            <div>
                                <label>Contact Number:</label>
                                <input
                                    type="text"
                                    name="contact_number"
                                    value={extractedData.contact_number || ''}
                                    onChange={handleExtractedDataChange}
                                    className="input-field"
                                />
                            </div>
                            <div>
                                <label>Email:</label>
                                <input
                                    type="text"
                                    name="email"
                                    value={extractedData.email || ''}
                                    onChange={handleExtractedDataChange}
                                    className="input-field"
                                />
                            </div>
                            <div>
                                <label>Service Interest:</label>
                                <textarea
                                    name="service_interest"
                                    value={extractedData.service_interest || ''}
                                    onChange={handleExtractedDataChange}
                                    className="textarea-field"
                                />
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <label>Review Notes:</label>
                                <textarea
                                    name="review_notes"
                                    value={extractedData.review_notes || ''}
                                    onChange={handleExtractedDataChange}
                                    className="textarea-field"
                                />
                            </div>
                            
                            <div style={{ marginTop: '1rem' }}>
                                {!isProcessed && (
                                    <>
                                        <button 
                                            type="button" 
                                            onClick={() => handleReviewAction('approve')}
                                            disabled={!isReadyForReview}
                                            className="btn btn-primary"
                                        >
                                            Approve
                                        </button>
                                        <button 
                                            type="button" 
                                            onClick={() => handleReviewAction('reject')}
                                            disabled={!isReadyForReview}
                                            className="btn btn-secondary"
                                        >
                                            Reject
                                        </button>
                                    </>
                                )}
                                {isProcessed && (
                                    <p>This record has been {selectedCallDetails.status}.</p>
                                )}
                            </div>
                        </form>
                    </div>
                ) : (
                    <p>Select a call from the left to view details.</p>
                )}
            </div>
        </div>
    );
}

export default Dashboard;