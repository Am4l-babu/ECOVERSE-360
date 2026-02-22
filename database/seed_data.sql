-- ════════════════════════════════════════════════════════════════════════
-- ECOVERSE 360 — Seed Data
-- Demo data for development and testing
-- ════════════════════════════════════════════════════════════════════════

-- ── Users ───────────────────────────────────────────────────────────────

INSERT INTO users (id, email, username, password_hash, role, eco_level, total_points)
VALUES
  ('a0000000-0000-0000-0000-000000000001', 'admin@ecoverse.edu', 'EcoAdmin',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',  -- password: admin123
   'super_admin', 'Planetary Guardian', 120000),

  ('a0000000-0000-0000-0000-000000000002', 'alice@campus.edu', 'EcoChampion',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',
   'student', 'Ecosystem Architect', 52000),

  ('a0000000-0000-0000-0000-000000000003', 'bob@campus.edu', 'GreenNinja',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',
   'student', 'Climate Champion', 28000),

  ('a0000000-0000-0000-0000-000000000004', 'carol@campus.edu', 'TreeHugger',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',
   'student', 'Sustainability Hero', 12000),

  ('a0000000-0000-0000-0000-000000000005', 'dave@campus.edu', 'SolarKid',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',
   'student', 'Nature Keeper', 6500),

  ('a0000000-0000-0000-0000-000000000006', 'prof.green@campus.edu', 'ProfGreen',
   '$2b$12$LJ3m4ys4Pz4Z8X4h6FvJ5OQ7YlO9EfZnAFE1DV2D4hT8x3NJq3Ky',
   'faculty', 'Green Warrior', 2200);

-- ── Sensors ─────────────────────────────────────────────────────────────

INSERT INTO sensors (id, sensor_type, zone, location, model, firmware_version, status)
VALUES
  -- Air quality monitors
  ('b0000000-0000-0000-0000-000000000001', 'air_quality', 'Zone A - Library',
   'Library main entrance', 'ESP32+PMS5003+MQ135', '1.2.0', 'active'),
  ('b0000000-0000-0000-0000-000000000002', 'air_quality', 'Zone B - Engineering',
   'Engineering Block corridor', 'ESP32+PMS5003+MQ135', '1.2.0', 'active'),
  ('b0000000-0000-0000-0000-000000000003', 'air_quality', 'Zone C - Cafeteria',
   'Cafeteria outdoor area', 'ESP32+PMS5003+MQ135', '1.2.0', 'active'),

  -- Water quality probes
  ('b0000000-0000-0000-0000-000000000010', 'water_quality', 'Zone A - Library',
   'Library garden fountain', 'ESP32+TDS+pH', '1.0.0', 'active'),
  ('b0000000-0000-0000-0000-000000000011', 'water_quality', 'Zone D - Sports',
   'Swimming pool intake', 'ESP32+TDS+pH', '1.0.0', 'active'),

  -- Smart bins
  ('b0000000-0000-0000-0000-000000000020', 'waste_bin', 'Zone A - Library',
   'Library entrance bin', 'ESP8266+HC-SR04+HX711', '1.1.0', 'active'),
  ('b0000000-0000-0000-0000-000000000021', 'waste_bin', 'Zone B - Engineering',
   'Engineering lab bin', 'ESP8266+HC-SR04+HX711', '1.1.0', 'active'),
  ('b0000000-0000-0000-0000-000000000022', 'waste_bin', 'Zone C - Cafeteria',
   'Cafeteria recycling bin', 'ESP8266+HC-SR04+HX711', '1.1.0', 'active'),

  -- Farm nodes
  ('b0000000-0000-0000-0000-000000000030', 'farm', 'Zone E - Farm',
   'Microgreens Bed A', 'ESP32+SoilMoisture+BH1750', '1.0.0', 'active'),
  ('b0000000-0000-0000-0000-000000000031', 'farm', 'Zone E - Farm',
   'Herbs Bed B', 'ESP32+SoilMoisture+BH1750', '1.0.0', 'active'),

  -- Energy tiles
  ('b0000000-0000-0000-0000-000000000040', 'energy_tile', 'Zone B - Engineering',
   'Main Corridor A', 'ESP8266+Piezo', '1.0.0', 'active'),
  ('b0000000-0000-0000-0000-000000000041', 'energy_tile', 'Zone A - Library',
   'Library Walkway', 'ESP8266+Piezo', '1.0.0', 'active');

-- ── Sensor Readings (last 24h sample) ───────────────────────────────────

INSERT INTO sensor_readings (sensor_id, value, unit, metadata, recorded_at)
VALUES
  -- Air quality readings (AQI)
  ('b0000000-0000-0000-0000-000000000001', 42, 'AQI',
   '{"pm25": 12.3, "pm10": 28.1, "co2": 415, "temp": 27.5, "humidity": 62}',
   NOW() - INTERVAL '1 hour'),
  ('b0000000-0000-0000-0000-000000000001', 38, 'AQI',
   '{"pm25": 10.1, "pm10": 24.5, "co2": 405, "temp": 26.8, "humidity": 64}',
   NOW() - INTERVAL '2 hours'),
  ('b0000000-0000-0000-0000-000000000002', 55, 'AQI',
   '{"pm25": 18.7, "pm10": 35.2, "co2": 480, "temp": 29.1, "humidity": 58}',
   NOW() - INTERVAL '1 hour'),

  -- Water quality readings (TDS)
  ('b0000000-0000-0000-0000-000000000010', 285, 'ppm',
   '{"ph": 7.2, "temperature": 24.5, "quality": "Excellent"}',
   NOW() - INTERVAL '30 minutes'),

  -- Waste bin readings (fill %)
  ('b0000000-0000-0000-0000-000000000020', 72.5, '%',
   '{"weight_kg": 8.3, "bin_type": "recyclable"}',
   NOW() - INTERVAL '15 minutes'),
  ('b0000000-0000-0000-0000-000000000021', 45.0, '%',
   '{"weight_kg": 5.1, "bin_type": "general"}',
   NOW() - INTERVAL '20 minutes'),
  ('b0000000-0000-0000-0000-000000000022', 91.0, '%',
   '{"weight_kg": 12.7, "bin_type": "recyclable"}',
   NOW() - INTERVAL '10 minutes'),

  -- Farm readings
  ('b0000000-0000-0000-0000-000000000030', 58.0, '%',
   '{"air_temp": 26.5, "humidity": 70, "light_lux": 12000, "soil_ph": 6.8, "health_score": 85}',
   NOW() - INTERVAL '30 minutes'),

  -- Energy tile readings
  ('b0000000-0000-0000-0000-000000000040', 245, 'steps',
   '{"energy_total_mj": 1.23, "traffic_density": "high", "peak_force": 780}',
   NOW() - INTERVAL '1 hour');

-- ── Smart Bins ──────────────────────────────────────────────────────────

INSERT INTO smart_bins (id, sensor_id, bin_type, zone, fill_level, weight_kg, last_collected)
VALUES
  (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000020', 'recyclable',
   'Zone A - Library', 72.5, 8.3, NOW() - INTERVAL '6 hours'),
  (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000021', 'general',
   'Zone B - Engineering', 45.0, 5.1, NOW() - INTERVAL '4 hours'),
  (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000022', 'recyclable',
   'Zone C - Cafeteria', 91.0, 12.7, NOW() - INTERVAL '8 hours');

-- ── Farm Plots ──────────────────────────────────────────────────────────

INSERT INTO farm_plots (id, plot_name, crop_type, zone, status)
VALUES
  (gen_random_uuid(), 'Microgreens Bed A', 'microgreens', 'Zone E - Farm', 'growing'),
  (gen_random_uuid(), 'Herbs Bed B', 'basil_mint', 'Zone E - Farm', 'growing'),
  (gen_random_uuid(), 'Lettuce Row C', 'lettuce', 'Zone E - Farm', 'seedling');

-- ── EcoPoint Balances ───────────────────────────────────────────────────

INSERT INTO eco_point_balance (user_id, total_earned, total_spent, current_balance, level, streak_days)
VALUES
  ('a0000000-0000-0000-0000-000000000002', 52000, 3200, 48800, 'Ecosystem Architect', 45),
  ('a0000000-0000-0000-0000-000000000003', 28000, 1500, 26500, 'Climate Champion', 22),
  ('a0000000-0000-0000-0000-000000000004', 12000, 800, 11200, 'Sustainability Hero', 15),
  ('a0000000-0000-0000-0000-000000000005', 6500, 200, 6300, 'Nature Keeper', 8),
  ('a0000000-0000-0000-0000-000000000006', 2200, 0, 2200, 'Green Warrior', 5);

-- ── Recent EcoPoint Transactions ────────────────────────────────────────

INSERT INTO eco_points (user_id, points, activity_type, description, co2_saved_kg)
VALUES
  ('a0000000-0000-0000-0000-000000000002', 12, 'recycle', 'Recycled 2.5kg plastic', 1.8),
  ('a0000000-0000-0000-0000-000000000002', 18, 'carpool', 'Carpooled to campus (3 riders)', 2.3),
  ('a0000000-0000-0000-0000-000000000003', 10, 'recycle', 'Recycled paper waste', 1.8),
  ('a0000000-0000-0000-0000-000000000003', 30, 'plant_tree', 'Planted oak tree in Zone D', 22.0),
  ('a0000000-0000-0000-0000-000000000004', 25, 'workshop', 'Attended sustainability workshop', 0),
  ('a0000000-0000-0000-0000-000000000005', 5, 'reusable_bottle', 'Used reusable bottle', 0.5),
  ('a0000000-0000-0000-0000-000000000006', 15, 'carpool', 'Carpooled from parking lot B', 2.3);

-- ── Challenges ──────────────────────────────────────────────────────────

INSERT INTO challenges (id, title, description, challenge_type, target_value, points_reward, start_date, end_date, is_active)
VALUES
  (gen_random_uuid(), 'Zero Waste Week',
   'Produce zero non-recyclable waste for 7 consecutive days',
   'waste_reduction', 7, 200,
   NOW(), NOW() + INTERVAL '7 days', true),

  (gen_random_uuid(), 'Carpool Champion',
   'Complete 10 carpool trips this month',
   'transport', 10, 300,
   NOW(), NOW() + INTERVAL '30 days', true),

  (gen_random_uuid(), 'Plant-a-thon',
   'Help plant 50 trees across campus this semester',
   'community', 50, 500,
   NOW(), NOW() + INTERVAL '90 days', true),

  (gen_random_uuid(), 'Sensor Scout',
   'Deploy 5 new environmental sensors in under-monitored zones',
   'technology', 5, 400,
   NOW(), NOW() + INTERVAL '60 days', true);

-- ── Carbon Footprints ───────────────────────────────────────────────────

INSERT INTO carbon_footprints (user_id, period, transport_kg, food_kg, electricity_kg, total_kg)
VALUES
  ('a0000000-0000-0000-0000-000000000002', 'monthly', 45.2, 32.1, 28.5, 105.8),
  ('a0000000-0000-0000-0000-000000000003', 'monthly', 62.8, 38.4, 35.2, 136.4),
  ('a0000000-0000-0000-0000-000000000004', 'monthly', 28.1, 42.0, 22.0, 92.1),
  ('a0000000-0000-0000-0000-000000000005', 'monthly', 85.0, 35.5, 30.0, 150.5);

-- ── Digital Twin State ──────────────────────────────────────────────────

INSERT INTO digital_twin_state (zone, health_score, metrics)
VALUES
  ('Zone A - Library', 82.5,
   '{"aqi": 42, "water_tds": 285, "waste_fill_avg": 72.5, "noise_db": 45, "energy_kwh": 120}'),
  ('Zone B - Engineering', 71.0,
   '{"aqi": 55, "water_tds": 310, "waste_fill_avg": 45.0, "noise_db": 62, "energy_kwh": 280}'),
  ('Zone C - Cafeteria', 65.3,
   '{"aqi": 48, "water_tds": 295, "waste_fill_avg": 91.0, "noise_db": 72, "energy_kwh": 95}'),
  ('Zone D - Sports', 88.0,
   '{"aqi": 35, "water_tds": 260, "waste_fill_avg": 30.0, "noise_db": 55, "energy_kwh": 180}'),
  ('Zone E - Farm', 90.2,
   '{"aqi": 28, "soil_moisture": 58, "light_lux": 12000, "soil_ph": 6.8, "crop_health": 85}');

-- ── Trees ───────────────────────────────────────────────────────────────

INSERT INTO trees (id, species, planted_by, zone, planted_at, co2_absorbed_kg)
VALUES
  (gen_random_uuid(), 'Neem', 'a0000000-0000-0000-0000-000000000003', 'Zone D - Sports',
   NOW() - INTERVAL '180 days', 11.0),
  (gen_random_uuid(), 'Banyan', 'a0000000-0000-0000-0000-000000000002', 'Zone A - Library',
   NOW() - INTERVAL '365 days', 22.0),
  (gen_random_uuid(), 'Peepal', 'a0000000-0000-0000-0000-000000000004', 'Zone E - Farm',
   NOW() - INTERVAL '90 days', 5.5),
  (gen_random_uuid(), 'Mango', 'a0000000-0000-0000-0000-000000000002', 'Zone C - Cafeteria',
   NOW() - INTERVAL '60 days', 3.6);

-- ── Refresh Materialized View ───────────────────────────────────────────

REFRESH MATERIALIZED VIEW IF EXISTS leaderboard_users;
