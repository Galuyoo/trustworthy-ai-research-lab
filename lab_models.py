"""Deterministic teaching models. No research data, trained models, or network I/O."""
from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType

FULL_POWER_W = 40.0


@dataclass(frozen=True)
class Scenario:
    energy_wh: float
    night_h: float
    minimum_pct: float
    reserve_pct: float


PRESETS = MappingProxyType({
    "Comfortable": Scenario(480, 12, 40, 10),
    "Close call": Scenario(220, 12, 40, 10),
    "Impossible": Scenario(120, 12, 40, 10),
})


@dataclass(frozen=True)
class EnergyPlan:
    scenario: Scenario
    desired_pct: float
    reserve_wh: float
    budget_wh: float
    floor_wh: float
    brightness_pct: float
    service_h: float
    consumed_wh: float
    remaining_wh: float

    @property
    def feasible(self) -> bool:
        return self.budget_wh + 1e-9 >= self.floor_wh

    @property
    def physically_feasible(self) -> bool:
        return self.scenario.energy_wh + 1e-9 >= self.floor_wh

    @property
    def planning_gap_wh(self) -> float:
        return max(0.0, self.floor_wh - self.budget_wh)

    @property
    def physical_gap_wh(self) -> float:
        return max(0.0, self.floor_wh - self.scenario.energy_wh)

    @property
    def unmet_h(self) -> float:
        return max(0.0, self.scenario.night_h - self.service_h)

    def remaining_at(self, hour: float) -> float:
        if not isfinite(hour) or not 0 <= hour <= self.scenario.night_h:
            raise ValueError("Hour must lie within this night.")
        spent = FULL_POWER_W * self.brightness_pct / 100 * min(hour, self.service_h)
        return max(self.reserve_wh, self.scenario.energy_wh - spent)


def plan_energy(scenario: Scenario, desired_pct: float = 80) -> EnergyPlan:
    """Reserve is withheld energy, not a probability or a simulated battery loss.

    Use constant brightness. Meet the floor for the whole night before allocating
    extra brightness. If impossible, deliver the floor until the budget is spent,
    then explicitly mark the rest of the night as unserved (lamp off).
    """
    e, h, floor, reserve = (
        scenario.energy_wh, scenario.night_h, scenario.minimum_pct, scenario.reserve_pct
    )
    if not all(isfinite(v) for v in (e, h, floor, reserve, desired_pct)):
        raise ValueError("All inputs must be finite.")
    if e < 0 or h <= 0 or not 0 < floor <= 100 or not 0 <= reserve <= 100:
        raise ValueError("Require energy >= 0, hours > 0, 0 < floor <= 100, 0 <= reserve <= 100.")
    if not 0 <= desired_pct <= 100:
        raise ValueError("Desired brightness must be between 0 and 100%.")
    desired = max(floor, desired_pct)
    held = e * reserve / 100
    budget = e - held
    required = FULL_POWER_W * floor / 100 * h
    if budget + 1e-9 >= required:
        brightness = max(floor, min(desired, budget / (FULL_POWER_W * h) * 100))
        service = h
    else:
        brightness = floor
        service = budget / (FULL_POWER_W * floor / 100)
    consumed = min(budget, FULL_POWER_W * brightness / 100 * service)
    return EnergyPlan(scenario, desired, held, budget, required, brightness,
                      service, consumed, e - consumed)


def eligible(timestamp_min: int, cutoff_min: int) -> bool:
    """Inclusive synthetic rule on one shared date/clock: timestamp <= cutoff."""
    for value in (timestamp_min, cutoff_min):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 1440:
            raise ValueError("Times must be integer minutes on the same day (0..1439).")
    return timestamp_min <= cutoff_min


def clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass(frozen=True)
class ToyForecast:
    label: str
    input_soc: float
    prediction_soc: float
    outcome_soc: float
    absolute_error_pp: float


def reconstruction_example(later: bool = False) -> ToyForecast:
    """Both inputs and the fixed outcome are invented, unrelated to the audit rows."""
    input_soc = 58.0 if later else 70.0
    prediction = input_soc - 10.0
    outcome = 47.0
    return ToyForecast("Later reconstructed input" if later else "Frozen issued input",
                       input_soc, prediction, outcome, abs(prediction - outcome))


# User-authorised aggregate facts, corroborated in presentation plans on 2026-11-07.
# Constants cannot be mutated by widget/session state.
AUDIT = MappingProxyType({
    "a1_total": 782, "resource_eligible": 184, "receipt_eligible": 126,
    "resource_only": 62, "receipt_only": 4, "changed": 66,
    "a1_nights": 13, "a1_poles": 11,
    "a2_forecasts": 87, "a2_comparisons": 348, "a2_changed": 345, "a2_nights": 3,
})
