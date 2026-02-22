<p align="center">
  <img src="https://img.shields.io/badge/🌍-Ecoverse_360-16b364?style=for-the-badge&labelColor=084c2e" alt="Ecoverse 360" />
</p>

<h1 align="center">Ecoverse 360</h1>
<h3 align="center">Sustainability Operating System &nbsp;|&nbsp; Campuses → Cities</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169e1?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/MQTT-Mosquitto-3c5280?logo=eclipse-mosquitto&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/ESP32-IoT-e7352c?logo=espressif&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

<p align="center">
  <b>Real-time IoT sensing · Digital Twin simulation · ML predictions · Gamified engagement</b><br/>
  <sub>One platform to make sustainability measurable, actionable, and rewarding.</sub>
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Hardware Setup](#-hardware-setup)
- [ML Models](#-ml-models)
- [EcoPoints System](#-ecopoints-system)
- [Digital Twin](#-digital-twin)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌍 Overview

**Ecoverse 360** is a full-stack sustainability operating system designed to transform campuses into intelligent, eco-conscious ecosystems — and scale to entire cities.

It connects **200+ IoT sensors** (air quality, water quality, smart waste bins, vertical farms, energy-harvesting tiles) through an MQTT data pipeline into a **Digital Twin** that mirrors the campus in real time. **Machine learning models** forecast waste overflow, AQI, energy demand, and crop yields. A **gamification engine** rewards students with EcoPoints for sustainable actions — recycling, carpooling, tree planting, workshop attendance — driving behavioural change through leaderboards, streaks, and challenges.

### The Problem

| Challenge | Impact |
|-----------|--------|
| Campuses produce **~2 tonnes of CO₂/day** | No real-time visibility |
| 40% of collected waste is **misclassified** | Overflowing bins, contamination |
| Water & air quality issues go **undetected** | Health risks, resource waste |
| Student engagement in sustainability is **< 5%** | Low participation, no incentive |

### The Solution

```
 ┌─────────────────────────────────────────────────────────┐
 │                   ECOVERSE 360                          │
 │                                                         │
 │   Physical    Data        Storage    Intelligence       │
 │   Layer   →  Ingestion  →  Layer   →   Layer            │
 │  (IoT)      (MQTT)      (Postgres)  (ML + Twin)        │
 │                                         ↓               │
 │                              Application Layer          │
 │                            (Dashboard + API)            │
 │                                    ↓                    │
 │                           Incentive Layer               │
 │                          (EcoPoints + ESG)              │
 └─────────────────────────────────────────────────────────┘
```

---

## 🏗 Architecture

Ecoverse 360 follows a **6-layer modular architecture** designed for horizontal scalability:

### Layer 1 — Physical / IoT Layer
ESP32/ESP8266 microcontrollers with real sensors:
- **Smart Bins** — HC-SR04 ultrasonic (fill level) + HX711 load cell (weight)
- **Air Quality Monitors** — MQ135 (CO₂) + PMS5003 (PM2.5/PM10) + DHT22 (temp/humidity)
- **Water Quality Probes** — TDS sensor + pH sensor + DS18B20 (temperature)
- **Vertical Farm Nodes** — Soil moisture + BH1750 (light) + soil pH + auto-irrigation
- **Energy Tiles** — Piezoelectric sensors with step counting + energy harvesting

### Layer 2 — Data Ingestion
- **MQTT Broker** (Eclipse Mosquitto) — pub/sub message bus
- Topic structure: `ecoverse/sensors/+/data`, `ecoverse/bins/+/update`, `ecoverse/farm/+/data`, `ecoverse/energy/tiles/+`
- Batch REST endpoint for sensor data backfill

### Layer 3 — Storage
- **PostgreSQL 16** — Relational store with 18+ tables, materialized views, triggers
- **Redis 7** — Caching, session store, real-time pub/sub
- Async I/O via `asyncpg` + SQLAlchemy 2.0 async engine

### Layer 4 — Intelligence
- **ML Prediction Service** — 4 trained models (waste overflow, AQI, energy, crop yield)
- **Digital Twin Engine** — Real-time state aggregation + what-if scenario simulator
- **Carbon Calculator** — Multi-factor footprint estimation (transport, food, electricity)

### Layer 5 — Application
- **FastAPI Backend** — Async REST API with JWT auth, RBAC, OpenAPI/Swagger docs
- **Next.js Frontend** — Server-rendered dashboard with Tailwind CSS, Recharts, Zustand

### Layer 6 — Incentive & Governance
- **EcoPoints Reward Engine** — 17 activity types, 9 levels, streak bonuses, marketplace
- **ESG Reporting** — Automated campus sustainability reports

```
    ┌──────────────────────────────────────────────────────────┐
    │                    Frontend (Next.js)                     │
    │   Landing • Dashboard • Digital Twin • Leaderboard       │
    ├──────────────────────────────────────────────────────────┤
    │                    Backend (FastAPI)                      │
    │   Auth • Sensors • EcoPoints • Dashboard • Twin • Users  │
    ├───────────┬──────────────┬──────────────┬────────────────┤
    │  Digital  │     ML       │   Reward     │    MQTT        │
    │  Twin     │  Predictor   │   Engine     │   Service      │
    ├───────────┴──────────────┴──────────────┴────────────────┤
    │              PostgreSQL  •  Redis  •  Mosquitto          │
    ├──────────────────────────────────────────────────────────┤
    │         ESP32/ESP8266 IoT Sensor Network                 │
    │   Smart Bins • Air • Water • Farm • Energy Tiles         │
    └──────────────────────────────────────────────────────────┘
```

---

## ⚙ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.12, FastAPI 0.115 | Async REST API |
| **ORM** | SQLAlchemy 2.0 (async) | Database models & queries |
| **Auth** | python-jose (JWT), bcrypt | Token auth, password hashing, RBAC |
| **Database** | PostgreSQL 16, asyncpg | Primary relational store |
| **Cache** | Redis 7 | Caching, sessions, real-time |
| **Message Bus** | Eclipse Mosquitto (MQTT) | IoT data pub/sub |
| **ML** | scikit-learn, pandas, numpy | Prediction models |
| **Frontend** | Next.js 14, React 18 | Server-rendered UI |
| **Styling** | Tailwind CSS 3.4 | Utility-first CSS |
| **Charts** | Recharts | Data visualization |
| **State** | Zustand 5 | Client state management |
| **Animations** | Framer Motion | UI transitions |
| **IoT** | ESP32, ESP8266, Arduino | Sensor nodes |
| **Protocols** | MQTT, HTTP/REST, WebSocket | Communication |
| **Containers** | Docker, Docker Compose | Orchestration |

---

## 📁 Repository Structure

```
ecoverse_360/
├── backend/
│   ├── app/
│   │   ├── api/                    # REST API route handlers
│   │   │   ├── auth.py             # Register, login, profile
│   │   │   ├── sensors.py          # Sensor CRUD, data ingestion
│   │   │   ├── ecopoints.py        # Award, earn, spend, leaderboard
│   │   │   ├── dashboard.py        # Stats, zones, trends, feeds
│   │   │   ├── digital_twin.py     # Twin state, simulate, alerts
│   │   │   └── users.py            # User management (admin)
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings (env vars)
│   │   │   ├── database.py         # Async SQLAlchemy engine
│   │   │   └── security.py         # JWT, passwords, RBAC
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── sensor.py
│   │   │   ├── ecopoints.py
│   │   │   ├── environmental.py
│   │   │   └── entities.py         # All other domain models
│   │   ├── schemas/                # Pydantic request/response
│   │   ├── services/
│   │   │   └── mqtt_service.py     # MQTT client & handlers
│   │   ├── digital_twin/
│   │   │   ├── simulator.py        # What-if scenario engine
│   │   │   └── aggregator.py       # Real-time state aggregation
│   │   ├── ml/
│   │   │   └── predictor.py        # 4 ML models + carbon calc
│   │   ├── reward_engine/
│   │   │   └── engine.py           # Points, levels, streaks
│   │   ├── utils/
│   │   └── main.py                 # FastAPI app entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Landing page
│   │   │   └── dashboard/
│   │   │       ├── layout.tsx      # Dashboard shell + sidebar
│   │   │       └── page.tsx        # Overview with charts
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── EcoChart.tsx
│   │   │   └── LeaderboardTable.tsx
│   │   └── lib/
│   │       ├── api.ts              # Axios API client
│   │       └── store.ts            # Zustand state stores
│   ├── Dockerfile
│   ├── tailwind.config.js
│   └── package.json
├── hardware/
│   ├── smart-bin/
│   │   └── smart_bin.ino           # ESP8266 + ultrasonic + load cell
│   ├── air-monitor/
│   │   └── air_monitor.ino         # ESP32 + MQ135 + PMS5003 + DHT22
│   ├── water-monitor/
│   │   └── water_monitor.ino       # ESP32 + TDS + pH + DS18B20
│   ├── vertical-farm/
│   │   └── farm_sensor.ino         # ESP32 + soil + light + auto-water
│   └── energy-tiles/
│       └── energy_tile.ino         # ESP8266 + piezo + step counter
├── database/
│   ├── schema.sql                  # Full PostgreSQL schema (18+ tables)
│   └── seed_data.sql               # Demo data
├── docker/
│   └── mosquitto/
│       └── mosquitto.conf
├── docs/
│   ├── architecture.md
│   ├── api-docs.md
│   └── deployment.md
├── scripts/
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## ✨ Features

### 🌬 Environmental Monitoring
- Real-time **Air Quality Index** (AQI) with EPA-standard breakpoint calculations
- **Water quality** tracking — TDS, pH, temperature with safety classifications
- Multi-zone monitoring with automated alert thresholds
- Historical trends and anomaly detection

### 🗑 Smart Waste Management
- Ultrasonic fill-level detection (0–100%) per bin
- Load cell weight measurement for waste categorization
- **ML-powered overflow prediction** — alerts before bins are full
- Recycling rate tracking and contamination detection

### 🌱 Vertical Farm Intelligence
- Soil moisture, pH, light intensity, air temp/humidity monitoring
- **Automated irrigation** triggered by moisture thresholds
- Crop yield prediction using Random Forest models
- Plant health scoring (0–100) based on environmental conditions

### ⚡ Energy Harvesting
- Piezoelectric tile step counting and energy estimation
- Foot traffic density classification (none → very high)
- Cumulative energy generation tracking
- Peak impact force monitoring

### 🏙 Digital Twin
- Real-time **campus state aggregation** from all sensor feeds
- **What-if simulation engine** — model the impact of:
  - Adding solar panels, carpoolers, recycling bins
  - Planting trees, deploying sensors
  - Changing student behaviours
- Zone-level health scoring (weighted: AQI 30%, water 20%, waste 25%, noise 15%)
- Automated alert generation (warning → critical thresholds)

### 🤖 Machine Learning
| Model | Algorithm | Input | Output |
|-------|-----------|-------|--------|
| Waste Overflow | Gradient Boosting | Fill rate, weight, time | Hours until full |
| AQI Forecast | Random Forest | PM2.5, CO₂, temp, humidity | Next-hour AQI |
| Energy Demand | Gradient Boosting | Time, occupancy, temp | kWh prediction |
| Crop Yield | Random Forest | Moisture, light, pH, NPK | Estimated kg yield |
| Carbon Footprint | Rule-based | Transport, food, electricity | kg CO₂/month |

### 🏆 EcoPoints Gamification

**17 Activity Types** — from recycling (10 pts) to deploying sensors (50 pts):

| Activity | Points | CO₂ Saved |
|----------|--------|-----------|
| Recycle waste | 10 | 1.8 kg |
| Carpool trip | 15 | 2.3 kg |
| Plant a tree | 30 | 22.0 kg/yr |
| Deploy sensor | 50 | — |
| Attend workshop | 25 | — |
| Use reusable bottle | 5 | 0.5 kg |
| Report food waste | 8 | 1.2 kg |

**9 Levels** — Seedling → Sapling → Green Warrior → Eco Guardian → Nature Keeper → Sustainability Hero → Climate Champion → Ecosystem Architect → Planetary Guardian

**Streak Bonuses** — 7-day streak: 1.2× multiplier → 30-day: 1.5× → 100-day: 2.0×

### 📊 Dashboard
- Live stat cards (AQI, CO₂ saved, waste recycled, energy)
- Interactive time-series charts (Recharts)
- Zone-level breakdowns
- Activity feed
- Leaderboard with rank, level, points, CO₂ saved

### 🔐 Authentication & Authorization
- JWT-based stateless auth
- bcrypt password hashing
- Role-Based Access Control (student, faculty, admin, super_admin)
- Protected routes with role guards

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- Or: Python 3.12+, Node.js 20+, PostgreSQL 16, Redis 7, Mosquitto

### Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/your-org/ecoverse-360.git
cd ecoverse-360

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# 3. Launch everything
docker compose up -d

# 4. Access
#    API:        http://localhost:8000
#    Swagger:    http://localhost:8000/docs
#    Frontend:   http://localhost:3000
#    MQTT:       localhost:1883
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Start PostgreSQL & Redis, then:
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

#### Database
```bash
# Apply schema
psql -U ecoverse -d ecoverse_db -f database/schema.sql

# Load demo data
psql -U ecoverse -d ecoverse_db -f database/seed_data.sql
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `MQTT_BROKER_HOST` | `localhost` | MQTT broker address |
| `MQTT_BROKER_PORT` | `1883` | MQTT broker port |
| `JWT_SECRET_KEY` | — | **Change this!** JWT signing key |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token TTL (24h) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/v1`

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/auth/me` | Current user profile |

### Sensors
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sensors` | List all sensors |
| `POST` | `/sensors` | Register sensor |
| `POST` | `/sensors/{id}/data` | Push reading |
| `POST` | `/sensors/batch` | Batch data ingest |
| `GET` | `/sensors/{id}/stats` | Sensor statistics |

### EcoPoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ecopoints/earn` | Log eco-activity |
| `GET` | `/ecopoints/balance` | User balance & level |
| `GET` | `/ecopoints/history` | Point history |
| `GET` | `/ecopoints/leaderboard` | Top users |
| `POST` | `/ecopoints/spend` | Redeem points |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/stats` | Campus-wide stats |
| `GET` | `/dashboard/zones` | Zone breakdown |
| `GET` | `/dashboard/trends/{metric}` | Time-series data |
| `GET` | `/dashboard/activity-feed` | Recent actions |

### Digital Twin
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/digital-twin/state` | Current twin state |
| `POST` | `/digital-twin/simulate` | Run what-if scenario |
| `GET` | `/digital-twin/zones` | Zone health scores |
| `GET` | `/digital-twin/alerts` | Active alerts |

Full interactive docs: **http://localhost:8000/docs** (Swagger UI)

---

## 🔧 Hardware Setup

### Smart Bin (ESP8266)
```
Components: ESP8266 NodeMCU, HC-SR04, HX711 + Load Cell
Wiring:
  HC-SR04  → TRIG=D1, ECHO=D2
  HX711    → DOUT=D5, SCK=D6
  LED      → D7 (green), D8 (red)
Power: 5V USB or 3.7V Li-Po + regulator
```

### Air Monitor (ESP32)
```
Components: ESP32, MQ135, PMS5003, DHT22
Wiring:
  MQ135    → Analog pin 34
  PMS5003  → Serial2 (RX=16, TX=17)
  DHT22    → GPIO 4
Note: MQ135 requires 24-48h burn-in for accurate readings
```

### Water Monitor (ESP32)
```
Components: ESP32, TDS sensor, pH sensor, DS18B20
Wiring:
  TDS      → Analog pin 34
  pH       → Analog pin 35
  DS18B20  → GPIO 4 (with 4.7kΩ pull-up)
Calibration: pH sensor needs 2-point calibration (pH 4.0 & 7.0)
```

### Vertical Farm (ESP32)
```
Components: ESP32, Soil Moisture, BH1750, DHT22, pH, Relay
Wiring:
  Soil     → Analog pin 34
  pH       → Analog pin 35
  BH1750   → I2C (SDA=21, SCL=22)
  DHT22    → GPIO 4
  Pump     → GPIO 25 via relay module
Auto-waters when soil moisture drops below 30%
```

### Energy Tile (ESP8266)
```
Components: ESP8266, Piezo disc, LED
Wiring:
  Piezo    → A0 (with voltage divider if needed)
  LED      → D1 (step feedback), D4 (status)
Debounce: 200ms between step registrations
```

---

## 🧠 ML Models

### Training & Inference

```python
from app.ml.predictor import SustainabilityPredictor

predictor = SustainabilityPredictor()

# Predict waste overflow
hours = predictor.predict_waste_overflow(
    fill_level=72.5, weight=8.3, fill_rate=2.1,
    hour=14, day_of_week=2
)

# Forecast AQI
aqi = predictor.predict_aqi(
    pm25=35.0, pm10=50.0, co2=420.0,
    temperature=28.5, humidity=65.0
)

# Estimate carbon footprint
footprint = predictor.estimate_carbon_footprint(
    transport_km=15.0, transport_mode="car",
    electricity_kwh=120.0, meals_per_day=3,
    meat_meals_per_week=5
)
```

### Model Persistence
Models are saved to `ml_models/` as pickle files and auto-loaded on startup.

---

## 🏆 EcoPoints System

```python
from app.reward_engine.engine import RewardEngine

engine = RewardEngine()

# Process an activity
result = engine.process_activity(
    activity_type="recycle",
    streak_days=15           # 1.2× bonus (7+ day streak)
)
# → {"base_points": 10, "multiplier": 1.2, "total_points": 12,
#     "co2_saved_kg": 1.8}

# Get user stats
stats = engine.get_user_stats(total_points=3500, streak_days=45)
# → {"level": "Eco Guardian", "next_level": "Nature Keeper",
#     "progress": 0.70, "streak_multiplier": 1.5}
```

### Level Progression

```
Seedling (0) → Sapling (100) → Green Warrior (500) → Eco Guardian (1500)
→ Nature Keeper (5000) → Sustainability Hero (10000) → Climate Champion (25000)
→ Ecosystem Architect (50000) → Planetary Guardian (100000)
```

---

## 🏙 Digital Twin

### What-If Simulation

```json
POST /api/v1/digital-twin/simulate
{
  "scenario_name": "Solar Panel Expansion",
  "parameters": {
    "solar_panels_added": 200,
    "carpoolers_added": 150,
    "recycling_bins_added": 50,
    "trees_planted": 100,
    "vertical_farm_sqm_added": 200
  }
}
```

**Response** — projected savings, percentage improvements, actionable recommendations.

### Health Score

Each campus zone gets a weighted health score:
- Air Quality: **30%**
- Water Quality: **20%**
- Waste Management: **25%**
- Noise Level: **15%**
- Energy Efficiency: **10%**

---

## 🐳 Deployment

### Docker Compose (Recommended)

```bash
docker compose up -d
```

Services launched:
| Service | Port | Container |
|---------|------|-----------|
| Backend API | 8000 | ecoverse-backend |
| Frontend | 3000 | ecoverse-frontend |
| PostgreSQL | 5432 | ecoverse-postgres |
| Redis | 6379 | ecoverse-redis |
| Mosquitto | 1883, 9001 | ecoverse-mosquitto |

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random string
- [ ] Set `CORS_ORIGINS` to your domain
- [ ] Enable Mosquitto authentication (disable `allow_anonymous`)
- [ ] Configure PostgreSQL SSL
- [ ] Set up reverse proxy (Nginx/Caddy) with HTTPS
- [ ] Enable Redis password
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Enable database backups (pg_dump cron)
- [ ] Rate-limit API endpoints

---

## 🗺 Roadmap

### Phase 1 — Foundation ✅
- [x] IoT sensor firmware (5 device types)
- [x] MQTT data pipeline
- [x] PostgreSQL schema (18+ tables)
- [x] FastAPI REST API (6 route modules)
- [x] JWT authentication & RBAC
- [x] EcoPoints reward engine

### Phase 2 — Intelligence 🔄
- [x] Digital Twin state aggregator
- [x] What-if scenario simulator
- [x] ML prediction models (4 types)
- [ ] Prophet time-series forecasting
- [ ] Real-time WebSocket feeds
- [ ] Anomaly detection pipeline

### Phase 3 — Engagement
- [x] Next.js dashboard scaffolding
- [ ] Interactive 3D campus map (Three.js)
- [ ] Mobile PWA with push notifications
- [ ] Social feed & peer challenges
- [ ] Marketplace for EcoPoint redemption
- [ ] Carpooling matching algorithm

### Phase 4 — Scale
- [ ] Multi-campus federation
- [ ] City-level aggregation
- [ ] Blockchain carbon credit verification
- [ ] Computer vision waste classification (YOLOv8)
- [ ] Voice assistant integration (Alexa/Google)
- [ ] AR campus sustainability overlay
- [ ] Satellite imagery integration (NDVI)
- [ ] ESG report auto-generation (PDF)

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m "Add amazing feature"`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Code Style
- **Python** — PEP 8, type hints everywhere, async/await
- **TypeScript** — strict mode, functional components, hooks
- **Arduino** — camelCase functions, UPPER_CASE constants

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built with 💚 for a sustainable future</b><br/>
  <sub>Ecoverse 360 — Because every campus can be an ecosystem.</sub>
</p>
