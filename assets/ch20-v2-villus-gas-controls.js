/* Held-input, presentation-clock controller. No molecular tracking. */
(function(){'use strict';const $=id=>document.getElementById(id),M=window.VillusGas,pref=matchMedia('(prefers-reduced-motion: reduce)');let phase=0,raf=null,last=null;
function pause(){if(raf!==null)cancelAnimationFrame(raf);raf=null;last=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
const signed=n=>(n>=0?'+':'')+n.toFixed(3);
function render(){const s=M.state(Number($('maternal').value),Number($('fetal').value),phase);phase=s.phase;
 $('maternal').value=String(s.maternal);$('fetal').value=String(s.fetal);$('seek').value=String(phase);
 for(const [name,value] of [['maternal',s.maternal],['fetal',s.fetal]]){$(name+'-value').textContent=value+' mmHg';$(name+'-bar').style.width=value+'%';$(name+'-bar').parentElement.setAttribute('aria-label',name+' partial pressure '+value+' mmHg, axis 0 to 100');}
 $('drive').textContent='J* = ('+s.maternal+' − '+s.fetal+') mmHg / (100 mmHg) = '+signed(s.drive);
 $('direction').textContent='Net drive: '+s.direction;
 $('integral').textContent='Q* = J* × phase = '+signed(s.integral);
 $('signed-bar').style.left=(s.integral<0?50+50*s.integral:50)+'%';$('signed-bar').style.width=(50*Math.abs(s.integral))+'%';$('signed-bar').parentElement.setAttribute('aria-label','Dimensionless integrated signed drive '+signed(s.integral)+', axis minus1 to plus1');
 $('phase').textContent='Phase '+phase.toFixed(2)+' / 1.00';$('previous').disabled=phase<=0;$('next').disabled=phase>=1;
}
function select(p){pause();phase=p;render();}
function inputs(){pause();phase=0;render();}
function applyPreset(){const [m,f]=M.preset($('gas').value,$('preset').value);$('maternal').value=String(m);$('fetal').value=String(f);inputs();}
$('gas').addEventListener('change',()=>{$('preset').options[0].textContent=$('gas').value==='CO2'?'CO₂: maternal 40 / fetal 45':'O₂: maternal 50 / fetal 25';$('preset').options[2].textContent=$('gas').value==='CO2'?'CO₂ reversed: maternal 50 / fetal 25':'O₂ reversed: maternal 25 / fetal 50';$('preset').value='forward';applyPreset();});$('preset').addEventListener('change',applyPreset);
$('maternal').addEventListener('change',inputs);$('fetal').addEventListener('change',inputs);
$('previous').addEventListener('click',()=>select(phase-.25));$('next').addEventListener('click',()=>select(phase+.25));$('reset').addEventListener('click',()=>select(0));$('seek').addEventListener('input',e=>select(Number(e.target.value)));
function tick(now){if(last!==null)phase=Math.min(1,phase+(now-last)/8000);last=now;render();if(phase>=1){pause();return;}raf=requestAnimationFrame(tick);}
$('play').addEventListener('click',()=>{if(raf!==null){pause();return;}if(phase>=1)phase=0;render();$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);pref.addEventListener('change',pause);render();
})();
