<p align="center">
  <img src="https://img.shields.io/badge/🌍-Ecoverse_360-16b364?style=for-the-badge&labelColor=084c2e" alt="Ecoverse 360" />
</p>

<h1 align="center">Ecoverse 360</h1>
<h3 align="center">The Sustainability Operating System — From Campuses to Cities</h3>

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
  <b>IoT Environmental Sensing · Digital Twin Simulation · ML Predictive Analytics · Gamified Engagement · Carbon Credit Ecosystem</b><br/>
  <sub>"Eco-preneurship for a Sustainable Future" — Making sustainability measurable, actionable, and rewarding.</sub>
</p>

---

## 🎯 What We're Building

**Ecoverse 360** is a unified Sustainability Operating System that makes environmental impact **visible**, **predictable**, and **rewarding** at every scale — starting from educational institutions and expanding to homes, government infrastructure, and private enterprises.

We connect real-world IoT sensor networks with an intelligent Digital Twin engine, machine learning forecasting, and a gamified carbon credit ecosystem to transform how organizations measure, manage, and incentivize sustainability.

### The Problem We're Solving

| Challenge | Scale | Impact |
|-----------|-------|--------|
| **No real-time environmental visibility** | Institutions produce tonnes of CO₂/day with zero tracking | Reactive decisions, wasted resources |
| **Waste mismanagement** | 40% of collected waste is misclassified; bins overflow before collection | Contamination, health risks, inefficiency |
| **Air & water quality blind spots** | Pollution and water contamination go undetected for hours/days | Health emergencies, compliance failures |
| **Energy waste in buildings** | HVAC/lighting runs regardless of occupancy or weather | 30-40% unnecessary energy consumption |
| **Thermal energy lost** | AC units & exhaust systems dump waste heat into atmosphere | Recoverable energy wasted, higher costs |
| **Zero engagement incentive** | Less than 5% of people actively participate in green programs | No behaviour change, no collective impact |
| **Individual eco-actions are invisible** | Walking, recycling, carpooling, planting — none of it is tracked or valued | No motivation to continue, no aggregate impact |

### Our Solution

Ecoverse 360 addresses all these problems through a **layered, modular platform**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ECOVERSE 360                                │
│                                                                     │
│  🔌 IoT Layer      → 200+ sensors (air, water, waste, farm, energy)│
│  📡 Ingestion      → MQTT real-time data pipeline                  │
│  💾 Storage        → PostgreSQL + Redis + time-series              │
│  🧠 Intelligence   → Digital Twin + 4 ML models + Carbon Engine    │
│  📊 Application    → Dashboard + REST API + WebSocket              │
│  🏆 Incentive      → EcoPoints + Carbon Credits + Challenges       │
│                                                                     │
│  Deployment scales: Campus → Home → City → Enterprise              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏗 System Architecture

Six-layer modular design built for horizontal scaling across deployment environments:

### Layer 1 — Physical / IoT Sensing
- **Smart Waste Bins** — HC-SR04 ultrasonic fill sensing + HX711 load cell weight measurement
- **Air Quality Monitors** — MQ135 gas sensor + PMS5003 laser particulate + DHT22 (temp/humidity)
- **Water Quality Probes** — TDS (total dissolved solids) + pH sensor + DS18B20 thermometer
- **Vertical Farm Nodes** — Soil moisture + BH1750 light + soil pH + auto-irrigation relay
- **Energy Harvesting Tiles** — Piezoelectric step sensing + energy estimation
- **Precision Farming Edge** — ESP32-S3 with DHT22 + LDR + capacitive soil moisture (3-layer fog architecture — **already built & tested**: [S6-MINI-PROJECT](https://github.com/Am4l-babu/S6-MINI-PROJECT))

### Layer 2 — Data Ingestion
- **MQTT Broker** (Eclipse Mosquitto) — real-time pub/sub IoT message bus
- **Fog Gateway** — local MQTT processing, emergency auto-control, offline buffering (Redis hot + SQLite cold)
- REST batch endpoint for historical data backfill

### Layer 3 — Storage & Persistence
- **PostgreSQL 16** — 18+ tables with UUID PKs, JSONB metadata, materialized views, triggers
- **Redis 7** — Sub-ms caching, session store, real-time pub/sub
- **SQLite** — Fog-layer cold buffer for offline resilience

### Layer 4 — Intelligence Engine
- **Digital Twin** — Real-time campus state aggregation + physics-based simulation (water balance, evapotranspiration modelling) + what-if scenario engine
- **ML Prediction** — 4 trained models (waste overflow, AQI forecast, energy demand, crop yield)
- **Carbon Calculator** — Multi-factor footprint estimation (transport, food, electricity, housing)
- **Occupancy-Aware Optimization** — AI-driven HVAC/lighting adjustment based on real-time occupancy and weather data (planned)
- **Thermal Recovery Intelligence** — Waste heat capture scheduling from AC/exhaust systems (planned)

### Layer 5 — Application
- **FastAPI Backend** — Async REST API (25+ endpoints) with JWT auth, RBAC, Swagger docs
- **Next.js Dashboard** — Server-rendered real-time visualization with Tailwind CSS and Recharts
- **WebSocket Feeds** — Live sensor data push to frontend (in progress)

### Layer 6 — Incentive & Carbon Economy
- **EcoPoints Reward Engine** — 17 tracked activities, 9 progression levels, streak multipliers
- **Carbon Credit Aggregation** — Individual eco-actions converted to measurable, verified carbon credits
- **Community Challenges** — Time-bound sustainability drives with bonus rewards
- **Leaderboards & Marketplace** — Competitive engagement + point redemption

```
    ┌──────────────────────────────────────────────────────────┐
    │                    Frontend (Next.js)                     │
    │   Landing • Dashboard • Digital Twin • Leaderboard       │
    ├──────────────────────────────────────────────────────────┤
    │                    Backend (FastAPI)                      │
    │   Auth • Sensors • EcoPoints • Dashboard • Twin • Users  │
    ├───────────┬──────────────┬──────────────┬────────────────┤
    │  Digital  │     ML       │   Carbon     │    MQTT + Fog  │
    │  Twin     │  Predictor   │   Engine     │   Gateway      │
    ├───────────┴──────────────┴──────────────┴────────────────┤
    │         PostgreSQL  •  Redis  •  SQLite  •  Mosquitto    │
    ├──────────────────────────────────────────────────────────┤
    │         ESP32/ESP8266 IoT Sensor Network                 │
    │   Bins • Air • Water • Farm • Energy • Precision Agri    │
    └──────────────────────────────────────────────────────────┘
```

---

## ⚙ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python 3.12, FastAPI 0.115 | Fastest async Python framework, auto-generates API docs |
| **ORM** | SQLAlchemy 2.0 (async) | Mature async ORM with relationship mapping |
| **Auth** | python-jose (JWT), bcrypt | Stateless token auth + industry-standard password hashing |
| **Database** | PostgreSQL 16, asyncpg | ACID-compliant, JSONB flex columns, materialized views |
| **Cache** | Redis 7 | Sub-ms caching, pub/sub, session management |
| **IoT Bus** | Eclipse Mosquitto (MQTT) | Lightweight pub/sub optimized for constrained devices |
| **Fog Layer** | Python + Redis + SQLite | Offline resilience, emergency auto-control, cloud sync |
| **ML** | scikit-learn, pandas, numpy | Production-grade prediction models |
| **Frontend** | Next.js 14, React 18, Tailwind CSS 3.4 | SSR dashboard with utility-first styling |
| **Charts** | Recharts | Composable React-native charting |
| **State** | Zustand 5 | Minimal, TypeScript-first state management |
| **IoT Hardware** | ESP32, ESP32-S3, ESP8266 | Dual-core WiFi MCUs with ADC, I2C, deep sleep |
| **Sensors** | HC-SR04, HX711, PMS5003, MQ135, DHT22, BH1750, DS18B20, TDS, pH, Piezo | Full environmental sensing suite |
| **Containers** | Docker, Docker Compose | One-command 5-service orchestration |

---

## ✨ Key Features

### 🌬 Environmental Monitoring
- EPA-standard Air Quality Index from PM2.5/PM10 + CO₂ estimation
- Water quality classification (Excellent → Unsafe) via TDS, pH, temperature
- Multi-zone coverage with configurable alert thresholds
- Micro-zone environmental profiling for localized interventions

### 🗑 Smart Waste Management
- Ultrasonic fill-level + load cell weight per bin
- ML-powered overflow prediction (hours until full)
- LED status indicators (green/yellow/red) on physical bins

### 🌱 Precision Agriculture & Smart Farming
- Soil moisture, pH, light intensity, temperature monitoring
- Physics-based Digital Twin with water balance & evapotranspiration modelling
- Automated irrigation when moisture drops below threshold
- Crop yield prediction using Random Forest
- **Already operational**: 3-layer Edge→Fog→Cloud precision farming system ([S6-MINI-PROJECT](https://github.com/Am4l-babu/S6-MINI-PROJECT))

### ⚡ Energy Intelligence
- Piezoelectric tile step counting + energy harvesting estimation
- Building occupancy-aware HVAC/lighting optimization (planned)
- Waste heat recovery intelligence from AC/exhaust (planned)
- Solar panel energy projection in Digital Twin simulator

### 🏙 Digital Twin Engine
- Real-time campus state from all sensors → unified health snapshot
- What-if simulator: project impact of solar panels, carpooling, trees, recycling
- Zone health scoring (AQI 30%, water 20%, waste 25%, noise 15%, energy 10%)
- Physics simulation: water balance model + Penman-Monteith evapotranspiration
- Auto-generated alerts when thresholds are breached

### 🤖 Machine Learning
| Model | Algorithm | Output |
|-------|-----------|--------|
| Waste Overflow | Gradient Boosting | Hours until bin is full |
| AQI Forecast | Random Forest | Next-hour Air Quality Index |
| Energy Demand | Gradient Boosting | kWh consumption prediction |
| Crop Yield | Random Forest | Estimated kg yield |
| Carbon Footprint | Rule-based | kg CO₂/month per person |

### 🏆 EcoPoints & Carbon Credit System
- **17 rewarded activities** — recycling (10 pts), carpooling (15 pts), tree planting (30 pts), sensor deployment (50 pts), and more
- **9 progression levels** — Seedling → Planetary Guardian (0 → 100,000 pts)
- **Streak bonuses** — 7-day (1.2×), 30-day (1.5×), 100-day (2.0×) multipliers
- **Carbon credit aggregation** — individual eco-actions convert to measurable carbon credits that can be verified and traded
- **Community challenges** with bonus point rewards
- **Marketplace** for point redemption on sustainable goods

### 🔐 Security
- JWT authentication (HS256) with configurable expiry
- bcrypt password hashing with auto-salt
- RBAC: student, faculty, admin, super_admin
- Protected routes with dependency-injected role guards

---

## 🗺 Implementation Rollout Plan

Ecoverse 360 is designed for **phased geographic scaling** — starting small and expanding outward:

### Phase 1 — Educational Institutions (Colleges, Schools, Universities) 🟢 Active
> *"Start where awareness begins"*

| Target | Deployment | Key Modules |
|--------|-----------|-------------|
| College campuses | IoT sensors across zones | Air, water, waste, farm monitoring |
| School compounds | Simplified sensor kit | Smart bins, air quality, EcoPoints |
| University labs | Research integration | Digital Twin, ML models, data API |

**Value**: Students learn sustainability through **real data + gamified engagement**. Institutions get measurable ESG metrics. Research departments get an open-source living lab.

### Phase 2 — Residential Communities (Homes, Apartments, Societies) 🔵 Next
> *"Bring sustainability into daily life"*

| Target | Deployment | Key Modules |
|--------|-----------|-------------|
| Smart homes | Room-level sensors | Energy, air quality, water monitoring |
| Apartments | Common-area bins, rooftop farms | Waste management, food production |
| Gated communities | Community-wide dashboard | Carbon tracking, shared leaderboards |

**Value**: Households track their carbon footprint, earn credits for green habits, and compete within their community. Waste heat recovery from AC/exhaust systems reduces energy bills.

### Phase 3 — Government & Public Infrastructure 🟡 Planned
> *"Data-driven governance for cleaner cities"*

| Target | Deployment | Key Modules |
|--------|-----------|-------------|
| Municipal buildings | Building-level monitoring | Energy optimization, occupancy-aware HVAC |
| Public parks & gardens | Environmental sensing + smart irrigation | Micro-zone climate management |
| Transport hubs | Air quality + energy tiles | Foot traffic energy harvesting, pollution hotspot mapping |

**Value**: Real-time environmental dashboards for policy decisions. Automated ESG compliance reporting. Citizen engagement through public EcoPoints.

### Phase 4 — Private Sector (Offices, Factories, Industrial Parks) 🟠 Vision
> *"Enterprise sustainability made measurable"*

| Target | Deployment | Key Modules |
|--------|-----------|-------------|
| Corporate offices | Smart building management | Occupancy HVAC, waste bins, carbon tracking |
| Factories | Emissions monitoring + waste heat recovery | Regulatory compliance, heat-to-energy conversion |
| Industrial parks | Multi-facility federation | Cross-facility benchmarking, aggregated carbon credits |

**Value**: Enterprises get automated carbon accounting, verified credits for offset trading, regulatory compliance dashboards, and bottom-line cost savings from energy optimization.

---

## ✅ Current Status

### What's Already Built & Working

| Component | Completion | Details |
|-----------|:----------:|---------|
| Database Schema | 100% | 18+ tables, triggers, indexes, materialized views |
| Backend API | 100% | 6 route modules, 25+ endpoints, JWT + RBAC |
| ORM Models | 100% | 22 SQLAlchemy models with relationships |
| Digital Twin Engine | 100% | State aggregator + what-if simulator + alerts |
| ML Models | 100% | 4 trained models + carbon footprint calculator |
| EcoPoints Engine | 100% | 17 activities, 9 levels, streak bonuses |
| MQTT IoT Pipeline | 100% | 4 topic handlers, pub/sub, auto-reconnect |
| IoT Firmware (5 types) | 100% | ESP32/ESP8266 production-ready sketches |
| Docker Infrastructure | 100% | 5-service Compose stack with health checks |
| Documentation | 100% | README, architecture, API docs, deployment guide |
| **Precision Farming DT** | **100%** | **3-layer Edge→Fog→Cloud system — live & tested** ([repo](https://github.com/Am4l-babu/S6-MINI-PROJECT)) |
| Frontend (Next.js) | 40% | Landing page, dashboard shell, key components |
| Testing | 0% | Planned (pytest + React Testing Library) |

### Precision Farming Digital Twin — Already Operational

Our **Plant Digital Twin** system ([github.com/Am4l-babu/S6-MINI-PROJECT](https://github.com/Am4l-babu/S6-MINI-PROJECT)) is a fully working 3-layer IoT system that demonstrates the core concepts of Ecoverse 360 at micro-farm scale:

**Architecture:**
```
ESP32-S3 (Edge)  →  Fog Gateway (Laptop/RPi)  →  Cloud Backend + Dashboard
  DHT22              Mosquitto MQTT Broker          FastAPI REST API
  LDR                Redis hot buffer               SQLite storage
  Soil Moisture      SQLite cold buffer             Digital Twin engine
                     Emergency auto-control         Next.js dashboard
                     Cloud sync service             WebSocket live feed
```

**Features already working:**
- Real-time sensor data collection (temperature, humidity, light, soil moisture) every 10 seconds
- Physics-based Digital Twin with water balance model & Penman-Monteith evapotranspiration
- Irrigation recommendations (URGENT / MONITOR / HEALTHY) based on soil state
- Emergency auto-control: auto-irrigation when soil < 30%, heat protection when temp > 35°C
- Fog-layer offline resilience — buffers data locally when cloud is unreachable
- Next.js real-time dashboard with historical charts
- What-if scenario simulation via API
- Docker Compose deployment (5+ services)
- Sensor calibration UI

---

## 🔮 Future Upgrades

### Near-Term
- Complete remaining dashboard pages (sensors, carbon, admin views)
- Real-time WebSocket feeds from MQTT → frontend
- Prophet time-series forecasting for long-range predictions
- pytest + React Testing Library coverage
- GitHub Actions CI/CD pipeline

### Medium-Term
- Three.js 3D interactive Digital Twin visualization
- Progressive Web App (PWA) with push notifications
- Computer vision waste classification (YOLOv8 + ESP32-CAM)
- Drone-based aerial environmental surveying for wider coverage
- Carpooling matching algorithm with route optimization
- Waste heat capture system from HVAC/exhaust units
- Building energy management with occupancy-aware optimization
- Social feed with activity timeline and community interaction

### Long-Term Vision
- Multi-campus/multi-site federation with city-level aggregation
- Blockchain-verified carbon credit trading ecosystem
- Augmented Reality sustainability overlay for physical spaces
- Satellite imagery integration (NDVI) for vegetation health monitoring
- Voice assistant integration (Alexa/Google) for eco-queries
- Automated ESG report generation (PDF export)
- OAuth2 social login (Google, GitHub SSO)
- Micro-zone environmental sculpting — AI-directed interventions at block/street level

---

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/Am4l-babu/ECOVERSE-360.git
cd ECOVERSE-360
cp backend/.env.example backend/.env
docker compose up -d

# Access:
#   API + Swagger UI  →  http://localhost:8000/docs
#   Frontend          →  http://localhost:3000
#   MQTT Broker       →  localhost:1883
```

### Manual Setup
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Database
psql -U ecoverse -d ecoverse_db -f database/schema.sql
psql -U ecoverse -d ecoverse_db -f database/seed_data.sql
```

### Precision Farm (Already Live)
```bash
git clone https://github.com/Am4l-babu/S6-MINI-PROJECT.git
cd S6-MINI-PROJECT
docker-compose up --build
# Dashboard: http://localhost:3000  |  API: http://localhost:8000/docs
```

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/v1` — Full interactive docs at `/docs` (Swagger UI)

| Group | Endpoints | Key Routes |
|-------|:---------:|------------|
| **Auth** | 3 | `POST /auth/register` · `POST /auth/login` · `GET /auth/me` |
| **Sensors** | 5 | `GET /sensors` · `POST /sensors/{id}/data` · `POST /sensors/batch` |
| **EcoPoints** | 6 | `POST /ecopoints/earn` · `GET /ecopoints/balance` · `GET /ecopoints/leaderboard` |
| **Dashboard** | 7 | `GET /dashboard/stats` · `GET /dashboard/trends/{metric}` · `GET /dashboard/zones` |
| **Digital Twin** | 5 | `GET /digital-twin/state` · `POST /digital-twin/simulate` · `GET /digital-twin/alerts` |
| **Users** | 4 | `GET /users` · `PATCH /users/{id}/deactivate` (admin only) |

---

## 📁 Repository Structure

```
ecoverse_360/
├── backend/                    # FastAPI async REST API
│   ├── app/
│   │   ├── api/                # 6 route modules (auth, sensors, ecopoints, dashboard, twin, users)
│   │   ├── core/               # Config, database engine, JWT/RBAC security
│   │   ├── models/             # 22 SQLAlchemy ORM models
│   │   ├── schemas/            # ~50 Pydantic request/response schemas
│   │   ├── services/           # MQTT client + topic handlers
│   │   ├── digital_twin/       # State aggregator + what-if simulator
│   │   ├── ml/                 # 4 ML models + carbon calculator
│   │   ├── reward_engine/      # EcoPoints: points, levels, streaks
│   │   └── main.py
│   └── Dockerfile
├── frontend/                   # Next.js 14 dashboard
│   └── src/
│       ├── app/                # Landing page + dashboard views
│       ├── components/         # StatCard, EcoChart, Sidebar, Leaderboard
│       └── lib/                # Axios API client + Zustand stores
├── hardware/                   # IoT firmware (5 device types)
│   ├── smart-bin/              # ESP8266 — ultrasonic + load cell
│   ├── air-monitor/            # ESP32 — MQ135 + PMS5003 + DHT22
│   ├── water-monitor/          # ESP32 — TDS + pH + DS18B20
│   ├── vertical-farm/          # ESP32 — soil + light + auto-irrigation
│   └── energy-tiles/           # ESP8266 — piezoelectric + step counter
├── database/
│   ├── schema.sql              # 18+ tables, triggers, materialized views
│   └── seed_data.sql           # Demo data
├── docker-compose.yml          # 5-service orchestration
├── docs/                       # Architecture, API docs, deployment guide
└── scripts/                    # Utility & presentation scripts
```

**Related Repository:**  
[**S6-MINI-PROJECT**](https://github.com/Am4l-babu/S6-MINI-PROJECT) — Precision Farming Digital Twin (3-layer Edge→Fog→Cloud, fully operational)

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| Total Files | 67+ |
| Lines of Code | 9,400+ |
| API Endpoints | 25+ |
| Database Tables | 18+ |
| ORM Models | 22 |
| ML Models | 4 trained + 1 rule-based |
| IoT Device Types | 6 (5 Ecoverse + 1 Precision Farm) |
| EcoPoint Activities | 17 |
| Gamification Levels | 9 |
| Docker Services | 5 (main) + 5 (plant DT) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with 💚 for a sustainable future</b><br/>
  <sub>Ecoverse 360 — Because every space can be a sustainable ecosystem.</sub><br/><br/>
  <a href="https://github.com/Am4l-babu/ECOVERSE-360">Main Repository</a> · 
  <a href="https://github.com/Am4l-babu/S6-MINI-PROJECT">Plant Digital Twin</a>
</p>
