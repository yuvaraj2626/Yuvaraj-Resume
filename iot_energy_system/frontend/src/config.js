/**
 * Configuration for the IoT Energy Monitoring Dashboard
 */

const config = {
  apiBaseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  wsBaseUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  refreshInterval: 30000, // 30 seconds
  chartDataPoints: 50,
};

export default config;
