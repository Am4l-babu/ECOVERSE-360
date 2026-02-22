"""
ECOVERSE 360 — Auth API
Registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.models.ecopoints import EcoPointBalance
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check existing
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        department=data.department,
        hostel=data.hostel,
    )
    db.add(user)
    await db.flush()

    # Initialize point balance
    balance = EcoPointBalance(user_id=user.id)
    db.add(balance)
    await db.flush()

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT token."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: str = None,
    department: str = None,
    hostel: str = None,
    avatar_url: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    if full_name:
        current_user.full_name = full_name
    if department:
        current_user.department = department
    if hostel:
        current_user.hostel = hostel
    if avatar_url:
        current_user.avatar_url = avatar_url

    db.add(current_user)
    await db.flush()

    return UserResponse.model_validate(current_user)
