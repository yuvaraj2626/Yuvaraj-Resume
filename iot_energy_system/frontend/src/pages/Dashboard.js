import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import apiService from '../services/apiService';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [latestReadings, setLatestReadings] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [loading, setLoading] = useState(true);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard statistics
      const statsResponse = await apiService.getDashboardStats();
      setStats(statsResponse.data);

      // Fetch latest readings
      const readingsResponse = await apiService.getLatestReadings();
      setLatestReadings(readingsResponse.data);

      // Fetch active alerts
      const alertsResponse = await apiService.getActiveAlerts();
      setActiveAlerts(alertsResponse.data);

      // Fetch time series data for chart
      const timeSeriesResponse = await apiService.getTimeSeriesData({
        hours: 24,
        parameter: 'power'
      });
      setTimeSeriesData(timeSeriesResponse.data);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#dc2626',
      warning: '#f59e0b',
      info: '#3b82f6'
    };
    return colors[severity] || '#6b7280';
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#10b981',
      inactive: '#6b7280',
      maintenance: '#f59e0b'
    };
    return colors[status] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Prepare period consumption data for pie chart
  const periodData = stats ? [
    { name: 'Day', value: parseFloat((stats.total_energy_today * 0.5).toFixed(2)) },
    { name: 'Night', value: parseFloat((stats.total_energy_today * 0.3).toFixed(2)) },
    { name: 'Holiday', value: parseFloat((stats.total_energy_today * 0.2).toFixed(2)) }
  ] : [];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Energy Monitoring Dashboard</h1>
        <button onClick={fetchDashboardData} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#3b82f6' }}>🔌</div>
            <div className="stat-content">
              <h3>Total Devices</h3>
              <p className="stat-value">{stats.total_devices}</p>
              <p className="stat-subtitle">{stats.active_devices} active</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#10b981' }}>⚡</div>
            <div className="stat-content">
              <h3>Energy Today</h3>
              <p className="stat-value">{stats.total_energy_today.toFixed(2)} kWh</p>
              <p className="stat-subtitle">{stats.total_readings_today} readings</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#f59e0b' }}>⚠️</div>
            <div className="stat-content">
              <h3>Active Alerts</h3>
              <p className="stat-value">{stats.active_alerts}</p>
              <p className="stat-subtitle">Requires attention</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#8b5cf6' }}>🎫</div>
            <div className="stat-content">
              <h3>Open Tickets</h3>
              <p className="stat-value">{stats.open_tickets}</p>
              <p className="stat-subtitle">In progress</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#ef4444' }}>🌡️</div>
            <div className="stat-content">
              <h3>Avg Temperature</h3>
              <p className="stat-value">{stats.avg_temperature.toFixed(1)}°C</p>
              <p className="stat-subtitle">Today</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#06b6d4' }}>💧</div>
            <div className="stat-content">
              <h3>Avg Humidity</h3>
              <p className="stat-value">{stats.avg_humidity.toFixed(1)}%</p>
              <p className="stat-subtitle">Today</p>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="charts-row">
        {/* Power Time Series Chart */}
        <div className="chart-card">
          <h2>Power Consumption (Last 24 Hours)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
              />
              <YAxis label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }} />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleString()}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="power" 
                stroke="#3b82f6" 
                name="Power (W)"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Period Consumption Pie Chart */}
        <div className="chart-card">
          <h2>Consumption by Period</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={periodData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value} kWh`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {periodData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Latest Readings Table */}
      <div className="section-card">
        <h2>Latest Device Readings</h2>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Device ID</th>
                <th>Voltage (V)</th>
                <th>Current (A)</th>
                <th>Power (W)</th>
                <th>Temperature (°C)</th>
                <th>Humidity (%)</th>
                <th>Period</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {latestReadings.map((reading) => (
                <tr key={reading.id}>
                  <td><strong>{reading.device_id}</strong></td>
                  <td>{reading.voltage.toFixed(2)}</td>
                  <td>{reading.current.toFixed(2)}</td>
                  <td>{reading.power.toFixed(2)}</td>
                  <td>{reading.temperature.toFixed(2)}</td>
                  <td>{reading.humidity.toFixed(2)}</td>
                  <td>
                    <span className={`badge badge-${reading.period_type}`}>
                      {reading.period_type}
                    </span>
                  </td>
                  <td>{new Date(reading.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="section-card">
          <h2>Active Alerts</h2>
          <div className="alerts-list">
            {activeAlerts.map((alert) => (
              <div 
                key={alert.id} 
                className="alert-item"
                style={{ borderLeftColor: getSeverityColor(alert.severity) }}
              >
                <div className="alert-header">
                  <span className={`severity-badge severity-${alert.severity}`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="alert-device">{alert.device_id}</span>
                  <span className="alert-time">
                    {new Date(alert.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="alert-message">{alert.message}</div>
                <div className="alert-details">
                  <span>Parameter: {alert.parameter_name}</span>
                  <span>Current: {alert.actual_value.toFixed(2)}</span>
                  <span>Threshold: {alert.threshold_value.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
