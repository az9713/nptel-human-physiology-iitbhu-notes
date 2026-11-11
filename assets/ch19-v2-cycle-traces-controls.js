/* Display clock for independent synthetic functions, not measured hormone kinetics. */
(function(){'use strict';const $=id=>document.getElementById(id),M=window.CycleTraces,pref=matchMedia('(prefers-reduced-motion: reduce)');let elapsed=0,raf=null,last=null;
function pause(){if(raf!==null)cancelAnimationFrame(raf);raf=null;last=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
function render(){elapsed=Math.max(0,Math.min(27.9,elapsed));const s=M.cycle(elapsed);$('plot').innerHTML=M.plot(elapsed);$('seek').value=String(elapsed);$('readout').textContent='Elapsed model day '+elapsed.toFixed(1)+'; chosen '+s.phase.toLowerCase()+' interval. Zero marks illustrative bleeding onset (conventional cycle day 1).';$('previous').disabled=elapsed<=0;$('next').disabled=elapsed>=27.9;}
function select(t){pause();elapsed=t;render();}
$('previous').addEventListener('click',()=>select(elapsed-3.5));$('next').addEventListener('click',()=>select(elapsed+3.5));$('reset').addEventListener('click',()=>select(0));$('seek').addEventListener('input',e=>select(Number(e.target.value)));
function tick(now){if(last!==null)elapsed=Math.min(27.9,elapsed+(now-last)*27.9/14000);last=now;render();if(elapsed>=27.9){pause();return;}raf=requestAnimationFrame(tick);}
$('play').addEventListener('click',()=>{if(raf!==null){pause();return;}if(elapsed>=27.9)elapsed=0;render();$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);pref.addEventListener('change',pause);render();
})();
