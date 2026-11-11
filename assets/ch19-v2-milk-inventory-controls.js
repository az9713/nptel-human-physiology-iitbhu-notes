/* Independent model-time clock, not the source experiment clock. */
(function(){'use strict';const $=id=>document.getElementById(id),M=window.MilkInventory,pref=matchMedia('(prefers-reduced-motion: reduce)');let tau=0,raf=null,last=null;
function pause(){if(raf!==null)cancelAnimationFrame(raf);raf=null;last=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
function render(){tau=Math.max(0,Math.min(20,tau));const S=Number($('synthesis').value),k=Number($('removal').value),s=M.milk(50,S,k,tau);$('plot').innerHTML=M.plot(S,k,tau);$('readout').textContent='τ='+tau.toFixed(2)+': A='+s.A.toFixed(3)+', D='+s.D.toFixed(3)+', initial stock + cumulative synthesis = '+s.input.toFixed(3)+'.';$('seek').value=String(tau);$('previous').disabled=tau<=0;$('next').disabled=tau>=20;}
function select(t){pause();tau=t;render();}
$('previous').addEventListener('click',()=>select(tau-2.5));$('next').addEventListener('click',()=>select(tau+2.5));$('reset').addEventListener('click',()=>select(0));$('seek').addEventListener('input',e=>select(Number(e.target.value)));for(const id of ['synthesis','removal'])$(id).addEventListener('change',()=>select(0));
function tick(now){if(last!==null)tau=Math.min(20,tau+(now-last)/500);last=now;render();if(tau>=20){pause();return;}raf=requestAnimationFrame(tick);}
$('play').addEventListener('click',()=>{if(raf!==null){pause();return;}if(tau>=20)tau=0;render();$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);pref.addEventListener('change',pause);render();
})();
