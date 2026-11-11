/* Original chosen-equivalent accounting; not measured kinetics. */
(function(root){'use strict';
const P=[[3,0,0,0,0],[0,3,0,0,0],[0,0,6,0,3],[0,0,0,6,3]];
const L=[[3,0,0,0],[3,0,0,0],[0,3,0,0],[0,3,0,0],[0,0,3,0],[0,0,0,3]];
function valid(p){if(!Number.isFinite(p)||p<0||p>1)throw new RangeError('phase0..1');}
function interp(a,p){valid(p);const x=p*(a.length-1),i=Math.min(a.length-2,Math.floor(x)),f=x-i;return a[i].map((v,k)=>v+(a[i+1][k]-v)*f);}
function protein(p){const a=interp(P,p),stage=Math.min(3,Math.floor(p*3+1e-10));return {phase:p,stage,dipeptideLumen:a[0],dipeptideCell:a[1],aminoAcidCell:a[2],aminoAcidInterstitium:a[3],hydrolysisWater:a[4],amounts:[2*a[0],2*a[1]+a[2],a[3]],basis:'amino-acid-residue equivalents',total:6};}
function lipid(p){const a=interp(L,p),stage=Math.min(5,Math.floor(p*5+1e-10));return {phase:p,stage,amounts:a,basis:'long-chain acyl equivalents',total:3,lipaseFraction:Math.min(1,p*5),lipaseWater:2*Math.min(1,p*5)};}
root.DigestionV2={protein,lipid};if(typeof module!=='undefined')module.exports=root.DigestionV2;
})(typeof window==='undefined'?globalThis:window);
