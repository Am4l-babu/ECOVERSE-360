"""
ECOVERSE 360 — Digital Twin API
Real-time campus simulation, what-if scenarios, and predictive state.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import DigitalTwinState
from app.schemas import (
    DigitalTwinStateResponse,
    SimulationRequest,
    SimulationResult,
)

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin"])


@router.get("/state", response_model=DigitalTwinStateResponse)
async def get_current_state(
    zone: str = "campus",
    db: AsyncSession = Depends(get_db),
):
    """Get the latest Digital Twin state for a zone."""
    result = await db.execute(
        select(DigitalTwinState)
        .where(DigitalTwinState.zone == zone)
        .order_by(DigitalTwinState.timestamp.desc())
        .limit(1)
    )
    state = result.scalar_one_or_none()

    if not state:
        # Return default state if none exists
        return DigitalTwinStateResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            zone=zone,
            timestamp="2026-01-01T00:00:00Z",
            overall_health=75.0,
            aqi_index=50.0,
            water_quality=80.0,
            waste_status=60.0,
            energy_balance=0.0,
            carbon_net=0.0,
            biodiversity=70.0,
            noise_index=40.0,
            foot_traffic=0,
            predicted_aqi=None,
            predicted_waste=None,
            predicted_water=None,
            predicted_energy=None,
        )

    return DigitalTwinStateResponse.model_validate(state)


@router.get("/history", response_model=List[DigitalTwinStateResponse])
async def get_state_history(
    zone: str = "campus",
    limit: int = Query(48, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get historical Digital Twin snapshots."""
    result = await db.execute(
        select(DigitalTwinState)
        .where(DigitalTwinState.zone == zone)
        .order_by(DigitalTwinState.timestamp.desc())
        .limit(limit)
    )

    return [
        DigitalTwinStateResponse.model_validate(s) for s in result.scalars().all()
    ]


@router.post("/simulate", response_model=SimulationResult)
async def run_simulation(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run a what-if scenario simulation.
    
    Example: "If 30% of students start carpooling, how much CO2 is saved in 6 months?"
    """
    from app.digital_twin.simulator import Simulator

    simulator = Simulator()
    result = await simulator.run_scenario(request, db)

    return result


@router.get("/zones")
async def list_zones(db: AsyncSession = Depends(get_db)):
    """List all monitored zones."""
    from sqlalchemy import distinct

    result = await db.execute(
        select(distinct(DigitalTwinState.zone))
    )

    zones = [row[0] for row in result.all()]
    return {"zones": zones if zones else ["campus"]}


@router.get("/alerts")
async def get_active_alerts(
    zone: str = "campus",
    db: AsyncSession = Depends(get_db),
):
    """Get active alerts from Digital Twin analysis."""
    from app.models.entities import Alert

    result = await db.execute(
        select(Alert)
        .where(Alert.is_resolved == False)
        .where((Alert.zone == zone) | (Alert.zone == None))
        .order_by(Alert.created_at.desc())
        .limit(20)
    )

    alerts = result.scalars().all()
    return {
        "zone": zone,
        "active_count": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "category": a.category,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
    }
