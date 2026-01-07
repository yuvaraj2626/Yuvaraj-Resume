# System Architecture Documentation

## Overview

The IoT Energy Meter Monitoring & Incident Management System is a production-ready, full-stack application designed to monitor energy consumption, detect threshold violations, manage alerts, and generate comprehensive reports.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         IoT Devices Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │Energy Meter │  │Energy Meter │  │Energy Meter │  ... (5 devices)  │
│  │   EMeter-001│  │   EMeter-002│  │   EMeter-003│                   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                   │
└─────────┼─────────────────┼─────────────────┼────────────────────────┘
          │                 │                 │
          │ HTTP POST       │ HTTP POST       │ HTTP POST
          │ (JSON)          │ (JSON)          │ (JSON)
          │                 │                 │
          └─────────────────┴─────────────────┴─────────┐
                                                         │
┌────────────────────────────────────────────────────────▼──────────────┐
│                         Application Layer                             │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                 Django REST Framework                        │     │
│  │  ┌──────────────────────────────────────────────────────┐   │     │
│  │  │              API Endpoints                           │   │     │
│  │  │  - /api/devices/      - Device management           │   │     │
│  │  │  - /api/readings/     - Sensor data ingestion       │   │     │
│  │  │  - /api/thresholds/   - Threshold configuration     │   │     │
│  │  │  - /api/alerts/       - Alert management            │   │     │
│  │  │  - /api/tickets/      - Ticket management           │   │     │
│  │  │  - /api/reports/      - Report generation           │   │     │
│  │  │  - /api/dashboard/    - Dashboard statistics        │   │     │
│  │  └──────────────────────────────────────────────────────┘   │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    Business Logic Layer                      │     │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐           │     │
│  │  │Alert       │  │Ticket      │  │Report        │           │     │
│  │  │Service     │  │Service     │  │Service       │           │     │
│  │  └─────┬──────┘  └─────┬──────┘  └──────┬───────┘           │     │
│  │        │                │                │                   │     │
│  │        │         ┌──────▼──────┐        │                   │     │
│  │        └────────►│Email        │◄───────┘                   │     │
│  │                  │Service      │                            │     │
│  │                  └─────────────┘                            │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │              Background Tasks & Scheduling                   │     │
│  │  ┌────────────────┐  ┌──────────────────────────────┐       │     │
│  │  │APScheduler     │  │Tasks:                        │       │     │
│  │  │                │  │- Periodic report generation  │       │     │
│  │  │                │  │- Data cleanup/archiving      │       │     │
│  │  │                │  │- Health checks               │       │     │
│  │  └────────────────┘  └──────────────────────────────┘       │     │
│  └─────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
         ┌──────────▼──────┐  ┌────▼────┐  ┌──────▼──────┐
         │   PostgreSQL    │  │  Redis  │  │   SMTP      │
         │   Database      │  │         │  │   Server    │
         │                 │  │         │  │             │
         │  - Devices      │  │- Cache  │  │- Email      │
         │  - Readings     │  │- Session│  │  Delivery   │
         │  - Thresholds   │  │- Channels│ │             │
         │  - Alerts       │  └─────────┘  └─────────────┘
         │  - Tickets      │
         │  - Audit Logs   │
         └─────────┬───────┘
                   │
         ┌─────────▼───────────────────────────────────────┐
         │           WebSocket Layer (Channels)             │
         │  ┌─────────────┐                                 │
         │  │Channel Layer│  - Real-time data broadcast     │
         │  │  (Redis)    │  - Alert notifications          │
         │  └─────────────┘  - Live updates                 │
         └─────────┬───────────────────────────────────────┘
                   │
                   │ WebSocket (ws://)
                   │
┌──────────────────▼────────────────────────────────────────────────────┐
│                      Presentation Layer                               │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                   React.js Frontend                          │     │
│  │  ┌──────────────────────────────────────────────────────┐   │     │
│  │  │                 Pages & Components                   │   │     │
│  │  │  - Dashboard      - Real-time charts                │   │     │
│  │  │  - Devices        - Device management UI             │   │     │
│  │  │  - Alerts         - Alert listing & actions          │   │     │
│  │  │  - Tickets        - Ticket management                │   │     │
│  │  │  - Reports        - Report generation & download     │   │     │
│  │  └──────────────────────────────────────────────────────┘   │     │
│  │                                                               │     │
│  │  ┌──────────────────────────────────────────────────────┐   │     │
│  │  │                 Services Layer                       │   │     │
│  │  │  - API Service    - HTTP client for backend APIs    │   │     │
│  │  │  - WebSocket      - Real-time connection manager    │   │     │
│  │  └──────────────────────────────────────────────────────┘   │     │
│  │                                                               │     │
│  │  ┌──────────────────────────────────────────────────────┐   │     │
│  │  │              Visualization Library                   │   │     │
│  │  │  - Recharts       - Line, Bar, Pie charts           │   │     │
│  │  │  - React Toastify - Toast notifications             │   │     │
│  │  └──────────────────────────────────────────────────────┘   │     │
│  └─────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. IoT Data Collection Flow

```
IoT Simulator → HTTP POST → Django REST API → Serializer Validation
                                                      │
                                                      ▼
                                              Save to Database
                                                      │
                                                      ▼
                                            Threshold Monitoring
                                                      │
                                    ┌─────────────────┴──────────────┐
                                    │                                │
                               Threshold OK                  Threshold Violated
                                    │                                │
                                    ▼                                ▼
                            Continue Processing                Create Alert
                                                                     │
                                                    ┌────────────────┼────────────────┐
                                                    │                │                │
                                              Send Email      Create Ticket   WebSocket Broadcast
                                                                                      │
                                                                                      ▼
                                                                            Frontend Receives Alert
                                                                                      │
                                                                                      ▼
                                                                            Show Alert Popup
```

### 2. Alert Processing Workflow

```
New Sensor Reading
        │
        ▼
Check All Active Thresholds
        │
    ┌───┴───────┐
    │           │
Upper Limit  Lower Limit
Exceeded     Breached
    │           │
    └─────┬─────┘
          │
          ▼
Calculate Severity
(Critical/Warning/Info)
          │
          ▼
Create Alert Record
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
Email      Generate Ticket
Service    (if Critical)
    │           │
    └─────┬─────┘
          │
          ▼
Broadcast via WebSocket
          │
          ▼
Update Dashboard
```

### 3. Report Generation Flow

```
User Request → API Endpoint → Report Service
                                     │
                            ┌────────┴────────┐
                            │                 │
                    Fetch Data           Aggregate
                    (Time Range)         Statistics
                            │                 │
                            └────────┬────────┘
                                     │
                                     ▼
                          Generate Report Data
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                    PDF Export                CSV Export
                        │                         │
                        └────────────┬────────────┘
                                     │
                                     ▼
                            Return to Frontend
                                     │
                                     ▼
                            Download to User
```

## Component Details

### Backend Components

#### 1. Models (Database Layer)
- **Device**: IoT device information
- **SensorReading**: Time-series sensor data
- **Threshold**: Alert threshold configuration
- **Alert**: Alert records
- **Ticket**: Support ticket information
- **User**: User authentication and RBAC
- **AuditLog**: Security audit trail

#### 2. Serializers
- Data validation and transformation
- JSON serialization/deserialization
- Nested relationships handling

#### 3. ViewSets (API Layer)
- RESTful CRUD operations
- Custom actions for specific workflows
- Filtering, searching, pagination
- Permission checks

#### 4. Services (Business Logic)
- **AlertService**: Threshold monitoring and alert creation
- **EmailService**: Email notification delivery
- **TicketService**: Automatic ticket generation
- **ReportService**: Report generation and export

#### 5. Consumers (WebSocket)
- **SensorDataConsumer**: Real-time sensor data broadcasting
- **AlertConsumer**: Real-time alert notifications

### Frontend Components

#### 1. Pages
- **Dashboard**: Overview with statistics and charts
- **DevicesPage**: Device management
- **AlertsPage**: Alert monitoring and management
- **TicketsPage**: Ticket tracking
- **ReportsPage**: Report generation and download

#### 2. Components
- **Navbar**: Navigation menu
- **Charts**: Data visualization components
- **Tables**: Data display tables
- **Forms**: Input forms for configuration

#### 3. Services
- **apiService**: HTTP client for backend APIs
- WebSocket connections for real-time updates

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌──────────────┐
│   Device    │◄──────│  SensorReading   │──────►│   Alert      │
│             │ 1   * │                  │ 1   * │              │
│  device_id  │       │   timestamp      │       │   severity   │
│  name       │       │   voltage        │       │   status     │
│  location   │       │   current        │       │   message    │
│  status     │       │   power          │       └──────┬───────┘
└──────┬──────┘       │   energy_kwh     │              │
       │              │   temperature    │              │ 1
       │              │   humidity       │              │
       │ 1            └──────────────────┘              │
       │                                                │
       │ *                                              │ *
┌──────▼──────┐                              ┌─────────▼────────┐
│  Threshold  │                              │     Ticket       │
│             │                              │                  │
│  parameter  │                              │   ticket_id      │
│  upper_limit│                              │   issue_type     │
│  lower_limit│                              │   severity       │
│  enabled    │                              │   status         │
└─────────────┘                              │   description    │
                                             └──────────────────┘

┌──────────────┐                             ┌──────────────────┐
│    User      │                             │    AuditLog      │
│              │                             │                  │
│  username    │──────────────────────────►  │   action         │
│  email       │ 1                        *  │   entity_type    │
│  role        │                             │   timestamp      │
│  password    │                             │   details        │
└──────────────┘                             └──────────────────┘
```

## Security Architecture

### Authentication Flow

```
User Login → JWT Token Generation → Token Storage (Frontend)
                                            │
                                            ▼
            Each API Request ──────► Token Validation
                                            │
                        ┌───────────────────┴────────────────┐
                        │                                    │
                    Valid Token                         Invalid Token
                        │                                    │
                        ▼                                    ▼
                Execute Request                     Return 401 Unauthorized
```

### Role-Based Access Control

```
┌─────────┐
│  Admin  │ ─── Full access to all features
└─────────┘     - Create/Edit/Delete devices
                - Configure thresholds
                - Manage all tickets
                - View all reports
                - Manage users

┌─────────┐
│ Manager │ ─── Operational access
└─────────┘     - View devices
                - Acknowledge alerts
                - Update tickets
                - Generate reports
                - View dashboard

┌─────────┐
│ Viewer  │ ─── Read-only access
└─────────┘     - View dashboard
                - View devices
                - View alerts (no actions)
                - View tickets
                - Generate reports
```

## Performance Considerations

### Database Optimization
- **Indexes**: Created on frequently queried fields (timestamp, device_id, status)
- **Time-series optimization**: Partition tables by date for readings
- **Connection pooling**: Reuse database connections
- **Query optimization**: Use select_related and prefetch_related

### Caching Strategy
- **Redis caching**: Dashboard statistics, latest readings
- **Cache invalidation**: On new data or configuration changes
- **TTL**: Appropriate time-to-live for different data types

### Real-time Updates
- **WebSocket**: Bidirectional communication for live updates
- **Channel layers**: Redis-backed for horizontal scaling
- **Selective broadcasting**: Only send relevant updates to subscribed clients

## Scalability

### Horizontal Scaling
- **Stateless backend**: Can run multiple instances behind load balancer
- **Redis for session**: Shared session storage across instances
- **Database read replicas**: Distribute read load

### Data Archiving
- **Hot data**: Last 30 days in main database
- **Warm data**: 31-365 days in separate partition
- **Cold data**: Older than 1 year archived to separate storage

## Monitoring & Logging

### Application Logs
- **Info**: Normal operations, data processing
- **Warning**: Threshold violations, retries
- **Error**: Failed operations, exceptions
- **Critical**: System failures, data loss

### Metrics to Monitor
- API response times
- Database query performance
- Active WebSocket connections
- Alert generation rate
- Email delivery success rate
- Data ingestion rate
- System resource usage (CPU, Memory, Disk)

## Disaster Recovery

### Backup Strategy
- **Database backups**: Daily full backups, hourly incrementals
- **Configuration backups**: Version controlled in Git
- **Media files**: Replicated to object storage

### Recovery Procedures
- **Database restoration**: From latest backup
- **Service restart**: Automated health checks and restarts
- **Failover**: Automatic failover to standby instances

---

This architecture provides a robust, scalable, and maintainable system for IoT energy monitoring and incident management.
