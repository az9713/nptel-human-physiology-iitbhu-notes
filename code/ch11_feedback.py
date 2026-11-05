"""Synthetic thyroid feedback and binding checks; no patient calibration.
Run with Python 3. No file/network effects or third-party dependencies.
"""
import json
import math


def nonnegative(*values):
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("Finite nonnegative inputs required")


def binding(free, capacity, kd):
    nonnegative(free, capacity, kd)
    if kd == 0:
        raise ValueError("Dissociation constant must be positive")
    numerator, denominator = capacity * free, kd + free
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        raise ValueError("Binding exceeds floating-point range")
    bound = numerator / denominator
    total = free + bound
    if not math.isfinite(bound) or not math.isfinite(total):
        raise ValueError("Binding exceeds floating-point range")
    return {"free": free, "bound": bound, "total": total}


def equilibrium(a=1.0, g=1.0, u=0.0):
    nonnegative(a, g, u)
    try:
        discriminant = (u + 1)**2 + 8*a*g
    except OverflowError as error:
        raise ValueError("Equilibrium exceeds floating-point range") from error
    if not math.isfinite(discriminant):
        raise ValueError("Equilibrium exceeds floating-point range")
    h = (u - 1 + math.sqrt(discriminant)) / 2
    s = 2*a/(1+h)
    if not math.isfinite(s) or not math.isfinite(h):
        raise ValueError("Equilibrium exceeds floating-point range")
    return {"s": s, "h": h}


def trajectory(a=1.0, g=1.0, u=0.0, duration=20.0, dt=0.01):
    nonnegative(a, g, u, duration, dt)
    if dt <= 0 or dt > 0.05 or duration > 100:
        raise ValueError("0 < dt <= 0.05; duration <= 100 model units")
    s, h = 1.0, 1.0
    out = [{"t": 0.0, "s": s, "h": h}]
    step_count = duration/dt
    if not math.isfinite(step_count):
        raise ValueError("Trajectory exceeds floating-point range")
    steps = math.ceil(step_count)
    for i in range(steps):
        step = min(dt, duration-i*dt)
        ds, dh = 2*a/(1+h)-s, g*s+u-h
        if not math.isfinite(ds) or not math.isfinite(dh):
            raise ValueError("Trajectory exceeds floating-point range")
        s, h = s+step*ds, h+step*dh
        if not math.isfinite(s) or not math.isfinite(h):
            raise ValueError("Trajectory exceeds floating-point range")
        out.append({"t": min((i+1)*dt, duration), "s": s, "h": h})
    return out


def checks():
    cases = [(1, 1, 0), (1, .25, 0), (.25, 1, 0), (1, 1, 1),
             (0, 1, 0), (1, 0, 0)]
    for a, g, u in cases:
        eq = equilibrium(a, g, u)
        assert abs(2*a/(1+eq["h"])-eq["s"]) < 1e-12
        assert abs(g*eq["s"]+u-eq["h"]) < 1e-12
        tr = trajectory(a, g, u, 40)
        assert all(r["s"] >= 0 and r["h"] >= 0 for r in tr)
        assert max(abs(tr[-1][k]-eq[k]) for k in ("s", "h")) < 1e-6
        fine = trajectory(a, g, u, 20, .005)[-1]
        coarse = trajectory(a, g, u, 20)[-1]
        assert max(abs(fine[k]-coarse[k]) for k in ("s", "h")) < 1e-5
    assert binding(0, 90, 9)["bound"] == 0
    for free in (0, 1, 10, 1000000):
        b = binding(free, 90, 9)
        assert 0 <= b["bound"] <= 90
        assert b["total"] == b["free"] + b["bound"]
    bad = [lambda: binding(1, -1, 9), lambda: binding(1, 90, 0),
           lambda: equilibrium(float("nan")),
           lambda: trajectory(dt=0), lambda: trajectory(dt=.2),
           lambda: equilibrium(1e308, 1e308, 0),
           lambda: equilibrium(1, 1, 1e308),
           lambda: trajectory(1e308, 1, 0, .01),
           lambda: trajectory(1, 1e308, 1e308, .01),
           lambda: trajectory(dt=5e-324),
           lambda: binding(1e308, 1e308, 9)]
    for call in bad:
        try:
            call()
        except ValueError:
            continue
        raise AssertionError("Invalid input accepted")
    assert trajectory(duration=0) == [{"t": 0.0, "s": 1.0, "h": 1.0}]
    assert trajectory(duration=.025)[-1]["t"] == .025
    return {"cases": [equilibrium(*p) for p in cases],
            "binding": [binding(1, 90, 9), binding(1, 180, 9)],
            "checks": "equilibrium residuals, nonnegative states, limits, "
                      "step refinement, binding accounting, invalid/overflow inputs"}


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))
