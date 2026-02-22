"""
ECOVERSE 360 — User Model
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, String, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(
        ENUM("student", "admin", "faculty", "public", "iot_node", name="user_role"),
        nullable=False,
        default="student",
    )
    department = Column(String(100))
    hostel = Column(String(100))
    avatar_url = Column(String(500))
    eco_score = Column(Float, default=0.0)
    carbon_score = Column(Float, default=0.0)
    water_score = Column(Float, default=0.0)
    waste_score = Column(Float, default=0.0)
    energy_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    eco_points = relationship("EcoPoint", back_populates="user", lazy="selectin")
    activities = relationship("Activity", back_populates="user", lazy="selectin")
    point_balance = relationship("EcoPointBalance", back_populates="user", uselist=False, lazy="selectin")

    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>"
