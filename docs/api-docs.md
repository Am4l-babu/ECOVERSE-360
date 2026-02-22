# API Documentation — Ecoverse 360

> **Base URL**: `http://localhost:8000/api/v1`  
> **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)  
> **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Authentication

All protected endpoints require a **Bearer JWT** in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### POST `/auth/register`

Create a new user account.

**Body:**
```json
{
  "email": "student@campus.edu",
  "username": "eco_warrior",
  "password": "securePassword123",
  "role": "student"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "student@campus.edu",
  "username": "eco_warrior",
  "role": "student",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### POST `/auth/login`

Authenticate and receive a JWT token.

**Body:**
```json
{
  "email": "student@campus.edu",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": { "id": "uuid", "username": "eco_warrior", "role": "student" }
}
```

### GET `/auth/me`

Get current user profile. **Requires auth.**

---

## Sensors

### GET `/sensors`

List all registered sensors. **Requires auth.**

**Query params:** `sensor_type` (optional), `zone` (optional), `status` (optional)

### POST `/sensors`

Register a new sensor. **Requires admin.**

**Body:**
```json
{
  "sensor_type": "air_quality",
  "zone": "Zone A - Library",
  "location": "Library entrance, 2nd floor",
  "model": "PMS5003+MQ135",
  "firmware_version": "1.2.0"
}
```

### POST `/sensors/{sensor_id}/data`

Push a sensor reading. **Requires auth.**

**Body:**
```json
{
  "value": 42.5,
  "unit": "AQI",
  "metadata": { "pm25": 12.3, "pm10": 28.1, "co2": 415 }
}
```

### POST `/sensors/batch`

Batch ingest multiple readings at once.

**Body:**
```json
{
  "readings": [
    { "sensor_id": "uuid", "value": 42.5, "unit": "AQI" },
    { "sensor_id": "uuid", "value": 72.0, "unit": "%" }
  ]
}
```

### GET `/sensors/{sensor_id}/stats?hours=24`

Get min/max/avg/count statistics for a sensor over the given time window.

---

## EcoPoints

### POST `/ecopoints/earn`

Log a sustainability activity and earn points. **Requires auth.**

**Body:**
```json
{
  "activity_type": "recycle",
  "metadata": { "weight_kg": 2.5, "material": "plastic" }
}
```

**Response (200):**
```json
{
  "points_earned": 12,
  "co2_saved_kg": 1.8,
  "streak_multiplier": 1.2,
  "new_balance": 1250,
  "level": "Green Warrior"
}
```

### GET `/ecopoints/balance`

Get current user's balance, level, and streak. **Requires auth.**

### GET `/ecopoints/history?page=1&per_page=20`

Paginated transaction history. **Requires auth.**

### GET `/ecopoints/leaderboard?limit=20`

Top users by total points.

### POST `/ecopoints/spend`

Redeem points for rewards. **Requires auth.**

**Body:**
```json
{
  "points": 100,
  "description": "Campus cafe voucher"
}
```

---

## Dashboard

### GET `/dashboard/stats`

Campus-wide aggregate statistics. **Requires auth.**

**Response:**
```json
{
  "aqi": 42,
  "co2_saved_today_kg": 1230.5,
  "bins_collected_pct": 87,
  "energy_saved_kwh": 340,
  "active_sensors": 156,
  "active_users": 892
}
```

### GET `/dashboard/zones`

Per-zone breakdown of environmental metrics.

### GET `/dashboard/trends/{metric}?days=30`

Time-series data for a given metric. Valid metrics: `aqi`, `co2`, `waste`, `energy`, `water`.

### GET `/dashboard/activity-feed?limit=20`

Recent eco-activities across all users.

### GET `/dashboard/carbon-summary`

Campus carbon emission/reduction summary.

---

## Digital Twin

### GET `/digital-twin/state`

Current aggregated campus state snapshot.

### GET `/digital-twin/zones`

Zone-level health scores and metrics.

### POST `/digital-twin/simulate`

Run a what-if scenario.

**Body:**
```json
{
  "scenario_name": "Green Expansion Q2",
  "parameters": {
    "solar_panels_added": 200,
    "carpoolers_added": 150,
    "trees_planted": 100,
    "recycling_bins_added": 50,
    "vertical_farm_sqm_added": 200
  }
}
```

**Response:**
```json
{
  "scenario_name": "Green Expansion Q2",
  "projections": {
    "carbon_reduction_kg_per_day": 487.2,
    "carbon_reduction_percent": 19.5,
    "water_savings_liters_per_day": 1200,
    "waste_diversion_percent": 35.0,
    "energy_generation_kwh_per_day": 800.0
  },
  "recommendations": [
    "Install 200 solar panels → 800.0 kWh/day generation",
    "Add 150 carpoolers → 345.0 kg CO₂/day reduction"
  ]
}
```

### GET `/digital-twin/alerts`

Active alerts with severity levels (warning, critical).

---

## Users (Admin)

### GET `/users`

List all users. **Requires admin.**

### GET `/users/{user_id}`

Get user details. **Requires admin.**

### PATCH `/users/{user_id}/deactivate`

Deactivate a user account. **Requires admin.**

### GET `/users/{user_id}/stats`

Get user's eco-statistics. **Requires admin.**

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Descriptive error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid JWT |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate email) |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## Rate Limiting

Production deployments should configure rate limiting via reverse proxy:

| Endpoint Group | Suggested Limit |
|---------------|----------------|
| `/auth/login` | 5 req/min |
| `/auth/register` | 3 req/min |
| `/sensors/*/data` | 60 req/min per sensor |
| `/ecopoints/earn` | 10 req/min per user |
| General API | 100 req/min per user |
