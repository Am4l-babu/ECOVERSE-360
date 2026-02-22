"""
ECOVERSE 360 — Activity, Smart Bin, Carpool, Farm, Carbon, Food Waste Models
"""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, ARRAY,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# ── Activity Log ─────────────────────────────────────────────────────────

class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(
        ENUM(
            "recycle", "carpool_ride", "bin_deposit", "workshop_attend",
            "sensor_deploy", "tree_plant", "compost_contribute", "farm_harvest",
            "cleanup_participate", "marketplace_sell", "marketplace_buy",
            "challenge_join", "energy_save", "water_save", "food_save",
            "report_issue", "innovation_submit",
            name="activity_type",
        ),
        nullable=False,
    )
    title = Column(String(300))
    description = Column(Text)
    quantity = Column(Float, default=1)
    unit = Column(String(50))
    carbon_saved_kg = Column(Float, default=0)
    points_awarded = Column(Integer, default=0)
    proof_url = Column(String(500))
    location = Column(String(200))
    verified = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="activities")


# ── Smart Bins ───────────────────────────────────────────────────────────

class SmartBin(Base):
    __tablename__ = "smart_bins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"))
    bin_code = Column(String(50), unique=True, nullable=False)
    category = Column(
        ENUM("plastic", "organic", "metal", "paper", "e_waste", "glass", "general", name="bin_category"),
        nullable=False,
    )
    location_name = Column(String(200))
    building = Column(String(100))
    capacity_liters = Column(Float, default=120)
    current_level = Column(Float, default=0)
    weight_kg = Column(Float, default=0)
    last_emptied = Column(DateTime(timezone=True))
    alert_threshold = Column(Float, default=80)
    is_full = Column(Boolean, default=False)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ── Carpooling ───────────────────────────────────────────────────────────

class CarpoolTrip(Base):
    __tablename__ = "carpool_trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    origin = Column(String(300), nullable=False)
    destination = Column(String(300), nullable=False)
    origin_lat = Column(Float)
    origin_lng = Column(Float)
    dest_lat = Column(Float)
    dest_lng = Column(Float)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    seats_total = Column(Integer, default=4)
    seats_available = Column(Integer, default=3)
    distance_km = Column(Float)
    co2_saved_kg = Column(Float, default=0)
    status = Column(
        ENUM("open", "full", "in_progress", "completed", "cancelled", name="trip_status"),
        default="open",
    )
    vehicle_type = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    driver = relationship("User", foreign_keys=[driver_id])
    passengers = relationship("CarpoolPassenger", back_populates="trip", lazy="selectin")


class CarpoolPassenger(Base):
    __tablename__ = "carpool_passengers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("carpool_trips.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="confirmed")
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    trip = relationship("CarpoolTrip", back_populates="passengers")
    user = relationship("User")


# ── Vertical Farming ────────────────────────────────────────────────────

class FarmPlot(Base):
    __tablename__ = "farm_plots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    location = Column(String(200))
    area_sqm = Column(Float)
    crop_type = Column(String(100))
    planting_date = Column(Date)
    expected_harvest = Column(Date)
    status = Column(String(50), default="active")
    carbon_offset = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    readings = relationship("FarmReading", back_populates="plot", lazy="dynamic")


class FarmReading(Base):
    __tablename__ = "farm_readings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    plot_id = Column(UUID(as_uuid=True), ForeignKey("farm_plots.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    soil_moisture = Column(Float)
    soil_temp = Column(Float)
    air_temp = Column(Float)
    humidity = Column(Float)
    light_lux = Column(Float)
    ph = Column(Float)
    nutrient_n = Column(Float)
    nutrient_p = Column(Float)
    nutrient_k = Column(Float)
    water_usage_ml = Column(Float, default=0)
    growth_cm = Column(Float)
    health_score = Column(Float)
    metadata_ = Column("metadata", JSONB, default={})

    plot = relationship("FarmPlot", back_populates="readings")


# ── Carbon Footprint ────────────────────────────────────────────────────

class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    zone = Column(String(100))
    date = Column(Date, default=date.today)
    transport_kg = Column(Float, default=0)
    electricity_kg = Column(Float, default=0)
    food_kg = Column(Float, default=0)
    waste_kg = Column(Float, default=0)
    water_kg = Column(Float, default=0)
    total_kg = Column(Float, default=0)
    offset_kg = Column(Float, default=0)
    net_kg = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Food Waste ───────────────────────────────────────────────────────────

class FoodWasteLog(Base):
    __tablename__ = "food_waste_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String(200), nullable=False)
    date = Column(Date, default=date.today)
    meal_type = Column(String(50))
    waste_kg = Column(Float, nullable=False)
    servings_prepared = Column(Integer)
    servings_consumed = Column(Integer)
    waste_type = Column(String(100))
    composted_kg = Column(Float, default=0)
    methane_potential = Column(Float, default=0)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Marketplace ──────────────────────────────────────────────────────────

class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price_ecopoints = Column(Integer, default=0)
    price_inr = Column(Float, default=0)
    image_urls = Column(ARRAY(Text))
    quantity = Column(Integer, default=1)
    status = Column(
        ENUM("active", "sold", "expired", "removed", name="listing_status"),
        default="active",
    )
    carbon_saved_kg = Column(Float, default=0)
    material_source = Column(String(200))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    seller = relationship("User", foreign_keys=[seller_id])


# ── Challenges ───────────────────────────────────────────────────────────

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(50))
    reward_points = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    scope = Column(String(50), default="individual")
    max_participants = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    participants = relationship("ChallengeParticipant", back_populates="challenge", lazy="selectin")


class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    progress = Column(Float, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User")


# ── Digital Twin State ───────────────────────────────────────────────────

class DigitalTwinState(Base):
    __tablename__ = "digital_twin_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    overall_health = Column(Float)
    aqi_index = Column(Float)
    water_quality = Column(Float)
    waste_status = Column(Float)
    energy_balance = Column(Float)
    carbon_net = Column(Float)
    biodiversity = Column(Float)
    noise_index = Column(Float)
    foot_traffic = Column(Integer)

    predicted_aqi = Column(Float)
    predicted_waste = Column(Float)
    predicted_water = Column(Float)
    predicted_energy = Column(Float)

    active_alerts = Column(JSONB, default=[])
    simulation_data = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Alerts ───────────────────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"))
    zone = Column(String(100))
    severity = Column(
        ENUM("info", "warning", "critical", "emergency", name="alert_severity"),
        nullable=False,
    )
    title = Column(String(300), nullable=False)
    message = Column(Text)
    category = Column(String(100))
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    auto_generated = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Trees & Reforestation ────────────────────────────────────────────────

class Tree(Base):
    __tablename__ = "trees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    species = Column(String(200), nullable=False)
    planted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    planted_date = Column(Date, nullable=False)
    location_name = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    height_cm = Column(Float)
    canopy_area_sqm = Column(Float)
    co2_absorbed_kg = Column(Float, default=0)
    health_status = Column(String(50), default="healthy")
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ── ESG Reports ──────────────────────────────────────────────────────────

class ESGReport(Base):
    __tablename__ = "esg_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    zone = Column(String(100), default="campus")

    total_carbon_kg = Column(Float, default=0)
    total_offset_kg = Column(Float, default=0)
    waste_diverted_kg = Column(Float, default=0)
    water_saved_liters = Column(Float, default=0)
    energy_saved_kwh = Column(Float, default=0)
    trees_planted = Column(Integer, default=0)

    participants = Column(Integer, default=0)
    workshops_held = Column(Integer, default=0)
    challenges_completed = Column(Integer, default=0)

    sensors_active = Column(Integer, default=0)
    data_points = Column(BigInteger, default=0)
    uptime_pct = Column(Float, default=0)

    sdg_scores = Column(JSONB, default={})
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
