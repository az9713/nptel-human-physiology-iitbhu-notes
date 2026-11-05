"""Chapter 2 synthetic transport/control examples; Python standard library only.

No patient data or fitted biological parameters. No network or file effects.
Concentrations: mmol/L (= mol/m^3); volumes: L; exchange conductance: L/s.
Electrochemical energies: J/mol; voltages: V; feedback time: s.
"""
from math import exp, isfinite, log

R = 8.31446261815324  # J/(mol K), gas constant
F = 96485.33212  # C/mol, Faraday constant (rounded)
T = 310.0  # K, illustrative temperature


def positive(**values):
    for name, value in values.items():
        if not isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")


def diffuse(t, vo=2.0, vi=1.0, co0=10.0, ci0=0.0, conductance=0.1):
    """Exact closed two-compartment solution; permits zero conductance."""
    positive(vo=vo, vi=vi)
    if any(not isfinite(x) or x < 0 for x in (t, co0, ci0, conductance)):
        raise ValueError("time, concentrations and conductance must be nonnegative")
    mean = (vo * co0 + vi * ci0) / (vo + vi)
    delta = (co0 - ci0) * exp(-conductance * (1 / vo + 1 / vi) * t)
    return mean + vi / (vo + vi) * delta, mean - vo / (vo + vi) * delta


def inward_energy(ci, co, z, vm, temperature=T):
    """Ideal dilute electrochemical free energy, extracellular -> cytosolic."""
    positive(ci=ci, co=co, temperature=temperature)
    if not all(isfinite(x) for x in (z, vm)):
        raise ValueError("charge and voltage must be finite")
    return R * temperature * log(ci / co) + z * F * vm


def nernst(ci, co, z=1, temperature=T):
    positive(ci=ci, co=co, temperature=temperature)
    if not isfinite(z) or z == 0:
        raise ValueError("charge must be finite and nonzero")
    return R * temperature / (z * F) * log(co / ci)


def feedback(t, disturbance=1.0, passive=0.05, gain=0.15, x0=0.0):
    """dx/dt = disturbance - (passive+gain)*x, constant disturbance."""
    if any(not isfinite(x) for x in (t, disturbance, passive, gain, x0)):
        raise ValueError("all arguments must be finite")
    if t < 0 or passive < 0 or gain < 0 or passive + gain <= 0:
        raise ValueError("time/rates invalid or no restoring rate")
    rate = passive + gain
    steady = disturbance / rate
    return steady + (x0 - steady) * exp(-rate * t)


def main():
    print("SYNTHETIC teaching models; not patient calibration")
    for t in (0, 5, 10, 20):
        co, ci = diffuse(t)
        print(f"diffusion t={t:2d}s outside={co:.6f} inside={ci:.6f} mmol/L")
        assert abs(2 * co + ci - 20) < 1e-12
    tau = 1 / (0.1 * (1 / 2 + 1 / 1))
    print(f"tau={tau:.6f}s half-time={log(2)*tau:.6f}s")
    ek = nernst(140, 4)
    print(f"K equilibrium={1000*ek:.6f}mV")
    assert abs(inward_energy(140, 4, 1, ek)) < 1e-9
    for name, ci, co, z in (("Na", 15, 145, 1), ("K", 140, 4, 1)):
        print(f"{name} inward at -70mV={inward_energy(ci,co,z,-0.070)/1000:.6f}kJ/mol")
    dg_na = inward_energy(15, 145, 1, -0.060)
    print(f"Na inward at -60mV={dg_na/1000:.6f}kJ/mol")
    print(f"ideal glucose ratio ceiling 1Na={exp(-dg_na/(R*T)):.6f}")
    print(f"ideal glucose ratio ceiling 2Na={exp(-2*dg_na/(R*T)):.6f}")
    print(f"glucose 10x uphill={R*T*log(10)/1000:.6f}kJ/mol")
    print(f"coupled 1Na/10x glucose={(dg_na+R*T*log(10))/1000:.6f}kJ/mol")
    print(f"NaK forward work={(-3*inward_energy(15,145,1,-0.070)+2*inward_energy(140,4,1,-0.070))/1000:.6f}kJ/mol cycles")
    for gain in (0, 0.15):
        rate = 0.05 + gain
        print(f"feedback gain={gain:.2f}/s steady={1/rate:.6f}au tau={1/rate:.6f}s x(10)={feedback(10,gain=gain):.6f}au")
    # Differential equation check, conservation over an independent time grid,
    # zero-permeability limit, gradient sign, and invalid-input boundaries.
    h, t = 1e-4, 7.0
    co, ci = diffuse(t)
    derivative = (diffuse(t+h)[1] - diffuse(t-h)[1]) / (2*h)
    assert abs(derivative - 0.1*(co-ci)) < 1e-9
    for j in range(101):
        co, ci = diffuse(j / 2)
        assert abs(2*co + ci - 20) < 1e-12 and co >= ci >= 0
    frozen = diffuse(100, conductance=0)
    assert abs(frozen[0]-10) < 1e-12 and abs(frozen[1]) < 1e-12
    assert inward_energy(140, 4, 1, -0.070) > 0
    for invalid in (lambda: diffuse(1, vi=0), lambda: diffuse(-1),
                    lambda: inward_energy(0,145,1,0), lambda: nernst(1,1,z=0),
                    lambda: feedback(1,passive=0,gain=0)):
        try:
            invalid()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    print("PASS: conservation, ODE residual, equilibrium, limits, input checks")


if __name__ == "__main__":
    main()
