"""Original blood-accounting constructions; synthetic values, no patient model.

Run directly with Python 3. Uses the standard library, performs no network
access, and writes no files. Volume accounting is not a clinical diagnosis.
Mean residence time determines stationary throughput, not transient survival.
"""

import math


def positive(value, name):
    """Validate a finite positive numeric model input."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive number")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return float(value)


def hematocrit(count_million_per_ul, mcv_fl):
    """Return fractional RBC volume from million cells/uL and fL/cell."""
    count = positive(count_million_per_ul, "count")
    volume = positive(mcv_fl, "MCV")
    result = count * volume * 1e-3
    if not math.isfinite(result) or result > 1:
        raise ValueError("implied hematocrit exceeds whole-blood volume")
    return result


def turnover(blood_l, count_million_per_ul, residence_days):
    """Return total cells, stationary cells/day and cells/s."""
    blood = positive(blood_l, "blood volume")
    count = positive(count_million_per_ul, "count")
    residence = positive(residence_days, "mean residence time")
    population = blood * count * 1e12
    per_day = population / residence
    per_second = per_day / 86400
    if not all(math.isfinite(x) for x in (population, per_day, per_second)):
        raise ValueError("inputs overflow the finite accounting model")
    return population, per_day, per_second


def specimen_change(blood_l, hct, removed_l, cell_free_added_l):
    """Perfect mixing; remove whole blood, then add cell-free volume.

    Return remaining RBC liters, post-removal Hct, post-addition Hct.
    No redistribution, production, hemolysis or continued loss is modeled.
    """
    blood = positive(blood_l, "blood volume")
    fraction = positive(hct, "hematocrit")
    if fraction > 1:
        raise ValueError("hematocrit cannot exceed one")
    if not isinstance(removed_l, (int, float)) or isinstance(removed_l, bool):
        raise ValueError("removed volume must be numeric")
    if not math.isfinite(removed_l) or not 0 <= removed_l < blood:
        raise ValueError("remove a finite volume below initial blood volume")
    if (not isinstance(cell_free_added_l, (int, float))
            or isinstance(cell_free_added_l, bool)
            or not math.isfinite(cell_free_added_l)
            or cell_free_added_l < 0):
        raise ValueError("added volume must be finite and nonnegative")
    remaining = blood - removed_l
    red_l = fraction * remaining
    return red_l, red_l / remaining, red_l / (remaining + cell_free_added_l)


def check():
    """Check dimensions/scaling and reject invalid input families."""
    assert math.isclose(hematocrit(5, 90), 0.45)
    assert math.isclose(hematocrit(4.8, 85), 0.408)
    assert math.isclose(hematocrit(4, 75), 0.30)
    assert math.isclose(2.5e9 * 90e-15 * 100, 0.0225)
    for count in (1, 2, 3, 4, 5):
        for mcv in (50, 75, 100):
            # Number/volume interpretation agrees with conventional units.
            expected = count * 1e12 * mcv * 1e-15
            assert math.isclose(hematocrit(count, mcv), expected)
    n, daily, seconds = turnover(5, 5, 120)
    assert math.isclose(n, 2.5e13)
    assert math.isclose(daily * 120, n)
    assert math.isclose(seconds * 86400, daily)
    assert math.isclose(turnover(5, 5, 60)[1], 2 * daily)
    assert all(math.isclose(a, b) for a, b in zip(
        specimen_change(5, 0.45, 1, 1), (1.8, 0.45, 0.36)))
    invalid = [
        lambda: hematocrit(0, 90),
        lambda: hematocrit(5, float("nan")),
        lambda: hematocrit(20, 100),
        lambda: turnover(5, 5, -1),
        lambda: turnover(True, 5, 120),
        lambda: specimen_change(5, 0.45, 5, 1),
        lambda: specimen_change(5, 0.45, 1, -1),
    ]
    for function in invalid:
        try:
            function()
        except ValueError:
            continue
        raise AssertionError("invalid input was accepted")


if __name__ == "__main__":
    check()
    print("Checks passed: units, scaling, balances, and invalid inputs.")
    print(f"Hct(5.0 million/uL, 90 fL) = {hematocrit(5, 90):.6f}")
    print(f"Hct(4.0 million/uL, 75 fL) = {hematocrit(4, 75):.6f}")
    print(f"Exercise 1 Hct = {hematocrit(4.8, 85):.6f}")
    for days in (120, 60):
        n, daily, seconds = turnover(5, 5, days)
        print(f"T={days} d: N={n:.6e}, P={daily:.6e}/d, {seconds:.6e}/s")
    red, before, after = specimen_change(5, 0.45, 1, 1)
    print(f"RBC={red:.6f} L; post-loss Hct={before:.6f}; "
          f"post-dilution Hct={after:.6f}")
