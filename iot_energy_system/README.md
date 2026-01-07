# IoT Energy Meter Monitoring & Incident Management System

## 📋 Project Overview

A production-ready, industrial-grade IoT Energy Meter Monitoring & Incident Management System that provides real-time monitoring, alerting, and analytics for energy consumption, temperature, and humidity across multiple devices.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  IoT Devices    │
│  (Simulated)    │
└────────┬────────┘
         │ REST API / MQTT
         ▼
┌─────────────────────────────────────────┐
│         Backend (Django + REST API)      │
│  ┌─────────────────────────────────┐   │
│  │  Data Ingestion Service         │   │
│  │  Threshold Monitoring Engine    │   │
│  │  Alert Detection System         │   │
│  │  Email Notification Service     │   │
│  │  Ticketing System               │   │
│  │  Report Generation Engine       │   │
│  └─────────────────────────────────┘   │
└──────────┬─────────────┬────────────────┘
           │             │
    ┌──────▼──────┐ ┌───▼──────┐
    │ PostgreSQL  │ │ WebSocket│
    │  Database   │ │  Server  │
    └─────────────┘ └─────┬────┘
                          │
                   ┌──────▼─────────┐
                   │  React.js      │
                   │  Dashboard     │
                   │  - Real-time   │
                   │    Graphs      │
                   │  - Alerts      │
                   │  - Tickets     │
                   │  - Reports     │
                   └────────────────┘
```

### Data Flow

1. **IoT → Backend**
   - IoT simulator generates sensor data (voltage, current, power, energy, temperature, humidity)
   - Data tagged with timestamp, device ID, and time period (Day/Night/Holiday)
   - Pushed to backend REST API every 10 seconds

2. **Backend Processing**
   - Validates and stores data in PostgreSQL
   - Threshold monitoring engine checks each reading against configured limits
   - If threshold violated:
     - Creates alert record with severity
     - Triggers email notification
     - Auto-generates support ticket
     - Broadcasts alert via WebSocket

3. **Dashboard Updates**
   - WebSocket receives real-time data
   - Charts update automatically
   - Alert popups shown for violations
   - Ticket panel refreshed
   - Color indicators updated (Green/Amber/Red)

4. **Reporting**
   - Background scheduler generates periodic reports
   - Aggregates data (hourly, daily, weekly, monthly)
   - Exports to PDF/CSV
   - Available for download in dashboard

## 📊 Database Schema

### Tables

1. **devices**
   - id (PK)
   - device_id (unique)
   - name
   - location
   - device_type
   - status (active/inactive)
   - created_at

2. **sensor_readings**
   - id (PK)
   - device_id (FK)
   - timestamp
   - voltage
   - current
   - power
   - energy_kwh
   - temperature
   - humidity
   - period_type (day/night/holiday)
   - created_at

3. **thresholds**
   - id (PK)
   - device_id (FK)
   - parameter_name
   - upper_limit
   - lower_limit
   - enabled
   - created_at
   - updated_at

4. **alerts**
   - id (PK)
   - device_id (FK)
   - reading_id (FK)
   - parameter_name
   - threshold_value
   - actual_value
   - violation_type (upper/lower)
   - severity (critical/warning/info)
   - status (active/resolved)
   - created_at
   - resolved_at

5. **tickets**
   - id (PK)
   - ticket_id (unique)
   - device_id (FK)
   - alert_id (FK)
   - issue_type
   - description
   - severity
   - status (open/in_progress/resolved)
   - assigned_to
   - created_at
   - updated_at
   - resolved_at

6. **users**
   - id (PK)
   - username
   - email
   - role (admin/manager/viewer)
   - password_hash
   - created_at

7. **audit_logs**
   - id (PK)
   - user_id (FK)
   - action
   - entity_type
   - entity_id
   - timestamp
   - details

## 🔧 Technology Stack

### Backend
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL 14+
- **Task Scheduler**: APScheduler
- **Email**: SMTP (Gmail/Custom)
- **WebSocket**: Django Channels
- **Authentication**: Django JWT

### Frontend
- **Framework**: React.js 18
- **Charts**: Recharts
- **Real-time**: Socket.io-client
- **Styling**: Tailwind CSS
- **State Management**: React Context/Redux

### IoT Simulation
- **Language**: Python 3.10+
- **Communication**: REST API
- **Libraries**: requests, schedule

## 🚀 Features

### Real-Time Monitoring
- ✅ Live energy consumption tracking
- ✅ Temperature and humidity monitoring
- ✅ Day/Night/Holiday consumption analysis
- ✅ Multiple device support

### Alert System
- ✅ Configurable thresholds (upper/lower limits)
- ✅ Real-time alert popups
- ✅ Color-coded severity indicators
- ✅ Alert history and logging

### Email Notifications
- ✅ Automatic warning emails on threshold violations
- ✅ Detailed alert information
- ✅ Multiple recipient support
- ✅ HTML email templates

### Ticketing System
- ✅ Auto-ticket generation on alerts
- ✅ Ticket status management
- ✅ Assignment to team members
- ✅ Ticket history tracking

### Analytics & Reports
- ✅ Hourly consumption reports
- ✅ Daily summary reports
- ✅ Weekly trend analysis
- ✅ Monthly consolidated reports
- ✅ PDF and CSV export
- ✅ Peak usage analysis
- ✅ Downtime tracking

### Security
- ✅ Role-based access control (RBAC)
- ✅ JWT authentication
- ✅ Data validation
- ✅ Audit logging
- ✅ Secure password hashing

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 14+
- pip and npm

### Backend Setup

```bash
cd iot_energy_system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
# Edit backend/config/settings.py with your PostgreSQL credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd iot_energy_system/frontend

# Install dependencies
npm install

# Configure API endpoint
# Edit src/config.js with your backend URL

# Start development server
npm start
```

### IoT Simulator Setup

```bash
cd iot_energy_system/iot_simulator

# Install dependencies
pip install -r requirements.txt

# Configure backend URL
# Edit config.py with your backend URL

# Start simulator
python simulator.py
```

## 🎯 Usage

### 1. Start Backend Server
```bash
cd backend
python manage.py runserver
```

### 2. Start Frontend Dashboard
```bash
cd frontend
npm start
```

### 3. Run IoT Simulator
```bash
cd iot_simulator
python simulator.py
```

### 4. Access Dashboard
Open browser: http://localhost:3000

### 5. Admin Panel
Access: http://localhost:8000/admin

## 📖 API Documentation

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token

### Devices
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create new device
- `GET /api/devices/{id}/` - Get device details
- `PUT /api/devices/{id}/` - Update device
- `DELETE /api/devices/{id}/` - Delete device

### Readings
- `POST /api/readings/` - Submit new reading
- `GET /api/readings/` - Get readings (with filters)
- `GET /api/readings/latest/` - Get latest readings

### Thresholds
- `GET /api/thresholds/` - List thresholds
- `POST /api/thresholds/` - Create threshold
- `PUT /api/thresholds/{id}/` - Update threshold
- `DELETE /api/thresholds/{id}/` - Delete threshold

### Alerts
- `GET /api/alerts/` - List alerts
- `GET /api/alerts/{id}/` - Get alert details
- `PUT /api/alerts/{id}/resolve/` - Resolve alert

### Tickets
- `GET /api/tickets/` - List tickets
- `POST /api/tickets/` - Create ticket
- `GET /api/tickets/{id}/` - Get ticket details
- `PUT /api/tickets/{id}/` - Update ticket status

### Reports
- `GET /api/reports/hourly/` - Generate hourly report
- `GET /api/reports/daily/` - Generate daily report
- `GET /api/reports/weekly/` - Generate weekly report
- `GET /api/reports/monthly/` - Generate monthly report
- `GET /api/reports/export/pdf/` - Export report as PDF
- `GET /api/reports/export/csv/` - Export report as CSV

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Manager, Viewer)
- Session management
- Password hashing (bcrypt)

### Data Security
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection

### Audit Trail
- All critical actions logged
- User action tracking
- Alert history
- Ticket modification history

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Pagination for large datasets
- Caching for dashboard data
- WebSocket for real-time updates (no polling)
- Optimized queries with select_related/prefetch_related

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## 📝 Deployment

### Production Deployment Steps

1. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb iot_energy_system
   ```

2. **Backend Deployment**
   ```bash
   # Set environment variables
   export DEBUG=False
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=postgresql://user:pass@host/db
   
   # Collect static files
   python manage.py collectstatic
   
   # Run with Gunicorn
   gunicorn backend.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Frontend Deployment**
   ```bash
   # Build production bundle
   npm run build
   
   # Deploy to web server (Nginx/Apache)
   ```

4. **Background Tasks**
   ```bash
   # Start scheduler for reports
   python manage.py start_scheduler
   ```

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in settings.py
- Ensure database exists

### WebSocket Connection Failed
- Check CORS settings
- Verify WebSocket port is open
- Check firewall rules

### Email Not Sending
- Verify SMTP settings
- Check email credentials
- Test with a simple email script

## 📞 Support

For issues and questions, please create an issue in the repository.

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributors

- Yuvaraj - Full Stack Developer & IoT Engineer

## 🎓 Project Type

Final Year Project / Industry-Grade Production System

---

**Note**: This is a complete, production-ready system designed for industrial use cases. All modules are fully functional and ready for deployment.
