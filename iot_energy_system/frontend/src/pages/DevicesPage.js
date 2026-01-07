import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/apiService';
import './Common.css';

function DevicesPage() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await apiService.getDevices();
      setDevices(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching devices:', error);
      toast.error('Failed to load devices');
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-container"><div className="loading-spinner"></div></div>;
  }

  return (
    <div className="page-container">
      <h1>Devices Management</h1>
      <div className="devices-grid">
        {devices.map((device) => (
          <div key={device.id} className="device-card">
            <h3>{device.name}</h3>
            <p><strong>Device ID:</strong> {device.device_id}</p>
            <p><strong>Location:</strong> {device.location}</p>
            <p><strong>Type:</strong> {device.device_type}</p>
            <span className={`status-badge status-${device.status}`}>
              {device.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DevicesPage;
