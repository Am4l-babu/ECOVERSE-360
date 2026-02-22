"""
ECOVERSE 360 — Sensors API
IoT device registration, data ingestion, and querying.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.sensor import Sensor, SensorReading
from app.models.user import User
from app.schemas import (
    SensorCreate,
    SensorResponse,
    SensorReadingCreate,
    SensorReadingResponse,
    SensorDataBatch,
    MessageResponse,
)

router = APIRouter(prefix="/sensors", tags=["Sensors & IoT"])


# ── Sensor Management ───────────────────────────────────────────────────

@router.post("/", response_model=SensorResponse, status_code=201)
async def register_sensor(
    data: SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new IoT sensor/device."""
    existing = await db.execute(
        select(Sensor).where(Sensor.device_id == data.device_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Device ID already registered")

    sensor = Sensor(
        device_id=data.device_id,
        sensor_type=data.sensor_type,
        name=data.name,
        description=data.description,
        location_name=data.location_name,
        latitude=data.latitude,
        longitude=data.longitude,
        building=data.building,
        floor=data.floor,
        firmware_ver=data.firmware_ver,
        installed_by=current_user.id,
        status="online",
        last_seen=datetime.now(timezone.utc),
    )
    db.add(sensor)
    await db.flush()

    return SensorResponse.model_validate(sensor)


@router.get("/", response_model=List[SensorResponse])
async def list_sensors(
    sensor_type: Optional[str] = None,
    status: Optional[str] = None,
    building: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all sensors with optional filters."""
    query = select(Sensor)

    if sensor_type:
        query = query.where(Sensor.sensor_type == sensor_type)
    if status:
        query = query.where(Sensor.status == status)
    if building:
        query = query.where(Sensor.building == building)

    query = query.offset(skip).limit(limit).order_by(Sensor.created_at.desc())
    result = await db.execute(query)

    return [SensorResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(sensor_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get sensor details by ID."""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return SensorResponse.model_validate(sensor)


@router.delete("/{sensor_id}", response_model=MessageResponse)
async def delete_sensor(
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a sensor (admin only)."""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    await db.delete(sensor)
    return MessageResponse(message="Sensor deleted successfully")


# ── Sensor Data Ingestion ────────────────────────────────────────────────

@router.post("/data", response_model=MessageResponse)
async def ingest_reading(
    data: SensorReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a single sensor reading.
    Accepts either sensor_id (UUID) or device_id (string).
    """
    sensor_id = data.sensor_id
    if not sensor_id and data.device_id:
        result = await db.execute(
            select(Sensor).where(Sensor.device_id == data.device_id)
        )
        sensor = result.scalar_one_or_none()
        if not sensor:
            raise HTTPException(status_code=404, detail=f"Device '{data.device_id}' not found")
        sensor_id = sensor.id
        sensor.last_seen = datetime.now(timezone.utc)
        sensor.status = "online"
    elif sensor_id:
        result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
        sensor = result.scalar_one_or_none()
        if sensor:
            sensor.last_seen = datetime.now(timezone.utc)
            sensor.status = "online"

    reading = SensorReading(
        sensor_id=sensor_id,
        value=data.value,
        unit=data.unit,
        quality=data.quality,
        metadata_=data.metadata,
        timestamp=data.timestamp or datetime.now(timezone.utc),
    )
    db.add(reading)

    return MessageResponse(message="Reading ingested successfully")


@router.post("/data/batch", response_model=MessageResponse)
async def ingest_batch(
    data: SensorDataBatch,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a batch of readings from one device."""
    result = await db.execute(
        select(Sensor).where(Sensor.device_id == data.device_id)
    )
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Device '{data.device_id}' not found")

    sensor.last_seen = datetime.now(timezone.utc)
    sensor.status = "online"

    for r in data.readings:
        reading = SensorReading(
            sensor_id=sensor.id,
            value=r.value,
            unit=r.unit,
            quality=r.quality,
            metadata_=r.metadata,
            timestamp=r.timestamp or datetime.now(timezone.utc),
        )
        db.add(reading)

    return MessageResponse(
        message=f"{len(data.readings)} readings ingested for {data.device_id}"
    )


# ── Sensor Data Queries ─────────────────────────────────────────────────

@router.get("/{sensor_id}/readings", response_model=List[SensorReadingResponse])
async def get_readings(
    sensor_id: UUID,
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """Get recent readings for a sensor."""
    from datetime import timedelta

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id)
        .where(SensorReading.timestamp >= since)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
    )
    result = await db.execute(query)

    return [SensorReadingResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/{sensor_id}/stats")
async def get_sensor_stats(
    sensor_id: UUID,
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    """Get statistical summary of sensor readings."""
    from datetime import timedelta

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(
            func.count(SensorReading.id).label("count"),
            func.avg(SensorReading.value).label("avg"),
            func.min(SensorReading.value).label("min"),
            func.max(SensorReading.value).label("max"),
            func.stddev(SensorReading.value).label("stddev"),
        )
        .where(SensorReading.sensor_id == sensor_id)
        .where(SensorReading.timestamp >= since)
    )
    row = result.one()

    return {
        "sensor_id": str(sensor_id),
        "period_hours": hours,
        "count": row.count,
        "average": round(row.avg, 3) if row.avg else None,
        "minimum": round(row.min, 3) if row.min else None,
        "maximum": round(row.max, 3) if row.max else None,
        "std_deviation": round(row.stddev, 3) if row.stddev else None,
    }
