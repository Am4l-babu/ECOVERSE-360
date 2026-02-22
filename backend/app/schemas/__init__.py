"""
ECOVERSE 360 — Pydantic Schemas
Request/Response validation models for all API endpoints.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: str = "student"
    department: Optional[str] = None
    hostel: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    department: Optional[str]
    hostel: Optional[str]
    avatar_url: Optional[str]
    eco_score: float
    carbon_score: float
    water_score: float
    waste_score: float
    energy_score: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Sensor ───────────────────────────────────────────────────────────────

class SensorCreate(BaseModel):
    device_id: str
    sensor_type: str
    name: str
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    firmware_ver: Optional[str] = None


class SensorResponse(BaseModel):
    id: UUID
    device_id: str
    sensor_type: str
    name: str
    description: Optional[str]
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    building: Optional[str]
    status: str
    battery_level: Optional[float]
    last_seen: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    sensor_id: Optional[UUID] = None
    device_id: Optional[str] = None  # alternative to sensor_id
    value: float
    unit: str
    quality: float = 1.0
    metadata: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: UUID
    timestamp: datetime
    value: float
    unit: str
    quality: float

    class Config:
        from_attributes = True


class SensorDataBatch(BaseModel):
    """Batch of readings from an IoT device."""
    device_id: str
    readings: List[SensorReadingCreate]


# ── EcoPoints ────────────────────────────────────────────────────────────

class EcoPointAward(BaseModel):
    user_id: UUID
    points: int = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    carbon_impact: float = 0
    activity_ref: Optional[UUID] = None


class EcoPointResponse(BaseModel):
    id: UUID
    user_id: UUID
    points: int
    category: str
    description: Optional[str]
    carbon_impact: float
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EcoPointBalanceResponse(BaseModel):
    user_id: UUID
    total_earned: int
    total_spent: int
    current_balance: int
    lifetime_carbon: float
    level: int
    level_name: str
    streak_days: int
    last_activity: Optional[datetime]

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    full_name: str
    department: Optional[str]
    hostel: Optional[str]
    total_earned: int
    current_balance: int
    carbon_saved_kg: float
    level: int


# ── Activity ─────────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    activity_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    quantity: float = 1
    unit: Optional[str] = None
    carbon_saved_kg: float = 0
    proof_url: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ActivityResponse(BaseModel):
    id: UUID
    user_id: UUID
    activity_type: str
    title: Optional[str]
    description: Optional[str]
    quantity: float
    carbon_saved_kg: float
    points_awarded: int
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Smart Bin ────────────────────────────────────────────────────────────

class SmartBinCreate(BaseModel):
    sensor_id: Optional[UUID] = None
    bin_code: str
    category: str
    location_name: Optional[str] = None
    building: Optional[str] = None
    capacity_liters: float = 120
    alert_threshold: float = 80
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SmartBinResponse(BaseModel):
    id: UUID
    bin_code: str
    category: str
    location_name: Optional[str]
    building: Optional[str]
    capacity_liters: float
    current_level: float
    weight_kg: float
    is_full: bool
    last_emptied: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SmartBinUpdate(BaseModel):
    current_level: Optional[float] = None
    weight_kg: Optional[float] = None
    is_full: Optional[bool] = None


# ── Carpool ──────────────────────────────────────────────────────────────

class CarpoolTripCreate(BaseModel):
    origin: str
    destination: str
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None
    departure_time: datetime
    seats_total: int = 4
    distance_km: Optional[float] = None
    vehicle_type: Optional[str] = None
    notes: Optional[str] = None


class CarpoolTripResponse(BaseModel):
    id: UUID
    driver_id: UUID
    origin: str
    destination: str
    departure_time: datetime
    seats_total: int
    seats_available: int
    distance_km: Optional[float]
    co2_saved_kg: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Carbon Footprint ────────────────────────────────────────────────────

class CarbonFootprintCreate(BaseModel):
    zone: Optional[str] = None
    date: Optional[date] = None
    transport_kg: float = 0
    electricity_kg: float = 0
    food_kg: float = 0
    waste_kg: float = 0
    water_kg: float = 0
    offset_kg: float = 0


class CarbonFootprintResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    zone: Optional[str]
    date: date
    transport_kg: float
    electricity_kg: float
    food_kg: float
    waste_kg: float
    water_kg: float
    total_kg: float
    offset_kg: float
    net_kg: float

    class Config:
        from_attributes = True


# ── Digital Twin ─────────────────────────────────────────────────────────

class DigitalTwinStateResponse(BaseModel):
    id: UUID
    zone: str
    timestamp: datetime
    overall_health: Optional[float]
    aqi_index: Optional[float]
    water_quality: Optional[float]
    waste_status: Optional[float]
    energy_balance: Optional[float]
    carbon_net: Optional[float]
    biodiversity: Optional[float]
    noise_index: Optional[float]
    foot_traffic: Optional[int]
    predicted_aqi: Optional[float]
    predicted_waste: Optional[float]
    predicted_water: Optional[float]
    predicted_energy: Optional[float]
    active_alerts: List[Dict[str, Any]] = []
    simulation_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class SimulationRequest(BaseModel):
    """What-if scenario simulation."""
    zone: str = "campus"
    food_waste_change_pct: float = 0       # e.g., -20 means 20% reduction
    carpool_adoption_pct: float = 0        # e.g., 30 means 30% adopt
    recycling_rate_change_pct: float = 0
    energy_reduction_pct: float = 0
    tree_planting_count: int = 0
    water_saving_pct: float = 0
    timeframe_months: int = 6


class SimulationResult(BaseModel):
    zone: str
    timeframe_months: int
    carbon_saved_kg: float
    water_saved_liters: float
    waste_diverted_kg: float
    energy_saved_kwh: float
    eco_score_change: float
    summary: str
    recommendations: List[str]


# ── Dashboard ────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_users: int
    active_sensors: int
    total_ecopoints: int
    carbon_saved_kg: float
    waste_diverted_kg: float
    water_saved_liters: float
    trees_planted: int
    active_challenges: int
    carpool_trips: int
    overall_health_score: float


class ZoneStats(BaseModel):
    zone: str
    aqi: Optional[float]
    temperature: Optional[float]
    humidity: Optional[float]
    waste_level: Optional[float]
    noise_db: Optional[float]
    energy_generated_wh: Optional[float]
    carbon_net: Optional[float]
    health_score: Optional[float]


# ── Challenges ───────────────────────────────────────────────────────────

class ChallengeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: float
    target_unit: Optional[str] = None
    reward_points: int
    start_date: datetime
    end_date: datetime
    scope: str = "individual"
    max_participants: Optional[int] = None


class ChallengeResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    category: Optional[str]
    target_value: float
    reward_points: int
    start_date: datetime
    end_date: datetime
    scope: str
    is_active: bool
    participants_count: int = 0

    class Config:
        from_attributes = True


# ── Marketplace ──────────────────────────────────────────────────────────

class MarketplaceListingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price_ecopoints: int = 0
    price_inr: float = 0
    image_urls: List[str] = []
    quantity: int = 1
    carbon_saved_kg: float = 0
    material_source: Optional[str] = None


class MarketplaceListingResponse(BaseModel):
    id: UUID
    seller_id: UUID
    title: str
    description: Optional[str]
    category: Optional[str]
    price_ecopoints: int
    price_inr: float
    quantity: int
    status: str
    carbon_saved_kg: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Food Waste ───────────────────────────────────────────────────────────

class FoodWasteLogCreate(BaseModel):
    location: str
    date: Optional[date] = None
    meal_type: Optional[str] = None
    waste_kg: float
    servings_prepared: Optional[int] = None
    servings_consumed: Optional[int] = None
    waste_type: Optional[str] = None
    composted_kg: float = 0


# ── Farm ─────────────────────────────────────────────────────────────────

class FarmPlotCreate(BaseModel):
    name: str
    location: Optional[str] = None
    area_sqm: Optional[float] = None
    crop_type: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest: Optional[date] = None


class FarmPlotResponse(BaseModel):
    id: UUID
    name: str
    location: Optional[str]
    area_sqm: Optional[float]
    crop_type: Optional[str]
    planting_date: Optional[date]
    expected_harvest: Optional[date]
    status: str
    carbon_offset: float

    class Config:
        from_attributes = True


# ── Generic ──────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
