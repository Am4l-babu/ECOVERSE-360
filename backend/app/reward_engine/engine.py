"""
ECOVERSE 360 — EcoPoints Reward Engine
Centralized logic for calculating, awarding, and managing EcoPoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.ecopoints import EcoPoint, EcoPointBalance
from app.models.entities import Activity

settings = get_settings()


# ── Point Rules Configuration ────────────────────────────────────────────

POINT_RULES = {
    # category: (base_points, carbon_impact_kg, description)
    "recycle": (10, 1.8, "Recycled materials"),
    "carpool_ride": (15, 2.3, "Shared a carpool ride"),
    "bin_deposit": (5, 0.5, "Deposited waste in smart bin"),
    "workshop_attend": (25, 0.0, "Attended sustainability workshop"),
    "sensor_deploy": (50, 0.0, "Deployed a citizen sensor"),
    "tree_plant": (30, 22.0, "Planted a tree"),
    "compost_contribute": (10, 2.5, "Contributed to composting"),
    "farm_harvest": (20, 1.0, "Harvested from vertical farm"),
    "cleanup_participate": (20, 0.5, "Participated in cleanup drive"),
    "marketplace_sell": (15, 1.5, "Sold recycled product"),
    "marketplace_buy": (5, 0.5, "Bought sustainable product"),
    "challenge_join": (10, 0.0, "Joined an eco-challenge"),
    "energy_save": (10, 0.82, "Energy saving action"),
    "water_save": (8, 0.03, "Water conservation action"),
    "food_save": (12, 2.5, "Reduced food waste"),
    "report_issue": (5, 0.0, "Reported environmental issue"),
    "innovation_submit": (40, 0.0, "Submitted green innovation"),
}

# ── Level Thresholds ─────────────────────────────────────────────────────

LEVEL_THRESHOLDS = {
    1: (0, "Seedling"),
    2: (100, "Sprout"),
    3: (300, "Sapling"),
    4: (700, "Tree"),
    5: (1500, "Forest"),
    6: (3000, "Ecosystem"),
    7: (6000, "Biome"),
    8: (12000, "Planet Guardian"),
    9: (25000, "Cosmic Steward"),
}

# ── Streak Bonuses ───────────────────────────────────────────────────────

STREAK_BONUSES = {
    7: 1.2,     # 7-day streak = 20% bonus
    14: 1.3,    # 14-day streak = 30% bonus
    30: 1.5,    # 30-day streak = 50% bonus
    60: 1.75,   # 60-day streak = 75% bonus
    100: 2.0,   # 100-day streak = 2x points!
}


class RewardEngine:
    """
    Core reward calculation engine.

    Handles:
    - Point calculation with modifiers
    - Streak tracking
    - Level progression
    - Carbon impact tracking
    - Activity-based auto-awarding
    """

    async def process_activity(
        self,
        db: AsyncSession,
        user_id: UUID,
        activity_type: str,
        quantity: float = 1.0,
        metadata: Dict = None,
    ) -> Dict:
        """
        Process an eco-activity: log it, calculate points, update balance.
        Returns summary of points awarded and impact.
        """
        rule = POINT_RULES.get(activity_type)
        if not rule:
            return {"error": f"Unknown activity type: {activity_type}"}

        base_points, carbon_per_unit, description = rule

        # ── Calculate Points ─────────────────────────────────────────
        raw_points = int(base_points * quantity)
        carbon_impact = carbon_per_unit * quantity

        # Get balance for streak bonus
        balance = await self._get_or_create_balance(db, user_id)
        streak_multiplier = self._get_streak_multiplier(balance.streak_days)
        final_points = int(raw_points * streak_multiplier)

        # ── Log Activity ─────────────────────────────────────────────
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type,
            title=description,
            quantity=quantity,
            carbon_saved_kg=carbon_impact,
            points_awarded=final_points,
            metadata_=metadata or {},
        )
        db.add(activity)

        # ── Award Points ─────────────────────────────────────────────
        point = EcoPoint(
            user_id=user_id,
            points=final_points,
            category=activity_type if activity_type in [r for r in POINT_RULES] else "bonus",
            description=f"{description} (x{quantity})",
            activity_ref=activity.id,
            carbon_impact=carbon_impact,
            verified=True,
        )
        db.add(point)

        # ── Update Balance ───────────────────────────────────────────
        balance.total_earned += final_points
        balance.current_balance += final_points
        balance.lifetime_carbon += carbon_impact
        balance.last_activity = datetime.now(timezone.utc)

        # Update streak
        await self._update_streak(balance)

        # Level up check
        new_level = self._calculate_level(balance.total_earned)
        leveled_up = new_level > balance.level
        balance.level = new_level

        db.add(balance)
        await db.flush()

        return {
            "points_earned": final_points,
            "streak_multiplier": streak_multiplier,
            "carbon_impact_kg": round(carbon_impact, 3),
            "new_balance": balance.current_balance,
            "level": balance.level,
            "level_name": LEVEL_THRESHOLDS.get(balance.level, (0, "Unknown"))[1],
            "leveled_up": leveled_up,
            "streak_days": balance.streak_days,
        }

    async def get_user_stats(self, db: AsyncSession, user_id: UUID) -> Dict:
        """Get comprehensive stats for a user."""
        balance = await self._get_or_create_balance(db, user_id)

        # Activity breakdown
        result = await db.execute(
            select(
                Activity.activity_type,
                func.count(Activity.id).label("count"),
                func.sum(Activity.carbon_saved_kg).label("carbon"),
                func.sum(Activity.points_awarded).label("points"),
            )
            .where(Activity.user_id == user_id)
            .group_by(Activity.activity_type)
        )

        breakdown = {}
        for row in result.all():
            breakdown[row.activity_type] = {
                "count": row.count,
                "carbon_saved_kg": round(row.carbon or 0, 2),
                "points_earned": row.points or 0,
            }

        level_info = LEVEL_THRESHOLDS.get(balance.level, (0, "Unknown"))
        next_level = LEVEL_THRESHOLDS.get(balance.level + 1)
        points_to_next = (next_level[0] - balance.total_earned) if next_level else 0

        return {
            "total_earned": balance.total_earned,
            "current_balance": balance.current_balance,
            "total_spent": balance.total_spent,
            "lifetime_carbon_kg": round(balance.lifetime_carbon, 2),
            "level": balance.level,
            "level_name": level_info[1],
            "points_to_next_level": max(0, points_to_next),
            "streak_days": balance.streak_days,
            "streak_multiplier": self._get_streak_multiplier(balance.streak_days),
            "activity_breakdown": breakdown,
        }

    # ── Internal Helpers ─────────────────────────────────────────────

    async def _get_or_create_balance(
        self, db: AsyncSession, user_id: UUID
    ) -> EcoPointBalance:
        result = await db.execute(
            select(EcoPointBalance).where(EcoPointBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        if not balance:
            balance = EcoPointBalance(user_id=user_id)
            db.add(balance)
            await db.flush()
        return balance

    async def _update_streak(self, balance: EcoPointBalance):
        """Update daily activity streak."""
        now = datetime.now(timezone.utc)
        if balance.last_activity:
            diff = (now - balance.last_activity).days
            if diff <= 1:
                if diff == 1:
                    balance.streak_days += 1
                # same day = no change
            else:
                balance.streak_days = 1  # reset
        else:
            balance.streak_days = 1

    @staticmethod
    def _get_streak_multiplier(streak_days: int) -> float:
        multiplier = 1.0
        for threshold, bonus in sorted(STREAK_BONUSES.items()):
            if streak_days >= threshold:
                multiplier = bonus
        return multiplier

    @staticmethod
    def _calculate_level(total_earned: int) -> int:
        level = 1
        for lvl, (threshold, _) in sorted(LEVEL_THRESHOLDS.items()):
            if total_earned >= threshold:
                level = lvl
        return level
