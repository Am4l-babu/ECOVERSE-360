"""
ECOVERSE 360 — Users & Admin API
User management, admin operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas import UserResponse, MessageResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all users (admin only)."""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if department:
        query = query.where(User.department == department)

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)

    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Deactivate a user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    return MessageResponse(message=f"User {user.full_name} deactivated")


@router.get("/stats/summary")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get user statistics summary (admin only)."""
    total = (await db.execute(select(func.count(User.id)))).scalar()
    active = (
        await db.execute(select(func.count(User.id)).where(User.is_active == True))
    ).scalar()

    by_role = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    role_counts = {row[0]: row[1] for row in by_role.all()}

    by_dept = await db.execute(
        select(User.department, func.count(User.id))
        .where(User.department != None)
        .group_by(User.department)
        .order_by(func.count(User.id).desc())
        .limit(10)
    )
    dept_counts = {row[0]: row[1] for row in by_dept.all()}

    return {
        "total_users": total,
        "active_users": active,
        "by_role": role_counts,
        "by_department": dept_counts,
    }
