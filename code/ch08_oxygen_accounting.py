"""Chapter 8: explicit synthetic oxygen accounting; standard library only.
Run: python code/ch08_oxygen_accounting.py
No diagnosis, patient fitting, universal optical calibration or treatment model.
"""
import json
import math


def require(value, low, high):
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError("Input outside the finite teaching domain")


def content(hb, sat, pressure, coefficient=1.31, unit="mmHg"):
    require(hb, 0, 30)
    require(sat, 0, 1)
    require(pressure, 0, 1000)
    require(coefficient, 0, 2)
    if unit not in ("mmHg", "kPa"):
        raise ValueError("Specify mmHg or kPa")
    alpha = 0.003 if unit == "mmHg" else 0.003 * 7.500616827
    bound = coefficient * hb * sat
    dissolved = alpha * pressure
    return dict(bound=bound, dissolved=dissolved, total=bound + dissolved)


def balance(ca, cv, flow):
    require(ca, 0, 100)
    require(cv, 0, ca)
    require(flow, 0, 100)
    return dict(delivery=10 * flow * ca,
                consumption=10 * flow * (ca - cv),
                returned=10 * flow * cv,
                extraction=(ca - cv) / ca if ca > 0 and flow > 0 else None)


def volumes(vt=0.5, irv=3, erv=1.1, rv=1.2):
    for value in (vt, irv, erv, rv):
        require(value, 0, 20)
    return dict(vt=vt, irv=irv, erv=erv, rv=rv, ic=vt + irv,
                frc=erv + rv, vc=vt + irv + erv,
                tlc=vt + irv + erv + rv)


def optical(ac_red, dc_red, ac_ir, dc_ir):
    for value in (ac_red, dc_red, ac_ir, dc_ir):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Signals must be finite and positive")
    ratio = (ac_red / dc_red) / (ac_ir / dc_ir)
    return dict(r=ratio, illustrativePercent=130 - 30 * ratio)


def occupancy(co, functional=0.98):
    require(co, 0, 1)
    require(functional, 0, 1)
    return dict(co=co, oxy=(1 - co) * functional,
                deoxy=(1 - co) * (1 - functional))


def checks():
    v = volumes()
    assert math.isclose(v["tlc"], v["frc"] + v["ic"])
    assert math.isclose(v["tlc"], v["rv"] + v["vc"])
    ca = content(15, 0.98, 100)["total"]
    assert math.isclose(ca, 19.557)
    assert math.isclose(content(15, 0.98, 100 / 7.500616827,
                                unit="kPa")["total"], ca)
    assert math.isclose(content(15, 1, 13.3, unit="kPa")["total"],
                        19.95, abs_tol=0.001)
    for hb in (0, 7.5, 15, 30):
        for sat in (0, 0.5, 1):
            for flow in (0, 0.5, 5, 20):
                arterial = content(hb, sat, 100)["total"]
                for extraction in (0, 0.25, 1):
                    b = balance(arterial, arterial * (1 - extraction), flow)
                    assert math.isclose(b["delivery"],
                                        b["consumption"] + b["returned"],
                                        abs_tol=1e-10)
    for fraction in (0, 0.2, 1):
        o = occupancy(fraction)
        assert math.isclose(sum(o.values()), 1)
    assert optical(2, 100, 2, 100)["r"] == 1
    assert optical(1, 100, 2, 100)["illustrativePercent"] == 115
    for args in ((-1, 0.98, 100), (15, 98, 100), (15, 0.98, math.nan)):
        try:
            content(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input accepted")
    assert balance(0, 0, 0)["extraction"] is None
    assert balance(20, 15, 0)["extraction"] is None
    assert balance(0, 0, 5)["extraction"] is None
    assert balance(20, 15, 5)["extraction"] == 0.25
    print("PASS: 144 mass balances, units, capacities, limits, invalid inputs")
    print(json.dumps(dict(volumes=v, arterial=content(15, 0.98, 100),
                          balance=balance(20, 15, 5),
                          muscle=balance(19, 9, 0.5),
                          optical=optical(2, 100, 2, 100),
                          occupancy=occupancy(0.2)), sort_keys=True))
    print("Hb-pool capacity:", 1.34 * 150 * 5, "mL O2")
    print("Exercise VO2:", 45 * 70 / 1000, 52 * 70 / 1000,
          (52 - 45) * 70 / 1000, "L/min")
    print("Corrected lecture DO2:", 5 * 10 * ca, "mL/min")
    print("Lecture rest extraction:", 254.5 / 997.5)


if __name__ == "__main__":
    checks()
