/* Two explicitly separate molecules; idealized reaction states, no kinetic fit. */
(function(root){'use strict';
function state(phase){if(!Number.isFinite(phase)||phase<0||phase>1)throw new RangeError('phase0..1');const stage=Math.min(2,Math.floor(phase*3));const cuts=[0,1,7][stage];return {phase,stage,residues:9,water:cuts,remainingBonds:7-cuts,fragments:2+cuts,alpha14:[6,5,0][stage],alpha16:[1,1,0][stage],glucose:[0,0,9][stage]};}
root.CarbohydrateV2={state};if(typeof module!=='undefined')module.exports=root.CarbohydrateV2;
})(typeof window==='undefined'?globalThis:window);
