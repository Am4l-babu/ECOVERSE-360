"""
ECOVERSE 360 — EcoPoints & Gamification Models
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class EcoPoint(Base):
    __tablename__ = "eco_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, nullable=False)
    category = Column(
        ENUM(
            "recycling", "carpool", "smart_bin", "workshop", "sensor_contribution",
            "tree_planting", "water_saving", "energy_saving", "food_waste_reduction",
            "marketplace_trade", "challenge_completion", "referral", "innovation",
            "compost", "vertical_farm", "cleanup_drive", "bonus",
            name="point_category",
        ),
        nullable=False,
    )
    description = Column(Text)
    activity_ref = Column(UUID(as_uuid=True))
    carbon_impact = Column(Float, default=0)
    verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="eco_points", foreign_keys=[user_id])

    def __repr__(self):
        return f"<EcoPoint +{self.points} ({self.category}) → user={self.user_id}>"


class EcoPointBalance(Base):
    __tablename__ = "eco_point_balance"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    current_balance = Column(Integer, default=0)
    lifetime_carbon = Column(Float, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="point_balance")

    @property
    def level_name(self) -> str:
        levels = {
            1: "Seedling",
            2: "Sprout",
            3: "Sapling",
            4: "Tree",
            5: "Forest",
            6: "Ecosystem",
            7: "Biome",
            8: "Planet Guardian",
        }
        return levels.get(self.level, "Cosmic Steward")

    def __repr__(self):
        return f"<Balance user={self.user_id} pts={self.current_balance} lvl={self.level}>"
