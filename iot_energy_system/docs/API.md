# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

### Obtain JWT Token
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
**Endpoint:** `POST /api/auth/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using Token
Include in headers:
```
Authorization: Bearer <access_token>
```

---

## Devices API

### List All Devices
**Endpoint:** `GET /api/devices/`

**Query Parameters:**
- `status` - Filter by status (active, inactive, maintenance)
- `device_type` - Filter by type
- `search` - Search by device_id, name, location
- `page` - Page number
- `page_size` - Results per page

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "device_id": "EMeter-001",
      "name": "Energy Meter 1",
      "location": "Building-1, Floor-1",
      "device_type": "combined",
      "status": "active",
      "description": "IoT Energy Meter #1",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Device
**Endpoint:** `POST /api/devices/`

**Request Body:**
```json
{
  "device_id": "EMeter-006",
  "name": "Energy Meter 6",
  "location": "Building-2, Floor-3",
  "device_type": "combined",
  "status": "active",
  "description": "New energy meter"
}
```

### Get Device Details
**Endpoint:** `GET /api/devices/{id}/`

### Update Device
**Endpoint:** `PUT /api/devices/{id}/`

### Delete Device
**Endpoint:** `DELETE /api/devices/{id}/`

### Get Device Statistics
**Endpoint:** `GET /api/devices/{id}/statistics/`

**Query Parameters:**
- `hours` - Time range in hours (default: 24)

**Response:**
```json
{
  "total_energy": 125.45,
  "avg_power": 5234.67,
  "max_power": 8900.12,
  "avg_temperature": 28.34,
  "avg_humidity": 65.78,
  "readings_count": 8640
}
```

### Get Latest Reading for Device
**Endpoint:** `GET /api/devices/{id}/latest_reading/`

---

## Sensor Readings API

### List Readings
**Endpoint:** `GET /api/readings/`

**Query Parameters:**
- `device` - Filter by device ID
- `period_type` - Filter by period (day, night, holiday)
- `page` - Page number
- `page_size` - Results per page

**Response:**
```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/readings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "device": 1,
      "device_id": "EMeter-001",
      "device_name": "Energy Meter 1",
      "timestamp": "2024-01-15T14:30:00Z",
      "voltage": 230.45,
      "current": 25.67,
      "power": 5915.05,
      "energy_kwh": 0.0164,
      "temperature": 28.5,
      "humidity": 65.2,
      "period_type": "day",
      "created_at": "2024-01-15T14:30:05Z"
    }
  ]
}
```

### Create Reading
**Endpoint:** `POST /api/readings/`

**Request Body:**
```json
{
  "device_id": "EMeter-001",
  "timestamp": "2024-01-15T14:30:00Z",
  "voltage": 230.45,
  "current": 25.67,
  "power": 5915.05,
  "energy_kwh": 0.0164,
  "temperature": 28.5,
  "humidity": 65.2,
  "period_type": "day"
}
```

**Note:** Creating a reading automatically triggers threshold checking.

### Get Latest Readings
**Endpoint:** `GET /api/readings/latest/`

Returns the latest reading for each active device.

### Get Time Series Data
**Endpoint:** `GET /api/readings/time_series/`

**Query Parameters:**
- `device_id` - Specific device (optional)
- `hours` - Time range in hours (default: 24)
- `parameter` - Parameter to retrieve (default: power)

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T14:30:00Z",
    "power": 5915.05,
    "device__device_id": "EMeter-001"
  }
]
```

---

## Thresholds API

### List Thresholds
**Endpoint:** `GET /api/thresholds/`

**Query Parameters:**
- `device` - Filter by device ID
- `parameter_name` - Filter by parameter
- `enabled` - Filter by enabled status

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "device": 1,
      "device_id": "EMeter-001",
      "device_name": "Energy Meter 1",
      "parameter_name": "power",
      "upper_limit": 10000.0,
      "lower_limit": 100.0,
      "enabled": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Threshold
**Endpoint:** `POST /api/thresholds/`

**Request Body:**
```json
{
  "device": 1,
  "parameter_name": "temperature",
  "upper_limit": 45.0,
  "lower_limit": 10.0,
  "enabled": true
}
```

### Update Threshold
**Endpoint:** `PUT /api/thresholds/{id}/`

### Delete Threshold
**Endpoint:** `DELETE /api/thresholds/{id}/`

### Toggle Threshold
**Endpoint:** `POST /api/thresholds/{id}/toggle/`

Enables/disables the threshold.

---

## Alerts API

### List Alerts
**Endpoint:** `GET /api/alerts/`

**Query Parameters:**
- `device` - Filter by device ID
- `severity` - Filter by severity (critical, warning, info)
- `status` - Filter by status (active, acknowledged, resolved)
- `parameter_name` - Filter by parameter

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "device": 1,
      "device_id": "EMeter-001",
      "device_name": "Energy Meter 1",
      "reading": 1234,
      "threshold": 1,
      "parameter_name": "temperature",
      "threshold_value": 45.0,
      "actual_value": 48.5,
      "violation_type": "upper",
      "severity": "critical",
      "status": "active",
      "message": "Temperature exceeded threshold for device EMeter-001...",
      "acknowledged_by": null,
      "acknowledged_by_username": null,
      "acknowledged_at": null,
      "created_at": "2024-01-15T14:35:00Z",
      "resolved_at": null
    }
  ]
}
```

### Get Active Alerts
**Endpoint:** `GET /api/alerts/active/`

Returns all alerts with status='active'.

### Acknowledge Alert
**Endpoint:** `POST /api/alerts/{id}/acknowledge/`

Updates alert status to 'acknowledged' and records the user and timestamp.

### Resolve Alert
**Endpoint:** `POST /api/alerts/{id}/resolve/`

Updates alert status to 'resolved' and records the timestamp.

---

## Tickets API

### List Tickets
**Endpoint:** `GET /api/tickets/`

**Query Parameters:**
- `device` - Filter by device ID
- `severity` - Filter by severity (critical, high, medium, low)
- `status` - Filter by status (open, in_progress, resolved, closed)

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "ticket_id": "TKT-20240115-0001",
      "device": 1,
      "device_id": "EMeter-001",
      "device_name": "Energy Meter 1",
      "alert": 1,
      "issue_type": "TEMPERATURE Threshold Violation",
      "description": "Automated Ticket: Threshold Violation Detected...",
      "severity": "critical",
      "status": "open",
      "assigned_to": null,
      "assigned_to_username": null,
      "created_by": null,
      "created_by_username": null,
      "created_at": "2024-01-15T14:35:00Z",
      "updated_at": "2024-01-15T14:35:00Z",
      "resolved_at": null,
      "resolution_notes": null
    }
  ]
}
```

### Create Ticket
**Endpoint:** `POST /api/tickets/`

**Request Body:**
```json
{
  "device": 1,
  "alert": 1,
  "issue_type": "Manual Inspection Required",
  "description": "Need to check device physically",
  "severity": "medium"
}
```

### Update Ticket
**Endpoint:** `PUT /api/tickets/{id}/`

### Update Ticket Status
**Endpoint:** `POST /api/tickets/{id}/update_status/`

**Request Body:**
```json
{
  "status": "in_progress"
}
```

### Assign Ticket
**Endpoint:** `POST /api/tickets/{id}/assign/`

**Request Body:**
```json
{
  "user_id": 2
}
```

---

## Dashboard API

### Get Dashboard Statistics
**Endpoint:** `GET /api/dashboard/stats/`

**Response:**
```json
{
  "total_devices": 5,
  "active_devices": 5,
  "total_readings_today": 4320,
  "active_alerts": 3,
  "open_tickets": 2,
  "total_energy_today": 145.67,
  "avg_temperature": 27.8,
  "avg_humidity": 64.3
}
```

---

## Reports API

### Generate Hourly Report
**Endpoint:** `GET /api/reports/hourly/`

**Query Parameters:**
- `device_id` - Specific device (optional)

**Response:**
```json
{
  "report_type": "hourly",
  "start_date": "2024-01-15T13:00:00Z",
  "end_date": "2024-01-15T14:00:00Z",
  "total_consumption": 12.45,
  "peak_power": 8900.12,
  "avg_temperature": 28.34,
  "avg_humidity": 65.78,
  "total_alerts": 2,
  "day_consumption": 8.30,
  "night_consumption": 4.15,
  "holiday_consumption": 0.0,
  "readings_count": 360
}
```

### Generate Daily Report
**Endpoint:** `GET /api/reports/daily/`

**Query Parameters:**
- `device_id` - Specific device (optional)
- `date` - Specific date (YYYY-MM-DD, optional)

### Generate Weekly Report
**Endpoint:** `GET /api/reports/weekly/`

**Query Parameters:**
- `device_id` - Specific device (optional)

### Generate Monthly Report
**Endpoint:** `GET /api/reports/monthly/`

**Query Parameters:**
- `device_id` - Specific device (optional)

### Export Report as PDF
**Endpoint:** `GET /api/reports/export_pdf/`

**Query Parameters:**
- `type` - Report type (hourly, daily, weekly, monthly)
- `device_id` - Specific device (optional)

**Response:** PDF file download

### Export Report as CSV
**Endpoint:** `GET /api/reports/export_csv/`

**Query Parameters:**
- `type` - Report type (hourly, daily, weekly, monthly)
- `device_id` - Specific device (optional)

**Response:** CSV file download

---

## Users API

### List Users
**Endpoint:** `GET /api/users/`

**Query Parameters:**
- `search` - Search by username, email, name

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "phone": "+1234567890",
      "first_name": "Admin",
      "last_name": "User"
    }
  ]
}
```

---

## WebSocket API

### Sensor Data Stream
**Endpoint:** `ws://localhost:8000/ws/sensor-data/`

**Message Format:**
```json
{
  "type": "sensor_reading",
  "data": {
    "device_id": "EMeter-001",
    "voltage": 230.45,
    "current": 25.67,
    "power": 5915.05,
    "temperature": 28.5,
    "humidity": 65.2,
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

### Alert Notifications
**Endpoint:** `ws://localhost:8000/ws/alerts/`

**Message Format:**
```json
{
  "type": "alert",
  "data": {
    "alert_id": 1,
    "device_id": "EMeter-001",
    "severity": "critical",
    "message": "Temperature exceeded threshold...",
    "timestamp": "2024-01-15T14:35:00Z"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error."
}
```

---

## Rate Limiting

- Default: 100 requests per minute per user
- Burst: 200 requests
- Throttle response: HTTP 429 Too Many Requests

## Pagination

Default page size: 50 items

Response format:
```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": []
}
```

## Filtering

Most list endpoints support filtering via query parameters.

Example:
```
GET /api/alerts/?severity=critical&status=active&device=1
```

## Ordering

Use `ordering` parameter:
```
GET /api/readings/?ordering=-timestamp
```

Use `-` prefix for descending order.

---

## Testing APIs

### Using cURL

```bash
# Get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token
curl -X GET http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Python requests

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', 
                        json={'username': 'admin', 'password': 'admin123'})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/devices/', headers=headers)
devices = response.json()
```

### Using JavaScript fetch

```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});
const { access } = await response.json();

// Make authenticated request
const devicesResponse = await fetch('http://localhost:8000/api/devices/', {
  headers: {'Authorization': `Bearer ${access}`}
});
const devices = await devicesResponse.json();
```

---

**Note:** All timestamps are in ISO 8601 format (UTC).
