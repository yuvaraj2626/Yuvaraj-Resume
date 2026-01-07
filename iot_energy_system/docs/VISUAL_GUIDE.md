# Visual Guide - IoT Energy Monitoring System

## System Overview Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                     IoT ENERGY MONITORING SYSTEM                    │
└────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────┐
                        │   IoT Devices   │
                        │  (5 Simulators) │
                        └────────┬────────┘
                                 │
                    Every 10 seconds: POST /api/readings/
                    {voltage, current, power, energy, temp, humidity}
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                        BACKEND (Django)                             │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  REST API Layer (30+ endpoints)                              │ │
│  │  • Authentication (JWT)                                      │ │
│  │  • Devices CRUD                                              │ │
│  │  • Readings ingestion → Validate → Save → Check thresholds  │ │
│  │  • Alerts management                                         │ │
│  │  • Tickets management                                        │ │
│  │  • Reports generation                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Business Logic Services                                     │ │
│  │  • AlertService: Detects violations → Creates alerts        │ │
│  │  • EmailService: Sends HTML emails                          │ │
│  │  • TicketService: Auto-creates tickets for critical alerts  │ │
│  │  • ReportService: Generates PDF/CSV reports                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  WebSocket Layer (Django Channels)                          │ │
│  │  • Broadcasts sensor data in real-time                      │ │
│  │  • Pushes alert notifications instantly                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────┬────────────────────────┬──────────────────────────┬─────────┘
      │                        │                          │
      ▼                        ▼                          ▼
┌───────────┐          ┌──────────────┐          ┌──────────────┐
│PostgreSQL │          │    Redis     │          │ SMTP Server  │
│           │          │              │          │              │
│• Devices  │          │• WebSocket   │          │• Gmail/      │
│• Readings │          │  channels    │          │  Custom      │
│• Alerts   │          │• Cache       │          │• Send alerts │
│• Tickets  │          │              │          │              │
│• Users    │          │              │          │              │
└───────────┘          └──────────────┘          └──────────────┘
      │
      │ WebSocket Connection (ws://)
      │
      ▼
┌────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React.js)                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  📊 Dashboard Page                                           │ │
│  │  • 6 Statistics cards (devices, energy, alerts, tickets)    │ │
│  │  • Real-time line chart (power consumption)                 │ │
│  │  • Pie chart (day/night/holiday split)                      │ │
│  │  • Latest readings table                                    │ │
│  │  • Active alerts list                                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  🔌 Devices Page                                             │ │
│  │  • Grid view of all devices                                 │ │
│  │  • Device status indicators                                 │ │
│  │  • Device information cards                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  ⚠️  Alerts Page                                              │ │
│  │  • List of all alerts with filters                          │ │
│  │  • Severity badges (critical/warning/info)                  │ │
│  │  • Acknowledge and resolve buttons                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  🎫 Tickets Page                                             │ │
│  │  • Ticket listing table                                     │ │
│  │  • Status management (open/in_progress/resolved)           │ │
│  │  • Assignment to users                                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  📈 Reports Page                                             │ │
│  │  • Report type selector (hourly/daily/weekly/monthly)      │ │
│  │  • Statistics display                                       │ │
│  │  • PDF/CSV download buttons                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│ Simulator   │
│ generates   │
│ sensor data │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ POST /api/readings/                          │
│ {                                            │
│   device_id: "EMeter-001",                   │
│   voltage: 230.5,                            │
│   current: 25.3,                             │
│   power: 5831.65,                            │
│   energy_kwh: 0.0162,                        │
│   temperature: 28.7,                         │
│   humidity: 64.2,                            │
│   period_type: "day"                         │
│ }                                            │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Validate data       │
│ (serializer)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Save to database    │
│ (sensor_readings)   │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ Check all thresholds for this device        │
│                                              │
│ For each parameter (power, temp, humidity): │
│   if value > upper_limit OR                 │
│      value < lower_limit:                   │
│     → Create alert                          │
└──────┬───────────────────────────────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌──────────────┐         ┌─────────────────┐
│ Normal flow  │         │ Threshold       │
│ Continue     │         │ Violated!       │
└──────────────┘         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌───────────┐  ┌──────────┐  ┌──────────────┐
            │Create     │  │Send      │  │Create Ticket │
            │Alert      │  │Email     │  │(if critical) │
            │Record     │  │          │  │              │
            └───────────┘  └──────────┘  └──────┬───────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Broadcast via WebSocket  │
                    │ to all connected clients │
                    └──────────┬───────────────┘
                              │
                              ▼
                    ┌──────────────────────────┐
                    │ Frontend receives alert  │
                    │ Shows popup notification │
                    │ Updates dashboard        │
                    └──────────────────────────┘
```

## Alert Severity Flow

```
Reading violates threshold
          │
          ▼
Calculate deviation = |actual - threshold| / threshold * 100
          │
          ├───────────────┬───────────────┐
          │               │               │
    deviation > 50%  deviation > 20%  deviation ≤ 20%
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌──────┐
    │CRITICAL │     │ WARNING │     │ INFO │
    │  🔴     │     │   🟠    │     │  🔵  │
    └────┬────┘     └────┬────┘     └───┬──┘
         │               │               │
    Auto-create    Send email      Log only
    ticket
```

## User Roles & Permissions

```
┌──────────────────────────────────────────────────────────┐
│                    ADMIN (Full Access)                    │
├──────────────────────────────────────────────────────────┤
│ ✅ View dashboard                                         │
│ ✅ Manage devices (create, edit, delete)                 │
│ ✅ Configure thresholds                                   │
│ ✅ View & manage alerts                                   │
│ ✅ View & manage all tickets                              │
│ ✅ Generate & download reports                            │
│ ✅ Manage users                                           │
│ ✅ Access admin panel                                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                 MANAGER (Operational Access)              │
├──────────────────────────────────────────────────────────┤
│ ✅ View dashboard                                         │
│ ✅ View devices (no edit)                                │
│ ✅ View thresholds                                        │
│ ✅ Acknowledge & resolve alerts                           │
│ ✅ Update assigned tickets                                │
│ ✅ Generate & download reports                            │
│ ❌ Cannot manage users                                    │
│ ❌ Cannot access admin panel                              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  VIEWER (Read-Only Access)                │
├──────────────────────────────────────────────────────────┤
│ ✅ View dashboard                                         │
│ ✅ View devices                                           │
│ ✅ View alerts (no actions)                               │
│ ✅ View tickets                                           │
│ ✅ Generate & view reports                                │
│ ❌ Cannot modify anything                                 │
│ ❌ Cannot acknowledge alerts                              │
│ ❌ Cannot update tickets                                  │
│ ❌ Cannot access admin panel                              │
└──────────────────────────────────────────────────────────┘
```

## Database Relationships

```
┌──────────┐
│ devices  │───┐
└──────────┘   │
               │ 1:N
               │
               ├────┐
               │    ▼
               │  ┌─────────────────┐
               │  │ sensor_readings │
               │  └─────────────────┘
               │
               ├────┐
               │    ▼
               │  ┌────────────┐
               │  │ thresholds │
               │  └────────────┘
               │
               ├────┐
               │    ▼
               │  ┌────────┐      ┌──────────┐
               │  │ alerts │──────│ tickets  │
               │  └────────┘  1:1 └──────────┘
               │
               └────┐
                    ▼
                  ┌─────────────┐
                  │ audit_logs  │
                  └─────────────┘

┌───────┐
│ users │────────────────┐
└───────┘                │
                         │ N:1
                         ▼
              ┌──────────────────────┐
              │ alerts.acknowledged_by│
              │ tickets.assigned_to   │
              │ tickets.created_by    │
              │ audit_logs.user_id    │
              └──────────────────────┘
```

## Report Generation Flow

```
User selects report type
        │
        ├────────┬────────┬────────┬────────┐
        │        │        │        │        │
    Hourly   Daily   Weekly  Monthly
   (1 hour) (Today) (7 days)(30 days)
        │        │        │        │
        └────────┴────────┴────────┘
                 │
                 ▼
    Query sensor_readings for date range
                 │
                 ▼
    ┌────────────────────────────────┐
    │ Aggregate data:                │
    │ • Total energy (kWh)           │
    │ • Peak power (W)               │
    │ • Average temperature          │
    │ • Average humidity             │
    │ • Count alerts                 │
    │                                │
    │ By period:                     │
    │ • Day consumption              │
    │ • Night consumption            │
    │ • Holiday consumption          │
    └────────┬───────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ Export  │      │ Export  │
│  PDF    │      │  CSV    │
│         │      │         │
│• Title  │      │• Headers│
│• Summary│      │• Rows   │
│• Tables │      │• All    │
│• Charts │      │  data   │
└─────────┘      └─────────┘
```

## System Monitoring Dashboard

```
┌────────────────────────────────────────────────────────────┐
│                    ENERGY MONITORING DASHBOARD              │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Statistics (6 Cards)                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │🔌Total  │ │⚡Energy │ │⚠️Alerts │ │🎫Tickets│         │
│  │Devices  │ │Today    │ │Active   │ │Open     │         │
│  │   5     │ │145.67kWh│ │   3     │ │   2     │         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
│  ┌─────────┐ ┌─────────┐                                  │
│  │🌡️Temp  │ │💧Humidity│                                  │
│  │Avg      │ │Avg      │                                  │
│  │27.8°C   │ │64.3%    │                                  │
│  └─────────┘ └─────────┘                                  │
│                                                             │
│  📈 Charts                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────┐ │
│  │ Power Consumption (24h)     │ │ Consumption Split   │ │
│  │                             │ │                     │ │
│  │     /\      /\              │ │   ╱─────╲          │ │
│  │    /  \    /  \    /\       │ │  │ Day   │50%      │ │
│  │   /    \  /    \  /  \      │ │  │ Night │30%      │ │
│  │  /      \/      \/    \     │ │  │Holiday│20%      │ │
│  │ /                      \    │ │   ╲─────╱          │ │
│  └─────────────────────────────┘ └─────────────────────┘ │
│                                                             │
│  📋 Latest Readings Table                                  │
│  ┌──────────┬────────┬────────┬───────┬──────┬────────┐  │
│  │Device ID │Voltage │Current │Power  │Temp  │Humidity│  │
│  ├──────────┼────────┼────────┼───────┼──────┼────────┤  │
│  │EMeter-001│230.5 V │25.3 A  │5831 W │28.7°C│64.2%   │  │
│  │EMeter-002│229.8 V │18.9 A  │4344 W │27.1°C│62.8%   │  │
│  │...       │...     │...     │...    │...   │...     │  │
│  └──────────┴────────┴────────┴───────┴──────┴────────┘  │
│                                                             │
│  🚨 Active Alerts                                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 🔴 CRITICAL │ EMeter-001 │ 2024-01-15 14:35:00      │ │
│  │ Temperature exceeded threshold (48.5°C > 45°C)       │ │
│  │ [Acknowledge] [Resolve]                              │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Quick Reference Commands

```bash
# Start Backend
cd backend
source venv/bin/activate
python manage.py runserver

# Start Frontend
cd frontend
npm start

# Start Simulator
cd iot_simulator
python simulator.py

# Access Points
Dashboard:    http://localhost:3000
Admin Panel:  http://localhost:8000/admin
API:          http://localhost:8000/api/
```

## Color Coding

```
Status Colors:
🟢 Active/Resolved   - Green (#10b981)
🔴 Critical          - Red   (#dc2626)
🟠 Warning/Pending   - Orange(#f59e0b)
🔵 Info              - Blue  (#3b82f6)
⚫ Inactive          - Gray  (#6b7280)

Severity Levels:
🔴 Critical  - deviation > 50%
🟠 Warning   - deviation > 20%
🔵 Info      - deviation ≤ 20%

Period Types:
☀️  Day      - 06:00 - 18:00
🌙 Night    - 18:00 - 06:00
🎉 Holiday  - Weekends
```

---

**This visual guide provides an at-a-glance understanding of the system architecture and workflows.**
