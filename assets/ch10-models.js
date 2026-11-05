/* Original synthetic teaching models; no clinical use. Units are documented in Chapter 10. */
'use strict';
(function(root){
 const finite=(x,name)=>{if(!Number.isFinite(x))throw new RangeError(name+' must be finite');return x;};
 const nonnegative=(x,name)=>{finite(x,name);if(x<0)throw new RangeError(name+' must be nonnegative');return x;};
 const positive=(x,name)=>{finite(x,name);if(x<=0)throw new RangeError(name+' must be positive');return x;};
 function exchange(t,{volume=1,conductance=.05,external=.2,consumption=.05,initial=0,source=0}={}){
  nonnegative(t,'time');positive(volume,'volume');nonnegative(conductance,'conductance');nonnegative(external,'external');nonnegative(consumption,'consumption');nonnegative(initial,'initial');nonnegative(source,'source');
  const rate=conductance/volume+consumption,cinf=rate>0?(conductance*external+source)/(volume*rate):(source>0?null:initial);
  const c=rate>0?cinf+(initial-cinf)*Math.exp(-rate*t):initial+source*t/volume;
  const integral=rate>0?cinf*t+(initial-cinf)*(-Math.expm1(-rate*t))/rate:initial*t+source*t*t/(2*volume);
  const input=conductance*external*t,back=conductance*integral,used=consumption*volume*integral,produced=source*t,stored=volume*c;
  return {c,cinf,stored,input,back,used,produced,residual:initial*volume+input+produced-stored-back-used};
 }
 function lagStep(t,tissue=5,sensor=2){
  nonnegative(t,'time');positive(tissue,'tissue lag');positive(sensor,'sensor lag');
  const i=1-Math.exp(-t/tissue);
  const m=Math.abs(tissue-sensor)<1e-10?1-(1+t/tissue)*Math.exp(-t/tissue):1-(tissue*Math.exp(-t/tissue)-sensor*Math.exp(-t/sensor))/(tissue-sensor);
  return {i,m};
 }
 function sensing(t){
  nonnegative(t,'time');let blood=5,tissue=5,sensor=5;
  for(const event of [{time:10,delta:5},{time:40,delta:-5}])if(t>=event.time){const x=lagStep(t-event.time);blood+=event.delta;tissue+=event.delta*x.i;sensor+=event.delta*x.m;}
  return {blood,tissue,sensor};
 }
 function control(duration=100,dt=.05,{sensorLag=5,effectorLag=10,gainScale=5}={}){
  nonnegative(duration,'duration');positive(dt,'step');positive(sensorLag,'sensor lag');positive(effectorLag,'effector lag');positive(gainScale,'gain scale');
  if(duration>10000||duration/dt>2000000)throw new RangeError('simulation too large');
  let t=0,g=5,s=5,a=0,input=0,basal=0,extra=0;const out=[];
  const row=()=>({t,g,s,a,u:Math.min(1,Math.max(0,(s-5)/gainScale)),input,basal,extra,residual:5+input-g-basal-extra});out.push(row());
  while(t<duration-1e-10){let step=Math.min(dt,duration-t);for(const e of [20,40])if(t<e-1e-10&&t+step>e)step=e-t;
   const q=.5+(t>=20-1e-10&&t<40-1e-10?.6:0),u=Math.min(1,Math.max(0,(s-5)/gainScale)),r=.1+.08*a,steady=q/r;
   const nextG=steady+(g-steady)*Math.exp(-r*step),integral=steady*step+(g-steady)*(-Math.expm1(-r*step))/r;
   input+=q*step;basal+=.1*integral;extra+=.08*a*integral;
   s=g+(s-g)*Math.exp(-step/sensorLag);a=u+(a-u)*Math.exp(-step/effectorLag);g=nextG;t+=step;out.push(row());
  }return out;
 }
 const api={exchange,lagStep,sensing,control};root.Ch10=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
