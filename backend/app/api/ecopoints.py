"""
ECOVERSE 360 — EcoPoints API
Award, query, spend points. Leaderboards.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.ecopoints import EcoPoint, EcoPointBalance
from app.schemas import (
    EcoPointAward,
    EcoPointResponse,
    EcoPointBalanceResponse,
    LeaderboardEntry,
    MessageResponse,
)

router = APIRouter(prefix="/ecopoints", tags=["EcoPoints & Rewards"])


@router.post("/award", response_model=EcoPointResponse)
async def award_points(
    data: EcoPointAward,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Award EcoPoints to a user (admin only)."""
    # Verify user exists
    result = await db.execute(select(User).where(User.id == data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create point record
    point = EcoPoint(
        user_id=data.user_id,
        points=data.points,
        category=data.category,
        description=data.description,
        carbon_impact=data.carbon_impact,
        activity_ref=data.activity_ref,
        verified=True,
        verified_by=admin.id,
    )
    db.add(point)

    # Update balance
    balance = await _get_or_create_balance(db, data.user_id)
    balance.total_earned += data.points
    balance.current_balance += data.points
    balance.lifetime_carbon += data.carbon_impact
    balance.level = _calculate_level(balance.total_earned)
    db.add(balance)

    await db.flush()

    return EcoPointResponse.model_validate(point)


@router.post("/earn", response_model=EcoPointResponse)
async def earn_points(
    category: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Self-report an eco-activity and earn pending points."""
    from app.core.config import get_settings

    settings = get_settings()
    points_map = {
        "recycling": settings.DEFAULT_RECYCLE_POINTS,
        "carpool": settings.DEFAULT_CARPOOL_POINTS,
        "smart_bin": settings.DEFAULT_BIN_DEPOSIT_POINTS,
        "workshop": settings.DEFAULT_WORKSHOP_POINTS,
        "tree_planting": settings.DEFAULT_TREE_PLANT_POINTS,
        "sensor_contribution": settings.DEFAULT_SENSOR_DEPLOY_POINTS,
    }
    points = points_map.get(category, 5)

    point = EcoPoint(
        user_id=current_user.id,
        points=points,
        category=category,
        description=description,
        verified=False,  # needs admin approval
    )
    db.add(point)
    await db.flush()

    return EcoPointResponse.model_validate(point)


@router.get("/balance", response_model=EcoPointBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's EcoPoint balance."""
    balance = await _get_or_create_balance(db, current_user.id)
    response = EcoPointBalanceResponse.model_validate(balance)
    response.level_name = balance.level_name
    return response


@router.get("/balance/{user_id}", response_model=EcoPointBalanceResponse)
async def get_user_balance(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user's EcoPoint balance."""
    balance = await _get_or_create_balance(db, user_id)
    response = EcoPointBalanceResponse.model_validate(balance)
    response.level_name = balance.level_name
    return response


@router.get("/history", response_model=List[EcoPointResponse])
async def get_history(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's point transaction history."""
    query = select(EcoPoint).where(EcoPoint.user_id == current_user.id)

    if category:
        query = query.where(EcoPoint.category == category)

    query = query.order_by(EcoPoint.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return [EcoPointResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    department: Optional[str] = None,
    hostel: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get EcoPoints leaderboard."""
    query = (
        select(
            User.id,
            User.full_name,
            User.department,
            User.hostel,
            EcoPointBalance.total_earned,
            EcoPointBalance.current_balance,
            EcoPointBalance.lifetime_carbon,
            EcoPointBalance.level,
        )
        .join(EcoPointBalance, User.id == EcoPointBalance.user_id)
        .where(User.is_active == True)
        .where(User.role == "student")
    )

    if department:
        query = query.where(User.department == department)
    if hostel:
        query = query.where(User.hostel == hostel)

    query = query.order_by(desc(EcoPointBalance.total_earned)).limit(limit)
    result = await db.execute(query)

    entries = []
    for i, row in enumerate(result.all(), 1):
        entries.append(
            LeaderboardEntry(
                rank=i,
                user_id=row.id,
                full_name=row.full_name,
                department=row.department,
                hostel=row.hostel,
                total_earned=row.total_earned or 0,
                current_balance=row.current_balance or 0,
                carbon_saved_kg=row.lifetime_carbon or 0,
                level=row.level or 1,
            )
        )

    return entries


@router.post("/spend", response_model=MessageResponse)
async def spend_points(
    points: int,
    description: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Spend EcoPoints (for marketplace, rewards, etc.)."""
    balance = await _get_or_create_balance(db, current_user.id)

    if balance.current_balance < points:
        raise HTTPException(status_code=400, detail="Insufficient EcoPoints")

    balance.current_balance -= points
    balance.total_spent += points
    db.add(balance)

    # Log the spend
    point = EcoPoint(
        user_id=current_user.id,
        points=-points,
        category="bonus",
        description=f"Spent: {description}",
        verified=True,
    )
    db.add(point)

    return MessageResponse(message=f"Spent {points} EcoPoints: {description}")


# ── Helpers ──────────────────────────────────────────────────────────────

async def _get_or_create_balance(db: AsyncSession, user_id: UUID) -> EcoPointBalance:
    result = await db.execute(
        select(EcoPointBalance).where(EcoPointBalance.user_id == user_id)
    )
    balance = result.scalar_one_or_none()
    if not balance:
        balance = EcoPointBalance(user_id=user_id)
        db.add(balance)
        await db.flush()
    return balance


def _calculate_level(total_earned: int) -> int:
    thresholds = [0, 100, 300, 700, 1500, 3000, 6000, 12000]
    level = 1
    for i, threshold in enumerate(thresholds):
        if total_earned >= threshold:
            level = i + 1
    return level
