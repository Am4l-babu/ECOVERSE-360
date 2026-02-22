"""
ECOVERSE 360 — Sensor & IoT Device Models
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    sensor_type = Column(
        ENUM(
            "smart_bin", "air_quality", "water_quality", "soil_moisture",
            "temperature", "humidity", "energy_tile", "rain_gauge",
            "traffic_counter", "noise_level", "solar_panel", "water_level",
            "pressure", "light", "co2", "ph", "tds", "uv_index",
            name="sensor_type",
        ),
        nullable=False,
    )
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location_name = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    building = Column(String(100))
    floor = Column(Integer)
    status = Column(
        ENUM("online", "offline", "maintenance", "error", name="sensor_status"),
        default="offline",
    )
    firmware_ver = Column(String(50))
    battery_level = Column(Float)
    last_seen = Column(DateTime(timezone=True))
    metadata_ = Column("metadata", JSONB, default={})
    installed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", lazy="dynamic")

    def __repr__(self):
        return f"<Sensor {self.device_id} ({self.sensor_type})>"


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    quality = Column(Float, default=1.0)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")

    def __repr__(self):
        return f"<Reading sensor={self.sensor_id} value={self.value}{self.unit}>"
