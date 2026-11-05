"""Synthetic Chapter 25 models: no human rates, diagnosis or treatment model.

Run directly for focused checks and the printed worked-example outputs.
Pass --export to write deterministic states used by the chapter's controls.
The four recycling pools count represented five-carbon skeletons, not nitrogen,
ATP or all metabolic carbon. Equal stage rates and closure are teaching choices.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys


def bounded(value: float, lower: float, upper: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    if not lower <= value <= upper or not math.isfinite(value):
        raise ValueError(f"{name} must be finite in [{lower}, {upper}]")
    return float(value)


def recycling(time: float, rate: float = 1, amount: float = 1) -> dict:
    """Three irreversible equal-rate stages, finite bounded artificial units."""
    t = bounded(time, 0, 100, "time")
    k = bounded(rate, 0, 100, "rate")
    total = bounded(amount, 0, 1e6, "amount")
    if 0 < total < 1e-100:
        raise ValueError("positive amount must be at least 1e-100 for relative conservation")
    x = k*t
    e = math.exp(-x)
    a = x*e
    q = x*x*e/2
    returned = max(0.0, 1-math.fsum((e, a, q)))
    pools = [total*p for p in (e, a, q, returned)]
    if not all(math.isfinite(v) and 0 <= v <= total for v in pools):
        raise ValueError("pool output outside representable amount domain")
    if not math.isclose(math.fsum(pools), total, rel_tol=1e-12, abs_tol=0):
        raise ValueError("pool output cannot preserve relative amount conservation")
    return dict(zip(("extracellular_glu", "astrocyte_glu",
                     "astrocyte_gln", "returned_neuronal"), pools))


def photo_response(time: float, tau: float = 1) -> dict:
    """Unit light pulse on [1,4), response y'=(u-y)/tau; artificial time."""
    t = bounded(time, 0, 100, "time")
    tc = bounded(tau, .05, 10, "tau")
    if t < 1:
        y = 0.0
    elif t < 4:
        y = -math.expm1(-(t-1)/tc)
    else:
        y = -math.expm1(-3/tc)*math.exp(-(t-4)/tc)
    return {"light": int(1 <= t < 4), "closure": y,
            "open_fraction": 1-y, "release_proxy": 1-y}


ROUTES = (
    {"field": "right", "eye": "left", "retina": "temporal",
     "crosses": False, "hemisphere": "left"},
    {"field": "right", "eye": "right", "retina": "nasal",
     "crosses": True, "hemisphere": "left"},
    {"field": "left", "eye": "left", "retina": "nasal",
     "crosses": True, "hemisphere": "right"},
    {"field": "left", "eye": "right", "retina": "temporal",
     "crosses": False, "hemisphere": "right"},
)


def checks() -> int:
    count = 0
    for t, k, m in [(0, 1, 1), (2, 1, 1), (2, .25, 1),
                    (2, 1, 1e-100), (100, 100, 1e-100),
                    (100, 100, 1e6), (3, 0, 2), (3, 2, 0)]:
        p = recycling(t, k, m)
        assert math.isclose(math.fsum(p.values()), m, rel_tol=1e-12, abs_tol=0)
        assert all(0 <= v <= m for v in p.values())
        count += 2
    assert recycling(0)["extracellular_glu"] == 1
    assert recycling(3, 0)["extracellular_glu"] == 1
    assert recycling(2)["extracellular_glu"] < recycling(2, .25)["extracellular_glu"]
    count += 3
    for t in [0, 1, 2, 4, 5, 8, 100]:
        p = photo_response(t)
        assert 0 <= p["closure"] <= 1
        assert p["open_fraction"] == p["release_proxy"]
        count += 2
    assert photo_response(1)["closure"] == 0
    assert math.isclose(photo_response(4)["closure"], 1-math.exp(-3))
    assert photo_response(4)["light"] == 0
    count += 3
    for r in ROUTES:
        assert r["crosses"] == (r["retina"] == "nasal")
        assert r["hemisphere"] != r["field"]
        count += 2
    for bad in [-1, math.nan, math.inf, 101, True]:
        try:
            recycling(bad)
            raise AssertionError("bad domain accepted")
        except (ValueError, TypeError):
            count += 1
    for function, args in [(recycling,(1,-1,1)), (recycling,(1,math.inf,1)),
                           (recycling,(1,1,1e7)), (recycling,(1,1,math.nan)),
                           (recycling,(2,1,5e-324)), (recycling,(2,1,1e-323)),
                           (recycling,(2,1,1e-101)), (recycling,(10**1000,1,1)),
                           (recycling,(1,10**1000,1)), (recycling,(1,1,10**1000)),
                           (photo_response,(10**1000,1)), (photo_response,(1,10**1000)),
                           (photo_response,(1,0)), (photo_response,(1,11)),
                           (photo_response,(math.nan,1)), (photo_response,(1,True))]:
        try:
            function(*args)
        except (ValueError,TypeError):
            count += 1
        else:
            raise AssertionError("invalid secondary parameter accepted")
    for tau in (.05,10):
        assert 0 <= photo_response(4,tau)["closure"] <= 1
        assert photo_response(100,tau)["closure"] < photo_response(4,tau)["closure"]
        count += 2
    return count


if __name__ == "__main__":
    print(f"PASS {checks()} focused numerical/domain/topology checks")
    print("recycling t=2, k=1:", json.dumps(recycling(2), sort_keys=True))
    print("recycling t=2, k=.25:", json.dumps(recycling(2, .25), sort_keys=True))
    print("photo t=4:", json.dumps(photo_response(4), sort_keys=True))
    print("photo t=5:", json.dumps(photo_response(5), sort_keys=True))
    if "--export" in sys.argv:
        states = [{"time": i/20, "recycling": recycling(i/20),
                   "slower": recycling(i/20, .25),
                   "photo": photo_response(i/20)} for i in range(161)]
        out = Path(__file__).resolve().parents[1]/"assets/ch25-data.json"
        out.write_text(json.dumps({"time_unit": "artificial model unit",
                                  "states": states, "routes": ROUTES},
                                 indent=2)+"\n", encoding="utf-8")
