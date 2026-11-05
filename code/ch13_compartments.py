"""Closed four-pool digestion model; synthetic coefficients, not patient data.

P -> A -> E -> B, in conserved residue/acyl equivalents. Uniformization
evaluates the linear first-order system without removing more than exists.
Inputs: finite nonnegative amounts/rates/time and finite total inventory.
Outputs: four amounts; nonfinite propagation results raise an error.
No I/O except console in main; standard library only.
"""

import math


def nonnegative(value):
    """Reject invalid rates, amounts and durations."""
    if not math.isfinite(value) or value < 0:
        raise ValueError("Expected a finite nonnegative value")
    return value


def evolve(state, rates, duration):
    """Propagate a closed serial chain by positive stochastic substeps.

    Rates have inverse-time units and duration uses the matching unit.
    Each substep has q*dt <= 1; Poisson tail < 1e-15 is assigned to the
    last iterate, bounding omitted-tail state error by total*1e-15.
    """
    if len(state) != 4 or len(rates) != 3:
        raise ValueError("Require four pools and three transfer rates")
    state = tuple(nonnegative(x) for x in state)
    try:
        inventory = math.fsum(state)
    except OverflowError as exc:
        raise ValueError("Total pool amount exceeds finite range") from exc
    if not math.isfinite(inventory):
        raise ValueError("Total pool amount exceeds finite range")
    rates = tuple(nonnegative(x) for x in rates)
    duration = nonnegative(duration)
    q = max(rates)
    if q == 0 or duration == 0:
        return state
    if q * duration > 10000:
        raise ValueError("Teaching range exceeded")
    steps = max(1, math.ceil(q * duration))
    z = q * duration / steps
    coefficients = tuple(k / q for k in rates)
    for _ in range(steps):
        term = state
        weight = math.exp(-z)
        weight_sum = weight
        result = [weight * x for x in term]
        for order in range(1, 100):
            transfers = [coefficients[i] * term[i] for i in range(3)]
            term = (term[0] - transfers[0],
                    term[1] + transfers[0] - transfers[1],
                    term[2] + transfers[1] - transfers[2],
                    term[3] + transfers[2])
            weight *= z / order
            weight_sum += weight
            result = [result[i] + weight * term[i] for i in range(4)]
            if weight < 1e-16:
                break
        tail = max(0.0, 1.0 - weight_sum)
        state = tuple(result[i] + tail * term[i] for i in range(4))
        if not all(math.isfinite(x) for x in state):
            raise ValueError("Propagation exceeds finite range")
    return state


def droplet_area(volume_m3, radius_m):
    """Area = 3V/r for identical spherical droplets, SI units."""
    nonnegative(volume_m3)
    if not math.isfinite(radius_m) or radius_m <= 0:
        raise ValueError("Radius must be finite and positive")
    return 3 * volume_m3 / radius_m


def neutral_peptide_boundary(ph_lumen, ph_cell, voltage_v, temp_k=310):
    """Ideal reversible 1H+/neutral-cargo cycle; not general PEPT1 stoichiometry."""
    if not all(math.isfinite(x) for x in
               (ph_lumen, ph_cell, voltage_v, temp_k)) or temp_k <= 0:
        raise ValueError("Finite inputs and positive temperature required")
    return 10 ** (ph_cell - ph_lumen) * math.exp(
        -96485 * voltage_v / (8.314 * temp_k))


def checks():
    """Independent analytic, semigroup, scaling and conservation checks."""
    for t in (0, 0.01, 0.3, 2, 6, 20):
        baseline = evolve((100, 0, 0, 0), (1, 1, 1), t)
        expected = (100 * math.exp(-t), 100 * t * math.exp(-t),
                    50 * t * t * math.exp(-t),
                    100 * (1 - math.exp(-t) * (1 + t + t * t / 2)))
        assert max(abs(a - b) for a, b in zip(baseline, expected)) < 1e-10
        for rates in ((0, 1, 1), (0.2, 1, 1), (1, 0, 1), (1, 1, 0)):
            result = evolve((100, 0, 0, 0), rates, t)
            assert min(result) >= 0
            assert abs(sum(result) - 100) < 1e-10
    initial = (17, 3, 2, 1)
    rates = (0.2, 0.7, 1.3)
    direct = evolve(initial, rates, 3)
    split = evolve(evolve(initial, rates, 1), rates, 2)
    assert max(abs(a - b) for a, b in zip(direct, split)) < 1e-11
    scaled = evolve(tuple(7 * x for x in initial), rates, 3)
    assert max(abs(7 * a - b) for a, b in zip(direct, scaled)) < 1e-10
    assert evolve(initial, (0, 0, 0), 100) == initial
    assert neutral_peptide_boundary(7, 7, 0) == 1
    for duration in (0, 1):
        try:
            evolve((1e308, 1e308, 1e308, 1e308), (1, 1, 1), duration)
        except ValueError as exc:
            assert str(exc) == "Total pool amount exceeds finite range"
        else:
            raise AssertionError("Nonfinite total inventory accepted")
    maximum = float.fromhex("0x1.fffffffffffffp+1023")
    try:
        evolve((0, maximum, 0, 0), (1, 1, 1), 2)
    except ValueError as exc:
        assert str(exc) == "Propagation exceeds finite range"
    else:
        raise AssertionError("Nonfinite propagation result accepted")
    for bad in (-1, float("nan"), float("inf")):
        try:
            evolve((100, 0, 0, 0), (bad, 1, 1), 2)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid rate accepted")
    return "analytic/positivity/conservation/semigroup/scaling/limits/invalid: PASS"


if __name__ == "__main__":
    print(checks())
    for label, rates in (("baseline", (1, 1, 1)),
                         ("reduced hydrolysis", (0.2, 1, 1)),
                         ("reduced uptake", (1, 0.2, 1)),
                         ("reduced export", (1, 1, 0.2))):
        pools = evolve((100, 0, 0, 0), rates, 2)
        print(label, "P,A,E,B =", *(f"{x:.6f}" for x in pools),
              f"sum={sum(pools):.6f}")
    print("Areas m^2:", droplet_area(1e-6, 100e-6),
          droplet_area(1e-6, 10e-6))
    print("Ideal neutral peptide boundary:",
          f"{neutral_peptide_boundary(6, 7.2, -0.04):.6f}")
    print("Chain fragments, 12 residues, 3 distinct cuts:", 1 + 3)
    print("Peptide bonds before and after:", 12 - 1, 12 - 1 - 3)
    print("Selected ion accounting, 6 mmol Na / 3 Na per ATP:", 6 / 3)
    print("Food-energy convention, 10 g x 9 kcal/g:", 10 * 9)
    print("Radius reduction area/count ratios:", 100 / 10, (100 / 10) ** 3)
    print("2 mmol TAG -> MAG, free FA, consumed water (mmol):", 2, 2 * 2, 2 * 2)
