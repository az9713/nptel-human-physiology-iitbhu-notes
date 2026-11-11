/* Exact chosen linked-cycle count construction, not empirical clinical rates. */
(function(root){'use strict';
const cohort=[100,90,72,54,36,27],names=['Cycle starts','Actual retrieval','At least one fertilization','Embryo transfer','Clinical pregnancy','Live-birth delivery'];
function counts(xs){if(!Array.isArray(xs)||xs.length<2||xs.some(x=>!Number.isSafeInteger(x)||x<0)||xs[0]===0||xs.some((x,i)=>i&&x>xs[i-1]))throw new RangeError('nonincreasing nonnegative safe integer cohort, positive start');return xs.map((x,i)=>({n:x,perStart:x/xs[0],conditional:i&&xs[i-1]>0?x/xs[i-1]:i?null:1,notProgressed:i?xs[i-1]-x:0}));}

function state(i){if(!Number.isInteger(i)||i<0||i>5)throw new RangeError('completed event0–5');return {...counts(cohort)[i],index:i,name:names[i],previous:i?cohort[i-1]:null};}
const api=Object.freeze({cohort:Object.freeze(cohort),names:Object.freeze(names),counts,state});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.IVFAccounting=api;})(typeof window!=='undefined'?window:globalThis);
