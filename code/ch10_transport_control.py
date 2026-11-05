"""Original nonclinical Chapter 10 models. No patient data, doses or side effects.
Concentration: exchange umol/mL; sensing/control mmol/L. Time: min.
exchange volume mL, conductance mL/min, consumption 1/min, source umol/min.
control reservoir volume 1 L; controller/effector dimensionless.
"""
import math
import json


def valid(value, name, positive=False):
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError(name + ' outside permitted domain')
    return value


def exchange(t, volume=1, conductance=.05, external=.2, consumption=.05,
             initial=0, source=0):
    valid(t, 'time'); valid(volume, 'volume', True)
    for name, value in [('conductance', conductance), ('external', external),
                        ('consumption', consumption), ('initial', initial), ('source', source)]:
        valid(value, name)
    rate = conductance / volume + consumption
    cinf = (conductance * external + source) / (volume * rate) if rate else (None if source > 0 else initial)
    c = cinf + (initial - cinf) * math.exp(-rate * t) if rate else initial + source*t/volume
    integral = (cinf*t + (initial-cinf)*(-math.expm1(-rate*t))/rate
                if rate else initial*t+source*t*t/(2*volume))
    incoming = conductance*external*t
    back = conductance*integral
    used = consumption*volume*integral
    produced = source*t
    stored = volume*c
    return dict(c=c, cinf=cinf, stored=stored, input=incoming, back=back,
                used=used, produced=produced,
                residual=initial*volume+incoming+produced-stored-back-used)


def lag_step(t, tissue=5, sensor=2):
    valid(t, 'time'); valid(tissue, 'tissue', True); valid(sensor, 'sensor', True)
    i = 1-math.exp(-t/tissue)
    m = (1-(1+t/tissue)*math.exp(-t/tissue) if abs(tissue-sensor)<1e-10 else
         1-(tissue*math.exp(-t/tissue)-sensor*math.exp(-t/sensor))/(tissue-sensor))
    return dict(i=i, m=m)


def sensing(t):
    valid(t, 'time')
    blood = tissue = sensor = 5.
    for when, delta in [(10, 5), (40, -5)]:
        if t >= when:
            state = lag_step(t-when)
            blood += delta; tissue += delta*state['i']; sensor += delta*state['m']
    return dict(blood=blood, tissue=tissue, sensor=sensor)


def control(duration=100, dt=.05, sensor_lag=5, effector_lag=10, gain_scale=5):
    valid(duration, 'duration'); valid(dt, 'step', True)
    valid(sensor_lag, 'sensor lag', True); valid(effector_lag, 'effector lag', True)
    valid(gain_scale, 'gain scale', True)
    if duration > 10000 or duration/dt > 2000000:
        raise ValueError('simulation too large')
    t=0.; g=5.; s=5.; a=0.; incoming=0.; basal=0.; extra=0.
    def row():
        return dict(t=t, g=g, s=s, a=a, u=min(1,max(0,(s-5)/gain_scale)),
                    input=incoming, basal=basal, extra=extra,
                    residual=5+incoming-g-basal-extra)
    out=[row()]
    while t < duration-1e-10:
        step=min(dt,duration-t)
        for event in (20,40):
            if t < event-1e-10 and t+step > event:
                step=event-t
        q=.5+(.6 if t>=20-1e-10 and t<40-1e-10 else 0)
        u=min(1,max(0,(s-5)/gain_scale))
        rate=.1+.08*a; steady=q/rate
        next_g=steady+(g-steady)*math.exp(-rate*step)
        integral=steady*step+(g-steady)*(-math.expm1(-rate*step))/rate
        incoming+=q*step; basal+=.1*integral; extra+=.08*a*integral
        s=g+(s-g)*math.exp(-step/sensor_lag)
        a=u+(a-u)*math.exp(-step/effector_lag)
        g=next_g; t+=step; out.append(row())
    return out


def checks():
    count=0
    for t in range(101):
        for args in ({}, dict(conductance=.025),
                     dict(conductance=.08,external=0,consumption=0,source=.03),
                     dict(conductance=0,external=0,consumption=0,source=.03)):
            state=exchange(t, **args)
            assert abs(state['residual']) < 1e-11 and state['c'] >= 0
            count+=1
    assert exchange(10,conductance=0,consumption=0,source=0)['c']==0
    assert abs(exchange(10,consumption=0)['cinf']-.2)<1e-12
    assert all(abs(x)<1e-12 for x in lag_step(0).values())
    assert abs(lag_step(5,2,2)['m']-(1-3.5*math.exp(-2.5)))<1e-12
    assert sensing(10)==dict(blood=10,tissue=5,sensor=5)
    assert abs(sensing(40)['tissue']-sensing(40-1e-8)['tissue'])<1e-7
    bad=[lambda:exchange(-1),lambda:exchange(1,volume=0),lambda:exchange(1,source=-1),
         lambda:lag_step(1,0),lambda:sensing(float('nan')),lambda:control(1,0),
         lambda:control(1,sensor_lag=-1),lambda:control(1,gain_scale=0)]
    for call in bad:
        try: call()
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    coarse=control(); fine=control(dt=.025)
    assert max(abs(r['residual']) for r in coarse)<1e-9
    assert all(0<=r['u']<=1 and 0<=r['a']<=1 and r['g']>0 for r in coarse)
    assert abs(coarse[-1]['input']-62)<1e-8
    convergence=abs(coarse[-1]['g']-fine[-1]['g'])
    assert convergence<.002
    return dict(exchange_balance_states=count, invalid_cases=len(bad),
                control_states=len(coarse), control_balance_max=max(abs(r['residual']) for r in coarse),
                endpoint_step_difference=convergence, control_final=coarse[-1])


if __name__ == '__main__':
    print(json.dumps(dict(oxygen10=exchange(10), oxygen_half_conductance10=exchange(10,conductance=.025),
                         sensing15=sensing(15), volumes_ml=[2000/d for d in (4000,8000,16000)],
                         hypothetical_volumes_ml=[1e6/d for d in (4000,8000,16000)],
                         glucose126_mmol_L=126/18.0156,
                         permeability_cm_min=[1/(.01/.001),1/(.01/.001+.02/.001)],
                         checks=checks()), indent=2))
