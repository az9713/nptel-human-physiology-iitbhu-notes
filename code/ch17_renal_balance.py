"""Original synthetic renal teaching model; standard library only.

Run from the book root: python code/ch17_renal_balance.py
Writes assets/ch17-countercurrent-data.json. No patient calibration.
Outer-medullary paired-flow submodel: every A bin is an active TAL surrogate.
Thin ascending limbs and the anatomical bend are omitted. The deepest D-to-A
connection is a lumped no-exchange return boundary, not a thin-limb model.
"""
import json
import math
from pathlib import Path


def countercurrent(pump=0.12, steps=20000, dt=0.01):
    if not math.isfinite(pump) or pump < 0:
        raise ValueError('Finite nonnegative TAL-surrogate transfer required')
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError('Finite positive time step required')
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError('Nonnegative integer step count required')
    # Four axial bins; each of D, A, I has fixed unit water volume.
    # Solute is total generic osmoles, not separately conserved ionic species.
    d, a, inter = [1.0]*4, [1.0]*4, [1.0]*4
    supplied = discharged = removed = water_removed = 0.0
    records = []
    max_error = 0.0
    for step in range(steps+1):
        error = sum(d+a+inter)+removed+discharged-supplied-12
        max_error = max(max_error, abs(error))
        if step % 100 == 0:
            records.append(dict(t=step*dt, d=d[:], a=a[:], inter=inter[:],
                                residual=error, removed=removed,
                                supplied=supplied, discharged=discharged,
                                water_removed=water_removed))
        if step == steps:
            break
        flow = 0.2
        q, w = [], []
        for j in range(4):
            # Only outward water movement included. Cap preserves positive flow.
            water = min(0.03*max(inter[j]-d[j], 0.0), flow*0.4)
            w.append(water)
            flow -= water
            q.append(flow)
        # All modeled A bins are TAL surrogates, including the deepest model bin.
        # No thin ascending segment is represented or assigned active transport.
        salt = [pump*max(a[j]-inter[j]+0.6, 0) for j in range(4)]
        wash = [0.01/(j+1)*(inter[j]-1) for j in range(4)]
        nd, na, ni = [], [], []
        for j in range(4):
            di = (0.2 if j == 0 else q[j-1])*(1 if j == 0 else d[j-1])
            # Bottom input is the stated no-exchange lumped return boundary.
            ai = q[-1]*(d[-1] if j == 3 else a[j+1])
            nd.append(d[j]+dt*(di-q[j]*d[j]))
            na.append(a[j]+dt*(ai-q[-1]*a[j]-salt[j]))
            # Equal and opposite axial diffusion between adjacent I bins.
            diffuse = 0.003*sum(inter[k]-inter[j] for k in (j-1,j+1) if 0 <= k < 4)
            ni.append(inter[j]+dt*(salt[j]-w[j]*inter[j]-wash[j]+diffuse))
        supplied += dt*0.2
        discharged += dt*q[-1]*a[0]
        removed += dt*sum(w[j]*inter[j]+wash[j] for j in range(4))
        water_removed += dt*sum(w)
        d, a, inter = nd, na, ni
        assert min(d+a+inter) >= 0, "Negative amount: reduce step or change parameters"
    return records, max_error


def numbers():
    return {
        'filtered_glucose_mmol_min': 0.125*5,
        'filtered_sodium_mmol_min': 0.125*140,
        'proximal_water_L_day': 0.125*1440*0.65,
        'proximal_outflow_L_day': 0.125*1440*0.35,
        'sodium_remaining_mmol_min': 0.125*140*0.35,
        'filtered_bicarbonate_mmol_day': 0.125*1440*24,
        'reclaimed_bicarbonate_85pct': 0.125*1440*24*0.85,
        'new_bicarbonate_30_glutamine': 30*2,
        'net_acid_mEq_day': 45+25-5,
        'urine_concentrated_L_day': 600/1200,
        'urine_dilute_L_day': 600/100,
        'osmolar_clearance_L_day': 600/300,
        'freewater_concentrated': 0.5-600/300,
        'freewater_dilute': 6-600/300,
        'solute_after_halfwater_removed': 300/0.5,
        'dialysis_C_final_mmol_L': 20*math.exp(-0.2*240/40),
        'dialysis_ideal_removed_mmol': 40*20*(1-math.exp(-0.2*240/40)),
        'dialysis_ideal_reduction_percent': 100*(1-math.exp(-0.2*240/40)),
        'dialysis_fluid_rate_mL_min': 2000/240,
        'synthetic_albumin_creatinine_mg_g': 80/1,
    }


def main():
    records, error = countercurrent()
    passive, passive_error = countercurrent(pump=0)
    assert error < 1e-10 and passive_error < 1e-10
    assert all(abs(x-1) < 1e-12 for key in ('d','a','inter') for x in passive[-1][key])
    assert records[-1]['inter'][-1] > records[-1]['inter'][0] > 1
    assert records[-1]['a'][0] < 1
    # Time-step convergence, not an assertion of physiological truth.
    half, half_error = countercurrent(steps=40000, dt=0.005)
    difference = max(abs(records[-1][k][j]-half[-1][k][j])
                     for k in ('d','a','inter') for j in range(4))
    assert difference < 0.001
    result = {'model':'four-level open outer-medullary TAL-surrogate balance',
              'anatomical_scope':{'ascending_bins':'active TAL surrogate at every level',
                                  'depth':'four ordered outer-medullary model levels, not papillary depth',
                                  'omitted':'thin ascending limb and anatomical bend',
                                  'return_boundary':'deepest D connects to deepest A without modeled exchange'},
              'units':'arbitrary osmoles, water units, and model time',
              'parameters':{'pump':0.12,'dt':0.01,'steps':20000,'inflow':0.2,
                            'water_conductance':0.03,'axial_diffusion':0.003},
              'frames':records,'no_pump_final':passive[-1],
              'max_mass_residual':error,'half_step_max_difference':difference,
              'numbers':numbers()}
    target = Path(__file__).resolve().parents[1]/'assets/ch17-countercurrent-data.json'
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'frames'},indent=2))
    print('final',json.dumps(records[-1]))


if __name__ == '__main__':
    main()
