"""Synthetic five-pool glucose-equivalent accounting; no patient calibration.
Run with Python 3; no dependencies. Time min, amounts g glucose equivalent.
The 10 L pool and 180 g/mol molar mass are explicit teaching choices.
"""
import json
import math


def simulate(sensitivity=1.0, meal=30.0, duration=240.0, dt=0.1):
    if not all(math.isfinite(x) for x in
               (sensitivity, meal, duration, dt)):
        raise ValueError("finite inputs required")
    if not (0 <= sensitivity <= 2 and 0 <= meal <= 60
            and 0 <= duration <= 240 and 0 < dt <= 0.5):
        raise ValueError("input outside teaching domain")
    d, b, liver, precursor, used = meal, 9.0, 60.0, 30.0, 0.0
    insulin, glucagon = 1.0, 1.0
    total = d + b + liver + precursor + used
    rows = []
    t = 0.0
    while True:
        absorption = 0.03*d
        storage = 0.003*insulin*b
        release = 0.002*glucagon*liver
        synthesis = 0.001*glucagon*precursor
        utilization = (0.008 + 0.006*sensitivity*insulin)*b
        rows.append(dict(t=t, gut=d, blood=b, liver=liver,
                         precursor=precursor, used=used,
                         glucose=b/1.8, insulin=insulin,
                         glucagon=glucagon, absorption=absorption,
                         storage=storage, release=release,
                         synthesis=synthesis, utilization=utilization,
                         residual=d+b+liver+precursor+used-total))
        if t >= duration - 1e-9:
            break
        h = min(dt, duration-t)
        insulin_target = 0.3 + 0.35*max(b-7, 0)
        glucagon_target = 1/(0.3+0.7*insulin)
        d -= h*absorption
        b += h*(absorption+release+synthesis-storage-utilization)
        liver += h*(storage-release)
        precursor -= h*synthesis
        used += h*utilization
        insulin += h*(insulin_target-insulin)/5
        glucagon += h*(glucagon_target-glucagon)/10
        t = min(duration, t+h)
    return rows


def checks():
    for sensitivity in (0, 0.5, 1, 1.5, 2):
        for meal in (0, 30, 60):
            rows = simulate(sensitivity, meal)
            assert max(abs(r["residual"]) for r in rows) < 1e-9
            assert all(min(r[k] for k in
                           ("gut", "blood", "liver", "precursor", "used"))
                       >= 0 for r in rows)
            assert all(rows[i+1]["used"] >= rows[i]["used"]
                       for i in range(len(rows)-1))
    fine = simulate(dt=0.05)
    standard = simulate()
    assert abs(fine[-1]["glucose"]-standard[-1]["glucose"]) < 0.005
    assert simulate(meal=0)[0]["absorption"] == 0
    assert simulate(duration=0)[0]["glucose"] == 5
    for bad in (-1, 3, float("nan")):
        try:
            simulate(sensitivity=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid sensitivity accepted")
    return "15 trajectories conserve glucose-equivalent carbon; limits passed"


if __name__ == "__main__":
    print(checks())
    for s in (0.5, 1.0, 1.5):
        rows = simulate(s)
        peak = max(rows, key=lambda r: r["glucose"])
        print(json.dumps(dict(sensitivity=s,
                              peak_glucose=round(peak["glucose"], 6),
                              peak_min=round(peak["t"], 3),
                              final_glucose=round(rows[-1]["glucose"], 6),
                              final_liver=round(rows[-1]["liver"], 6),
                              final_used=round(rows[-1]["used"], 6))))
    print("calcium:", 3+2-4, 3-4)
    print("pool g:", 5*10*180/1000)
    print("pulse change mmol/L:", 2*5/10)
