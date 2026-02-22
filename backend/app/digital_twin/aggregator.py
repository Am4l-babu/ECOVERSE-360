"""
ECOVERSE 360 — Digital Twin State Aggregator
Periodically aggregates sensor data into a comprehensive campus state snapshot.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Sensor, SensorReading, EnvironmentalData,
    SmartBin, DigitalTwinState, Alert,
)


class StateAggregator:
    """
    Aggregates all sensor & activity data into a Digital Twin snapshot.
    Run this every 15-30 minutes via background task.
    """

    ALERT_THRESHOLDS = {
        "aqi": {"warning": 100, "critical": 200, "emergency": 300},
        "water_ph": {"warning_low": 6.0, "warning_high": 8.5},
        "noise_db": {"warning": 70, "critical": 85},
        "waste_level": {"warning": 80, "critical": 95},
        "temperature": {"warning": 40, "critical": 45},
    }

    async def aggregate(self, db: AsyncSession, zone: str = "campus") -> DigitalTwinState:
        """Aggregate all data sources into a single state snapshot."""

        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)

        # ── Air Quality ──────────────────────────────────────────────
        aqi_data = await self._get_avg_reading(db, "air_quality", one_hour_ago)

        # ── Water Quality ────────────────────────────────────────────
        water_data = await self._get_avg_reading(db, "water_quality", one_hour_ago)
        water_quality_score = self._calculate_water_score(water_data)

        # ── Waste Status ─────────────────────────────────────────────
        waste_status = await self._get_waste_status(db)

        # ── Energy Balance ───────────────────────────────────────────
        energy_gen = await self._get_avg_reading(db, "energy_tile", one_hour_ago)
        solar_gen = await self._get_avg_reading(db, "solar_panel", one_hour_ago)
        energy_balance = (energy_gen or 0) + (solar_gen or 0)

        # ── Noise ────────────────────────────────────────────────────
        noise = await self._get_avg_reading(db, "noise_level", one_hour_ago)

        # ── Foot Traffic ─────────────────────────────────────────────
        traffic = await self._get_sum_reading(db, "traffic_counter", one_hour_ago)

        # ── Carbon Net ───────────────────────────────────────────────
        # Simple model: carbon = energy * grid factor - offsets
        carbon_emission = (energy_balance * 0.82 / 1000) if energy_balance else 0
        carbon_offset = 0  # populated from activities

        # ── Overall Health Score ─────────────────────────────────────
        overall_health = self._calculate_health_score(
            aqi=aqi_data, water=water_quality_score,
            waste=waste_status, noise=noise,
        )

        # ── Alerts ───────────────────────────────────────────────────
        alerts = await self._check_thresholds(db, zone, aqi_data, water_data, noise, waste_status)

        # ── Create State ─────────────────────────────────────────────
        state = DigitalTwinState(
            zone=zone,
            timestamp=now,
            overall_health=overall_health,
            aqi_index=aqi_data,
            water_quality=water_quality_score,
            waste_status=100 - (waste_status or 50),  # invert: 100 = all empty
            energy_balance=energy_balance,
            carbon_net=carbon_emission - carbon_offset,
            noise_index=self._noise_to_score(noise),
            foot_traffic=int(traffic or 0),
            active_alerts=[{"id": str(a.id), "title": a.title, "severity": a.severity} for a in alerts],
            simulation_data={
                "aggregated_at": now.isoformat(),
                "data_sources": {
                    "air_quality": aqi_data is not None,
                    "water_quality": water_data is not None,
                    "waste": waste_status is not None,
                    "energy": energy_balance > 0,
                    "noise": noise is not None,
                    "traffic": traffic is not None,
                },
            },
        )

        db.add(state)
        return state

    async def _get_avg_reading(
        self, db: AsyncSession, sensor_type: str, since: datetime
    ):
        """Get average reading value for a sensor type."""
        result = await db.execute(
            select(func.avg(SensorReading.value))
            .join(Sensor, SensorReading.sensor_id == Sensor.id)
            .where(Sensor.sensor_type == sensor_type)
            .where(SensorReading.timestamp >= since)
        )
        return result.scalar()

    async def _get_sum_reading(
        self, db: AsyncSession, sensor_type: str, since: datetime
    ):
        """Get sum of readings for a sensor type."""
        result = await db.execute(
            select(func.sum(SensorReading.value))
            .join(Sensor, SensorReading.sensor_id == Sensor.id)
            .where(Sensor.sensor_type == sensor_type)
            .where(SensorReading.timestamp >= since)
        )
        return result.scalar()

    async def _get_waste_status(self, db: AsyncSession):
        """Get average fill level across all smart bins."""
        result = await db.execute(
            select(func.avg(SmartBin.current_level))
        )
        return result.scalar()

    def _calculate_water_score(self, ph_value) -> float:
        """Convert raw water pH to 0-100 quality score."""
        if ph_value is None:
            return 80.0
        # Ideal pH: 7.0, acceptable 6.5-8.5
        deviation = abs(ph_value - 7.0)
        if deviation <= 0.5:
            return 100.0
        elif deviation <= 1.5:
            return 100 - (deviation - 0.5) * 20
        else:
            return max(0, 100 - deviation * 25)

    def _noise_to_score(self, noise_db) -> float:
        """Convert noise dB to 0-100 index (100 = quiet)."""
        if noise_db is None:
            return 60.0
        return max(0, min(100, 100 - (noise_db - 30) * 1.5))

    def _calculate_health_score(self, aqi, water, waste, noise) -> float:
        """Weighted average of all environmental scores."""
        scores = []
        weights = []

        if aqi is not None:
            # AQI < 50 = excellent, > 200 = hazardous
            aqi_score = max(0, 100 - aqi * 0.5)
            scores.append(aqi_score)
            weights.append(0.3)

        if water is not None:
            scores.append(water)
            weights.append(0.2)

        if waste is not None:
            waste_score = 100 - waste  # lower fill = better
            scores.append(waste_score)
            weights.append(0.25)

        if noise is not None:
            scores.append(self._noise_to_score(noise))
            weights.append(0.15)

        if not scores:
            return 75.0

        total_weight = sum(weights)
        return sum(s * w for s, w in zip(scores, weights)) / total_weight

    async def _check_thresholds(
        self, db: AsyncSession, zone: str,
        aqi, water_ph, noise, waste_level
    ) -> list:
        """Check values against thresholds and create alerts."""
        alerts = []

        if aqi and aqi > self.ALERT_THRESHOLDS["aqi"]["critical"]:
            alert = Alert(
                zone=zone,
                severity="critical",
                title="Air Quality Critical",
                message=f"AQI has reached {aqi:.0f} — above safe threshold of 200.",
                category="air_quality",
                auto_generated=True,
            )
            db.add(alert)
            alerts.append(alert)
        elif aqi and aqi > self.ALERT_THRESHOLDS["aqi"]["warning"]:
            alert = Alert(
                zone=zone,
                severity="warning",
                title="Air Quality Warning",
                message=f"AQI at {aqi:.0f} — approaching unhealthy levels.",
                category="air_quality",
                auto_generated=True,
            )
            db.add(alert)
            alerts.append(alert)

        if waste_level and waste_level > self.ALERT_THRESHOLDS["waste_level"]["critical"]:
            alert = Alert(
                zone=zone,
                severity="critical",
                title="Waste Bins Critical",
                message=f"Average bin level at {waste_level:.0f}% — immediate collection needed.",
                category="waste",
                auto_generated=True,
            )
            db.add(alert)
            alerts.append(alert)

        if noise and noise > self.ALERT_THRESHOLDS["noise_db"]["critical"]:
            alert = Alert(
                zone=zone,
                severity="warning",
                title="High Noise Level",
                message=f"Noise at {noise:.0f} dB — exceeds comfortable threshold.",
                category="noise",
                auto_generated=True,
            )
            db.add(alert)
            alerts.append(alert)

        return alerts
