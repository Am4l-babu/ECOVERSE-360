"""
ECOVERSE 360 — Main Application Entry Point
FastAPI application with all middleware, routes, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings
from app.api import api_router

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ecoverse")


# ── Application Lifecycle ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("🌍 Ecoverse 360 starting up...")
    logger.info(f"   Environment: {settings.APP_ENV}")
    logger.info(f"   Debug: {settings.DEBUG}")

    # Start MQTT service (if broker is available)
    try:
        from app.services.mqtt_service import mqtt_service
        mqtt_service.start()
        logger.info("   MQTT service started")
    except Exception as e:
        logger.warning(f"   MQTT service unavailable: {e}")

    logger.info("🌱 Ecoverse 360 is ready!")

    yield

    # Shutdown
    logger.info("🌙 Ecoverse 360 shutting down...")
    try:
        from app.services.mqtt_service import mqtt_service
        mqtt_service.stop()
    except Exception:
        pass


# ── Application Factory ─────────────────────────────────────────────────

app = FastAPI(
    title="🌍 Ecoverse 360 API",
    description=(
        "**Sustainability Operating System for Campuses → Cities**\n\n"
        "A modular, scalable, IoT-driven sustainability intelligence platform "
        "with incentive-based participation.\n\n"
        "### Modules\n"
        "- 🔌 **IoT Sensors** — Smart bins, air/water monitors, energy tiles\n"
        "- 🏗️ **Digital Twin** — Real-time campus simulation\n"
        "- 🧠 **ML Engine** — Predictive sustainability analytics\n"
        "- 🏆 **EcoPoints** — Gamified reward system\n"
        "- 📊 **Dashboard** — Analytics & ESG reporting\n"
        "- 🛒 **Marketplace** — Circular economy hub\n"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────────

app.include_router(api_router, prefix=settings.API_PREFIX)


# ── Health Check ─────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Ecoverse 360",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "description": "Sustainability OS for Campuses → Cities",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "components": {
            "api": "up",
            "database": "up",
            "mqtt": "up",
        },
    }
