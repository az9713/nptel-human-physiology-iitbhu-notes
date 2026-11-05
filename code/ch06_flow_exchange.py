"""Chapter 6: ideal hydraulics and regional fluid accounting, no patient model."""
from math import isclose, isfinite, pi


def positive(name, value):
    if not isfinite(value) or value <= 0:
        raise ValueError(name + " must be finite and positive")


def poiseuille(delta_p, radius, length, viscosity):
    """Pa, m, m, Pa s -> m^3/s; signed pressure, fixed ideal tube."""
    for name, value in (("radius", radius), ("length", length),
                        ("viscosity", viscosity)):
        positive(name, value)
    if not isfinite(delta_p):
        raise ValueError("pressure must be finite")
    return pi * radius**4 * delta_p / (8 * viscosity * length)


def classical_drive(pc, pi_c=25, p_i=0, pi_i=1, sigma=1):
    """mmHg -> mmHg. Boundary inputs are fixed, not a kinetic law."""
    vals = (pc, pi_c, p_i, pi_i, sigma)
    if not all(isfinite(x) for x in vals) or not 0 <= sigma <= 1:
        raise ValueError("invalid pressure or reflection coefficient")
    if min(pi_c, pi_i) < 0:
        raise ValueError("oncotic pressures must be nonnegative")
    return pc - p_i - sigma * (pi_c - pi_i)


def accounting(filtration, lymph, minutes, initial=(100, 20, 0)):
    """Fixed positive mL/min rates, min, and regional Vblood,Vtissue,Vreturn.

    The third compartment receives lymph. No external reservoir or hidden loss.
    The prescribed rates hold only over the stated interval, with enough fluid.
    """
    if not all(isfinite(x) and x >= 0 for x in
               (filtration, lymph, minutes, *initial)):
        raise ValueError("finite nonnegative accounting inputs required")
    blood, tissue, returned = initial
    result = (blood - filtration * minutes,
              tissue + (filtration - lymph) * minutes,
              returned + lymph * minutes)
    if min(result) < 0:
        raise ValueError("prescribed rates exhaust a compartment")
    return result


def control(t, pressure=1.3):
    """Dimensionless illustrative pressure step at t=2 s; synthetic tau=3 s."""
    from math import exp
    positive("pressure", pressure)
    if not isfinite(t) or t < 0:
        raise ValueError("time must be finite and nonnegative")
    target = min(1.5, max(0.7, pressure))
    resistance = 1 if t < 2 else target + (1 - target) * exp(-(t - 2) / 3)
    p = 1 if t < 2 else pressure
    return p, resistance, p / resistance


def checks():
    q = poiseuille(1000, 20e-6, 1e-3, 3e-3)
    assert isclose(q, 2.094395102393196e-11)
    assert isclose(poiseuille(1000, 16e-6, 1e-3, 3e-3) / q, 0.4096)
    assert poiseuille(0, 20e-6, 1e-3, 3e-3) == 0
    assert isclose(poiseuille(-1000, 20e-6, 1e-3, 3e-3), -q)
    assert isclose(poiseuille(1000, 20e-6, 2e-3, 3e-3), q / 2)
    assert isclose(poiseuille(1000, 20e-6, 1e-3, 6e-3), q / 2)
    assert classical_drive(35) == 11 and classical_drive(17) == -7
    assert classical_drive(24) == 0
    assert classical_drive(35, sigma=0) == 35
    for rates in ((0.3, 0.3), (0.3, 0.1), (0.5, 0.3), (0, 0)):
        final = accounting(*rates, 20)
        assert isclose(sum(final), 120)
    assert accounting(0.3, 0.3, 20)[1] == 20
    assert accounting(0.3, 0.1, 20)[1] == 24
    assert accounting(0.5, 0.3, 20)[1] == 24
    assert isclose(control(100)[2], 1, abs_tol=1e-12)
    assert isclose(control(100, 2)[2], 4 / 3, abs_tol=1e-12)
    for args in ((1000, 0, 1, 1), (1000, 1, -1, 1),
                 (1000, 1, 1, float("nan"))):
        try:
            poiseuille(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid tube accepted")
    try:
        accounting(100, 0, 20)
    except ValueError:
        pass
    else:
        raise AssertionError("exhausted compartment accepted")
    print("All dimensional, symmetry, limit, conservation and rejection checks passed.")
    print(f"Ideal tube Q = {q:.9e} m^3/s = {q * 60e9:.6f} microliter/min")
    print("Radius ratios: r/r0, Q/Q0, R/R0")
    for factor in (0.8, 1, 1.2):
        print(f"{factor:.1f} {factor**4:.6f} {factor**-4:.6f}")
    print("Classical end drives: +11.0, -7.0 mmHg; mean linear drive +2.0 mmHg")
    print("Illustrative K=0.01 mL/(min mmHg): net classical filtration 0.020 mL/min")
    for label, f, l in (("balanced", 0.3, 0.3), ("low drainage", 0.3, 0.1),
                        ("high filtration", 0.5, 0.3)):
        print(label, "final regional volumes (mL):", accounting(f, l, 20))
    for time in (0, 2, 5, 11):
        print(f"Synthetic control t={time}: P,R,Q =", tuple(round(v, 6) for v in control(time)))
    print("Bounded final Q at doubled pressure = 1.333333 baseline")
    print("Equal branches R=2 -> Rparallel=1; Rseries=4 (arbitrary consistent units)")
    print(f"20% narrowing: flow reduction = {(1 - 0.8**4) * 100:.2f}%")
    print(f"100 branches at 0.1 upstream area: total area {100 * 0.1:g}; "
          f"speed ratio {1 / (100 * 0.1):g}")


if __name__ == "__main__":
    checks()
