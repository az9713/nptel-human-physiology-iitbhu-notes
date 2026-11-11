/* Presentation-only discrete completed-state controller. */
(function(){'use strict';
const $=id=>document.getElementById(id),M=window.OocyteInventory;
let index=0,timer=null;const pref=matchMedia('(prefers-reduced-motion: reduce)');
function pause(){if(timer!==null)clearInterval(timer);timer=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
function render(){
 const branch=$('conditional').checked,s=M.state(index,branch);index=s.index;
 $('seek').max=String(M.limit(branch));$('seek').value=String(index);
 $('state-title').textContent=s.name;$('state-event').textContent=s.status;
 for(const [id,value] of [['chromosomes',s.chromosomes],['chromatids',s.chromatids],['dna',s.dnaC+'C'],['ploidy',s.ploidy]])$(id).textContent=String(value);
 for(const [id,value,max,label] of [['chromosome-bar',s.chromosomes,92,'Chromosomes'],['chromatid-bar',s.chromatids,92,'Chromatids'],['dna-bar',s.dnaC,4,'DNA in C units']]){
  $(id).style.width=(100*value/max)+'%';$(id).parentElement.setAttribute('aria-label',label+': '+value+'; axis 0 to '+max);
 }
 $('branch-status').textContent=branch?'Conditional branch enabled; final state counts only the maternal product.':'Default branch: release is the final displayed state.';
 $('previous').disabled=index===0;$('next').disabled=index===M.limit(branch);
 document.querySelectorAll('tr[data-state]').forEach(row=>{row.classList.toggle('selected',Number(row.dataset.state)===index);});
}
function select(n){pause();index=n;render();}
$('previous').addEventListener('click',()=>select(index-1));$('next').addEventListener('click',()=>select(index+1));$('reset').addEventListener('click',()=>select(0));
$('seek').addEventListener('input',e=>select(Number(e.target.value)));
$('conditional').addEventListener('change',()=>{pause();render();});
$('play').addEventListener('click',()=>{
 if(timer!==null){pause();return;}if(index>=M.limit($('conditional').checked))index=0;render();
 $('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');
 timer=setInterval(()=>{index++;render();if(index>=M.limit($('conditional').checked))pause();},3000);
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);pref.addEventListener('change',pause);
render();
})();
