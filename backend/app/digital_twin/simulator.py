"""
ECOVERSE 360 — Digital Twin Simulator
What-if scenario engine for campus sustainability modeling.

This is the mathematical core of the Digital Twin:
- Aggregates real-time sensor + activity data
- Calculates sustainability health scores
- Runs predictive what-if simulations
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SimulationRequest, SimulationResult


# ── Constants: Emission Factors & Baselines ──────────────────────────────

# Average daily emissions for a campus of ~5000 students (kg CO2)
BASELINE_DAILY_CARBON_KG = 2500.0
BASELINE_DAILY_WASTE_KG = 800.0
BASELINE_DAILY_WATER_LITERS = 150000.0
BASELINE_DAILY_ENERGY_KWH = 5000.0

# Per-person emission factors
CARPOOL_CO2_SAVE_PER_PERSON_KG = 2.3       # per trip
RECYCLING_CO2_SAVE_PER_KG = 1.8
TREE_CO2_ABSORPTION_PER_YEAR_KG = 22.0     # mature tree
FOOD_WASTE_CO2_PER_KG = 2.5                # methane equivalent
ENERGY_CO2_PER_KWH = 0.82                  # India grid average
WATER_CO2_PER_LITER = 0.0003               # treatment + pumping

CAMPUS_POPULATION = 5000


class Simulator:
    """
    Campus sustainability simulation engine.

    Supports:
    - What-if scenario analysis
    - Carbon impact projection
    - Resource savings estimation
    - Actionable recommendations
    """

    async def run_scenario(
        self, request: SimulationRequest, db: AsyncSession
    ) -> SimulationResult:
        """Run a what-if simulation and return projected impact."""

        days = request.timeframe_months * 30

        # ── Carbon savings from carpooling ───────────────────────────
        carpool_participants = CAMPUS_POPULATION * (request.carpool_adoption_pct / 100)
        # Assume 5 commute trips per week
        carpool_trips = carpool_participants * 5 * (days / 7)
        carbon_from_carpool = carpool_trips * CARPOOL_CO2_SAVE_PER_PERSON_KG

        # ── Carbon savings from food waste reduction ─────────────────
        daily_food_waste_reduction = BASELINE_DAILY_WASTE_KG * 0.3 * abs(request.food_waste_change_pct) / 100
        carbon_from_food = daily_food_waste_reduction * days * FOOD_WASTE_CO2_PER_KG
        waste_diverted = daily_food_waste_reduction * days

        # ── Carbon savings from recycling ────────────────────────────
        daily_recycling_increase = BASELINE_DAILY_WASTE_KG * 0.2 * abs(request.recycling_rate_change_pct) / 100
        carbon_from_recycling = daily_recycling_increase * days * RECYCLING_CO2_SAVE_PER_KG
        waste_diverted += daily_recycling_increase * days

        # ── Energy savings ───────────────────────────────────────────
        daily_energy_saving = BASELINE_DAILY_ENERGY_KWH * abs(request.energy_reduction_pct) / 100
        energy_saved = daily_energy_saving * days
        carbon_from_energy = energy_saved * ENERGY_CO2_PER_KWH

        # ── Water savings ────────────────────────────────────────────
        daily_water_saving = BASELINE_DAILY_WATER_LITERS * abs(request.water_saving_pct) / 100
        water_saved = daily_water_saving * days

        # ── Tree planting ────────────────────────────────────────────
        carbon_from_trees = request.tree_planting_count * TREE_CO2_ABSORPTION_PER_YEAR_KG * (request.timeframe_months / 12)

        # ── Total ────────────────────────────────────────────────────
        total_carbon_saved = (
            carbon_from_carpool
            + carbon_from_food
            + carbon_from_recycling
            + carbon_from_energy
            + carbon_from_trees
        )

        # ── Eco Score Change ─────────────────────────────────────────
        baseline_carbon = BASELINE_DAILY_CARBON_KG * days
        eco_score_change = min(
            (total_carbon_saved / baseline_carbon) * 100 if baseline_carbon > 0 else 0,
            100,
        )

        # ── Generate Recommendations ────────────────────────────────
        recommendations = self._generate_recommendations(request, total_carbon_saved)

        # ── Build Summary ────────────────────────────────────────────
        summary = (
            f"Over {request.timeframe_months} months, the proposed changes could save "
            f"{total_carbon_saved:,.0f} kg CO₂, divert {waste_diverted:,.0f} kg of waste, "
            f"conserve {water_saved:,.0f} liters of water, and save {energy_saved:,.0f} kWh "
            f"of energy. Campus eco-score would improve by {eco_score_change:.1f}%."
        )

        return SimulationResult(
            zone=request.zone,
            timeframe_months=request.timeframe_months,
            carbon_saved_kg=round(total_carbon_saved, 2),
            water_saved_liters=round(water_saved, 2),
            waste_diverted_kg=round(waste_diverted, 2),
            energy_saved_kwh=round(energy_saved, 2),
            eco_score_change=round(eco_score_change, 2),
            summary=summary,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self, request: SimulationRequest, total_carbon: float
    ) -> List[str]:
        """Generate actionable recommendations based on scenario."""
        recs = []

        if request.carpool_adoption_pct < 20:
            recs.append(
                "Increase carpooling adoption to 20%+ with incentives — "
                "this alone can cut transport emissions by 35%."
            )

        if request.food_waste_change_pct > -15:
            recs.append(
                "Implement smart portion control in canteens. "
                "Even 15% food waste reduction saves significant methane emissions."
            )

        if request.recycling_rate_change_pct < 25:
            recs.append(
                "Deploy more smart bins with real-time segregation feedback. "
                "Target 25%+ recycling rate improvement."
            )

        if request.energy_reduction_pct < 10:
            recs.append(
                "Install motion-sensor lighting and smart HVAC scheduling. "
                "10% energy reduction is achievable with zero discomfort."
            )

        if request.tree_planting_count < 50:
            recs.append(
                "Launch a tree planting drive. Each tree absorbs ~22 kg CO₂/year. "
                "50 trees create a visible carbon sink."
            )

        if request.water_saving_pct < 10:
            recs.append(
                "Install low-flow fixtures and fix leaks. "
                "10% water saving reduces both consumption and energy for pumping."
            )

        if total_carbon > 5000:
            recs.append(
                "🎯 This scenario saves over 5 tonnes of CO₂ — "
                "equivalent to taking 2 cars off the road for a year!"
            )

        if not recs:
            recs.append(
                "Great scenario! Consider combining multiple interventions "
                "for compounding sustainability impact."
            )

        return recs
