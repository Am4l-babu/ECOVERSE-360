# Architecture — Ecoverse 360

## Overview

Ecoverse 360 follows a **6-layer modular architecture** where each layer is independently deployable and horizontally scalable. Data flows upward from physical sensors through ingestion, storage, intelligence, and application layers, while commands and configurations flow downward.

---

## System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         LAYER 6: INCENTIVE                           │
│  EcoPoints Engine · Leaderboard · Challenges · ESG Reports          │
├──────────────────────────────────────────────────────────────────────┤
│                         LAYER 5: APPLICATION                         │
│  Next.js Dashboard · FastAPI REST · Swagger Docs · WebSocket        │
├──────────────┬──────────────┬───────────────┬────────────────────────┤
│  DIGITAL TWIN│   ML ENGINE  │ REWARD ENGINE │    MQTT SERVICE        │
│  Aggregator  │  Predictor   │  Points/Lvls  │  Topic Handlers        │
│  Simulator   │  4 Models    │  Streaks      │  Pub/Sub               │
│              │  Carbon Calc │  9 Levels     │                        │
├──────────────┴──────────────┴───────────────┴────────────────────────┤
│                         LAYER 3: STORAGE                             │
│  PostgreSQL 16 (async) · Redis 7 · File Storage (ML models)         │
│  18+ tables · Materialized Views · Triggers · Indexes                │
├──────────────────────────────────────────────────────────────────────┤
│                         LAYER 2: INGESTION                           │
│  Eclipse Mosquitto MQTT Broker                                       │
│  Topics: ecoverse/sensors/+/data · bins · farm · energy             │
│  REST Batch Endpoint: POST /sensors/batch                            │
├──────────────────────────────────────────────────────────────────────┤
│                         LAYER 1: PHYSICAL / IoT                      │
│  Smart Bins (ESP8266) · Air Monitors (ESP32) · Water Probes (ESP32) │
│  Vertical Farm Nodes (ESP32) · Energy Tiles (ESP8266)                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Backend Module Map

```
app/
├── main.py              ← FastAPI app, lifespan, CORS
├── core/
│   ├── config.py        ← Pydantic Settings (all env vars)
│   ├── database.py      ← Async SQLAlchemy engine, session factory
│   └── security.py      ← JWT, bcrypt, RBAC decorators
├── models/              ← SQLAlchemy ORM (mapped to PostgreSQL)
│   ├── user.py          ← User table
│   ├── sensor.py        ← Sensor, SensorReading
│   ├── ecopoints.py     ← EcoPoint, EcoPointBalance
│   ├── environmental.py ← EnvironmentalData
│   └── entities.py      ← 15+ domain tables
├── schemas/             ← Pydantic v2 request/response models (~50)
├── api/                 ← Route handlers (6 routers)
│   ├── auth.py          ← /auth/*
│   ├── sensors.py       ← /sensors/*
│   ├── ecopoints.py     ← /ecopoints/*
│   ├── dashboard.py     ← /dashboard/*
│   ├── digital_twin.py  ← /digital-twin/*
│   └── users.py         ← /users/*
├── services/
│   └── mqtt_service.py  ← MQTT client, topic handlers
├── digital_twin/
│   ├── aggregator.py    ← Sensor → DigitalTwinState
│   └── simulator.py     ← What-if scenario engine
├── ml/
│   └── predictor.py     ← 4 sklearn models + carbon calc
└── reward_engine/
    └── engine.py        ← Activity → Points → Levels
```

---

## Data Flow

### Sensor → Dashboard (Read Path)

```
ESP32 Sensor
    │
    ▼ MQTT publish (JSON)
Mosquitto Broker
    │
    ▼ paho-mqtt subscriber
MQTTService.handle_sensor_data()
    │
    ├─▶ PostgreSQL (sensor_readings table)
    ├─▶ StateAggregator → DigitalTwinState update
    └─▶ Redis cache invalidation
           │
           ▼
    GET /dashboard/stats  ──▶  Frontend renders
```

### User Action → EcoPoints (Write Path)

```
Student clicks "Log Recycling"
    │
    ▼ POST /ecopoints/earn
Auth middleware (JWT verify)
    │
    ▼
RewardEngine.process_activity("recycle")
    │
    ├─▶ Calculate base points (10)
    ├─▶ Apply streak multiplier (1.2×)
    ├─▶ Calculate CO₂ saved (1.8 kg)
    └─▶ Check level progression
           │
           ▼
    PostgreSQL (eco_points, eco_point_balance tables)
           │
           ▼
    Response: { points: 12, co2_saved: 1.8, level: "Green Warrior" }
```

---

## Database Schema (Key Tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | Accounts & roles | email, role, eco_level, total_points |
| `sensors` | Registered devices | sensor_type, zone, location, status |
| `sensor_readings` | Time-series data | sensor_id, value, unit, timestamp |
| `eco_points` | Transaction log | user_id, points, activity_type, co2_saved |
| `eco_point_balance` | Running balance | user_id, total_earned, total_spent, level |
| `digital_twin_state` | Campus snapshots | zone, health_score, metrics (JSONB) |
| `alerts` | Threshold events | severity, zone, sensor_id, resolved |
| `challenges` | Community events | title, points_reward, start/end dates |
| `carbon_footprints` | User emissions | transport, food, electricity, total |
| `smart_bins` | Bin status | fill_level, weight, last_collected |
| `farm_plots` | Crop tracking | plot_name, crop_type, status |

---

## Security Model

```
Request → CORS Check → JWT Decode → Role Check → Handler
                         │              │
                    decode_token()   require_roles()
                         │              │
                    Extracts user_id   Verifies role ∈ {admin, faculty, ...}
                         │
                    get_current_user() → User from DB
```

- Passwords: **bcrypt** with salt rounds
- Tokens: **HS256 JWT** with configurable TTL
- Roles: `student`, `faculty`, `admin`, `super_admin`
- Each role inherits the permissions of lower roles

---

## Scalability Considerations

| Concern | Strategy |
|---------|----------|
| High sensor throughput | MQTT broker handles 100K+ msg/s; async DB writes |
| Database growth | Materialized views for aggregates; partitioning-ready |
| API concurrency | Async FastAPI + uvicorn workers |
| ML inference latency | Pre-trained models loaded in memory; batch prediction |
| Frontend performance | Next.js SSR + static pre-rendering; Zustand (minimal re-renders) |
| Multi-campus | Database schema supports `zone` isolation; federation-ready |
