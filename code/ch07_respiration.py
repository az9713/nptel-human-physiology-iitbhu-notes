"""Chapter 7: synthetic ventilation and empirical binding, standard library only.

Run: python code/ch07_respiration.py
No patient calibration, gas kinetics, heterogeneous lung or clinical prediction.
"""
import json
import math


def ventilation(t, tidal=0.5, period=4.0, resistance=2.0, compliance=0.1):
    """L, s, cmH2O; inward flow positive. Prescribed volume, derived pressures."""
    if not all(math.isfinite(v) for v in (t, tidal, period, resistance, compliance)):
        raise ValueError('finite inputs required')
    if tidal < 0 or period <= 0 or resistance < 0 or compliance <= 0:
        raise ValueError('invalid mechanical parameter')
    a = 2 * math.pi * ((t / period) % 1)
    dv = tidal * (1 - math.cos(a)) / 2
    q = tidal * math.pi / period * math.sin(a)
    alv = -resistance * q
    recoil = 5 + dv / compliance
    return dict(volume=2.5 + dv, flow=q, alveolar=alv,
                pleural=alv-recoil, transpulmonary=recoil)


def saturation(p, p50=26, n=2.7):
    if not all(math.isfinite(v) for v in (p, p50, n)) or p < 0 or p50 <= 0 or n <= 0:
        raise ValueError('p >= 0, P50 > 0, n > 0 required')
    if p == 0:
        return 0.0
    return 1 / (1 + (p50/p)**n)


def minute_ventilation(tidal, frequency, deadspace=0.15):
    if not all(math.isfinite(x) for x in (tidal, frequency, deadspace)):
        raise ValueError('finite ventilation inputs required')
    if min(tidal, frequency, deadspace) < 0 or deadspace > tidal:
        raise ValueError('require 0 <= deadspace <= tidal and frequency >= 0')
    return dict(total=tidal*frequency, alveolar=(tidal-deadspace)*frequency)


def diffusion_relative(area=1, thickness=1, coefficient=1, gradient=64):
    if not all(math.isfinite(x) for x in (area, thickness, coefficient, gradient)):
        raise ValueError('finite diffusion inputs required')
    if min(area, coefficient) < 0 or thickness <= 0:
        raise ValueError('nonnegative area/coefficient and positive thickness required')
    return coefficient*area/thickness*gradient


def checks():
    max_mass_error = 0
    for i in range(1001):
        t = 4*i/1000
        s = ventilation(t)
        h = 1e-5
        derivative = (ventilation(t+h)['volume']-ventilation(t-h)['volume'])/(2*h)
        max_mass_error = max(max_mass_error, abs(derivative-s['flow']))
        assert 2.5-1e-12 <= s['volume'] <= 3+1e-12
        assert abs(s['alveolar']+2*s['flow']) < 1e-12
        assert abs(s['alveolar']-s['pleural']-s['transpulmonary']) < 1e-12
        assert s['pleural'] < 0
        assert abs(ventilation(t+4)['volume']-s['volume']) < 1e-12
    assert max_mass_error < 1e-8
    for t in (0, 2, 4):
        assert abs(ventilation(t)['flow']) < 1e-12
        assert abs(ventilation(t)['alveolar']) < 1e-12
    assert ventilation(0)['pleural'] == -5
    assert ventilation(2)['pleural'] == -10
    assert ventilation(1, tidal=0)['flow'] == 0
    assert ventilation(1, resistance=0)['alveolar'] == 0
    assert abs(ventilation(1, resistance=4)['alveolar']/ventilation(1)['alveolar']-2) < 1e-12
    assert ventilation(2, compliance=.2)['transpulmonary'] == 7.5
    assert saturation(26) == .5 and saturation(0) == 0
    assert saturation(1e9) > .999999
    seq = [saturation(i) for i in range(121)]
    assert all(0 <= x <= 1 for x in seq)
    assert all(a <= b for a, b in zip(seq, seq[1:]))
    assert saturation(40, 34) < saturation(40, 26)
    assert diffusion_relative(thickness=2) == 32
    assert diffusion_relative(area=2, thickness=2) == 64
    assert diffusion_relative(gradient=0) == 0
    assert diffusion_relative(gradient=-64) == -64
    for fn, args in [(ventilation,(1, .5, 0)), (ventilation,(1,.5,4,2,0)),
                     (saturation,(-1,)), (saturation,(1,0)),
                     (minute_ventilation,(.1,15,.15)), (diffusion_relative,(1,0))]:
        try:
            fn(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid input accepted')
    for bad in (float('nan'), float('inf'), -float('inf')):
        for fn, valid in ((minute_ventilation, [.5, 15, .15]),
                          (diffusion_relative, [1, 1, 1, 64])):
            for index in range(len(valid)):
                args = list(valid)
                args[index] = bad
                try:
                    fn(*args)
                except ValueError:
                    pass
                else:
                    raise AssertionError('nonfinite input accepted')
    return max_mass_error


if __name__ == '__main__':
    error = checks()
    output = dict(
        provenance='All mechanics and Hill parameters selected for teaching; not fitted human data.',
        max_finite_difference_mass_error_L_per_s=error,
        mechanical_samples={str(t):ventilation(t) for t in (0,1,2,3,4)},
        ventilation_cases={f'{v}L_at_{f}/min':minute_ventilation(v,f)
                           for v,f in ((.5,15),(.25,30),(.75,10))},
        saturation={str(p):dict(baseline=saturation(p),right_shift=saturation(p,34),
                                myoglobin=saturation(p,3,1)) for p in (20,26,40,104)},
        gradient_mmHg=104-40,
        dissolved_coefficient_mL_per_dL_per_mmHg=3e-5*100,
        dissolved_at_100_mL_per_dL=3e-5*100*100,
        incompatible_fraction_0_3_over_5=.3/5,
        illustrative_content=dict(bound=1.31*15*.98, dissolved=.003*100,
                                  total=1.31*15*.98+.003*100),
        relative_diffusion=dict(baseline=diffusion_relative(),double_thickness=diffusion_relative(thickness=2),
                                double_area_and_thickness=diffusion_relative(area=2,thickness=2)),
        checks='1001-state mass balance, pressure identities, bounds, periodicity; zero/limit/shift/invalid-input checks passed')
    print(json.dumps(output, indent=2))
