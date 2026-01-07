# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
python3 --version  # Should be 3.10+
node --version     # Should be 16+
psql --version     # Should be 14+
```

### Step 1: Clone and Navigate
```bash
cd iot_energy_system
```

### Step 2: Start PostgreSQL
```bash
# Create database
sudo -u postgres createdb iot_energy_system

# Or using psql:
sudo -u postgres psql
CREATE DATABASE iot_energy_system;
\q
```

### Step 3: Backend Setup (Terminal 1)
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser  # Create admin account

# Start server
python manage.py runserver
```

Backend running at: **http://localhost:8000**

### Step 4: Frontend Setup (Terminal 2)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend running at: **http://localhost:3000**

### Step 5: IoT Simulator (Terminal 3)
```bash
cd iot_simulator

# Install dependencies
pip install -r requirements.txt

# Start simulator
python simulator.py
```

### Step 6: Access the System

1. **Dashboard**: http://localhost:3000
2. **Admin Panel**: http://localhost:8000/admin
3. **API**: http://localhost:8000/api/

### What to Expect

1. **Simulator** generates data every 10 seconds
2. **Dashboard** updates in real-time
3. **Alerts** trigger when thresholds are exceeded
4. **Tickets** automatically created for critical alerts
5. **Reports** available for download

## 📊 Demo Data

The simulator creates 5 energy meters automatically:
- EMeter-001 through EMeter-005
- Located across different buildings and floors
- Generates realistic voltage, current, power, temperature, and humidity data

## ⚙️ Configuration

### Set Email Notifications
Edit `backend/.env`:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=manager@company.com
```

### Configure Thresholds
Login to admin panel:
1. Go to http://localhost:8000/admin
2. Click "Thresholds"
3. Add/Edit threshold values for each parameter

## 🔧 Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Check status
sudo systemctl status postgresql
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Backend
pip install -r requirements.txt
```

## 📱 Features to Try

1. **Real-time Monitoring**: Watch dashboard update live
2. **Threshold Configuration**: Set custom limits in admin panel
3. **Alert Management**: Acknowledge and resolve alerts
4. **Ticket Tracking**: Update ticket status
5. **Report Generation**: Download PDF/CSV reports

## 🎯 Next Steps

1. Read [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production setup
2. Review [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
3. Customize thresholds for your use case
4. Configure email notifications
5. Set up user roles and permissions

---

**System is ready! Start monitoring your energy consumption! ⚡**
