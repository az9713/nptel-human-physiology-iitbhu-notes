/* Independently drawn generic signed-gradient exercise; no tissue coefficients. */
(function(root){'use strict';
function clamp(x,a,b){return Math.max(a,Math.min(b,Number.isFinite(Number(x))?Number(x):a));}
function state(maternal,fetal,phase){const m=clamp(maternal,0,100),f=clamp(fetal,0,100),p=clamp(phase,0,1),j=(m-f)/100;return Object.freeze({maternal:m,fetal:f,phase:p,drive:j,integral:j*p,direction:j>0?'toward fetus':j<0?'toward mother':'zero net drive; molecular motion persists'});}
function preset(gas,key){return key==='equal'?[40,40]:key==='reverse'?(gas==='CO2'?[50,25]:[25,50]):gas==='CO2'?[40,45]:[50,25];}
const api=Object.freeze({state,preset});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.VillusGas=api;
})(typeof window!=='undefined'?window:globalThis);
