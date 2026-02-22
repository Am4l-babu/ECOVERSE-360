"""
ECOVERSE 360 — ML Prediction Engine
Time-series forecasting and anomaly detection for sustainability metrics.

Models:
- Waste overflow prediction
- Air quality spike forecasting
- Energy demand prediction
- Carbon savings estimation
- Crop yield prediction (vertical farm)
"""

import os
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from app.core.config import get_settings

settings = get_settings()


class SustainabilityPredictor:
    """
    Multi-model prediction engine for campus sustainability metrics.

    Supports:
    - Waste bin overflow prediction
    - AQI spike forecasting
    - Energy demand prediction
    - Crop yield estimation
    - Carbon footprint projection
    """

    def __init__(self):
        self.models: Dict[str, object] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_dir = settings.ML_MODEL_PATH
        os.makedirs(self.model_dir, exist_ok=True)

    # ── Waste Overflow Prediction ────────────────────────────────────

    def train_waste_model(self, data: pd.DataFrame) -> dict:
        """
        Train waste overflow prediction model.

        Expected columns:
        - hour, day_of_week, is_weekend, building_code
        - prev_level, avg_daily_waste, campus_events
        - fill_level (target)
        """
        features = [
            "hour", "day_of_week", "is_weekend",
            "prev_level", "avg_daily_waste", "campus_events",
        ]
        target = "fill_level"

        X = data[features].values
        y = data[target].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 3),
            "r2": round(r2_score(y_test, y_pred), 3),
        }

        self.models["waste"] = model
        self.scalers["waste"] = scaler
        self._save_model("waste", model, scaler)

        return metrics

    def predict_waste(
        self, hour: int, day_of_week: int, prev_level: float,
        avg_daily_waste: float, campus_events: int = 0
    ) -> Dict:
        """Predict bin fill level."""
        model, scaler = self._load_model("waste")

        features = np.array([[
            hour, day_of_week, 1 if day_of_week >= 5 else 0,
            prev_level, avg_daily_waste, campus_events,
        ]])

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]

        return {
            "predicted_fill_level": round(min(max(prediction, 0), 100), 1),
            "overflow_risk": "high" if prediction > 80 else "medium" if prediction > 60 else "low",
            "recommended_action": (
                "Schedule immediate collection" if prediction > 85
                else "Monitor closely" if prediction > 70
                else "Normal schedule"
            ),
        }

    # ── AQI Prediction ──────────────────────────────────────────────

    def train_aqi_model(self, data: pd.DataFrame) -> dict:
        """
        Train AQI forecasting model.

        Expected columns:
        - hour, day_of_week, month, temperature, humidity
        - wind_speed, traffic_density, prev_aqi
        - aqi (target)
        """
        features = [
            "hour", "day_of_week", "month", "temperature",
            "humidity", "wind_speed", "traffic_density", "prev_aqi",
        ]
        target = "aqi"

        X = data[features].values
        y = data[target].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 3),
            "r2": round(r2_score(y_test, y_pred), 3),
        }

        self.models["aqi"] = model
        self.scalers["aqi"] = scaler
        self._save_model("aqi", model, scaler)

        return metrics

    def predict_aqi(
        self, hour: int, day_of_week: int, month: int,
        temperature: float, humidity: float, wind_speed: float,
        traffic_density: float, prev_aqi: float
    ) -> Dict:
        """Predict Air Quality Index."""
        model, scaler = self._load_model("aqi")

        features = np.array([[
            hour, day_of_week, month, temperature,
            humidity, wind_speed, traffic_density, prev_aqi,
        ]])

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]

        aqi_val = max(0, round(prediction, 1))
        category = self._aqi_category(aqi_val)

        return {
            "predicted_aqi": aqi_val,
            "category": category,
            "health_advisory": self._aqi_advisory(aqi_val),
        }

    # ── Energy Demand Prediction ────────────────────────────────────

    def train_energy_model(self, data: pd.DataFrame) -> dict:
        """Train energy demand prediction model."""
        features = [
            "hour", "day_of_week", "month", "temperature",
            "occupancy", "is_exam_period", "prev_consumption",
        ]
        target = "energy_kwh"

        X = data[features].values
        y = data[target].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=120,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 3),
            "r2": round(r2_score(y_test, y_pred), 3),
        }

        self.models["energy"] = model
        self.scalers["energy"] = scaler
        self._save_model("energy", model, scaler)

        return metrics

    # ── Crop Yield Prediction (Vertical Farm) ───────────────────────

    def train_crop_model(self, data: pd.DataFrame) -> dict:
        """Train vertical farm crop yield prediction model."""
        features = [
            "days_since_planting", "soil_moisture", "soil_temp",
            "air_temp", "humidity", "light_hours", "ph",
            "nutrient_n", "nutrient_p", "nutrient_k",
        ]
        target = "yield_kg"

        X = data[features].values
        y = data[target].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 3),
            "r2": round(r2_score(y_test, y_pred), 3),
        }

        self.models["crop"] = model
        self.scalers["crop"] = scaler
        self._save_model("crop", model, scaler)

        return metrics

    # ── Carbon Footprint Estimation ─────────────────────────────────

    def estimate_carbon_footprint(
        self,
        transport_km: float = 0,
        transport_mode: str = "car",
        electricity_kwh: float = 0,
        food_meals: int = 3,
        food_type: str = "mixed",
        waste_kg: float = 0,
        water_liters: float = 0,
    ) -> Dict:
        """Calculate estimated carbon footprint."""
        # Transport emission factors (kg CO2 per km)
        transport_factors = {
            "car": 0.21,
            "bike": 0.0,
            "bus": 0.089,
            "train": 0.041,
            "walk": 0.0,
            "carpool": 0.07,
            "electric": 0.05,
        }

        # Food emission factors (kg CO2 per meal)
        food_factors = {
            "vegan": 0.7,
            "vegetarian": 1.0,
            "mixed": 2.5,
            "meat_heavy": 4.0,
        }

        transport_kg = transport_km * transport_factors.get(transport_mode, 0.21)
        electricity_kg = electricity_kwh * 0.82  # India grid
        food_kg = food_meals * food_factors.get(food_type, 2.5)
        waste_kg_co2 = waste_kg * 2.5
        water_kg = water_liters * 0.0003

        total = transport_kg + electricity_kg + food_kg + waste_kg_co2 + water_kg

        return {
            "total_kg_co2": round(total, 3),
            "breakdown": {
                "transport": round(transport_kg, 3),
                "electricity": round(electricity_kg, 3),
                "food": round(food_kg, 3),
                "waste": round(waste_kg_co2, 3),
                "water": round(water_kg, 3),
            },
            "comparison": {
                "india_avg_daily": 5.5,
                "global_avg_daily": 13.7,
                "your_daily": round(total, 2),
                "rating": (
                    "Excellent" if total < 3
                    else "Good" if total < 5
                    else "Average" if total < 8
                    else "High" if total < 15
                    else "Very High"
                ),
            },
            "tips": self._carbon_reduction_tips(transport_kg, electricity_kg, food_kg),
        }

    # ── Helpers ──────────────────────────────────────────────────────

    def _save_model(self, name: str, model, scaler):
        """Persist model and scaler to disk."""
        path = os.path.join(self.model_dir, f"{name}_model.pkl")
        with open(path, "wb") as f:
            pickle.dump({"model": model, "scaler": scaler}, f)

    def _load_model(self, name: str) -> Tuple:
        """Load model and scaler from disk."""
        if name in self.models:
            return self.models[name], self.scalers[name]

        path = os.path.join(self.model_dir, f"{name}_model.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model '{name}' not trained yet. Call train_{name}_model() first."
            )

        with open(path, "rb") as f:
            data = pickle.load(f)
            self.models[name] = data["model"]
            self.scalers[name] = data["scaler"]
            return data["model"], data["scaler"]

    @staticmethod
    def _aqi_category(aqi: float) -> str:
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    @staticmethod
    def _aqi_advisory(aqi: float) -> str:
        if aqi <= 50:
            return "Air quality is excellent. Enjoy outdoor activities!"
        elif aqi <= 100:
            return "Air quality is acceptable. Sensitive individuals should limit prolonged outdoor exertion."
        elif aqi <= 200:
            return "Everyone may begin to experience health effects. Limit outdoor activities."
        else:
            return "Health alert! Everyone should avoid outdoor exposure."

    @staticmethod
    def _carbon_reduction_tips(transport: float, electricity: float, food: float) -> List[str]:
        tips = []
        if transport > 3:
            tips.append("Consider carpooling or public transit to cut transport emissions by 60%.")
        if electricity > 4:
            tips.append("Switch off unused appliances. LED lighting saves 75% energy.")
        if food > 5:
            tips.append("Try 2 plant-based meals per week — reduces food carbon by 30%.")
        if not tips:
            tips.append("You're doing great! Keep up the sustainable habits.")
        return tips
