/* Original idealized coupled-entry bookkeeping, not a flux or cell-inventory model. */
(function(root){'use strict';
function state(phase,cargo='glucose'){
 if(!Number.isFinite(phase)||phase<0||phase>1)throw new RangeError('phase must be 0..1');
 if(!['glucose','fructose'].includes(cargo))throw new RangeError('unknown cargo');
 const entered=Math.min(1,phase*2),exited=Math.max(0,phase*2-1),coupling=cargo==='glucose'?2:0;
 return {phase,cargo,carrier:coupling?'SGLT1':'GLUT5',stage:phase===0?'Before entry':phase<=.5?'Apical entry':'Basolateral exit',
  sugar:[3*(1-entered),3*(entered-exited),3*exited],sodium:[3*coupling*(1-entered),3*coupling*entered,0],coupling,
  totalSugar:3,totalCoupledSodium:3*coupling};
}
root.EpithelialV2={state};if(typeof module!=='undefined')module.exports=root.EpithelialV2;
})(typeof window==='undefined'?globalThis:window);
