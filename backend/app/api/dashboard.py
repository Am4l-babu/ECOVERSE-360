"""
ECOVERSE 360 — Dashboard API
Aggregated analytics, stats, and campus overview.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import (
    User, Sensor, EcoPoint, EcoPointBalance, Activity,
    SmartBin, CarpoolTrip, DigitalTwinState, CarbonFootprint,
    EnvironmentalData, Tree, Challenge, FoodWasteLog,
)
from app.schemas import DashboardStats, ZoneStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get high-level campus sustainability statistics."""
    # Total users
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    # Active sensors
    active_sensors = (
        await db.execute(
            select(func.count(Sensor.id)).where(Sensor.status == "online")
        )
    ).scalar() or 0

    # Total EcoPoints earned
    total_ecopoints = (
        await db.execute(
            select(func.coalesce(func.sum(EcoPointBalance.total_earned), 0))
        )
    ).scalar() or 0

    # Carbon saved
    carbon_saved = (
        await db.execute(
            select(func.coalesce(func.sum(EcoPointBalance.lifetime_carbon), 0))
        )
    ).scalar() or 0

    # Waste diverted (sum of recycling activities quantity)
    waste_diverted = (
        await db.execute(
            select(func.coalesce(func.sum(Activity.quantity), 0)).where(
                Activity.activity_type.in_(["recycle", "compost_contribute", "bin_deposit"])
            )
        )
    ).scalar() or 0

    # Trees planted
    trees_planted = (await db.execute(select(func.count(Tree.id)))).scalar() or 0

    # Active challenges
    active_challenges = (
        await db.execute(
            select(func.count(Challenge.id)).where(Challenge.is_active == True)
        )
    ).scalar() or 0

    # Carpool trips
    carpool_trips = (
        await db.execute(
            select(func.count(CarpoolTrip.id)).where(
                CarpoolTrip.status.in_(["completed", "in_progress"])
            )
        )
    ).scalar() or 0

    # Overall health score from latest digital twin
    dt_result = await db.execute(
        select(DigitalTwinState.overall_health)
        .order_by(DigitalTwinState.timestamp.desc())
        .limit(1)
    )
    overall_health = dt_result.scalar() or 75.0

    return DashboardStats(
        total_users=total_users,
        active_sensors=active_sensors,
        total_ecopoints=total_ecopoints,
        carbon_saved_kg=round(carbon_saved, 2),
        waste_diverted_kg=round(waste_diverted, 2),
        water_saved_liters=0,  # calculated from activities
        trees_planted=trees_planted,
        active_challenges=active_challenges,
        carpool_trips=carpool_trips,
        overall_health_score=round(overall_health, 1),
    )


@router.get("/zones", response_model=List[ZoneStats])
async def get_zone_stats(db: AsyncSession = Depends(get_db)):
    """Get environmental stats per zone."""
    # Get latest reading per zone
    subquery = (
        select(
            EnvironmentalData.zone,
            func.max(EnvironmentalData.timestamp).label("latest"),
        )
        .group_by(EnvironmentalData.zone)
        .subquery()
    )

    result = await db.execute(
        select(EnvironmentalData)
        .join(
            subquery,
            (EnvironmentalData.zone == subquery.c.zone)
            & (EnvironmentalData.timestamp == subquery.c.latest),
        )
    )

    zones = []
    for env in result.scalars().all():
        zones.append(
            ZoneStats(
                zone=env.zone,
                aqi=env.aqi,
                temperature=env.temperature,
                humidity=env.humidity,
                waste_level=env.waste_level_pct,
                noise_db=env.noise_db,
                energy_generated_wh=env.energy_generated_wh,
                carbon_net=(env.carbon_emission_kg or 0) - (env.carbon_offset_kg or 0),
                health_score=None,
            )
        )

    return zones


@router.get("/trends")
async def get_trends(
    metric: str = Query("aqi", description="Metric to track: aqi, temperature, waste, carbon, energy"),
    zone: str = "campus",
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get time-series trends for a specific metric."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    metric_column = {
        "aqi": EnvironmentalData.aqi,
        "temperature": EnvironmentalData.temperature,
        "humidity": EnvironmentalData.humidity,
        "waste": EnvironmentalData.waste_level_pct,
        "carbon": EnvironmentalData.carbon_emission_kg,
        "energy": EnvironmentalData.energy_generated_wh,
        "noise": EnvironmentalData.noise_db,
        "water_ph": EnvironmentalData.water_ph,
    }.get(metric)

    if not metric_column:
        return {"error": f"Unknown metric: {metric}"}

    result = await db.execute(
        select(EnvironmentalData.timestamp, metric_column)
        .where(EnvironmentalData.zone == zone)
        .where(EnvironmentalData.timestamp >= since)
        .order_by(EnvironmentalData.timestamp.asc())
    )

    data_points = [
        {"timestamp": row[0].isoformat(), "value": row[1]}
        for row in result.all()
        if row[1] is not None
    ]

    return {
        "metric": metric,
        "zone": zone,
        "period_days": days,
        "data_points": data_points,
        "count": len(data_points),
    }


@router.get("/activity-feed")
async def get_activity_feed(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get recent campus activity feed."""
    result = await db.execute(
        select(Activity, User.full_name)
        .join(User, Activity.user_id == User.id)
        .order_by(Activity.created_at.desc())
        .limit(limit)
    )

    feed = []
    for activity, name in result.all():
        feed.append({
            "id": str(activity.id),
            "user": name,
            "type": activity.activity_type,
            "title": activity.title,
            "carbon_saved_kg": activity.carbon_saved_kg,
            "points": activity.points_awarded,
            "created_at": activity.created_at.isoformat(),
        })

    return {"feed": feed, "count": len(feed)}


@router.get("/carbon-summary")
async def get_carbon_summary(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get carbon footprint summary."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.coalesce(func.sum(CarbonFootprint.total_kg), 0).label("total_emission"),
            func.coalesce(func.sum(CarbonFootprint.offset_kg), 0).label("total_offset"),
            func.coalesce(func.sum(CarbonFootprint.transport_kg), 0).label("transport"),
            func.coalesce(func.sum(CarbonFootprint.electricity_kg), 0).label("electricity"),
            func.coalesce(func.sum(CarbonFootprint.food_kg), 0).label("food"),
            func.coalesce(func.sum(CarbonFootprint.waste_kg), 0).label("waste"),
            func.coalesce(func.sum(CarbonFootprint.water_kg), 0).label("water"),
        ).where(CarbonFootprint.created_at >= since)
    )
    row = result.one()

    return {
        "period_days": days,
        "total_emission_kg": round(row.total_emission, 2),
        "total_offset_kg": round(row.total_offset, 2),
        "net_carbon_kg": round(row.total_emission - row.total_offset, 2),
        "breakdown": {
            "transport_kg": round(row.transport, 2),
            "electricity_kg": round(row.electricity, 2),
            "food_kg": round(row.food, 2),
            "waste_kg": round(row.waste, 2),
            "water_kg": round(row.water, 2),
        },
    }


@router.get("/food-waste-summary")
async def get_food_waste_summary(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get food waste summary across canteens."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            FoodWasteLog.location,
            func.sum(FoodWasteLog.waste_kg).label("total_waste"),
            func.sum(FoodWasteLog.composted_kg).label("total_composted"),
            func.count(FoodWasteLog.id).label("entries"),
        )
        .where(FoodWasteLog.created_at >= since)
        .group_by(FoodWasteLog.location)
    )

    locations = []
    for row in result.all():
        locations.append({
            "location": row.location,
            "total_waste_kg": round(row.total_waste, 2),
            "composted_kg": round(row.total_composted, 2),
            "diversion_rate": round(
                (row.total_composted / row.total_waste * 100) if row.total_waste > 0 else 0, 1
            ),
            "entries": row.entries,
        })

    return {"period_days": days, "locations": locations}


@router.get("/bins-status")
async def get_bins_status(db: AsyncSession = Depends(get_db)):
    """Get current status of all smart bins."""
    result = await db.execute(
        select(SmartBin).order_by(SmartBin.current_level.desc())
    )
    bins = result.scalars().all()

    return {
        "total_bins": len(bins),
        "full_bins": sum(1 for b in bins if b.is_full),
        "average_level": round(
            sum(b.current_level for b in bins) / len(bins) if bins else 0, 1
        ),
        "bins": [
            {
                "id": str(b.id),
                "code": b.bin_code,
                "category": b.category,
                "location": b.location_name,
                "level_pct": b.current_level,
                "weight_kg": b.weight_kg,
                "is_full": b.is_full,
            }
            for b in bins
        ],
    }
