"""Chapter 23 dimensional comparisons, not measured patient rates or prognosis."""
from __future__ import annotations
import math


def travel_time(distance_m: float, speed_m_per_s: float) -> float:
    """Seconds for imposed constant speed over a named path length."""
    if not (math.isfinite(distance_m) and math.isfinite(speed_m_per_s)):
        raise ValueError("distance and speed must be finite")
    if distance_m < 0 or speed_m_per_s <= 0:
        raise ValueError("distance nonnegative and speed positive")
    quotient = distance_m / speed_m_per_s
    if not math.isfinite(quotient):
        raise ValueError("travel quotient is not representable")
    return quotient


def three_clocks(distance_m: float, voltage_speed_m_per_s: float,
                 cargo_speed_m_per_s: float, growth_speed_m_per_day: float) -> dict:
    """Three *different* events over the same illustrative distance.

    The growth quotient excludes latency, guidance, branching, target survival,
    remyelination, and functional recovery. No rate is fit to a human.
    """
    if not math.isfinite(growth_speed_m_per_day) or growth_speed_m_per_day <= 0:
        raise ValueError("growth speed must be finite positive")
    voltage_s = travel_time(distance_m, voltage_speed_m_per_s)
    cargo_s = travel_time(distance_m, cargo_speed_m_per_s)
    growth_days = distance_m / growth_speed_m_per_day
    if not math.isfinite(growth_days):
        raise ValueError("growth quotient is not representable")
    return {"distance_m": distance_m, "voltage_s": voltage_s,
            "cargo_s": cargo_s, "cargo_days": cargo_s / 86400,
            "bare_growth_days": growth_days}


if __name__ == "__main__":
    case = three_clocks(0.6, 60, 1e-6, 1e-3)
    assert math.isclose(case["voltage_s"], 0.01)
    assert math.isclose(case["cargo_days"], 6.944444444444445)
    assert math.isclose(case["bare_growth_days"], 600)
    assert travel_time(0, 60) == 0
    for bad in [float("nan"), float("inf"), -1]:
        try:
            travel_time(bad, 1)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid distance accepted")
    for args in [(1e308, 1e-308), (float("nan"), 1)]:
        try:
            travel_time(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("nonrepresentable quotient accepted")
    print(case)
