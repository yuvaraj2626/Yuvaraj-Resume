import React, { useState } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/apiService';
import './Common.css';

function ReportsPage() {
  const [reportType, setReportType] = useState('daily');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    try {
      let response;
      switch (reportType) {
        case 'hourly':
          response = await apiService.getHourlyReport();
          break;
        case 'daily':
          response = await apiService.getDailyReport();
          break;
        case 'weekly':
          response = await apiService.getWeeklyReport();
          break;
        case 'monthly':
          response = await apiService.getMonthlyReport();
          break;
        default:
          response = await apiService.getDailyReport();
      }
      setReportData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const response = await apiService.exportPDF(reportType);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report_${reportType}.pdf`;
      link.click();
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const downloadCSV = async () => {
    try {
      const response = await apiService.exportCSV(reportType);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report_${reportType}.csv`;
      link.click();
      toast.success('CSV downloaded successfully');
    } catch (error) {
      toast.error('Failed to download CSV');
    }
  };

  return (
    <div className="page-container">
      <h1>Reports & Analytics</h1>
      
      <div className="report-controls">
        <select 
          value={reportType} 
          onChange={(e) => setReportType(e.target.value)}
          className="select-input"
        >
          <option value="hourly">Hourly Report</option>
          <option value="daily">Daily Report</option>
          <option value="weekly">Weekly Report</option>
          <option value="monthly">Monthly Report</option>
        </select>
        
        <button onClick={generateReport} className="btn-primary" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {reportData && (
        <div className="report-container">
          <div className="report-header">
            <h2>{reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report</h2>
            <div className="report-actions">
              <button onClick={downloadPDF} className="btn-secondary">
                📄 Download PDF
              </button>
              <button onClick={downloadCSV} className="btn-secondary">
                📊 Download CSV
              </button>
            </div>
          </div>

          <div className="report-stats">
            <div className="report-stat">
              <h3>Total Consumption</h3>
              <p className="report-value">{reportData.total_consumption.toFixed(2)} kWh</p>
            </div>
            <div className="report-stat">
              <h3>Peak Power</h3>
              <p className="report-value">{reportData.peak_power.toFixed(2)} W</p>
            </div>
            <div className="report-stat">
              <h3>Avg Temperature</h3>
              <p className="report-value">{reportData.avg_temperature.toFixed(2)}°C</p>
            </div>
            <div className="report-stat">
              <h3>Avg Humidity</h3>
              <p className="report-value">{reportData.avg_humidity.toFixed(2)}%</p>
            </div>
            <div className="report-stat">
              <h3>Total Alerts</h3>
              <p className="report-value">{reportData.total_alerts}</p>
            </div>
            <div className="report-stat">
              <h3>Readings Count</h3>
              <p className="report-value">{reportData.readings_count}</p>
            </div>
          </div>

          <div className="period-breakdown">
            <h3>Consumption by Period</h3>
            <div className="period-stats">
              <div className="period-item">
                <span>Day Time:</span>
                <strong>{reportData.day_consumption.toFixed(2)} kWh</strong>
              </div>
              <div className="period-item">
                <span>Night Time:</span>
                <strong>{reportData.night_consumption.toFixed(2)} kWh</strong>
              </div>
              <div className="period-item">
                <span>Holiday:</span>
                <strong>{reportData.holiday_consumption.toFixed(2)} kWh</strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportsPage;
