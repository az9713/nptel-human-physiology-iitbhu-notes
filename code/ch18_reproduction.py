"""Original Chapter18 bookkeeping, not a patient or kinetic model.
Run: python -X utf8 code/ch18_reproduction.py
Writes deterministic assets/ch18-data.json; standard library only.
"""
import json
import math
from pathlib import Path


def finite(value, name, lower=0):
    if isinstance(value, bool) or not math.isfinite(value) or value < lower:
        raise ValueError(name + ' must be finite and in the stated domain')


def cohort(primary=100, p1=0.9, p2=0.8, p3=0.75):
    finite(primary, 'primary cohort')
    if primary > 1e12:
        raise ValueError('Cohort outside bounded teaching domain [0, 1e12]')
    for p in (p1, p2, p3):
        finite(p, 'conditional survival')
        if p > 1:
            raise ValueError('Survival cannot exceed one')
    secondary = 2*primary*p1
    spermatids = 2*secondary*p2
    sperm = spermatids*p3
    discarded = 4*primary*(1-p1)+2*secondary*(1-p2)+spermatids*(1-p3)
    return {'primary': primary, 'secondary': secondary,
            'spermatids': spermatids, 'sperm': sperm,
            'discarded_C': discarded, 'initial_C': 4*primary,
            'DNA_residual': sperm+discarded-4*primary}


def axis(exogenous=0, leydig=1, inhibin_gain=1):
    # Independent minimal steroid and inhibin steady loops, fixed drive=2.
    # No GnRH pulses, steroid influence on FSH, concentration units or time.
    for x, name in ((exogenous, 'E'), (leydig, 'a'), (inhibin_gain, 'b')):
        finite(x, name)
        if x > 1e6:
            raise ValueError('Outside bounded teaching domain [0, 1e6]')
    c = 1+exogenous
    local = 4*leydig/(c+math.sqrt(c*c+8*leydig))
    lh = 2/(1+exogenous+local)
    fsh = 4/(1+math.sqrt(1+8*inhibin_gain))
    inhibin = inhibin_gain*fsh
    return {'E': exogenous, 'a': leydig, 'b': inhibin_gain,
            'LH': lh, 'T_local': local, 'T_systemic': local+exogenous,
            'FSH': fsh, 'inhibin': inhibin}


def mix(number_million, volume_ml):
    finite(number_million, 'count')
    finite(volume_ml, 'volume')
    if volume_ml == 0:
        raise ValueError('Concentration requires positive volume')
    result = number_million/volume_ml
    if not math.isfinite(result):
        raise ValueError('Concentration overflow')
    return result


def stages():
    return [
        {'id': 'preS', 'name': 'Pre-S committed precursor', 'cells': 1,
         'n': 2, 'C': 2, 'chromosomes': 46, 'chromatids': 46},
        {'id': 'postS', 'name': 'Post-S primary spermatocyte', 'cells': 1,
         'n': 2, 'C': 4, 'chromosomes': 46, 'chromatids': 92},
        {'id': 'MI', 'name': 'Completed meiosis I: secondary cells', 'cells': 2,
         'n': 1, 'C': 2, 'chromosomes': 23, 'chromatids': 46},
        {'id': 'MII', 'name': 'Completed meiosis II: round spermatids', 'cells': 4,
         'n': 1, 'C': 1, 'chromosomes': 23, 'chromatids': 23},
        {'id': 'shape', 'name': 'Elongating spermatids', 'cells': 4,
         'n': 1, 'C': 1, 'chromosomes': 23, 'chromatids': 23},
        {'id': 'release', 'name': 'Spermiation: released spermatozoa', 'cells': 4,
         'n': 1, 'C': 1, 'chromosomes': 23, 'chromatids': 23}]


def checks():
    full = cohort(100, 1, 1, 1)
    assert full['sperm'] == 400 and full['discarded_C'] == 0
    loss = cohort()
    assert abs(loss['DNA_residual']) < 1e-12
    assert loss['sperm'] == 216
    for p in (0, 0.1, 0.5, 1):
        r = cohort(100, p, p, p)
        assert abs(r['DNA_residual']) < 1e-10
    assert axis()['T_local'] == 1 and axis()['FSH'] == 1
    assert axis(inhibin_gain=0)['FSH'] == 2
    assert axis(leydig=0)['T_local'] == 0
    assert axis(2)['T_local'] < 1 < axis(2)['T_systemic']
    for r in [axis(e, a, b) for e in (0, 2, 100)
              for a in (0, 0.25, 1) for b in (0, 0.25, 1)]:
        assert abs(r['T_local']-r['a']*r['LH']) < 1e-12
        assert abs(r['FSH']*(1+r['inhibin'])-2) < 1e-12
    invalid = 0
    for call in (lambda: axis(math.nan), lambda: axis(-1),
                 lambda: axis(math.inf), lambda: axis(1e7),
                 lambda: cohort(p1=1.1), lambda: cohort(-1),
                 lambda: cohort(p2=math.nan), lambda: mix(1, 0)):
        try:
            call()
        except ValueError:
            invalid += 1
        else:
            raise AssertionError('Invalid domain accepted')
    assert invalid == 8
    return {'domain_rejections': invalid, 'cohort_conservation': True,
            'axis_equilibrium_residuals': True}


def main():
    result = {'scope': 'Synthetic count and steady-loop accounting; no time fit',
              'stages': stages(), 'cohort': cohort(),
              'axis_baseline': axis(), 'axis_exogenous': axis(2),
              'axis_inhibin_reduced': axis(inhibin_gain=0.25),
              'axis_leyddamage': axis(leydig=0.25),
              'axis_sweep': [axis(j/20) for j in range(101)],
              'numbers': {'concentration_before': mix(90, 3),
                          'concentration_after': mix(90, 6),
                          'ideal_primary100_products': 400,
                          'assortment_combinations': 2**23,
                          'four_point_six_times_sixteen': 4.6*16},
              'checks': checks()}
    target = Path(__file__).resolve().parents[1]/'assets/ch18-data.json'
    target.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'axis_sweep'},
                     indent=2))


if __name__ == '__main__':
    main()
