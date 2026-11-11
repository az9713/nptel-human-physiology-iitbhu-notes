/* Eq11.1 population equilibrium. Presentation phase is not binding kinetics. */
(function(root){
 'use strict';
 const modes=['fixed-free','closed-total'];
 function compute(phase,mode){
  if(!modes.includes(mode))throw new RangeError('Unknown operating assumption');
  if(!Number.isFinite(phase))throw new TypeError('Finite presentation phase required');
  const p=Math.max(0,Math.min(1,phase)),capacity=90+90*p,kd=9;
  let free;
  if(mode==='fixed-free')free=1;
  else {const total=10,a=capacity+kd-total;free=2*total*kd/(a+Math.sqrt(a*a+4*total*kd));}
  const bound=capacity*free/(kd+free),total=free+bound;
  return {phase:p,mode,capacity,kd,free,bound,total,freeFraction:free/total};
 }
 const api={compute,modes,duration:12};
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.TbgBindingModel=api;
})(typeof window==='object'?window:globalThis);
