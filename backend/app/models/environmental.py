"""
ECOVERSE 360 — Environmental Data Model
Aggregated zone-level environmental readings for Digital Twin.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Air Quality
    aqi = Column(Float)
    pm25 = Column(Float)
    pm10 = Column(Float)
    co2_ppm = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    ozone = Column(Float)

    # Water Quality
    water_ph = Column(Float)
    water_tds = Column(Float)
    water_turbidity = Column(Float)
    water_temperature = Column(Float)

    # Weather
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    rainfall_mm = Column(Float)
    wind_speed = Column(Float)
    uv_index = Column(Float)

    # Noise
    noise_db = Column(Float)

    # Energy
    energy_generated_wh = Column(Float, default=0)
    energy_consumed_wh = Column(Float, default=0)
    solar_output_wh = Column(Float, default=0)
    tile_energy_wh = Column(Float, default=0)

    # Waste
    waste_level_pct = Column(Float)
    waste_weight_kg = Column(Float)

    # Carbon
    carbon_emission_kg = Column(Float, default=0)
    carbon_offset_kg = Column(Float, default=0)

    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EnvData zone={self.zone} aqi={self.aqi} @ {self.timestamp}>"
