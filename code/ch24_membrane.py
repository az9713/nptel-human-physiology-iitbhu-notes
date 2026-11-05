"""Chapter 24: sign-explicit teaching calculations and a canonical squid HH trace.

Voltages are V_inside - V_outside. Ionic/pump current is outward-positive;
applied injected current in the HH balance is inward-positive.
The HH parameters are the modern-voltage form of the 1952 squid giant-axon
model at 6.3 C; they are not a human axon, synapse, or spatial cable fit.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R, F = 8.314462618, 96485.33212


def finite(*values):
    try:
        valid = all(math.isfinite(x) for x in values)
    except (TypeError, OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError("all numeric inputs must be finite")


def nernst_mv(z: int, inside: float, outside: float, temp_k: float) -> float:
    """Single-ion ideal-activity approximation; output millivolts."""
    finite(z, inside, outside, temp_k)
    if z == 0 or inside <= 0 or outside <= 0 or temp_k <= 0:
        raise ValueError("nonzero valence and positive activities/temperature required")
    # Log difference avoids overflow in outside/inside for extreme positive inputs.
    value = 1000 * R * temp_k / (z * F) * (math.log(outside) - math.log(inside))
    if not math.isfinite(value):
        raise ValueError("Nernst output not representable")
    return value


def steady_mv(reversals: tuple[float, ...], conductances: tuple[float, ...],
              pump_out_ua_cm2: float = 0) -> float:
    """Synthetic balance; finite inputs and intermediate sums are required."""
    if len(reversals) != len(conductances) or not reversals:
        raise ValueError("matching nonempty pathways required")
    finite(*reversals, *conductances, pump_out_ua_cm2)
    reversals = tuple(float(e) for e in reversals)
    conductances = tuple(float(g) for g in conductances)
    pump_out_ua_cm2 = float(pump_out_ua_cm2)
    if min(conductances) < 0:
        raise ValueError("nonnegative conductances with positive total required")
    total = sum(conductances)
    if not math.isfinite(total) or total <= 0:
        raise ValueError("positive total conductance must be representable")
    terms = [g * e for g, e in zip(conductances, reversals)]
    if not all(math.isfinite(term) for term in terms):
        raise ValueError("conductance-reversal products must be representable")
    if any(g != 0 and e != 0 and term == 0
           for g, e, term in zip(conductances, reversals, terms)):
        raise ValueError("nonzero conductance-reversal product underflowed")
    numerator = sum(terms) - pump_out_ua_cm2
    if not math.isfinite(numerator):
        raise ValueError("steady numerator must be representable")
    result = numerator / total
    if not math.isfinite(result):
        raise ValueError("steady output not representable")
    if numerator != 0 and result == 0:
        raise ValueError("nonzero steady output underflowed")
    return result


def _vtrap(x: float, scale: float) -> float:
    """x/(1-exp(-x/scale)) with a removable zero limit."""
    y = x / scale
    if abs(y) < 1e-7:
        return scale * (1 + y / 2 + y * y / 12)
    return x / -math.expm1(-y)


def rates(v: float) -> tuple[float, float, float, float, float, float]:
    finite(v)
    return (.1 * _vtrap(v + 40, 10), 4 * math.exp(-(v + 65) / 18),
            .07 * math.exp(-(v + 65) / 20), 1 / (1 + math.exp(-(v + 35) / 10)),
            .01 * _vtrap(v + 55, 10), .125 * math.exp(-(v + 65) / 80))


def hh_rhs(t: float, y: tuple[float, float, float, float], pulses: tuple[tuple[float, float, float], ...]):
    v, m, h, n = y
    am, bm, ah, bh, an, bn = rates(v)
    ina = 120 * m**3 * h * (v - 50)
    ik = 36 * n**4 * (v + 77)
    il = .3 * (v + 54.387)
    injected = sum(amp for start, stop, amp in pulses if start <= t < stop)
    return (injected - ina - ik - il, am * (1 - m) - bm * m,
            ah * (1 - h) - bh * h, an * (1 - n) - bn * n)


def hh_trace(duration_ms=25.0, step_ms=.0025,
             pulses=((1.0, 2.0, 10.0), (6.0, 7.0, 10.0), (18.0, 19.0, 10.0))):
    """RK4 single-compartment trace; m,h,n dimensionless, I in microA/cm2."""
    finite(duration_ms, step_ms)
    if duration_ms <= 0 or step_ms <= 0 or step_ms > .05:
        raise ValueError("positive duration and step <= .05 ms required")
    if any(not (math.isfinite(a) and math.isfinite(b) and math.isfinite(c) and 0 <= a < b <= duration_ms)
           for a, b, c in pulses):
        raise ValueError("finite pulses in duration required")
    am, bm, ah, bh, an, bn = rates(-65)
    y = (-65., am/(am+bm), ah/(ah+bh), an/(an+bn))
    count = round(duration_ms / step_ms)
    if not math.isclose(count*step_ms, duration_ms, abs_tol=1e-9):
        raise ValueError("duration must be an integer step count")
    out = []
    def add(a, b, k): return tuple(x + k*z for x, z in zip(a, b))
    for i in range(count + 1):
        t = i * step_ms
        v, m, h, n = y
        if i % max(1, round(.1 / step_ms)) == 0:
            out.append({"t": round(t, 5), "v": v, "m": m, "h": h, "n": n,
                        "gNa": 120*m**3*h, "gK": 36*n**4})
        if i == count: break
        k1 = hh_rhs(t, y, pulses)
        k2 = hh_rhs(t + step_ms/2, add(y, k1, step_ms/2), pulses)
        k3 = hh_rhs(t + step_ms/2, add(y, k2, step_ms/2), pulses)
        k4 = hh_rhs(t + step_ms, add(y, k3, step_ms), pulses)
        y = tuple(x + step_ms*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(y,k1,k2,k3,k4))
        if not all(math.isfinite(x) for x in y) or not all(-.00001 <= x <= 1.00001 for x in y[1:]):
            raise ArithmeticError("HH integration left finite gate domain")
    return out


def rc_trace(duration_ms=40.0, step_ms=.05, e_gaba_mv=-70.0, gaba_on=True):
    """Synthetic current-clamp RC synapse, no spike threshold or cable."""
    finite(duration_ms, step_ms, e_gaba_mv)
    if duration_ms <= 0 or step_ms <= 0 or step_ms > .1:
        raise ValueError("positive duration and step <= .1 ms required")
    count = round(duration_ms / step_ms)
    if not math.isclose(count*step_ms, duration_ms, abs_tol=1e-9):
        raise ValueError("duration must be an integer step count")
    v = -70.0
    out = []
    for i in range(count + 1):
        t = i*step_ms
        ge = .06*math.exp(-(t-8)/8) if t >= 8 else 0
        gi = (.10*math.exp(-(t-8)/10) if t >= 8 else 0) if gaba_on else 0
        if i % max(1, round(.1/step_ms)) == 0:
            out.append({"t": round(t,5), "v": v, "gE": ge, "gGABA": gi,
                        "eGABA": e_gaba_mv})
        if i == count: break
        # C=1 uF/cm2, conductances mS/cm2, so dV/dt in mV/ms.
        dv = -(.1*(v+70) + ge*v + gi*(v-e_gaba_mv))
        v += step_ms*dv
        if not math.isfinite(v): raise ArithmeticError("RC output nonfinite")
    return out


def checks():
    ek = nernst_mv(1, 140, 4, 310.15)
    ena = nernst_mv(1, 15, 145, 310.15)
    assert -100 < ek < -90 and 55 < ena < 65
    assert math.isclose(nernst_mv(-1, 10, 100, 310.15), -nernst_mv(1, 10, 100, 310.15))
    for bad in [(0,1,1,310), (1,0,1,310), (1,1,0,310), (1,1,1,0)]:
        try: nernst_mv(*bad)
        except ValueError: pass
        else: raise AssertionError("invalid Nernst domain accepted")
    baseline = steady_mv((-90,60,-70), (.8,.15,.25), 0)
    pump = steady_mv((-90,60,-70), (.8,.15,.25), 2)
    assert math.isclose(baseline-pump, 2/1.2)
    assert steady_mv((-70,), (1.2,), 0) == -70
    assert steady_mv((1e150,), (1e150,), 0) == 1e150
    assert math.isclose(steady_mv((1e-100,), (1e-200,), 0), 1e-100)
    assert steady_mv((1e-100, -70), (0, 1), 0) == -70
    assert steady_mv((0,), (1,), 0) == 0
    for reversals, conductances, pump_current in (
        ((0., 0.), (1e308, 1e308), 1e308),
        ((1e308,), (1e308,), 0),
        ((0.,), (1e-308,), 1e308),
        ((0.,), (10**1000,), 0),
        ((1e-100,), (1e-300,), 0),
        ((0.,), (1e308,), 5e-324),
    ):
        try:
            steady_mv(reversals, conductances, pump_current)
        except ValueError:
            pass
        else:
            raise AssertionError("unrepresentable steady balance accepted")
    assert math.isclose(_vtrap(0, 10), 10) and math.isclose(_vtrap(0,10), _vtrap(1e-9,10), rel_tol=1e-8)
    trace = hh_trace()
    assert len(trace)==251 and min(q["v"] for q in trace)<-70 and max(q["v"] for q in trace)>0
    assert max(q["v"] for q in trace if 0<=q["t"]<5)>0
    assert max(q["v"] for q in trace if 5<=q["t"]<11)<0
    assert max(q["v"] for q in trace if 16<=q["t"]<24)>0
    assert all(0<=q[k]<=1 for q in trace for k in ("m","h","n"))
    e = rc_trace(gaba_on=False)
    shunt = rc_trace(e_gaba_mv=-70, gaba_on=True)
    assert max(q["v"] for q in shunt) < max(q["v"] for q in e)
    dep = rc_trace(e_gaba_mv=-60, gaba_on=True)
    assert max(q["v"] for q in dep) > max(q["v"] for q in shunt)
    return {"E_K_mV": ek, "E_Na_mV": ena, "steady_no_pump_mV": baseline,
            "steady_with_outward_pump_mV": pump, "HH_peak_mV": max(q["v"] for q in trace),
            "HH_min_mV": min(q["v"] for q in trace), "EPSP_peak_mV": max(q["v"] for q in e),
            "shunted_peak_mV": max(q["v"] for q in shunt), "depolarizing_GABA_peak_mV": max(q["v"] for q in dep)}


def export():
    result = {"schema": "ch24-model-v1", "sign": "V_inside - V_outside; outward-positive ionic/pump current; inward-positive HH applied injection", "units": {"t":"ms", "v":"mV", "g":"mS/cm2"},
              "boundaries": "HH single-compartment squid giant axon at 6.3 C; RC synapse and rest examples are separate synthetic teaching constructions; no human fit or cable propagation speed",
              "nernst": {"T_K": 310.15, "K_inside":140,"K_outside":4,"Na_inside":15,"Na_outside":145,
                          "E_K_mV":nernst_mv(1,140,4,310.15),"E_Na_mV":nernst_mv(1,15,145,310.15)},
              "rest": {"reversals_mV":[-90,60,-70],"conductances_mS_cm2":[.8,.15,.25],"outward_pump_uA_cm2":2,
                       "without_pump_mV":steady_mv((-90,60,-70),(.8,.15,.25),0),
                       "with_pump_mV":steady_mv((-90,60,-70),(.8,.15,.25),2)},
              "hh": {"temperature_C":6.3,"C_uF_cm2":1,"gbar_mS_cm2":{"Na":120,"K":36,"leak":.3},"E_mV":{"Na":50,"K":-77,"leak":-54.387},
                     "pulses_uA_cm2_ms":[[1,2,10],[6,7,10],[18,19,10]],"states":hh_trace()},
              "synapse": {"C_uF_cm2":1,"leak_mS_cm2":.1,"E_leak_mV":-70,"E_exc_mV":0,
                          "E_GABA_cases_mV":[-70,-60],"exc_only":rc_trace(gaba_on=False),"shunt":rc_trace(e_gaba_mv=-70,gaba_on=True),"depolarizing_GABA":rc_trace(e_gaba_mv=-60,gaba_on=True)}}
    target=ROOT/"assets/ch24-model.json"
    target.write_text(json.dumps(result,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf8")
    return target


if __name__ == "__main__":
    print(json.dumps({"checks":checks(),"export":str(export().relative_to(ROOT))},indent=2))
