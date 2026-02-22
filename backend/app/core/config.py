"""
ECOVERSE 360 — Configuration Module
Central configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "Ecoverse 360"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    API_PREFIX: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://ecoverse:ecoverse360@localhost:5432/ecoverse360"
    DATABASE_SYNC_URL: str = "postgresql://ecoverse:ecoverse360@localhost:5432/ecoverse360"

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── MQTT ─────────────────────────────────────────────────────────────
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""

    # ── JWT Authentication ───────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ── ML ───────────────────────────────────────────────────────────────
    ML_MODEL_PATH: str = "./ml_models"
    PREDICTION_INTERVAL_MINUTES: int = 15

    # ── EcoPoints Defaults ───────────────────────────────────────────────
    DEFAULT_RECYCLE_POINTS: int = 10
    DEFAULT_CARPOOL_POINTS: int = 15
    DEFAULT_BIN_DEPOSIT_POINTS: int = 5
    DEFAULT_WORKSHOP_POINTS: int = 25
    DEFAULT_SENSOR_DEPLOY_POINTS: int = 50
    DEFAULT_TREE_PLANT_POINTS: int = 30
    DEFAULT_CHALLENGE_POINTS: int = 20

    # ── Logging ──────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
