"""Synthetic Chapter 12 accounting; standard library only, no patient inputs."""

import json
import math


def finite_nonnegative(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError("Expected a finite nonnegative input")


def rate(concentration, maximum=2.0, half=10.0):
    """Return mmol/min for concentration and half in mmol/L."""
    finite_nonnegative(concentration)
    finite_nonnegative(maximum)
    if not math.isfinite(half) or half <= 0:
        raise ValueError("half must be positive and finite")
    return 0.0 if concentration == 0 else maximum / (1 + half / concentration)


def absorb(initial=20.0, volume=1.0, maximum=2.0, half=10.0,
           duration=10.0):
    """Exact implicit depletion law, solved in log-fraction coordinates.

    Amounts: mmol; volume: L; duration: min. Returned tuple is remaining,
    absorbed. Constant volume, maintained driving, matched exit; no metabolism.
    """
    for value in (initial, maximum, duration):
        finite_nonnegative(value)
    for value in (volume, half):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("volume and half must be positive and finite")
    if initial == 0 or maximum == 0 or duration == 0:
        return initial, 0.0
    a = half * volume
    target = maximum * duration
    if a <= 0 or not math.isfinite(a) or not math.isfinite(target):
        raise ValueError("Derived scale exceeds floating-point range")
    if target == 0:
        return initial, 0.0
    # z = -log(n/initial); bracket the root before bisection.
    def balance(z):
        return -initial * math.expm1(-z) + a * z

    low, high = 0.0, min(1.0, target / a)
    if high <= 0 or not math.isfinite(high):
        raise ValueError("Dimensionless exposure exceeds floating-point range")
    while balance(high) < target:
        low = high
        high *= 2
        if not math.isfinite(high):
            raise ValueError("Dimensionless exposure exceeds floating-point range")
    for _ in range(120):
        middle = low + (high - low) / 2
        if balance(middle) < target:
            low = middle
        else:
            high = middle
    remaining = initial * math.exp(-(low + (high - low) / 2))
    return remaining, initial - remaining


def coupling_boundary(sodium_lumen=140.0, sodium_cell=14.0,
                      voltage=-0.05, temperature=310.0):
    """Ideal reversible concentration-ratio boundary; not a human prediction."""
    for value in (sodium_lumen, sodium_cell, temperature):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Concentrations and temperature must be positive")
    if not math.isfinite(voltage):
        raise ValueError("Voltage must be finite")
    return (sodium_lumen / sodium_cell) ** 2 * math.exp(
        -2 * 96485 * voltage / (8.314 * temperature))


def checks():
    assert rate(0) == 0
    assert rate(10) == 1
    assert math.isclose(rate(1), 2 / 11)
    assert math.isclose(rate(100), 20 / 11)
    assert rate(1e9) < 2
    assert math.isclose(rate(1e9), 2, rel_tol=1e-7)
    for initial in (0, 0.01, 1, 20, 1000):
        prior = initial
        for duration in (0, 0.1, 1, 10, 100):
            remaining, absorbed = absorb(initial=initial, duration=duration)
            assert 0 <= remaining <= prior + 1e-10
            assert 0 <= absorbed <= initial
            assert absorbed <= 2 * duration + 1e-10
            assert math.isclose(remaining + absorbed, initial)
            prior = remaining
    assert absorb(maximum=0) == (20, 0)
    remaining, absorbed = absorb(initial=20, volume=1e-40, half=1,
                                 maximum=2, duration=1)
    assert math.isclose(remaining, 18)
    assert math.isclose(absorbed, 2)
    assert absorbed <= 2
    for observed, expected in zip(
            absorb(initial=40, volume=2, maximum=4), absorb()):
        assert math.isclose(observed, 2 * expected)
    assert coupling_boundary(voltage=0) == 100
    assert coupling_boundary(14, 14, voltage=0) == 1
    assert rate(20 / 2) < rate(20 / 1)
    assert rate(40 / 2) == rate(20 / 1)
    for bad in (-1, float("nan"), float("inf")):
        try:
            absorb(initial=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input was accepted")
    for volume in (0, -1):
        try:
            absorb(volume=volume)
        except ValueError:
            pass
        else:
            raise AssertionError("Nonpositive volume was accepted")
    # Food-label residue accounting: glucose, galactose, fructose in mmol.
    assert 10 + 20 + 8 == 38
    assert 38 + 8 + 15 == 61
    assert 10 * 12 == (10 + 10) * 6
    assert 3 * 2 / 3 == 2  # Selected pump ATP demand, mmol.
    assert math.isclose((1.2 - 0.8) * 5, 2)


if __name__ == "__main__":
    checks()
    remaining, absorbed = absorb()
    print(json.dumps({
        "checks": "passed",
        "rates_mmol_min": [rate(c) for c in (1, 10, 100)],
        "remaining_mmol": remaining,
        "absorbed_mmol": absorbed,
        "sum_mmol": remaining + absorbed,
        "capacity_doubled_absorbed_mmol": absorb(maximum=4)[1],
        "volume_doubled_absorbed_mmol": absorb(volume=2)[1],
        "initial_rate_mmol_min": rate(20),
        "coupling_boundary": coupling_boundary(),
        "voltage_factor": coupling_boundary() / 100,
        "pH_activity_ratio": 10 ** (7 - 2),
        "selected_pump_ATP_mmol": 3 * 2 / 3,
        "food_sugars_mmol": {"glucose": 38, "galactose": 8, "fructose": 15}
    }, indent=2))
