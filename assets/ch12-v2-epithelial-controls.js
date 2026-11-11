/* Interactive teaching phase; no symbols or paths are painted on specimen pixels. */
(()=>{'use strict';const $=id=>document.getElementById(id);let phase=0,playing=false,last=null;
function draw(){const s=EpithelialV2.state(phase,$('cargo').value);$('seek').value=phase;
 $('phase').textContent=`${s.stage} · ${(100*phase).toFixed(0)}% presentation phase`;
 $('carrier').textContent=s.coupling?'Glucose (galactose uses the same principal route): SGLT1 entry, 2 Na⁺ per sugar.':'Fructose: GLUT5 entry, no directly coupled Na⁺ or ATP.';
 $('sodium-note').textContent=s.coupling?'Only the six Na⁺ equivalents accompanying this idealized entry are accounted for. Other Na⁺ movements and pump turnover are omitted.':'Zero here means no Na⁺ directly coupled to GLUT5, not absence of sodium from a living cell.';
 ['lumen','cell','tissue'].forEach((id,i)=>{const g=s.sugar[i],na=s.sodium[i];$(id+'-g').textContent=g.toFixed(2);$(id+'-na').textContent=na.toFixed(2);$(id+'-bar').style.width=(100*g/3)+'%';});
 $('conservation').textContent=`Sugar sum ${s.sugar.reduce((a,b)=>a+b,0).toFixed(2)} / 3 equivalents. Coupled Na⁺ sum ${s.sodium.reduce((a,b)=>a+b,0).toFixed(2)} / ${s.totalCoupledSodium}.`;
 $('play').textContent=playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(playing));}
function pause(){playing=false;last=null;draw();}
$('play').onclick=()=>{if(playing){pause();return;}if(phase>=1)phase=0;playing=true;last=null;draw();};
$('replay').onclick=()=>{phase=0;pause();};
for(const [id,delta] of [['previous',-.5],['next',.5]])$(id).onclick=()=>{phase=Math.max(0,Math.min(1,(delta>0?Math.floor(phase*2+1e-9)+1:Math.ceil(phase*2-1e-9)-1)/2));pause();};
$('seek').oninput=()=>{phase=Number($('seek').value);pause();};$('cargo').onchange=()=>{phase=0;pause();};$('speed').onchange=pause;
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);
matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',pause);
document.querySelectorAll('.ledger-scroll').forEach(v=>v.addEventListener('keydown',e=>{if(e.target!==v)return;let x=v.scrollLeft;if(e.key==='ArrowRight')x+=60;else if(e.key==='ArrowLeft')x-=60;else if(e.key==='Home')x=0;else if(e.key==='End')x=v.scrollWidth-v.clientWidth;else return;e.preventDefault();v.scrollLeft=x;}));
function tick(now){if(playing){if(last!==null){phase=Math.min(1,phase+Math.min(100,now-last)/12000*Number($('speed').value));if(phase>=1){pause();}else draw();}last=playing?now:null;}requestAnimationFrame(tick);}
draw();requestAnimationFrame(tick);
})();
