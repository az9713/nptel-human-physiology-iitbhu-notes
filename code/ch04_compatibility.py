"""Restricted ABO component logic: an educational model, not a blood-bank tool.

Inputs are exact adult ABO labels O/A/B/AB and component red_cells/plasma.
Outputs are Boolean ABO compatibility and printable donor-row matrices.
No patient data, network calls, file writes, RhD allocation or clinical decisions.
"""

from itertools import product
from math import isclose, isfinite

GROUPS = ("O", "A", "B", "AB")
ANTIGENS = {
    "O": frozenset(),
    "A": frozenset({"A"}),
    "B": frozenset({"B"}),
    "AB": frozenset({"A", "B"}),
}
TARGETS = {group: frozenset({"A", "B"}) - a
           for group, a in ANTIGENS.items()}


def compatible(donor, recipient, component):
    """True means no opposing A/B target in the restricted component model."""
    if donor not in GROUPS or recipient not in GROUPS:
        raise ValueError("ABO labels must be O, A, B or AB")
    if component == "red_cells":
        return not ANTIGENS[donor] & TARGETS[recipient]
    if component == "plasma":
        return not TARGETS[donor] & ANTIGENS[recipient]
    raise ValueError("component must be red_cells or plasma")


def net_accumulation(inflow, outflow, duration):
    """Constant-rate synthetic fluid balance in mL/min and min; returns mL."""
    values = (inflow, outflow, duration)
    if any(not isinstance(x, (int, float)) or isinstance(x, bool)
           or not isfinite(x) or x < 0 for x in values):
        raise ValueError("rates and duration must be finite and nonnegative")
    result = (inflow - outflow) * duration
    if not isfinite(result):
        raise ValueError("fluid accumulation exceeds the finite model")
    return result


def check():
    expected_rbc = ("1111", "0101", "0011", "0001")
    expected_plasma = ("1000", "1100", "1010", "1111")
    for component, expected in (("red_cells", expected_rbc),
                                ("plasma", expected_plasma)):
        rows = tuple("".join(str(int(compatible(d, r, component)))
                             for r in GROUPS) for d in GROUPS)
        assert rows == expected
    for d, r in product(GROUPS, repeat=2):
        assert compatible(d, r, "red_cells") == compatible(r, d, "plasma")
    # Direction matters; the same directed pair changes with component.
    assert compatible("O", "AB", "red_cells")
    assert not compatible("O", "AB", "plasma")
    assert isclose(net_accumulation(0.30, 0.10, 40), 8.0)
    for args in (("X", "O", "red_cells"), ("O", "A", "whole_blood")):
        try:
            compatible(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    print("Checks: two independent matrices, 16 reversed pairs, "
          "component counterexample, input rejection")


def main():
    for component in ("red_cells", "plasma"):
        print(component + ": donor rows; recipient columns O A B AB")
        for donor in GROUPS:
            row = " ".join(str(int(compatible(donor, r, component)))
                           for r in GROUPS)
            print(f"{donor:>2} {row}")
        count = sum(compatible(d, r, component)
                    for d, r in product(GROUPS, repeat=2))
        print(f"Compatible directed pairs: {count}/16")
    for outflow in (0.10, 0.25, 0.30):
        value = net_accumulation(0.30, outflow, 40)
        print(f"Synthetic outflow {outflow:.2f} mL/min: "
              f"accumulation {value:.2f} mL over 40 min")
    check()


if __name__ == "__main__":
    main()
