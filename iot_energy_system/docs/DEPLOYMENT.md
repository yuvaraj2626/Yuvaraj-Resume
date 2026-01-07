# IoT Energy Monitoring System - Deployment Guide

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **Python**: 3.10 or higher
- **Node.js**: 16.x or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 6.x or higher (for WebSocket support)

### Software Installation

#### On Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server
```

## Step 1: Database Setup

### Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell
CREATE DATABASE iot_energy_system;
CREATE USER iot_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE iot_energy_system TO iot_user;
\q
```

## Step 2: Backend Setup

### Navigate to backend directory
```bash
cd iot_energy_system/backend
```

### Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure environment
```bash
cp .env.example .env
# Edit .env with your actual credentials
nano .env
```

### Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Create initial devices and thresholds
```bash
python manage.py shell
```

In the Python shell:
```python
from energy_monitor.models import Device, Threshold

# Create sample devices
for i in range(1, 6):
    device = Device.objects.create(
        device_id=f'EMeter-{i:03d}',
        name=f'Energy Meter {i}',
        location=f'Building-{(i-1)//3 + 1}, Floor-{((i-1)%3) + 1}',
        device_type='combined',
        status='active'
    )
    
    # Create thresholds for each device
    Threshold.objects.create(
        device=device,
        parameter_name='power',
        upper_limit=10000,
        lower_limit=100,
        enabled=True
    )
    
    Threshold.objects.create(
        device=device,
        parameter_name='temperature',
        upper_limit=45,
        lower_limit=10,
        enabled=True
    )
    
    Threshold.objects.create(
        device=device,
        parameter_name='humidity',
        upper_limit=80,
        lower_limit=30,
        enabled=True
    )
    
    print(f"Created device: {device.device_id}")

exit()
```

### Collect static files (for production)
```bash
python manage.py collectstatic --noinput
```

### Run development server
```bash
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Run with Daphne (for WebSocket support)
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Step 3: Frontend Setup

### Navigate to frontend directory
```bash
cd ../frontend
```

### Install dependencies
```bash
npm install
```

### Configure environment
```bash
cp .env.example .env
# Edit .env if backend is on different host/port
nano .env
```

### Run development server
```bash
npm start
```

Frontend will be available at: http://localhost:3000

### Build for production
```bash
npm run build
```

Production files will be in the `build` directory.

## Step 4: IoT Simulator Setup

### Navigate to simulator directory
```bash
cd ../iot_simulator
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure backend URL (if needed)
Edit `simulator.py` to change API_URL if backend is on different host.

### Run simulator
```bash
python simulator.py
```

The simulator will:
- Create 5 energy meter devices
- Generate realistic sensor data every 10 seconds
- Automatically push data to the backend

## Step 5: Verification

### Check all services are running:

1. **Backend**: http://localhost:8000/admin (login with superuser)
2. **Frontend**: http://localhost:3000 (dashboard should load)
3. **API**: http://localhost:8000/api/devices/ (should return devices list)
4. **Simulator**: Check console for data push logs

### Expected Flow:

1. Simulator generates data every 10 seconds
2. Backend receives data and checks thresholds
3. If threshold violated:
   - Alert created in database
   - Email sent to configured recipients
   - Ticket auto-generated for critical alerts
   - WebSocket notification sent to frontend
4. Dashboard updates in real-time

## Production Deployment

### Using Gunicorn for Backend

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Nginx as Reverse Proxy

Create `/etc/nginx/sites-available/iot-energy`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/iot-energy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd for Service Management

Create `/etc/systemd/system/iot-backend.service`:

```ini
[Unit]
Description=IoT Energy Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start iot-backend
sudo systemctl enable iot-backend
```

### Docker Deployment (Optional)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: iot_energy_system
      POSTGRES_USER: iot_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6

  backend:
    build: ./backend
    command: daphne -b 0.0.0.0 -p 8000 config.asgi:application
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Run with Docker:
```bash
docker-compose up -d
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U iot_user -d iot_energy_system -h localhost
```

### Redis Connection Issues
```bash
# Check Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

### Email Not Sending
- Verify SMTP credentials in `.env`
- For Gmail, enable "Less secure app access" or use App Password
- Check firewall allows outbound connections on port 587

### Frontend Can't Connect to Backend
- Verify backend is running: `curl http://localhost:8000/api/devices/`
- Check CORS settings in `backend/config/settings.py`
- Verify `.env` in frontend has correct API URL

### Simulator Not Sending Data
- Ensure backend is running and accessible
- Check device IDs match between simulator and database
- Verify API endpoint URL in simulator configuration

## Monitoring & Logs

### View Backend Logs
```bash
tail -f backend/logs/iot_energy.log
```

### View Systemd Service Logs
```bash
sudo journalctl -u iot-backend -f
```

### Database Queries
```bash
sudo -u postgres psql iot_energy_system
```

## Backup & Restore

### Backup Database
```bash
pg_dump -U iot_user iot_energy_system > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql -U iot_user iot_energy_system < backup_20240115.sql
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall rules
- [ ] Set up regular database backups
- [ ] Enable audit logging
- [ ] Review CORS allowed origins
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting on APIs

## Support

For issues or questions:
1. Check logs for error messages
2. Verify all services are running
3. Test database and Redis connections
4. Review configuration files
5. Create an issue in the repository

---

**Deployment completed successfully! Your IoT Energy Monitoring System is now ready for use.**
