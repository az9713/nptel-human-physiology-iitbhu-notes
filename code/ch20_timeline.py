"""Bounded teaching checks for Chapter 20. No clinical dating or assay prediction."""
from __future__ import annotations

from datetime import date, timedelta
import math


def cycle_coordinates(cycle_day: int, ovulation_day: int) -> dict[str, int]:
    if not isinstance(cycle_day, int) or not isinstance(ovulation_day, int):
        raise TypeError("cycle and ovulation days must be integers")
    if cycle_day < 1 or ovulation_day < 1:
        raise ValueError("days are counted from 1")
    return {"cycle_day": cycle_day, "days_since_ovulation": cycle_day - ovulation_day,
            "gestational_elapsed_days_from_lmp": cycle_day - 1}


def due_date_280(lmp: date) -> date:
    return lmp + timedelta(days=280)


def due_date_calendar_naegele(lmp: date) -> date:
    """Add one calendar year, subtract three months, then add seven days.

    Restrict to day <= 28 so the calendar-month transform is unambiguous.
    This is an arithmetic illustration, not a clinically recommended algorithm.
    """
    if lmp.day > 28:
        raise ValueError("calendar rule ambiguous for days 29-31 in some months")
    shifted_month = lmp.month - 3
    shifted_year = lmp.year + 1
    if shifted_month < 1:
        shifted_month += 12
        shifted_year -= 1
    return date(shifted_year, shifted_month, lmp.day) + timedelta(days=7)



def sealed_exchange(v_m: float, v_f: float, c_m0: float, c_f0: float,
                    conductance: float, time: float) -> dict[str, float]:
    """Exact two-reservoir mass balance; artificial units, no perfusion or metabolism.

    Transfer J=conductance*(c_m-c_f) across a separating boundary. The
    compartments retain their own volume and blood identities. This is not
    a placental transport-rate estimator. Finite inputs are accepted only when
    initial and returned inventories are representable in binary64; otherwise
    ValueError is raised. Exact zero-time/zero-transfer states are preserved.
    """
    values=(v_m,v_f,c_m0,c_f0,conductance,time)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("all exchange inputs must be finite")
    if v_m<=0 or v_f<=0 or min(c_m0,c_f0,conductance,time)<0:
        raise ValueError("volumes positive; concentrations, conductance and time nonnegative")
    m0, f0 = v_m*c_m0, v_f*c_f0
    total = m0 + f0
    if (not all(math.isfinite(x) for x in (m0, f0, total)) or
            (c_m0 > 0 and m0 == 0) or (c_f0 > 0 and f0 == 0)):
        raise ValueError("initial inventories are not representable")
    delta0 = c_m0-c_f0
    # Exact limit branches precede reciprocal/rate arithmetic, which can
    # overflow even while a zero-time or zero-conductance answer is finite.
    if time == 0 or conductance == 0 or delta0 == 0:
        return {"maternal_concentration":c_m0,"fetal_concentration":c_f0,
                "maternal_inventory":m0,"fetal_inventory":f0,
                "total_inventory":total,"difference":delta0}
    scale = max(v_m, v_f)
    wm, wf = v_m/scale, v_f/scale
    frac_m, frac_f = wm/(wm+wf), wf/(wm+wf)
    # log(k) for k=G*t*(1/Vm+1/Vf), without overflowing a reciprocal.
    small, large = min(v_m,v_f), max(v_m,v_f)
    log_rate = (math.log(conductance)+math.log(time)-math.log(small)
                + math.log1p(small/large))
    rate = math.inf if log_rate > math.log(745) else math.exp(log_rate)
    decay = 0.0 if rate == math.inf else math.exp(-rate)
    volume_sum = v_m + v_f
    mean = (total/volume_sum if math.isfinite(volume_sum)
            else frac_m*c_m0 + frac_f*c_f0)
    c_m = mean + frac_f*delta0*decay
    c_f = mean - frac_m*delta0*decay
    lo, hi = min(c_m0,c_f0), max(c_m0,c_f0)
    c_m, c_f = min(hi,max(lo,c_m)), min(hi,max(lo,c_f))
    m_inv, f_inv = v_m*c_m, v_f*c_f
    values_out = (c_m,c_f,m_inv,f_inv,delta0*decay)
    if not all(math.isfinite(x) for x in values_out):
        raise ValueError("exchange output is not representable")
    tolerance = max(total*1e-12, 32*math.ulp(total))
    if abs((m_inv+f_inv)-total) > tolerance:
        raise ValueError("exchange inventory is not representable")
    return {"maternal_concentration":c_m,"fetal_concentration":c_f,
            "maternal_inventory":m_inv,"fetal_inventory":f_inv,
            "total_inventory":total,"difference":c_m-c_f}


def urine_test_state(control: bool, hcg: float, threshold: float) -> str:
    if not isinstance(control, bool):
        raise TypeError("control must be Boolean")
    if not (0 <= hcg < float("inf") and 0 < threshold < float("inf")):
        raise ValueError("hCG and threshold must be finite; hCG nonnegative, threshold positive")
    if not control:
        return "invalid"
    return "positive" if hcg >= threshold else "negative"


if __name__ == "__main__":
    lmp = date(2009, 5, 8)
    assert cycle_coordinates(21, 14)["days_since_ovulation"] == 7
    assert cycle_coordinates(21, 18)["days_since_ovulation"] == 3
    assert due_date_280(lmp).isoformat() == "2010-02-12"
    assert due_date_calendar_naegele(lmp).isoformat() == "2010-02-15"
    assert urine_test_state(True, 12, 20) == "negative"
    assert urine_test_state(True, 26, 20) == "positive"
    assert urine_test_state(False, 26, 20) == "invalid"
    print("cycle day 21: +7 days if ovulation day 14; +3 if day 18")
    print("LMP 2009-05-08: 280-day 2010-02-12; calendar Naegele 2010-02-15")
    x=sealed_exchange(3,1,1,0,.2,5)
    assert math.isclose(x["maternal_inventory"]+x["fetal_inventory"],3,abs_tol=1e-12)
    assert math.isclose(x["difference"],math.exp(-4/3),abs_tol=1e-12)
    assert sealed_exchange(3,1,1,0,0,5)["maternal_concentration"]==1
    assert sealed_exchange(3,1,1,1,.2,5)["difference"]==0
    print("synthetic assay: 12/20 negative; 26/20 positive; absent control invalid")
    print("closed reservoir exchange: total=3 conserved; difference=exp(-4/3) at artificial time 5")
