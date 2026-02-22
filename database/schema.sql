-- ============================================================================
-- ECOVERSE 360 — Database Schema
-- Sustainability Operating System for Campuses → Cities
-- PostgreSQL 15+
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";          -- spatial data for heatmaps
CREATE EXTENSION IF NOT EXISTS "pg_trgm";          -- fuzzy text search

-- ============================================================================
-- 1. USERS & AUTH
-- ============================================================================

CREATE TYPE user_role AS ENUM ('student', 'admin', 'faculty', 'public', 'iot_node');

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    role            user_role NOT NULL DEFAULT 'student',
    department      VARCHAR(100),
    hostel          VARCHAR(100),
    avatar_url      VARCHAR(500),
    eco_score       FLOAT DEFAULT 0.0,
    carbon_score    FLOAT DEFAULT 0.0,
    water_score     FLOAT DEFAULT 0.0,
    waste_score     FLOAT DEFAULT 0.0,
    energy_score    FLOAT DEFAULT 0.0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department);

-- ============================================================================
-- 2. IoT SENSORS & DEVICES
-- ============================================================================

CREATE TYPE sensor_type AS ENUM (
    'smart_bin', 'air_quality', 'water_quality', 'soil_moisture',
    'temperature', 'humidity', 'energy_tile', 'rain_gauge',
    'traffic_counter', 'noise_level', 'solar_panel', 'water_level',
    'pressure', 'light', 'co2', 'ph', 'tds', 'uv_index'
);

CREATE TYPE sensor_status AS ENUM ('online', 'offline', 'maintenance', 'error');

CREATE TABLE sensors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id       VARCHAR(100) UNIQUE NOT NULL,
    sensor_type     sensor_type NOT NULL,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    location_name   VARCHAR(200),
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    geom            GEOMETRY(Point, 4326),    -- PostGIS point
    building        VARCHAR(100),
    floor           INTEGER,
    status          sensor_status DEFAULT 'offline',
    firmware_ver    VARCHAR(50),
    battery_level   FLOAT,
    last_seen       TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}',
    installed_by    UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sensors_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_sensors_device ON sensors(device_id);
CREATE INDEX idx_sensors_geom ON sensors USING GIST(geom);

-- ============================================================================
-- 3. SENSOR READINGS (Time-Series Data)
-- ============================================================================

CREATE TABLE sensor_readings (
    id              BIGSERIAL PRIMARY KEY,
    sensor_id       UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    value           DOUBLE PRECISION NOT NULL,
    unit            VARCHAR(50) NOT NULL,
    quality         FLOAT DEFAULT 1.0,   -- data quality score 0-1
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_readings_sensor ON sensor_readings(sensor_id);
CREATE INDEX idx_readings_time ON sensor_readings(timestamp DESC);
CREATE INDEX idx_readings_sensor_time ON sensor_readings(sensor_id, timestamp DESC);

-- Partition by month (for production scale)
-- CREATE TABLE sensor_readings_y2026m01 PARTITION OF sensor_readings
--     FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- ============================================================================
-- 4. ENVIRONMENTAL DATA (Aggregated Digital Twin State)
-- ============================================================================

CREATE TABLE environmental_data (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone                VARCHAR(100) NOT NULL,
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Air Quality
    aqi                 FLOAT,
    pm25                FLOAT,
    pm10                FLOAT,
    co2_ppm             FLOAT,
    no2                 FLOAT,
    so2                 FLOAT,
    ozone               FLOAT,
    
    -- Water Quality
    water_ph            FLOAT,
    water_tds           FLOAT,
    water_turbidity     FLOAT,
    water_temperature   FLOAT,
    
    -- Weather
    temperature         FLOAT,
    humidity            FLOAT,
    pressure            FLOAT,
    rainfall_mm         FLOAT,
    wind_speed          FLOAT,
    uv_index            FLOAT,
    
    -- Noise
    noise_db            FLOAT,
    
    -- Energy
    energy_generated_wh FLOAT DEFAULT 0,
    energy_consumed_wh  FLOAT DEFAULT 0,
    solar_output_wh     FLOAT DEFAULT 0,
    tile_energy_wh      FLOAT DEFAULT 0,
    
    -- Waste
    waste_level_pct     FLOAT,
    waste_weight_kg     FLOAT,
    
    -- Carbon
    carbon_emission_kg  FLOAT DEFAULT 0,
    carbon_offset_kg    FLOAT DEFAULT 0,
    
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_envdata_zone ON environmental_data(zone);
CREATE INDEX idx_envdata_time ON environmental_data(timestamp DESC);

-- ============================================================================
-- 5. ECOPOINTS SYSTEM
-- ============================================================================

CREATE TYPE point_category AS ENUM (
    'recycling', 'carpool', 'smart_bin', 'workshop', 'sensor_contribution',
    'tree_planting', 'water_saving', 'energy_saving', 'food_waste_reduction',
    'marketplace_trade', 'challenge_completion', 'referral', 'innovation',
    'compost', 'vertical_farm', 'cleanup_drive', 'bonus'
);

CREATE TABLE eco_points (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points          INTEGER NOT NULL,
    category        point_category NOT NULL,
    description     TEXT,
    activity_ref    UUID,               -- reference to specific activity
    carbon_impact   FLOAT DEFAULT 0,    -- kg CO2 equivalent
    verified        BOOLEAN DEFAULT FALSE,
    verified_by     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ecopoints_user ON eco_points(user_id);
CREATE INDEX idx_ecopoints_category ON eco_points(category);
CREATE INDEX idx_ecopoints_created ON eco_points(created_at DESC);

CREATE TABLE eco_point_balance (
    user_id         UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_earned    INTEGER DEFAULT 0,
    total_spent     INTEGER DEFAULT 0,
    current_balance INTEGER DEFAULT 0,
    lifetime_carbon FLOAT DEFAULT 0,    -- total kg CO2 saved
    level           INTEGER DEFAULT 1,
    streak_days     INTEGER DEFAULT 0,
    last_activity   TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. ACTIVITIES & ACTIONS LOG
-- ============================================================================

CREATE TYPE activity_type AS ENUM (
    'recycle', 'carpool_ride', 'bin_deposit', 'workshop_attend',
    'sensor_deploy', 'tree_plant', 'compost_contribute', 'farm_harvest',
    'cleanup_participate', 'marketplace_sell', 'marketplace_buy',
    'challenge_join', 'energy_save', 'water_save', 'food_save',
    'report_issue', 'innovation_submit'
);

CREATE TABLE activities (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type   activity_type NOT NULL,
    title           VARCHAR(300),
    description     TEXT,
    quantity         FLOAT DEFAULT 1,
    unit            VARCHAR(50),
    carbon_saved_kg FLOAT DEFAULT 0,
    points_awarded  INTEGER DEFAULT 0,
    proof_url       VARCHAR(500),
    location        VARCHAR(200),
    verified        BOOLEAN DEFAULT FALSE,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_activities_user ON activities(user_id);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_created ON activities(created_at DESC);

-- ============================================================================
-- 7. SMART BINS
-- ============================================================================

CREATE TYPE bin_category AS ENUM ('plastic', 'organic', 'metal', 'paper', 'e_waste', 'glass', 'general');

CREATE TABLE smart_bins (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id       UUID REFERENCES sensors(id),
    bin_code        VARCHAR(50) UNIQUE NOT NULL,
    category        bin_category NOT NULL,
    location_name   VARCHAR(200),
    building        VARCHAR(100),
    capacity_liters FLOAT DEFAULT 120,
    current_level   FLOAT DEFAULT 0,      -- percentage 0-100
    weight_kg       FLOAT DEFAULT 0,
    last_emptied    TIMESTAMPTZ,
    alert_threshold FLOAT DEFAULT 80,     -- % to trigger alert
    is_full         BOOLEAN DEFAULT FALSE,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bins_category ON smart_bins(category);
CREATE INDEX idx_bins_full ON smart_bins(is_full);

-- ============================================================================
-- 8. CARPOOLING
-- ============================================================================

CREATE TYPE trip_status AS ENUM ('open', 'full', 'in_progress', 'completed', 'cancelled');

CREATE TABLE carpool_trips (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id       UUID NOT NULL REFERENCES users(id),
    origin          VARCHAR(300) NOT NULL,
    destination     VARCHAR(300) NOT NULL,
    origin_lat      DOUBLE PRECISION,
    origin_lng      DOUBLE PRECISION,
    dest_lat        DOUBLE PRECISION,
    dest_lng        DOUBLE PRECISION,
    departure_time  TIMESTAMPTZ NOT NULL,
    seats_total     INTEGER NOT NULL DEFAULT 4,
    seats_available INTEGER NOT NULL DEFAULT 3,
    distance_km     FLOAT,
    co2_saved_kg    FLOAT DEFAULT 0,
    status          trip_status DEFAULT 'open',
    vehicle_type    VARCHAR(100),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE carpool_passengers (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id     UUID NOT NULL REFERENCES carpool_trips(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id),
    status      VARCHAR(20) DEFAULT 'confirmed',
    joined_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trip_id, user_id)
);

CREATE INDEX idx_carpool_driver ON carpool_trips(driver_id);
CREATE INDEX idx_carpool_status ON carpool_trips(status);
CREATE INDEX idx_carpool_departure ON carpool_trips(departure_time);

-- ============================================================================
-- 9. VERTICAL FARMING
-- ============================================================================

CREATE TABLE farm_plots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(200) NOT NULL,
    location        VARCHAR(200),
    area_sqm        FLOAT,
    crop_type       VARCHAR(100),
    planting_date   DATE,
    expected_harvest DATE,
    status          VARCHAR(50) DEFAULT 'active',
    sensor_ids      UUID[],
    carbon_offset   FLOAT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE farm_readings (
    id              BIGSERIAL PRIMARY KEY,
    plot_id         UUID NOT NULL REFERENCES farm_plots(id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    soil_moisture   FLOAT,
    soil_temp       FLOAT,
    air_temp        FLOAT,
    humidity        FLOAT,
    light_lux       FLOAT,
    ph              FLOAT,
    nutrient_n      FLOAT,
    nutrient_p      FLOAT,
    nutrient_k      FLOAT,
    water_usage_ml  FLOAT DEFAULT 0,
    growth_cm       FLOAT,
    health_score    FLOAT,    -- AI-predicted 0-1
    metadata        JSONB DEFAULT '{}'
);

CREATE INDEX idx_farm_readings_plot ON farm_readings(plot_id);
CREATE INDEX idx_farm_readings_time ON farm_readings(timestamp DESC);

-- ============================================================================
-- 10. CARBON FOOTPRINT TRACKING
-- ============================================================================

CREATE TABLE carbon_footprints (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id),
    zone            VARCHAR(100),
    date            DATE NOT NULL DEFAULT CURRENT_DATE,
    transport_kg    FLOAT DEFAULT 0,
    electricity_kg  FLOAT DEFAULT 0,
    food_kg         FLOAT DEFAULT 0,
    waste_kg        FLOAT DEFAULT 0,
    water_kg        FLOAT DEFAULT 0,
    total_kg        FLOAT DEFAULT 0,
    offset_kg       FLOAT DEFAULT 0,
    net_kg          FLOAT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_carbon_user ON carbon_footprints(user_id);
CREATE INDEX idx_carbon_date ON carbon_footprints(date DESC);

-- ============================================================================
-- 11. FOOD WASTE TRACKING
-- ============================================================================

CREATE TABLE food_waste_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location        VARCHAR(200) NOT NULL,  -- canteen name
    date            DATE NOT NULL DEFAULT CURRENT_DATE,
    meal_type       VARCHAR(50),            -- breakfast, lunch, dinner
    waste_kg        FLOAT NOT NULL,
    servings_prepared INTEGER,
    servings_consumed INTEGER,
    waste_type      VARCHAR(100),           -- cooked, raw, plate waste
    composted_kg    FLOAT DEFAULT 0,
    methane_potential FLOAT DEFAULT 0,      -- estimated biogas potential
    reported_by     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 12. MARKETPLACE (Circular Economy)
-- ============================================================================

CREATE TYPE listing_status AS ENUM ('active', 'sold', 'expired', 'removed');

CREATE TABLE marketplace_listings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id       UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(300) NOT NULL,
    description     TEXT,
    category        VARCHAR(100),       -- recycled_product, compost, plants, etc.
    price_ecopoints INTEGER DEFAULT 0,
    price_inr       FLOAT DEFAULT 0,
    image_urls      TEXT[],
    quantity         INTEGER DEFAULT 1,
    status          listing_status DEFAULT 'active',
    carbon_saved_kg FLOAT DEFAULT 0,
    material_source VARCHAR(200),       -- e.g., "recycled PET bottles"
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE marketplace_transactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id      UUID NOT NULL REFERENCES marketplace_listings(id),
    buyer_id        UUID NOT NULL REFERENCES users(id),
    seller_id       UUID NOT NULL REFERENCES users(id),
    quantity         INTEGER DEFAULT 1,
    total_ecopoints INTEGER DEFAULT 0,
    total_inr       FLOAT DEFAULT 0,
    status          VARCHAR(50) DEFAULT 'completed',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 13. CHALLENGES & GAMIFICATION
-- ============================================================================

CREATE TABLE challenges (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(300) NOT NULL,
    description     TEXT,
    category        VARCHAR(100),
    target_value    FLOAT NOT NULL,
    target_unit     VARCHAR(50),
    reward_points   INTEGER NOT NULL,
    start_date      TIMESTAMPTZ NOT NULL,
    end_date        TIMESTAMPTZ NOT NULL,
    scope           VARCHAR(50) DEFAULT 'individual', -- individual, hostel, department
    max_participants INTEGER,
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE challenge_participants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_id    UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    progress        FLOAT DEFAULT 0,
    completed       BOOLEAN DEFAULT FALSE,
    completed_at    TIMESTAMPTZ,
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(challenge_id, user_id)
);

-- ============================================================================
-- 14. DIGITAL TWIN STATE
-- ============================================================================

CREATE TABLE digital_twin_state (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone            VARCHAR(100) NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Aggregated State
    overall_health  FLOAT,        -- 0-100 sustainability score
    aqi_index       FLOAT,
    water_quality   FLOAT,        -- 0-100
    waste_status    FLOAT,        -- 0-100 (100 = bins empty)
    energy_balance  FLOAT,        -- generated - consumed
    carbon_net      FLOAT,        -- emission - offset
    biodiversity    FLOAT,        -- 0-100
    noise_index     FLOAT,        -- 0-100
    foot_traffic    INTEGER,
    
    -- Predictions
    predicted_aqi   FLOAT,
    predicted_waste FLOAT,
    predicted_water FLOAT,
    predicted_energy FLOAT,
    
    -- Alerts
    active_alerts   JSONB DEFAULT '[]',
    
    -- Simulation params
    simulation_data JSONB DEFAULT '{}',
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_dt_zone ON digital_twin_state(zone);
CREATE INDEX idx_dt_time ON digital_twin_state(timestamp DESC);

-- ============================================================================
-- 15. NOTIFICATIONS & ALERTS
-- ============================================================================

CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical', 'emergency');

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id       UUID REFERENCES sensors(id),
    zone            VARCHAR(100),
    severity        alert_severity NOT NULL,
    title           VARCHAR(300) NOT NULL,
    message         TEXT,
    category        VARCHAR(100),
    is_resolved     BOOLEAN DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ,
    resolved_by     UUID REFERENCES users(id),
    auto_generated  BOOLEAN DEFAULT TRUE,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);

-- ============================================================================
-- 16. TREE PLANTING & REFORESTATION
-- ============================================================================

CREATE TABLE trees (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species         VARCHAR(200) NOT NULL,
    planted_by      UUID REFERENCES users(id),
    planted_date    DATE NOT NULL,
    location_name   VARCHAR(200),
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    height_cm       FLOAT,
    canopy_area_sqm FLOAT,
    co2_absorbed_kg FLOAT DEFAULT 0,    -- lifetime absorption
    health_status   VARCHAR(50) DEFAULT 'healthy',
    image_url       VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 17. ESG & SDG REPORTING
-- ============================================================================

CREATE TABLE esg_reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    zone            VARCHAR(100) DEFAULT 'campus',
    
    -- Environmental
    total_carbon_kg     FLOAT DEFAULT 0,
    total_offset_kg     FLOAT DEFAULT 0,
    waste_diverted_kg   FLOAT DEFAULT 0,
    water_saved_liters  FLOAT DEFAULT 0,
    energy_saved_kwh    FLOAT DEFAULT 0,
    trees_planted       INTEGER DEFAULT 0,
    
    -- Social
    participants        INTEGER DEFAULT 0,
    workshops_held      INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    
    -- Governance
    sensors_active      INTEGER DEFAULT 0,
    data_points         BIGINT DEFAULT 0,
    uptime_pct          FLOAT DEFAULT 0,
    
    -- SDG Alignment
    sdg_scores          JSONB DEFAULT '{}', -- SDG 6,7,11,12,13,15 scores
    
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 18. LEADERBOARDS (Materialized View for Performance)
-- ============================================================================

CREATE MATERIALIZED VIEW leaderboard_users AS
SELECT
    u.id,
    u.full_name,
    u.department,
    u.hostel,
    u.avatar_url,
    COALESCE(b.current_balance, 0) AS current_points,
    COALESCE(b.total_earned, 0) AS total_earned,
    COALESCE(b.lifetime_carbon, 0) AS carbon_saved_kg,
    COALESCE(b.level, 1) AS level,
    COALESCE(b.streak_days, 0) AS streak_days,
    RANK() OVER (ORDER BY COALESCE(b.total_earned, 0) DESC) AS rank
FROM users u
LEFT JOIN eco_point_balance b ON u.id = b.user_id
WHERE u.is_active = TRUE AND u.role = 'student'
ORDER BY total_earned DESC;

CREATE UNIQUE INDEX idx_leaderboard_users_id ON leaderboard_users(id);

-- Refresh periodically: REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_users;

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_sensors_modtime
    BEFORE UPDATE ON sensors FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_bins_modtime
    BEFORE UPDATE ON smart_bins FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_carpool_modtime
    BEFORE UPDATE ON carpool_trips FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Auto-calculate carbon footprint total
CREATE OR REPLACE FUNCTION calc_carbon_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_kg = NEW.transport_kg + NEW.electricity_kg + NEW.food_kg + NEW.waste_kg + NEW.water_kg;
    NEW.net_kg = NEW.total_kg - NEW.offset_kg;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_carbon_before_insert
    BEFORE INSERT OR UPDATE ON carbon_footprints
    FOR EACH ROW EXECUTE FUNCTION calc_carbon_total();
