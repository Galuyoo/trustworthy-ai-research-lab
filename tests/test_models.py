import itertools
import math
import pytest
from lab_models import AUDIT, PRESETS, Scenario, eligible, plan_energy, reconstruction_example


def test_presets_and_reserve_tipping_point():
    comfy = plan_energy(PRESETS["Comfortable"])
    close = plan_energy(PRESETS["Close call"])
    impossible = plan_energy(PRESETS["Impossible"])
    assert comfy.feasible and comfy.brightness_pct == 80
    assert close.feasible and close.budget_wh - close.floor_wh == 6
    assert close.brightness_pct == pytest.approx(41.25)
    assert not impossible.feasible and not impossible.physically_feasible
    assert impossible.physical_gap_wh == 72
    assert impossible.service_h == pytest.approx(6.75)
    assert impossible.unmet_h == pytest.approx(5.25)
    tipped = plan_energy(Scenario(220, 12, 40, 15))
    assert not tipped.feasible and tipped.physically_feasible
    assert tipped.planning_gap_wh == 5


@pytest.mark.parametrize("energy,hours,floor,reserve", list(itertools.product(
    [0, 120, 192, 220, 480, 600], [4, 12, 16], [10, 40, 80, 100], [0, 10, 40, 100])))
def test_energy_is_conserved_and_floor_is_never_silently_lowered(energy, hours, floor, reserve):
    p = plan_energy(Scenario(energy, hours, floor, reserve))
    assert p.consumed_wh + p.remaining_wh == pytest.approx(energy)
    assert 0 <= p.service_h <= hours
    assert floor <= p.brightness_pct <= 100
    assert p.remaining_wh >= p.reserve_wh - 1e-9
    assert p.remaining_at(hours) == pytest.approx(p.remaining_wh)
    samples = [p.remaining_at(hours * i / 20) for i in range(21)]
    assert all(a >= b - 1e-9 for a, b in zip(samples, samples[1:]))
    assert p.feasible == (p.unmet_h < 1e-9)
    if not p.feasible:
        assert p.brightness_pct == floor


def test_exact_boundary_and_minimum_above_target():
    p = plan_energy(Scenario(192, 12, 40, 0))
    assert p.feasible and p.remaining_wh == 0 and p.brightness_pct == 40
    high = plan_energy(Scenario(600, 12, 90, 0), desired_pct=80)
    assert high.desired_pct == 90 and high.brightness_pct == 90


@pytest.mark.parametrize("scenario", [Scenario(-1, 12, 40, 0), Scenario(100, 0, 40, 0),
    Scenario(100, 12, 0, 0), Scenario(100, 12, 101, 0), Scenario(100, 12, 40, 101),
    Scenario(math.nan, 12, 40, 0), Scenario(math.inf, 12, 40, 0)])
def test_invalid_energy_inputs_rejected(scenario):
    with pytest.raises(ValueError):
        plan_energy(scenario)


@pytest.mark.parametrize("timestamp,cutoff,expected", [
    (1200, 1210, True), (1220, 1210, False), (1210, 1210, True),
    (1211, 1210, False), (1209, 1210, True), (0, 0, True), (1439, 1438, False)])
def test_timestamp_rule(timestamp, cutoff, expected):
    assert eligible(timestamp, cutoff) is expected


def test_audit_counts_are_immutable_and_reconcile():
    assert dict(AUDIT) == {"a1_total":782,"resource_eligible":184,"receipt_eligible":126,
        "resource_only":62,"receipt_only":4,"changed":66,"a1_nights":13,"a1_poles":11,
        "a2_forecasts":87,"a2_comparisons":348,"a2_changed":345,"a2_nights":3}
    both = AUDIT["resource_eligible"] - AUDIT["resource_only"]
    assert both == AUDIT["receipt_eligible"] - AUDIT["receipt_only"] == 122
    assert AUDIT["resource_only"] + AUDIT["receipt_only"] == 66
    assert 782 - both - 62 - 4 == 594
    with pytest.raises(TypeError):
        AUDIT["a1_total"] = 1


def test_reconstruction_changes_input_not_rule_or_outcome():
    frozen, later = reconstruction_example(), reconstruction_example(True)
    assert frozen.outcome_soc == later.outcome_soc == 47
    assert frozen.input_soc - frozen.prediction_soc == later.input_soc - later.prediction_soc == 10
    assert (frozen.absolute_error_pp, later.absolute_error_pp) == (13, 1)
