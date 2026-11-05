"""Reproduce Chapter 15's synthetic calculations; no fitted physiology."""
import math


def patch(g_ach, g_leak=1e-6, capacitance=10e-9,
          e_leak=-0.090, e_ach=0.0, threshold=-0.055):
    """SI inputs; constant conductances before AP onset, initial V=e_leak."""
    if (not all(math.isfinite(value) for value in
                (g_ach, g_leak, capacitance, e_leak, e_ach, threshold))
            or g_ach < 0 or g_leak <= 0 or capacitance <= 0):
        raise ValueError("nonphysical conductance/capacitance")
    equilibrium = (g_leak*e_leak + g_ach*e_ach)/(g_leak + g_ach)
    tau = capacitance/(g_leak + g_ach)
    crossing = math.inf
    if e_leak < threshold < equilibrium:
        crossing = -tau*math.log(
            (threshold - equilibrium)/(e_leak - equilibrium))
    return equilibrium, tau, crossing


def geometry(length, thin=1.0, thick=1.6):
    """Finite a,b>0 and max(b,2a)<=L<=b+2a; micrometers, no force law."""
    if (not all(math.isfinite(x) for x in (length, thin, thick))
            or thin <= 0 or thick <= 0
            or not max(thick, 2*thin) <= length <= thick + 2*thin):
        raise ValueError("outside finite noninterfering band-geometry domain")
    left = (-length/2, -length/2 + thin)
    right = (length/2 - thin, length/2)
    overlap = max(0.0, min(thin, (thick + 2*thin - length)/2))
    interval_overlap = max(
        0.0, min(left[1], thick/2) - max(left[0], -thick/2))
    assert math.isclose(overlap, interval_overlap, abs_tol=1e-12)
    assert math.isclose(left[1] - left[0], thin)
    assert math.isclose(right[1] - right[0], thin)
    assert left[0] == -right[1] and left[1] == -right[0]
    return thick, length - thick, max(0.0, length - 2*thin), overlap


def active_force(length, recruited):
    """Selected active capacity, N; ten identical parallel motor units."""
    if not (2.2 <= length <= 3.6 and isinstance(recruited, int)
            and 0 <= recruited <= 10):
        raise ValueError("outside selected force-law domain")
    overlap = geometry(length)[3]
    length_factor = min(1.0, overlap/0.7)
    return (recruited/10)*100*length_factor


def check_geometry_domain():
    """Independent interval/band bounds for default and nondefault lengths."""
    for thin, thick in ((1.0, 1.6), (0.8, 1.5), (1.2, 1.0), (0.4, 2.0)):
        lower, upper = max(thick, 2*thin), thick + 2*thin
        for index in range(201):
            length = upper if index == 200 else (
                lower + (upper - lower)*index/200)
            a_band, i_band, h_zone, overlap = geometry(length, thin, thick)
            assert h_zone <= a_band + 1e-12
            assert i_band <= 2*thin + 1e-12
            left_tip = -length/2 + thin
            intersection = max(0, min(left_tip, thick/2)
                               - max(-length/2, -thick/2))
            assert math.isclose(overlap, intersection, abs_tol=1e-12)
        a_band, i_band, h_zone, overlap = geometry(upper, thin, thick)
        assert math.isclose(h_zone, a_band, abs_tol=1e-12)
        assert math.isclose(i_band, 2*thin, abs_tol=1e-12)
        assert math.isclose(overlap, 0, abs_tol=1e-12)
        for length in (lower - 1e-8, upper + 1e-8):
            try:
                geometry(length, thin, thick)
            except ValueError:
                pass
            else:
                raise AssertionError("out-of-domain geometry accepted")
    for values in ((math.nan, 1, 1.6), (math.inf, 1, 1.6),
                   (-math.inf, 1, 1.6), (2.6, math.nan, 1.6),
                   (2.6, 1, math.inf), (2.6, 0, 1.6), (2.6, 1, 0),
                   (3.8, 1, 1.6), (10, 1, 1.6)):
        try:
            geometry(*values)
        except ValueError:
            pass
        else:
            raise AssertionError("nonfinite/nonphysical geometry accepted")


def main():
    check_geometry_domain()
    gas_constant = 8.314462618
    temperature = 310.0
    chemical_work = gas_constant*temperature*math.log(100)
    assert math.isclose(chemical_work, 11869.749762, abs_tol=0.00001)
    print(f"Concentration-only work: {chemical_work:.2f} J/mol")
    for conductance in (0, 0.5e-6, 1e-6):
        voltage, tau, crossing = patch(conductance)
        print(f"g_ACh={conductance*1e6:.1f} uS: "
              f"V_inf={voltage*1000:.3f} mV; tau={tau*1000:.3f} ms; "
              f"threshold={crossing*1000:.3f} ms")
    assert patch(0)[0] == -0.090
    assert math.isinf(patch(0.5e-6)[2])
    assert math.isclose(patch(1e-6)[2]*1000, 7.52038698)
    threshold_ratio = 35/55
    print(f"Threshold conductance ratio: {threshold_ratio:.6f}")
    for length in (2.6, 2.2, 3.6):
        print(f"L={length:.1f} um: A,I_total,H,O={geometry(length)}")
    for index in range(1001):
        geometry(2.6 - 0.4*index/1000)
    assert geometry(3.6)[3] == 0
    for recruited in (2, 6, 10):
        print(f"L=2.6 um; {recruited}/10 units: "
              f"active force={active_force(2.6, recruited):.3f} N")
    assert math.isclose(active_force(2.6, 6), 300/7)
    assert active_force(2.2, 6) == 60
    assert active_force(3.6, 10) == 0
    for length in (2.6, 2.2):
        minimum = next(n for n in range(11)
                       if active_force(length, n) >= 60)
        print(f"L={length:.1f} um; minimum units for 60 N: {minimum}")
    for recruited in range(11):
        for index in range(1001):
            length = 2.2 + 1.4*index/1000
            force = active_force(length, recruited)
            assert 0 <= force <= 100 + 1e-10
            assert math.isclose(force, recruited*active_force(length, 1),
                                abs_tol=1e-10)
    work = 20*0.010
    efficiency = 0.25
    atp_free_energy = 50000
    atp_moles = work/(efficiency*atp_free_energy)
    molecules = atp_moles*6.02214076e23
    shortening = (2.6 - 2.2)/2.6*100
    print(f"Shortening: {shortening:.3f}%")
    print(f"External work={work:.3f} J; ATP={atp_moles*1e6:.3f} umol; "
          f"molecules={molecules:.4e}")
    assert math.isclose(atp_moles*1e6, 16.0)
    print("PASS: circuit limits, threshold, 1001 geometry states, ATP units")


if __name__ == "__main__":
    main()
