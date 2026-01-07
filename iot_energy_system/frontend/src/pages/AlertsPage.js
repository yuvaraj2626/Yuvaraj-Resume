import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/apiService';
import './Common.css';

function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await apiService.getAlerts();
      setAlerts(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      toast.error('Failed to load alerts');
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await apiService.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      fetchAlerts();
    } catch (error) {
      toast.error('Failed to acknowledge alert');
    }
  };

  if (loading) {
    return <div className="loading-container"><div className="loading-spinner"></div></div>;
  }

  return (
    <div className="page-container">
      <h1>Alerts Management</h1>
      <div className="alerts-list">
        {alerts.map((alert) => (
          <div key={alert.id} className="alert-card">
            <div className="alert-header-row">
              <span className={`severity-badge severity-${alert.severity}`}>
                {alert.severity}
              </span>
              <span>{alert.device_name}</span>
              <span className="alert-time">
                {new Date(alert.created_at).toLocaleString()}
              </span>
            </div>
            <p>{alert.message}</p>
            <div className="alert-actions">
              {alert.status === 'active' && (
                <button 
                  onClick={() => handleAcknowledge(alert.id)}
                  className="btn-primary"
                >
                  Acknowledge
                </button>
              )}
              <span className={`status-badge status-${alert.status}`}>
                {alert.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AlertsPage;
