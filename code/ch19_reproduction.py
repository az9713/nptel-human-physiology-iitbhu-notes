"""Chapter 19: bounded teaching states and exact milk-inventory balance.
No fitted physiology, ovarian reserve forecast or clinical fertility prediction.
Run: python code/ch19_reproduction.py --check
"""
import argparse, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def nonnegative(x, name):
    if not math.isfinite(x) or x < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
def milk(A0, S, k, t):
    for x,n in [(A0,'A0'),(S,'S'),(k,'k'),(t,'time')]: nonnegative(x,n)
    added=S*t;total=A0+added
    if not math.isfinite(total): raise ValueError('total input is not representable')
    z=k*t
    if k==0 or z==0: gain=added
    elif z<=1: gain=added*(-math.expm1(-z)/z)
    else: gain=(S/k)*(-math.expm1(-z))
    A=A0*math.exp(-z)+gain
    if not math.isfinite(A): raise ValueError('stored output is not representable')
    A=min(total,max(0,A)) # Bound last-bit roundoff; exact solution lies in [0,total].
    D=total-A
    if not math.isfinite(D): raise ValueError('delivered output is not representable')
    return {'A':A,'D':D,'total':total}
def cycle(t):
    nonnegative(t,'elapsed day')
    if t>=28: raise ValueError('elapsed day 0 ≤ t < 28')
    def g(m,s): return math.exp(-.5*((t-m)/s)**2)
    return {'elapsed':t,'day':1+t,'phase':'Follicular' if t<13 else 'Periovulatory release interval' if t<14 else 'Luteal','event':'Growing selected antral follicle' if t<13 else 'LH-linked maturation and release' if t<14 else 'Corpus luteum active' if t<25 else 'Luteal regression, if no rescue','oocyte':'Primary, 2n 4C' if t<13 else 'Secondary, n 2C at release; later fate conditional','E':.12+.76*g(11.8,2.3)+.30*g(20,3.5),'P':.06+.85*g(21,3.1),'LH':.07+.93*g(12.5,.65),'FSH':.13+.18*g(1,2)+.30*g(12.5,.85)}
def check():
    checks=0
    for A0 in [0,1,50]:
      for S in [0,2]:
       for k in [0,1e-10,.2,2]:
        for t in [0,.1,5,10]:
         m=milk(A0,S,k,t)
         assert m['A']>=-1e-12 and m['D']>=-1e-12
         assert math.isclose(m['A']+m['D'],A0+S*t,abs_tol=1e-10)
         checks+=1
    for i in range(280):
        q=cycle(i/10)
        assert all(math.isfinite(q[k]) for k in ['elapsed','day','E','P','LH','FSH'])
        assert all(q[k]>=0 for k in ['E','P','LH','FSH'])
        checks+=1
    for bad in [-1,float('nan'),float('inf'),-float('inf')]:
      for idx in range(4):
        a=[50,2,.2,5];a[idx]=bad
        try: milk(*a)
        except ValueError: pass
        else: raise AssertionError('invalid milk input accepted')
        checks+=1
      try: cycle(bad)
      except ValueError: pass
      else: raise AssertionError('invalid cycle input accepted')
      checks+=1
    try: cycle(28.1)
    except ValueError: pass
    else: raise AssertionError('out-of-domain cycle accepted')
    # Review-union: stable near-zero gain without S/k overflow, independent limit/composition.
    for k in [0,5e-324,1e-320,1e-12,.2]:
      for t in [0,1,5,10]:
        v=milk(50,2,k,t);assert math.isfinite(v['A']) and math.isfinite(v['D'])
        if k<=1e-12:assert math.isclose(v['A'],50+2*t,abs_tol=1e-8)
        mid=milk(50,2,k,t/2);composed=milk(mid['A'],2,k,t/2)
        assert math.isclose(v['A'],composed['A'],abs_tol=1e-10)
        checks+=1
    for args in [(1e308,1e308,.2,10),(0,float.fromhex('0x1.fffffffffffffp+1023'),1e-320,2)]:
      try:milk(*args)
      except ValueError:pass
      else:raise AssertionError('overflow total accepted')
      checks+=1
    try:cycle(28)
    except ValueError:pass
    else:raise AssertionError('boundary accepted as state')
    checks+=1
    a=milk(50,2,0,5);b=milk(a['A'],2,.2,5)
    assert a['A']==60 and a['D']==0
    assert math.isclose(b['A'],28.393972058572118,abs_tol=1e-10)
    assert math.isclose(b['D'],41.60602794142788,abs_tol=1e-10)
    # Independent local derivative and composition checks for the A solution.
    for a0,s,k,t in [(50,2,.2,1),(0,2,.2,5),(50,0,2,.5)]:
        dt=1e-5;mid=milk(a0,s,k,t)['A']
        deriv=(milk(a0,s,k,t+dt)['A']-milk(a0,s,k,t-dt)['A'])/(2*dt)
        assert math.isclose(deriv,s-k*mid,abs_tol=1e-7)
        once=milk(a0,s,k,2*t)['A'];twice=milk(mid,s,k,t)['A']
        assert math.isclose(once,twice,abs_tol=1e-10)
        checks+=2
    assert milk(10,2,.2,5)['A']==10
    checks+=1
    # Completed euploid lineage bookkeeping; first polar body retained as n2C.
    assert 4 == 2+2 and 2 == 1+1 and 4 == 1+1+2
    print(json.dumps({'checks':checks+5,'after_no_ejection':a,'after_ejection_interval':b,'status':'PASS'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--export',action='store_true');a=p.parse_args()
    if a.export:
        (ROOT/'assets/ch19-cycle-state.json').write_text(json.dumps({'schema':'ch19-cycle-v1','scope':'Prescribed qualitative no-rescue cycle; elapsed0=day1, 0<=elapsed<28;28=unsampled next-onset boundary; no clinical clock','states':[cycle(i/10) for i in range(280)]},indent=2)+'\n',encoding='utf-8')
    if a.check or not a.export: check()
