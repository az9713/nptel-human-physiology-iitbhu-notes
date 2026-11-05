"""Chapter21 original teaching statistics. Synthetic cohorts, no clinical prediction.
Run python code/ch21_outcomes.py --check --export
"""
import argparse,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COHORT=[100,90,72,54,36,27]
def counts(xs):
 if not isinstance(xs,list) or len(xs)<2 or any(type(x) is not int or not 0<=x<=2**53-1 for x in xs) or xs[0]==0 or any(b>a for a,b in zip(xs,xs[1:])): raise ValueError('nonincreasing integer cohort, positive start')
 return [{'n':x,'perStart':x/xs[0],'conditional':1 if i==0 else x/xs[i-1] if xs[i-1]>0 else None,'notProgressed':0 if i==0 else xs[i-1]-x} for i,x in enumerate(xs)]
def ppv(p,se,sp):
 """PPV for finite probabilities with representable positive TP/FP masses.
 Reject positive products rounded to zero rather than call them absent events.
 """
 if any(type(x) not in (int,float) or not 0<=x<=1 or not math.isfinite(x) for x in [p,se,sp]): raise ValueError('numeric probabilities 0–1; booleans excluded')
 tp=p*se;fp=(1-p)*(1-sp)
 if (p>0 and se>0 and tp==0) or (p<1 and sp<1 and fp==0):raise ValueError('positive probability product is not representable')
 return {'tp':tp,'fp':fp,'ppv':tp/(tp+fp) if tp+fp else None}
def mixture(gs):
 if not isinstance(gs,list) or not gs or any(type(g['n']) is not int or type(g['events']) is not int or g['n']<=0 or not 0<=g['events']<=g['n'] for g in gs):raise ValueError('bounded integer event counts')
 return sum(g['events'] for g in gs)/sum(g['n'] for g in gs)
def check():
 checks=0
 for a in range(1,16):
  for b in range(a+1):
   for c in range(b+1):
    q=counts([a,b,c]);assert sum(z['notProgressed'] for z in q)+c==a
    if b:assert math.isclose(q[1]['conditional']*q[2]['conditional'],c/a,abs_tol=1e-15)
    else:assert q[2]['conditional'] is None
    checks+=1
 for p in [0,.01,.1,.5,1]:
  for se in [0,.5,.9,1]:
   for sp in [0,.5,.95,1]:
    v=ppv(p,se,sp);assert v['ppv'] is None or 0<=v['ppv']<=1
    if v['tp']+v['fp']:assert math.isclose(v['ppv']*(v['tp']+v['fp']),v['tp'],abs_tol=1e-15)
    checks+=1
 for bad in [-1,float('nan'),float('inf'),1.1]:
  for i in range(3):
   a=[.1,.9,.95];a[i]=bad
   try:ppv(*a)
   except ValueError:pass
   else:raise AssertionError('domain accepted')
   checks+=1
 for xs in [[],[0,0],[10,11],[10,-1],[10,1.5],[10,float('inf')],[10,True]]:
  try:counts(xs)
  except ValueError:pass
  else:raise AssertionError('invalid cohort accepted')
  checks+=1
 q=counts(COHORT);assert math.isclose(math.prod(x['conditional'] for x in q),.27,abs_tol=1e-15)
 A=mixture([{'n':50,'events':40},{'n':60,'events':18}]);B=mixture([{'n':100,'events':72},{'n':10,'events':2}]);assert .8>.72 and .3>.2 and A<B
 assert math.isclose(.30+(1-.30)*.20,.44,abs_tol=1e-15)
 assert 1000*.07==70 and 2/10000-1/10000==1/10000
 checks+=2
 print(json.dumps({'status':'PASS','checks':checks+2,'cohort':q,'screen_toy':ppv(.01,.9,.95),'mixture_A':A,'mixture_B':B},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--export',action='store_true');a=p.parse_args()
 if a.export:(ROOT/'assets/ch21-outcome-state.json').write_text(json.dumps({'scope':'Synthetic linked-cycle cohort, one transfer pathway and complete followup; no clinical rate','counts':COHORT,'states':counts(COHORT),'screen':ppv(.01,.9,.95)},indent=2)+'\n',encoding='utf8')
 if a.check or not a.export:check()
