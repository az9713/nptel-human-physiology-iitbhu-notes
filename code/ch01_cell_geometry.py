"""Reproduce Chapter 1's original geometry/diffusion teaching calculations.

Run: python code/ch01_cell_geometry.py
No dependencies, file writes, random numbers, or biological fitted constants.
Distances are micrometres; time is seconds. Concentration is in arbitrary
units (au). The chosen D=100 um^2/s, surface concentration=1 au, and uniform
consumption q=1 au/s are synthetic inputs, not human tissue measurements.
"""

from math import isclose, isfinite, pi, sqrt


def positive(value, name):
    """Reject invalid physical inputs rather than silently propagate them."""
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def sphere(radius):
    """Return area [um^2], volume [um^3], area/volume [1/um]."""
    positive(radius, "radius")
    area = 4 * pi * radius**2
    volume = 4 * pi * radius**3 / 3
    return area, volume, area / volume


def diffusion_time(distance, diffusivity):
    """1-D RMS displacement time L^2/(2D); not a first-arrival time."""
    positive(distance, "distance")
    positive(diffusivity, "diffusivity")
    return distance**2 / (2 * diffusivity)


def center_concentration(size, diffusivity, consumption, surface, geometry):
    """Steady zero-order model; negative result flags model inadmissibility."""
    for name, value in (("size", size), ("diffusivity", diffusivity),
                        ("consumption", consumption), ("surface", surface)):
        positive(value, name)
    if geometry not in {"sphere", "slab"}:
        raise ValueError("geometry must be sphere or slab")
    factor = 6 if geometry == "sphere" else 2
    return surface - consumption * size**2 / (factor * diffusivity)


def main():
    diffusivity, consumption, surface = 100.0, 1.0, 1.0
    print("Synthetic inputs: D=100 um^2/s; q=1 au/s; c_s=1 au")
    print("R_um A_um2 V_um3 A_over_V_per_um t_1D_s c_center_au")
    for radius in (5.0, 10.0, 20.0, 50.0):
        area, volume, ratio = sphere(radius)
        center = center_concentration(radius, diffusivity, consumption,
                                      surface, "sphere")
        print(f"{radius:g} {area:.6f} {volume:.6f} {ratio:.6f} "
              f"{diffusion_time(radius, diffusivity):.6f} {center:.6f}")
    sphere_limit = sqrt(6 * diffusivity * surface / consumption)
    slab_limit = sqrt(2 * diffusivity * surface / consumption)
    print(f"Critical sphere radius: {sphere_limit:.6f} um")
    print(f"Critical slab half-thickness: {slab_limit:.6f} um")
    print(f"Critical-size ratio sphere/slab: {sphere_limit / slab_limit:.6f}")
    print("At size=20 um: sphere center="
          f"{center_concentration(20, 100, 1, 1, 'sphere'):.6f} au; "
          "slab center="
          f"{center_concentration(20, 100, 1, 1, 'slab'):.6f} au")
    print("Double radius: area x4; volume x8; A/V x0.5; RMS time x4")
    print("Eight equal-volume daughters: radius ratio="
          f"{8**(-1 / 3):.6f}; total area ratio={8**(1 / 3):.6f}")
    print("Diffusion times: L=10 um, D=25 -> "
          f"{diffusion_time(10, 25):.6f} s; "
          f"L=1000 um, D=100 -> {diffusion_time(1000, 100):.6f} s")
    print(f"q/4 increases critical sphere radius to {2*sphere_limit:.6f} um")
    print("At R=20 um, doubled D gives center="
          f"{center_concentration(20, 200, 1, 1, 'sphere'):.6f} au")
    # Independent checks: dimensions alone do not catch incorrect factors.
    area, volume, ratio = sphere(10)
    assert isclose(ratio, 0.3)
    assert isclose(area * 10 / 3, volume)
    assert isclose(diffusion_time(20, 100), 2)
    assert isclose(center_concentration(sphere_limit, 100, 1, 1,
                                       "sphere"), 0, abs_tol=1e-14)
    assert center_concentration(50, 100, 1, 1, "sphere") < 0
    # Check PDE by exact polynomial finite differences at an interior point.
    radius, step, position = 20.0, 0.01, 8.0
    def profile(r):
        return surface - consumption*(radius**2-r**2)/(6*diffusivity)
    second = (profile(position + step) - 2*profile(position)
              + profile(position - step)) / step**2
    first = (profile(position + step) - profile(position - step))/(2*step)
    residual = diffusivity*(second + 2*first/position) - consumption
    assert abs(residual) < 1e-8
    for value in (0, -1, float("inf"), float("nan")):
        try:
            sphere(value)
        except ValueError:
            continue
        raise AssertionError("invalid radius accepted")
    print("Checks passed: geometry, scaling, center limit, PDE, invalid inputs")


if __name__ == "__main__":
    main()
