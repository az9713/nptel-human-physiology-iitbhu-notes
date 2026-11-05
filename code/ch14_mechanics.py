"""Chapter 14 original synthetic mechanics; standard library only.

No patient calibration, file writes, network or anatomical motion prediction.
Run python -X utf8 code/ch14_mechanics.py for printed cases and invariant checks.
"""
import math


def positive(*values):
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("finite positive inputs required")


def lever(load, arm, tendon_arm):
    """SI parallel-force balance; return tendon N and signed downward reaction N."""
    positive(load, arm, tendon_arm)
    tendon = load * arm / tendon_arm
    return tendon, tendon - load


def annulus(ro, ri):
    """Cross-sectional area and second area moment; metres -> m2, m4."""
    positive(ro)
    if not math.isfinite(ri) or not 0 <= ri < ro:
        raise ValueError("require 0 <= inner radius < outer radius")
    return math.pi * (ro**2-ri**2), math.pi/4*(ro**4-ri**4)


def stress(ro, ri, force, moment):
    """Linear homogeneous beam idealization: axial and extreme bending Pa."""
    if not all(math.isfinite(x) for x in (force, moment)):
        raise ValueError("finite force and moment required")
    area, inertia = annulus(ro, ri)
    return force/area, moment*ro/inertia


def remodeling(initial, formed, resorbed, cycles):
    """Aggregate volumes in mm3; zero allowed, no within-cycle feasibility check."""
    if not all(math.isfinite(x) and x >= 0 for x in (initial,formed,resorbed)):
        raise ValueError("nonnegative finite volumes required")
    if type(cycles) is not int or cycles < 0:
        raise ValueError("nonnegative integer cycles required")
    result = initial + cycles*(formed-resorbed)
    if result < 0:
        raise ValueError("negative terminal volume")
    return result


def load_share(t, total=600., initial_fluid_fraction=.8, tau=30.):
    """Synthetic held-load relaxation in seconds; not fitted cartilage data."""
    positive(total,tau)
    if not math.isfinite(t) or t < 0 or not 0 <= initial_fluid_fraction <= 1:
        raise ValueError("invalid time or fraction")
    fluid=total*initial_fluid_fraction*math.exp(-t/tau)
    return fluid,total-fluid


def main():
    ft, reaction=lever(50.,.30,.04)
    print(f"lever: tendon={ft:.6f} N; reaction={reaction:.6f} N downward")
    for ri in (.006,.008):
        a,i=annulus(.010,ri)
        axial,bending=stress(.010,ri,1000.,10.)
        print(f"tube ri={ri*1000:.0f} mm: A={a*1e6:.6f} mm2; I={i*1e12:.6f} mm4; "
              f"axial={axial/1e6:.6f} MPa; bending={bending/1e6:.6f} MPa; "
              f"same-side sum={(axial+bending)/1e6:.6f} MPa")
    print(f"remodeling: {remodeling(1000.,9.,10.,20):.6f} mm3; "
          f"balanced={remodeling(1000.,10.,10.,20):.6f} mm3")
    for t in (0.,30.,90.):
        fluid,solid=load_share(t)
        print(f"held load t={t:.0f} s: fluid={fluid:.6f} N; solid={solid:.6f} N")
    print(f"contact mean: {600/300:.6f} MPa at300 mm2; {600/150:.6f} MPa at150 mm2")
    # Independent balances and scaling laws test actual mathematical meaning.
    assert math.isclose(ft*.04,50*.30)
    assert math.isclose(ft-50-reaction,0.,abs_tol=1e-12)
    assert math.isclose(lever(50,.30,.08)[0],ft/2)
    # A negative signed downward reaction denotes an upward pivot force.
    small_ft, signed_downward = lever(50., .02, .04)
    assert small_ft == 25. and signed_downward == -25.
    assert small_ft - 50. - signed_downward == 0.
    a,i=annulus(.010,.006)
    a2,i2=annulus(.020,.012)
    assert math.isclose(a2,4*a) and math.isclose(i2,16*i)
    assert annulus(.010,0)[0] > a and annulus(.010,0)[1] > i
    assert annulus(.010,.009999)[0] > 0
    assert stress(.010,.006,0.,0.) == (0.,0.)
    axial, bending = stress(.010,.006,1000.,10.)
    assert math.isclose((axial-bending)/1e6, -9.654620, abs_tol=5e-7)
    assert remodeling(1000.,10.,10.,200)==1000
    assert remodeling(1000.,9.,10.,20)==980
    assert remodeling(1000.,11.,10.,20)==1020
    assert remodeling(1.,0.,1.,1)==0.  # Exact aggregate exhaustion is permitted.
    assert remodeling(0.,10.,10.,1)==0.  # No resorption-first chronology implied.
    assert remodeling(1.,2.,2.,1)==1.  # Local feasibility is outside this ledger.
    previous=math.inf
    for step in range(1001):
        f,s=load_share(step*.3)
        assert f >= 0 and s >= 0 and math.isclose(f+s,600.)
        assert f <= previous
        previous=f
    assert load_share(0.,initial_fluid_fraction=0.)==(0.,600.)
    assert math.isclose(load_share(3000.)[1],600.)
    invalid=[lambda: lever(0,1,1),lambda: lever(1,1,math.nan),
             lambda: annulus(1,1),lambda: annulus(1,-1),
             lambda: remodeling(1,0,2,1),lambda: remodeling(1,1,1,1.5),
             lambda: load_share(-1),lambda: load_share(0,tau=0)]
    for f in invalid:
        try: f()
        except ValueError: pass
        else: raise AssertionError("invalid input accepted")
    print("PASS: torque/force balances, geometry scaling/limits, turnover balance, "
          "1001 load states, asymptote, and8 invalid-input cases")


if __name__ == '__main__':
    main()
