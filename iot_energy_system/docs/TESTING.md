# Testing Guide

## Overview

This guide provides instructions for testing the IoT Energy Monitoring System.

## Prerequisites

Ensure system is running:
1. Backend server: http://localhost:8000
2. Frontend: http://localhost:3000
3. PostgreSQL database
4. IoT Simulator

## Manual Testing Checklist

### 1. Device Management

#### Test: View Devices
1. Navigate to http://localhost:3000/devices
2. Verify 5 devices are displayed (EMeter-001 to EMeter-005)
3. Check device information (name, location, status)

**Expected Result:** All devices show with correct information

#### Test: Device Status
1. Go to Admin panel: http://localhost:8000/admin
2. Login with superuser credentials
3. Navigate to Devices
4. Change device status to 'inactive'
5. Refresh frontend devices page

**Expected Result:** Status updated in real-time

### 2. Real-time Data Monitoring

#### Test: Dashboard Statistics
1. Navigate to http://localhost:3000/dashboard
2. Verify statistics cards display:
   - Total Devices: 5
   - Active Devices: 5
   - Energy Today: > 0 kWh
   - Active Alerts: Varies
   - Open Tickets: Varies
   - Avg Temperature: 20-35°C
   - Avg Humidity: 40-80%

**Expected Result:** All statistics show realistic values

#### Test: Real-time Charts
1. Stay on dashboard
2. Wait 10 seconds (simulator interval)
3. Observe if charts update

**Expected Result:** Charts update with new data points

#### Test: Latest Readings Table
1. Check latest readings table on dashboard
2. Verify each device has a reading
3. Check timestamp is recent (< 30 seconds old)

**Expected Result:** Fresh data from all devices

### 3. Threshold Monitoring & Alerts

#### Test: Configure Threshold
1. Login to admin: http://localhost:8000/admin
2. Go to Thresholds
3. Select a threshold (e.g., temperature for EMeter-001)
4. Change upper_limit to 25 (artificially low)
5. Save

**Expected Result:** Threshold saved successfully

#### Test: Alert Generation
1. Wait for next simulator cycle (10 seconds)
2. Navigate to http://localhost:3000/alerts
3. Check for new alert

**Expected Result:** Alert created for temperature > 25°C

#### Test: Alert Severity
1. Check alert severity badge color:
   - Critical: Red
   - Warning: Orange
   - Info: Blue

**Expected Result:** Severity displayed with appropriate color

#### Test: Acknowledge Alert
1. On alerts page, find active alert
2. Click "Acknowledge" button
3. Refresh page

**Expected Result:** Alert status changed to 'acknowledged'

### 4. Email Notifications

#### Test: Email Configuration
1. Edit `backend/.env`
2. Add your email credentials:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ALERT_EMAIL_RECIPIENTS=test@example.com
   ```
3. Restart backend server

#### Test: Receive Alert Email
1. Configure low threshold as above
2. Wait for violation
3. Check email inbox

**Expected Result:** HTML email received with alert details

**Email Content Should Include:**
- Device ID and name
- Parameter exceeded
- Current value
- Threshold value
- Timestamp
- Severity indicator

### 5. Ticketing System

#### Test: Auto-ticket Creation
1. Configure critical threshold (e.g., temperature > 25)
2. Wait for violation
3. Navigate to http://localhost:3000/tickets

**Expected Result:** New ticket auto-created with:
- Unique ticket ID (TKT-YYYYMMDD-XXXX)
- Device information
- Issue type
- Severity: Critical
- Status: Open

#### Test: Update Ticket Status
1. Find open ticket
2. Click "Start" button
3. Verify status changes to "In Progress"
4. Click "Resolve" button
5. Verify status changes to "Resolved"

**Expected Result:** Status transitions work correctly

#### Test: Manual Ticket Creation
1. Go to admin panel
2. Navigate to Tickets
3. Click "Add Ticket"
4. Fill in details and save

**Expected Result:** Ticket created successfully

### 6. Report Generation

#### Test: Generate Daily Report
1. Navigate to http://localhost:3000/reports
2. Select "Daily Report"
3. Click "Generate Report"

**Expected Result:** Report displayed with:
- Total consumption (kWh)
- Peak power (W)
- Average temperature
- Average humidity
- Total alerts
- Period breakdown (day/night/holiday)

#### Test: Download PDF
1. After generating report
2. Click "Download PDF"

**Expected Result:** PDF file downloads with formatted report

#### Test: Download CSV
1. After generating report
2. Click "Download CSV"

**Expected Result:** CSV file downloads with detailed readings

#### Test: Report Types
1. Test each report type:
   - Hourly (last hour)
   - Daily (today)
   - Weekly (last 7 days)
   - Monthly (last 30 days)

**Expected Result:** Each report shows appropriate time range

### 7. IoT Simulator

#### Test: Simulator Running
1. Check simulator terminal output
2. Verify messages every 10 seconds:
   ```
   ✓ EMeter-001: P=5915W, T=28.5°C, H=65.2%, Period=day
   ✓ EMeter-002: P=4230W, T=26.8°C, H=62.1%, Period=day
   ...
   ```

**Expected Result:** Continuous data generation

#### Test: Period Classification
1. Change system time to night (18:00 - 06:00)
2. Or wait until actual night time
3. Check simulator output

**Expected Result:** period_type = 'night'

#### Test: Data Variance
1. Observe multiple cycles
2. Check values vary realistically:
   - Voltage: ~230V ±5V
   - Current: 5-50A
   - Temperature: 20-35°C
   - Humidity: 40-80%

**Expected Result:** Realistic data patterns

### 8. API Testing

#### Test: Get Devices API
```bash
curl http://localhost:8000/api/devices/
```

**Expected Result:** JSON array of devices

#### Test: Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token
curl -X GET http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer <access_token>"
```

**Expected Result:** Token obtained and API accessible

#### Test: Create Reading
```bash
curl -X POST http://localhost:8000/api/readings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "device_id": "EMeter-001",
    "timestamp": "2024-01-15T14:30:00Z",
    "voltage": 230,
    "current": 25,
    "power": 5750,
    "energy_kwh": 0.016,
    "temperature": 28,
    "humidity": 65,
    "period_type": "day"
  }'
```

**Expected Result:** Reading created, thresholds checked

### 9. Database Verification

#### Test: Check Tables
```bash
sudo -u postgres psql iot_energy_system

\dt  -- List tables
```

**Expected Tables:**
- devices
- sensor_readings
- thresholds
- alerts
- tickets
- users
- audit_logs

#### Test: Query Recent Readings
```sql
SELECT device_id, timestamp, voltage, current, power, temperature
FROM sensor_readings
ORDER BY timestamp DESC
LIMIT 10;
```

**Expected Result:** 10 most recent readings

#### Test: Count Active Alerts
```sql
SELECT COUNT(*) FROM alerts WHERE status = 'active';
```

**Expected Result:** Count of active alerts

### 10. Performance Testing

#### Test: Dashboard Load Time
1. Open browser developer tools
2. Navigate to dashboard
3. Check network tab for load time

**Expected Result:** Page loads < 2 seconds

#### Test: API Response Time
```bash
time curl http://localhost:8000/api/devices/
```

**Expected Result:** Response < 500ms

#### Test: Concurrent Requests
1. Run multiple simulators simultaneously
2. Check backend handles load
3. Monitor CPU and memory usage

**Expected Result:** System remains responsive

### 11. Error Handling

#### Test: Invalid Data
```bash
curl -X POST http://localhost:8000/api/readings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "device_id": "INVALID",
    "voltage": -100
  }'
```

**Expected Result:** 400 Bad Request with error details

#### Test: Unauthorized Access
```bash
curl http://localhost:8000/api/readings/
```

**Expected Result:** 401 Unauthorized

#### Test: Network Error
1. Stop backend server
2. Try to load dashboard

**Expected Result:** Error toast notification displayed

### 12. Security Testing

#### Test: SQL Injection
Try entering SQL in form fields:
```
'; DROP TABLE devices; --
```

**Expected Result:** Input sanitized, no SQL execution

#### Test: XSS Protection
Try entering script in device name:
```
<script>alert('XSS')</script>
```

**Expected Result:** Script tags escaped

#### Test: CSRF Protection
1. Try POST without CSRF token
2. Check request blocked

**Expected Result:** 403 Forbidden

## Automated Testing

### Backend Unit Tests

```bash
cd backend
python manage.py test
```

**Expected Result:** All tests pass

### Frontend Tests

```bash
cd frontend
npm test
```

**Expected Result:** All tests pass

## Load Testing

### Using Apache Bench
```bash
ab -n 1000 -c 10 http://localhost:8000/api/devices/
```

Test 1000 requests with 10 concurrent connections.

**Expected Result:** 
- Requests/sec: > 100
- Failed requests: 0

### Using Locust (Optional)

Create `locustfile.py`:
```python
from locust import HttpUser, task, between

class EnergyMonitorUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_dashboard(self):
        self.client.get("/api/dashboard/stats/")
    
    @task
    def view_devices(self):
        self.client.get("/api/devices/")
```

Run:
```bash
locust -f locustfile.py
```

## Test Results Documentation

### Pass/Fail Checklist

- [ ] Device management works
- [ ] Real-time data updates
- [ ] Threshold monitoring functional
- [ ] Alerts generated correctly
- [ ] Email notifications sent
- [ ] Tickets auto-created
- [ ] Reports generate successfully
- [ ] PDF/CSV exports work
- [ ] API endpoints respond correctly
- [ ] Authentication works
- [ ] Database queries execute
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Security measures active

## Troubleshooting Test Failures

### Alert Not Generated
- Check threshold configuration
- Verify threshold is enabled
- Check data actually violates threshold
- Review backend logs

### Email Not Sent
- Verify SMTP settings in .env
- Check email credentials
- Test with simple email script
- Check spam folder

### Dashboard Not Updating
- Check WebSocket connection
- Verify simulator is running
- Check browser console for errors
- Test API directly

### Report Generation Failed
- Check date range has data
- Verify database connection
- Check reportlab/pandas installed
- Review backend logs

## Reporting Issues

When reporting test failures, include:
1. Test case that failed
2. Expected result
3. Actual result
4. Steps to reproduce
5. Error messages/logs
6. Environment details (OS, versions)
7. Screenshots if applicable

## Continuous Testing

Set up automated testing:
1. Run tests on every commit
2. Schedule daily integration tests
3. Monitor production metrics
4. Set up alerting for failures

---

**Testing completed successfully means the system is production-ready! ✅**
