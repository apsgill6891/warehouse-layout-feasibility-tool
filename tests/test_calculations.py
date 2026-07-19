import pytest

from calculations import calculate_feasibility


def base_inputs(**overrides):
    values = {"length": 100, "width": 100, "docks": 2, "daily_volume": 1_000,
              "peak_factor": 1.0, "holding_period": "1 day", "shifts": 1,
              "handling_unit": "Standard North American pallet", "storage_system": "Floor storage",
              "quantity_per_position": 10, "aisle_width": 10, "selected_areas": set()}
    values.update(overrides)
    return values


def test_main_area_calculations():
    result = calculate_feasibility(base_inputs())
    assert result.gross_area == 10_000
    assert result.peak_daily_volume == 1_000
    assert result.storage_positions == 100
    assert result.storage_area == pytest.approx(1_330)
    assert result.aisle_area == pytest.approx(465.5)
    assert result.total_required_area == pytest.approx(1_795.5)
    assert result.remaining_area == pytest.approx(8_204.5)
    assert result.status == "Feasible"


def test_optional_areas_are_added():
    selected = {"Dock staging", "Sortation area", "Office"}
    result = calculate_feasibility(base_inputs(selected_areas=selected))
    assert result.dock_staging_area == 1_000
    assert result.processing_area == 2_000
    assert result.support_area == 1_000
    assert result.total_required_area == pytest.approx(5_795.5)


def test_constrained_and_infeasible_thresholds():
    constrained = calculate_feasibility(base_inputs(quantity_per_position=2))
    infeasible = calculate_feasibility(base_inputs(quantity_per_position=1))
    assert constrained.status == "Feasible but constrained"
    assert 85 < constrained.utilization <= 100
    assert infeasible.status == "Not feasible"
    assert infeasible.remaining_area < 0


def test_same_day_uses_quarter_day_buffer_and_rounds_positions_up():
    result = calculate_feasibility(base_inputs(
        daily_volume=1_001, holding_period="Same day", quantity_per_position=100,
    ))
    assert result.storage_positions == 3
    assert result.peak_daily_volume == 1_001


def test_total_matches_breakdown():
    result = calculate_feasibility(base_inputs(
        selected_areas={"Dock staging", "Packing area", "Washrooms"},
    ))
    assert result.total_required_area == pytest.approx(sum(result.area_breakdown.values()))


@pytest.mark.parametrize("field", ["length", "width", "quantity_per_position"])
def test_non_positive_inputs_are_rejected(field):
    with pytest.raises(ValueError, match=f"{field} must be greater than zero"):
        calculate_feasibility(base_inputs(**{field: 0}))


def test_missing_inputs_have_a_clear_error():
    values = base_inputs()
    del values["daily_volume"]
    with pytest.raises(ValueError, match="Missing required inputs: daily_volume"):
        calculate_feasibility(values)
