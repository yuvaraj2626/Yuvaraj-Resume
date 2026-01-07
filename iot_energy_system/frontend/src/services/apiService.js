/**
 * API Service for backend communication
 */

import axios from 'axios';
import config from '../config';

const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const apiService = {
  // Authentication
  login: (credentials) => apiClient.post('/auth/login/', credentials),
  refreshToken: (refresh) => apiClient.post('/auth/refresh/', { refresh }),

  // Devices
  getDevices: () => apiClient.get('/devices/'),
  getDevice: (id) => apiClient.get(`/devices/${id}/`),
  createDevice: (data) => apiClient.post('/devices/', data),
  updateDevice: (id, data) => apiClient.put(`/devices/${id}/`, data),
  deleteDevice: (id) => apiClient.delete(`/devices/${id}/`),
  getDeviceStats: (id, hours = 24) => 
    apiClient.get(`/devices/${id}/statistics/`, { params: { hours } }),

  // Sensor Readings
  getReadings: (params = {}) => apiClient.get('/readings/', { params }),
  getLatestReadings: () => apiClient.get('/readings/latest/'),
  getTimeSeriesData: (params) => apiClient.get('/readings/time_series/', { params }),
  createReading: (data) => apiClient.post('/readings/', data),

  // Thresholds
  getThresholds: (params = {}) => apiClient.get('/thresholds/', { params }),
  createThreshold: (data) => apiClient.post('/thresholds/', data),
  updateThreshold: (id, data) => apiClient.put(`/thresholds/${id}/`, data),
  deleteThreshold: (id) => apiClient.delete(`/thresholds/${id}/`),
  toggleThreshold: (id) => apiClient.post(`/thresholds/${id}/toggle/`),

  // Alerts
  getAlerts: (params = {}) => apiClient.get('/alerts/', { params }),
  getActiveAlerts: () => apiClient.get('/alerts/active/'),
  acknowledgeAlert: (id) => apiClient.post(`/alerts/${id}/acknowledge/`),
  resolveAlert: (id) => apiClient.post(`/alerts/${id}/resolve/`),

  // Tickets
  getTickets: (params = {}) => apiClient.get('/tickets/', { params }),
  createTicket: (data) => apiClient.post('/tickets/', data),
  updateTicket: (id, data) => apiClient.put(`/tickets/${id}/`, data),
  updateTicketStatus: (id, status) => 
    apiClient.post(`/tickets/${id}/update_status/`, { status }),
  assignTicket: (id, userId) => 
    apiClient.post(`/tickets/${id}/assign/`, { user_id: userId }),

  // Dashboard
  getDashboardStats: () => apiClient.get('/dashboard/stats/'),

  // Reports
  getHourlyReport: (deviceId) => 
    apiClient.get('/reports/hourly/', { params: { device_id: deviceId } }),
  getDailyReport: (deviceId, date) => 
    apiClient.get('/reports/daily/', { params: { device_id: deviceId, date } }),
  getWeeklyReport: (deviceId) => 
    apiClient.get('/reports/weekly/', { params: { device_id: deviceId } }),
  getMonthlyReport: (deviceId) => 
    apiClient.get('/reports/monthly/', { params: { device_id: deviceId } }),
  exportPDF: (type, deviceId) => 
    apiClient.get('/reports/export_pdf/', { 
      params: { type, device_id: deviceId },
      responseType: 'blob'
    }),
  exportCSV: (type, deviceId) => 
    apiClient.get('/reports/export_csv/', { 
      params: { type, device_id: deviceId },
      responseType: 'blob'
    }),

  // Users
  getUsers: () => apiClient.get('/users/'),
};

export default apiService;
