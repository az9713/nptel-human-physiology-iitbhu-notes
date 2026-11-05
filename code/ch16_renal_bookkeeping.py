"""Synthetic renal accounting; standard library only, no patient estimation.

Run from any directory. Prints JSON; creates no files. Inputs must use matching
mL/min and mmHg conventions. Pressure flux is signed and not clipped into a
physiological GFR. The resistance analogy omits a filtration side branch.
"""
import json
import math


def flow(rbf, hct, gfr):
    """Return plasma/cell split and vascular outflows in mL/min."""
    if not all(math.isfinite(v) for v in (rbf, hct, gfr)):
        raise ValueError("Finite inputs required")
    if rbf <= 0 or not 0 <= hct < 1 or not 0 <= gfr <= rbf * (1-hct):
        raise ValueError("Incompatible flow inputs")
    rpf = rbf * (1-hct)
    return dict(rpf=rpf, cells=rbf*hct, ff=gfr/rpf,
                efferent_plasma=rpf-gfr, efferent_blood=rbf-gfr)


def pressure(pgc, pbs, oncotic_blood, oncotic_capsule, kf):
    """Signed outward flux from a fixed-coefficient Starling relation."""
    if not all(math.isfinite(v) for v in
               (pgc, pbs, oncotic_blood, oncotic_capsule, kf)) or kf < 0:
        raise ValueError("Invalid pressures or coefficient")
    nfp = pgc-pbs-oncotic_blood+oncotic_capsule
    return dict(nfp=nfp, signed_flux=kf*nfp)


def resistance(ra, re, pa=100, pv=10):
    """Forward two-resistor circuit: finite inputs, ra/re > 0 and pa > pv."""
    if not all(math.isfinite(v) for v in (ra, re, pa, pv)):
        raise ValueError("Finite inputs required")
    if min(ra, re) <= 0 or pa <= pv:
        raise ValueError("Positive resistances and inlet above outlet required")
    q = (pa-pv)/(ra+re)
    return dict(q=q, pgc=pv+q*re)


def check():
    hct = 1-625/1200
    f = flow(1200, hct, 125)
    assert math.isclose(f['rpf'], 625)
    assert math.isclose(f['cells'], 575)
    assert math.isclose(f['efferent_blood']+125, 1200)
    assert math.isclose(f['efferent_plasma']+f['cells'], 1075)
    for pbs in range(15, 26):
        p = pressure(55, pbs, 30, 0, 12.5)
        assert math.isclose(p['signed_flux'], 125-12.5*(pbs-15))
    assert pressure(55, 30, 30, 0, 12.5)['signed_flux'] < 0
    assert resistance(2, 1)['pgc'] == 40
    assert resistance(1, 2)['pgc'] == 70
    assert resistance(2, 1)['q'] == resistance(1, 2)['q'] == 30
    invalid_resistance = [(1, 1, 10, 10), (1, 1, 9, 10)]
    for value in (math.nan, math.inf, -math.inf):
        for index in range(4):
            args = [1, 1, 100, 10]
            args[index] = value
            invalid_resistance.append(tuple(args))
    for args in invalid_resistance:
        try:
            resistance(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid forward-circuit input accepted')
    for args in ((1200, -1, 125), (1200, 1, 125), (1200, .5, 700)):
        try:
            flow(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid input accepted')
    return dict(hct=hct, flows=f,
                daily_filtrate_liters=125*60*24/1000,
                pbs_sweep=[dict(pbs=x, **pressure(55, x, 30, 0, 12.5))
                           for x in (15, 20, 25)],
                resistance_baseline=resistance(1, 1),
                afferent_double=resistance(2, 1),
                efferent_double=resistance(1, 2),
                clearance=100*1.25/1,
                model_urine=125-124,
                daily_urine_liters=(125-124)*1440/1000,
                water_reabsorbed_percent=124/125*100,
                example_filtered_mg_min=125/100*1,
                right_obstructed=pressure(55, 20, 30, 0, 6.25),
                left_initial=pressure(55, 15, 30, 0, 6.25),
                bilateral_obstructed=6.25*5+6.25*10,
                checks='passed')


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
