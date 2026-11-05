"""Prescribed synthetic ventricular cycle with ideal-diode pressure checks.

This kinematic construction specifies stroke volume and phase durations, then
derives flows and compatible pressures. It does NOT predict stroke volume from
afterload, estimate a patient, or fit a measured pressure-volume loop.
Units: phase dimensionless; time s; volume mL; pressure mmHg;
resistance mmHg*s/mL; instantaneous flow mL/s; output L/min.
"""

from math import cos, isclose, isfinite, pi, sin


def diode(upstream, downstream, resistance):
    if not isfinite(resistance) or resistance <= 0:
        raise ValueError("resistance must be finite and positive")
    return max(upstream - downstream, 0.0) / resistance


def cycle(phase, stroke=70.0, period=0.8, out_resistance=0.04,
          inlet_pressure=10.0, outlet_pressure=80.0):
    if any(not isfinite(x) for x in (phase, stroke, period, out_resistance,
                                    inlet_pressure, outlet_pressure)):
        raise ValueError("all inputs must be finite")
    if not 0 <= phase <= 1 or not 0 <= stroke <= 100 or period <= 0:
        raise ValueError("phase 0..1, stroke 0..100, period positive")
    if out_resistance <= 0 or outlet_pressure <= inlet_pressure:
        raise ValueError("positive resistance and ordered reservoir pressures")
    end_systolic = 50.0
    inlet_resistance = 0.01
    q_in = q_out = 0.0
    if phase < 0.4:
        u = phase / 0.4
        volume = end_systolic + stroke * (1 - cos(pi * u)) / 2
        q_in = stroke * pi * sin(pi * u) / (2 * 0.4 * period)
        pressure = inlet_pressure - inlet_resistance * q_in
        label = "filling"
    elif phase < 0.5:
        u = (phase - 0.4) / 0.1
        volume = end_systolic + stroke
        pressure = inlet_pressure + (outlet_pressure - inlet_pressure) * u
        label = "isovolumic contraction"
    elif phase < 0.8:
        u = (phase - 0.5) / 0.3
        volume = end_systolic + stroke * (1 + cos(pi * u)) / 2
        q_out = stroke * pi * sin(pi * u) / (2 * 0.3 * period)
        pressure = outlet_pressure + out_resistance * q_out
        label = "ejection"
    else:
        u = (phase - 0.8) / 0.2
        volume = end_systolic
        pressure = outlet_pressure - (outlet_pressure - inlet_pressure) * u
        label = "isovolumic relaxation"
    return dict(phase=phase, volume=volume, pressure=pressure,
                q_in=q_in, q_out=q_out, label=label,
                inlet_open=q_in > 1e-8, outlet_open=q_out > 1e-8)


def integrate(key, steps=10000, **params):
    period = params.get("period", 0.8)
    return sum(cycle((i + 0.5) / steps, **params)[key]
               for i in range(steps)) * period / steps


def regional(hepatic_factor=1.0):
    """Separate steady fixed-pressure network; mmHg and L/min.

    Arterial=95, venous=5. Gut and hepatic-artery resistances join
    at one liver inlet; hepatic outflow resistance is downstream in series.
    Values are selected to produce a 5.25 L/min baseline total, not fitted.
    """
    if not isfinite(hepatic_factor) or hepatic_factor <= 0:
        raise ValueError("positive finite hepatic resistance factor")
    rg, ra, rh = 86 / 1.2, 86 / .3, (4 / 1.5) * hepatic_factor
    rp = 1 / (1 / rg + 1 / ra)
    liver_out = 90 / (rp + rh)
    portal_pressure = 5 + rh * liver_out
    gut = (95 - portal_pressure) / rg
    hepatic_artery = (95 - portal_pressure) / ra
    return dict(portal_pressure=portal_pressure, gut=gut,
                hepatic_artery=hepatic_artery, liver_out=liver_out,
                kidney=1.0, other=2.75, total=3.75 + liver_out)


def check():
    for phase in (i / 1000 for i in range(1001)):
        s = cycle(phase)
        assert 50 - 1e-10 <= s["volume"] <= 120 + 1e-10
        assert isclose(s["q_in"], diode(10, s["pressure"], .01),
                       abs_tol=1e-9)
        assert isclose(s["q_out"], diode(s["pressure"], 80, .04),
                       abs_tol=1e-9)
        assert not (s["inlet_open"] and s["outlet_open"])
    for p in (.1, .3, .45, .6, .7, .9):
        h = 1e-6
        derivative = (cycle(p + h)["volume"] -
                      cycle(p - h)["volume"]) / (2 * h * .8)
        s = cycle(p)
        assert isclose(derivative, s["q_in"] - s["q_out"],
                       abs_tol=1e-5)
    assert isclose(integrate("q_in"), 70, abs_tol=1e-5)
    assert isclose(integrate("q_out"), 70, abs_tol=1e-5)
    for p in (0, .2, .45, .65, .9, 1):
        zero = cycle(p, stroke=0)
        assert zero["volume"] == 50 and zero["q_in"] == zero["q_out"] == 0
    assert diode(5, 10, .04) == 0
    assert diode(10, 10, .04) == 0
    assert isclose(cycle(.65, out_resistance=.08)["pressure"] - 80,
                   2 * (cycle(.65)["pressure"] - 80))
    assert cycle(0)["volume"] == cycle(1)["volume"]
    for factor in (0.5, 1, 2, 10):
        r = regional(factor)
        assert isclose(r["gut"] + r["hepatic_artery"], r["liver_out"])
        assert 5 < r["portal_pressure"] < 95
    for kwargs in ({"period": 0}, {"stroke": -1},
                   {"out_resistance": 0}, {"phase": 2}):
        try:
            cycle(**({"phase": .2} | kwargs))
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    print("Checks: 1001 states, diode inequalities, finite-difference balance,")
    print("integrated inflow/outflow, zero stroke, reverse/equal pressure,")
    print("resistance scaling, periodic volume and invalid inputs: PASS")


def main():
    for p in (.2, .45, .65, .9):
        s = cycle(p)
        print(f"phase {p:.2f}: {s['label']}; V={s['volume']:.6f} mL; "
              f"P={s['pressure']:.6f} mmHg; "
              f"Qin={s['q_in']:.6f}, Qout={s['q_out']:.6f} mL/s")
    print(f"HR={60/.8:.6f} beats/min; SV=70.000000 mL/beat; "
          f"CO={60/.8*70/1000:.6f} L/min; EF={70/120:.6f}")
    print(f"24 h turnover={60/.8*70/1000*60*24:.6f} L")
    print(f"Integrated inflow={integrate('q_in'):.6f} mL; "
          f"outflow={integrate('q_out'):.6f} mL")
    for r in (.04, .08):
        print(f"Prescribed-flow Rout={r:.2f}: peak P="
              f"{cycle(.65, out_resistance=r)['pressure']:.6f} mmHg")
    for stroke in (70, 35, 0):
        print(f"HR 120 and SV {stroke}: CO={120*stroke/1000:.6f} L/min")
    print(f"Regional pressure drop90 and resistances30,60: "
          f"flows={90/30:.6f},{90/60:.6f} L/min; "
          f"parallel R={1/(1/30+1/60):.6f} mmHg min/L")
    print(f"US gallon lecture conversion: {2000*3.785411784:.6f} L/day, "
          f"{2000*3.785411784/1440:.6f} L/min")
    for factor in (1, 2):
        print(f"Regional hepatic resistance factor {factor}: {regional(factor)}")
    check()


if __name__ == "__main__":
    main()
