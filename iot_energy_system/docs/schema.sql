-- IoT Energy Monitoring System - Database Schema
-- PostgreSQL 14+

-- Users Table (extends Django's auth_user)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    role VARCHAR(20) DEFAULT 'viewer',
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Devices Table
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    device_type VARCHAR(50) DEFAULT 'combined',
    status VARCHAR(20) DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_devices_device_id ON devices(device_id);
CREATE INDEX idx_devices_status ON devices(status);

-- Sensor Readings Table (Time-series data)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    voltage NUMERIC(10, 2) NOT NULL CHECK (voltage >= 0),
    current NUMERIC(10, 2) NOT NULL CHECK (current >= 0),
    power NUMERIC(10, 2) NOT NULL CHECK (power >= 0),
    energy_kwh NUMERIC(10, 4) NOT NULL CHECK (energy_kwh >= 0),
    temperature NUMERIC(5, 2) NOT NULL,
    humidity NUMERIC(5, 2) NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    period_type VARCHAR(20) DEFAULT 'day',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_readings_device_timestamp ON sensor_readings(device_id, timestamp DESC);
CREATE INDEX idx_readings_timestamp ON sensor_readings(timestamp DESC);
CREATE INDEX idx_readings_period_timestamp ON sensor_readings(period_type, timestamp DESC);

-- Thresholds Table
CREATE TABLE IF NOT EXISTS thresholds (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    parameter_name VARCHAR(50) NOT NULL,
    upper_limit NUMERIC(10, 2),
    lower_limit NUMERIC(10, 2),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, parameter_name)
);

CREATE INDEX idx_thresholds_device ON thresholds(device_id);
CREATE INDEX idx_thresholds_enabled ON thresholds(enabled);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    reading_id INTEGER REFERENCES sensor_readings(id) ON DELETE CASCADE,
    threshold_id INTEGER REFERENCES thresholds(id) ON DELETE CASCADE,
    parameter_name VARCHAR(50) NOT NULL,
    threshold_value NUMERIC(10, 2) NOT NULL,
    actual_value NUMERIC(10, 2) NOT NULL,
    violation_type VARCHAR(20) NOT NULL,
    severity VARCHAR(20) DEFAULT 'warning',
    status VARCHAR(20) DEFAULT 'active',
    message TEXT NOT NULL,
    acknowledged_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_alerts_device_created ON alerts(device_id, created_at DESC);
CREATE INDEX idx_alerts_status_created ON alerts(status, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE NOT NULL,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    issue_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'open',
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT
);

CREATE INDEX idx_tickets_ticket_id ON tickets(ticket_id);
CREATE INDEX idx_tickets_status_created ON tickets(status, created_at DESC);
CREATE INDEX idx_tickets_severity_created ON tickets(severity, created_at DESC);
CREATE INDEX idx_tickets_device ON tickets(device_id);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}',
    ip_address INET
);

CREATE INDEX idx_audit_user_timestamp ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_entity_timestamp ON audit_logs(entity_type, timestamp DESC);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);

-- Sample Data Insertion

-- Insert admin user (password should be hashed)
INSERT INTO users (username, email, password, role, is_staff, is_superuser)
VALUES ('admin', 'admin@example.com', 'pbkdf2_sha256$...', 'admin', TRUE, TRUE);

-- Insert sample devices
INSERT INTO devices (device_id, name, location, device_type, status) VALUES
('EMeter-001', 'Energy Meter 1', 'Building-1, Floor-1', 'combined', 'active'),
('EMeter-002', 'Energy Meter 2', 'Building-1, Floor-2', 'combined', 'active'),
('EMeter-003', 'Energy Meter 3', 'Building-1, Floor-3', 'combined', 'active'),
('EMeter-004', 'Energy Meter 4', 'Building-2, Floor-1', 'combined', 'active'),
('EMeter-005', 'Energy Meter 5', 'Building-2, Floor-2', 'combined', 'active');

-- Insert sample thresholds
INSERT INTO thresholds (device_id, parameter_name, upper_limit, lower_limit, enabled)
SELECT id, 'power', 10000, 100, TRUE FROM devices;

INSERT INTO thresholds (device_id, parameter_name, upper_limit, lower_limit, enabled)
SELECT id, 'temperature', 45, 10, TRUE FROM devices;

INSERT INTO thresholds (device_id, parameter_name, upper_limit, lower_limit, enabled)
SELECT id, 'humidity', 80, 30, TRUE FROM devices;

-- Views for reporting

-- Daily consumption summary view
CREATE OR REPLACE VIEW daily_consumption_summary AS
SELECT 
    d.device_id,
    d.name as device_name,
    DATE(sr.timestamp) as date,
    SUM(sr.energy_kwh) as total_energy,
    MAX(sr.power) as peak_power,
    AVG(sr.temperature) as avg_temperature,
    AVG(sr.humidity) as avg_humidity,
    COUNT(*) as readings_count,
    SUM(CASE WHEN sr.period_type = 'day' THEN sr.energy_kwh ELSE 0 END) as day_consumption,
    SUM(CASE WHEN sr.period_type = 'night' THEN sr.energy_kwh ELSE 0 END) as night_consumption,
    SUM(CASE WHEN sr.period_type = 'holiday' THEN sr.energy_kwh ELSE 0 END) as holiday_consumption
FROM sensor_readings sr
JOIN devices d ON sr.device_id = d.id
GROUP BY d.device_id, d.name, DATE(sr.timestamp)
ORDER BY DATE(sr.timestamp) DESC, d.device_id;

-- Active alerts view
CREATE OR REPLACE VIEW active_alerts_summary AS
SELECT 
    d.device_id,
    d.name as device_name,
    COUNT(*) as active_alert_count,
    SUM(CASE WHEN a.severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN a.severity = 'warning' THEN 1 ELSE 0 END) as warning_count,
    SUM(CASE WHEN a.severity = 'info' THEN 1 ELSE 0 END) as info_count
FROM alerts a
JOIN devices d ON a.device_id = d.id
WHERE a.status = 'active'
GROUP BY d.device_id, d.name;

-- Open tickets view
CREATE OR REPLACE VIEW open_tickets_summary AS
SELECT 
    d.device_id,
    d.name as device_name,
    COUNT(*) as open_ticket_count,
    SUM(CASE WHEN t.severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN t.severity = 'high' THEN 1 ELSE 0 END) as high_count,
    SUM(CASE WHEN t.severity = 'medium' THEN 1 ELSE 0 END) as medium_count,
    SUM(CASE WHEN t.severity = 'low' THEN 1 ELSE 0 END) as low_count
FROM tickets t
JOIN devices d ON t.device_id = d.id
WHERE t.status IN ('open', 'in_progress')
GROUP BY d.device_id, d.name;

-- Functions for data management

-- Function to archive old readings
CREATE OR REPLACE FUNCTION archive_old_readings(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sensor_readings
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean resolved alerts
CREATE OR REPLACE FUNCTION clean_old_alerts(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM alerts
    WHERE status = 'resolved' 
    AND resolved_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_devices_modtime
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_thresholds_modtime
    BEFORE UPDATE ON thresholds
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_tickets_modtime
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Performance optimization: Partitioning sensor_readings by date (optional)
-- For high-volume data, consider partitioning by month

-- CREATE TABLE sensor_readings_2024_01 PARTITION OF sensor_readings
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO iot_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO iot_user;

-- Comments
COMMENT ON TABLE devices IS 'IoT energy meter devices';
COMMENT ON TABLE sensor_readings IS 'Time-series sensor data from devices';
COMMENT ON TABLE thresholds IS 'Alert threshold configuration';
COMMENT ON TABLE alerts IS 'Alert records for threshold violations';
COMMENT ON TABLE tickets IS 'Support tickets for incident management';
COMMENT ON TABLE audit_logs IS 'Audit trail for security and compliance';

-- End of schema
