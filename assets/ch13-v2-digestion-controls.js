/* Quantitative/chemical teaching states, separate from untouched microscopy. */
(()=>{'use strict';const $=id=>document.getElementById(id),mode=document.body.dataset.mode,stages=mode==='protein'?3:5;let phase=0,playing=false,last=null;
const titles=mode==='protein'?['Luminal dipeptide','Intracellular dipeptide','Intracellular amino acids','Interstitial amino acids']:['Luminal TAG','Luminal fatty acids / monoacylglycerol','Intracellular molecular products','Intracellular TAG-associated cargo','Interstitial chylomicron-associated cargo','Lymphatic chylomicron-associated cargo'];
const operations=mode==='protein'?['H⁺-coupled PEPT1 entry','Intracellular peptide hydrolysis','Basolateral amino-acid exit']:['Luminal TAG hydrolysis','Molecular apical uptake','Intracellular re-esterification / assembly','Basolateral cargo release','Lacteal entry / lymphatic transfer'];
function draw(){const s=DigestionV2[mode](phase);$('seek').value=phase;const x=phase*stages,i=Math.min(stages-1,Math.floor(x)),progress=Math.max(0,Math.min(1,x-i));$('phase').textContent=phase===1?'Final snapshot: '+titles[stages]+' · presentation complete':operations[i]+' · from '+titles[i]+' toward '+titles[i+1]+' · '+(100*progress).toFixed(1)+'% of this illustrative transition';
 s.amounts.forEach((v,i)=>{$('pool-'+i).textContent=v.toFixed(2);$('bar-'+i).style.width=(100*v/s.total)+'%';});
 $('conservation').textContent=s.amounts.reduce((a,b)=>a+b,0).toFixed(2)+' / '+s.total+' '+s.basis+' retained in the selected ledger.';
 if(mode==='protein'){
  const d=s.dipeptideLumen+s.dipeptideCell,aa=s.aminoAcidCell+s.aminoAcidInterstitium;
  $('form-0').textContent=d.toFixed(2)+' dipeptide equivalents';$('form-1').textContent=aa.toFixed(2)+' amino-acid equivalents';
  $('chem-0').style.opacity=d>1e-9?'1':'.25';$('chem-1').style.opacity=aa>1e-9?'1':'.25';
  $('chemistry').textContent='Selected hydrolysis: 3 Gly–Gly + 3 H₂O → 6 glycine. Water used so far: '+s.hydrolysisWater.toFixed(2)+' equivalents. Residue amount, not molecular count, is the conserved basis.';
 }else{
  const hydro=s.lipaseFraction,reester=Math.max(0,Math.min(1,phase*5-2)),tag=1-hydro+reester,products=hydro-reester;
  $('form-0').textContent=tag.toFixed(2)+' TAG-equivalent cargo (not particles)';$('form-1').textContent=(2*products).toFixed(2)+' fatty-acid + '+products.toFixed(2)+' monoacylglycerol equivalents';
  $('chem-0').style.opacity=tag>1e-9?'1':'.25';$('chem-1').style.opacity=products>1e-9?'1':'.25';
  $('chemistry').textContent='Selected luminal lipase hydrolysis uses '+s.lipaseWater.toFixed(2)+' / 2 water equivalents. Re-esterification/assembly is a separate intracellular process; this is not a complete water or energy balance.';
 }
 $('play').textContent=playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(playing));}
function pause(){playing=false;last=null;draw();}
$('play').onclick=()=>{if(playing){pause();return;}if(phase>=1)phase=0;playing=true;last=null;draw();};$('replay').onclick=()=>{phase=0;pause();};
for(const [id,d] of [['previous',-1],['next',1]])$(id).onclick=()=>{phase=Math.max(0,Math.min(1,(d>0?Math.floor(phase*stages+1e-9)+1:Math.ceil(phase*stages-1e-9)-1)/stages));pause();};
$('seek').oninput=()=>{phase=Number($('seek').value);pause();};$('speed').onchange=pause;
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',pause);
const dialog=$('enlargement'),im=$('enlarged-image'),vp=dialog.querySelector('.viewport');let op,width;
function native(){im.style.width=width+'px';im.style.maxWidth='none';}
document.querySelectorAll('[data-enlarge]').forEach(b=>b.onclick=()=>{op=b;width=Number(b.dataset.width);im.src=b.dataset.enlarge;im.alt=b.dataset.alt;native();dialog.showModal();vp.scrollLeft=0;vp.scrollTop=0;vp.focus();});
$('native').onclick=native;$('fit').onclick=()=>{im.style.width='100%';im.style.maxWidth=width+'px';};$('close').onclick=()=>dialog.close();dialog.addEventListener('close',()=>op?.focus());
function tick(now){if(playing){if(last!==null){phase=Math.min(1,phase+Math.min(100,now-last)/12000*Number($('speed').value));if(phase>=1)pause();else draw();}last=playing?now:null;}requestAnimationFrame(tick);}draw();requestAnimationFrame(tick);
})();
