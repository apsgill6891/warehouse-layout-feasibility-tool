"""Transparent area calculations for preliminary warehouse planning."""

import math
from dataclasses import dataclass

from assumptions import (
    DOCK_CAPACITY_UNITS_PER_SHIFT,
    DOCK_STAGING_SQFT_PER_DOCK,
    HANDLING_UNIT_AREA_SQFT,
    HOLDING_DAYS,
    PROCESSING_AREA_DEFAULTS,
    PROCESSING_SQFT_PER_1000_PEAK_UNITS,
    STORAGE_SYSTEMS,
    SUPPORT_AREA_DEFAULTS,
)


@dataclass(frozen=True)
class FeasibilityResult:
    gross_area: float
    peak_daily_volume: float
    storage_positions: int
    storage_area: float
    aisle_area: float
    dock_staging_area: float
    processing_area: float
    support_area: float
    total_required_area: float
    utilization: float
    remaining_area: float
    status: str
    dock_capacity: int
    area_breakdown: dict[str, float]


def calculate_feasibility(inputs: dict) -> FeasibilityResult:
    """Calculate space needs from normalized UI inputs."""
    gross_area = inputs["length"] * inputs["width"]
    peak_volume = inputs["daily_volume"] * inputs["peak_factor"]
    inventory_units = peak_volume * HOLDING_DAYS[inputs["holding_period"]]
    positions = math.ceil(inventory_units / inputs["quantity_per_position"])

    unit_area = HANDLING_UNIT_AREA_SQFT[inputs["handling_unit"]]
    system = STORAGE_SYSTEMS[inputs["storage_system"]]
    storage_area = positions * unit_area * system["footprint_factor"]
    aisle_ratio = system["base_aisle_ratio"] * inputs["aisle_width"] / 10
    aisle_area = storage_area * aisle_ratio

    dock_staging_area = (
        inputs["docks"] * DOCK_STAGING_SQFT_PER_DOCK
        if "Dock staging" in inputs["selected_areas"]
        else 0
    )
    processing_area = sum(
        max(PROCESSING_AREA_DEFAULTS[name], peak_volume / 1_000 * PROCESSING_SQFT_PER_1000_PEAK_UNITS)
        for name in PROCESSING_AREA_DEFAULTS
        if name in inputs["selected_areas"]
    )
    support_area = sum(
        area for name, area in SUPPORT_AREA_DEFAULTS.items() if name in inputs["selected_areas"]
    )
    total = storage_area + aisle_area + dock_staging_area + processing_area + support_area
    utilization = total / gross_area * 100
    remaining = gross_area - total
    status = "Feasible" if utilization <= 85 else "Feasible but constrained" if utilization <= 100 else "Not feasible"
    dock_capacity = inputs["docks"] * inputs["shifts"] * DOCK_CAPACITY_UNITS_PER_SHIFT

    return FeasibilityResult(
        gross_area, peak_volume, positions, storage_area, aisle_area,
        dock_staging_area, processing_area, support_area, total,
        utilization, remaining, status, dock_capacity,
        {"Storage": storage_area, "Aisles": aisle_area, "Dock staging": dock_staging_area,
         "Processing": processing_area, "Support areas": support_area},
    )


def generate_recommendations(result: FeasibilityResult, inputs: dict) -> list[str]:
    """Return simple rule-based planning ideas, not engineering advice."""
    recommendations = []
    if result.utilization > 100:
        recommendations.append("Increase the warehouse dimensions or reduce the space requirement.")
    elif result.utilization > 85:
        recommendations.append("Retain a larger operating buffer; the proposed facility is constrained.")
    if HOLDING_DAYS[inputs["holding_period"]] > 1:
        recommendations.append("Reduce holding time where the operation and service promise allow it.")
    if inputs["shifts"] < 3 and result.peak_daily_volume > result.dock_capacity:
        recommendations.append("Add another shift to spread peak throughput across more operating hours.")
    if result.support_area > result.gross_area * 0.08:
        recommendations.append("Review and reduce support-area allocation if appropriate.")
    if inputs["storage_system"] == "Floor storage":
        recommendations.append("Consider racking instead of floor storage to improve storage density.")
    if result.peak_daily_volume > result.dock_capacity:
        recommendations.append("Increase the number of docks; estimated peak volume exceeds the planning benchmark.")
    if not recommendations:
        recommendations.append("Preserve the available area as growth and operational circulation buffer.")
    return recommendations
