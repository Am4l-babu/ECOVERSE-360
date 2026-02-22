"""
ECOVERSE 360 — API Router Registry
All API routes consolidated here.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.sensors import router as sensors_router
from app.api.ecopoints import router as ecopoints_router
from app.api.dashboard import router as dashboard_router
from app.api.digital_twin import router as digital_twin_router
from app.api.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(sensors_router)
api_router.include_router(ecopoints_router)
api_router.include_router(dashboard_router)
api_router.include_router(digital_twin_router)
api_router.include_router(users_router)
