/* Original deterministic chapter16 pressure bookkeeping over observed TEM.
   No tissue dynamics, particle path or experimental-time conversion. */
(() => {
 'use strict';
 const DURATION=12000,clamp=x=>Math.max(0,Math.min(1,x));
 function stateFromPhase(x){if(!Number.isFinite(Number(x)))throw Error('Finite phase required');const phase=clamp(Number(x)),pbs=15+5*phase,nfp=55-pbs-30;return {phase,presentationMs:phase*DURATION,pgc:55,pbs,piGc:30,piBs:0,kf:12.5,nfp,flow:12.5*nfp};}
 if(typeof document==='undefined'){module.exports={stateFromPhase,durationMs:DURATION};return;}
 let phase=0,running=false,rate=1,previous=null;
 const $=id=>document.getElementById(id),play=$('play'),seek=$('seek'),parameter=$('pbs'),motion=matchMedia('(prefers-reduced-motion: reduce)');
 function draw(p){phase=clamp(p);const s=stateFromPhase(phase);seek.value=(s.presentationMs/1000).toFixed(2);parameter.value=s.pbs.toFixed(2);$('pbs-value').textContent=s.pbs.toFixed(2)+' mmHg';$('nfp-value').textContent=s.nfp.toFixed(2)+' mmHg';$('flow-value').textContent=s.flow.toFixed(2)+' mL/min';$('equation').textContent='55 − '+s.pbs.toFixed(2)+' − 30 + 0 = '+s.nfp.toFixed(2)+' mmHg';$('parameter-bar').setAttribute('width',String(s.pbs*5));$('net-bar').setAttribute('width',String(s.nfp*5));$('parameter-text').textContent=s.pbs.toFixed(2);$('net-text').textContent=s.nfp.toFixed(2);$('clock').textContent=(s.presentationMs/1000).toFixed(2)+' / 12.00 presentation s';$('state').textContent='Fixed capillary pressure and permeability: capsular pressure '+s.pbs.toFixed(2)+' mmHg; net driving pressure '+s.nfp.toFixed(2)+' mmHg; illustrative model filtration '+s.flow.toFixed(2)+' mL/min.';return s;}
 function stop(){running=false;previous=null;play.textContent='Play pressure sweep';play.setAttribute('aria-pressed','false');}
 play.addEventListener('click',()=>{if(running){stop();return}if(phase>=1)draw(0);running=true;previous=null;play.textContent='Pause pressure sweep';play.setAttribute('aria-pressed','true');});
 $('replay').addEventListener('click',()=>{stop();draw(0)});
 $('previous').addEventListener('click',()=>{stop();draw(phase-1/120)});
 $('next').addEventListener('click',()=>{stop();draw(phase+1/120)});
 seek.addEventListener('input',()=>{stop();draw(Number(seek.value)/12)});
 parameter.addEventListener('input',()=>{stop();draw((Number(parameter.value)-15)/5)});
 $('speed').addEventListener('change',()=>{rate=Number($('speed').value);previous=null});
 $('labels').addEventListener('change',()=>document.querySelector('.anatomy').classList.toggle('labels-hidden',!$('labels').checked));
 function frame(now){if(running){if(previous!==null){draw(phase+(now-previous)/DURATION*rate);if(phase>=1)stop()}previous=now;}requestAnimationFrame(frame)}
 motion.addEventListener('change',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});addEventListener('beforeprint',stop);
 document.querySelectorAll('.pan').forEach(p=>p.addEventListener('keydown',e=>{if(e.target!==p||e.altKey||e.ctrlKey||e.metaKey)return;let x=0,y=0;if(e.key==='ArrowLeft')x=-60;else if(e.key==='ArrowRight')x=60;else if(e.key==='ArrowUp')y=-60;else if(e.key==='ArrowDown')y=60;else if(e.key==='PageUp')y=-p.clientHeight*.9;else if(e.key==='PageDown')y=p.clientHeight*.9;else if(e.key==='Home'){p.scrollTo(0,0);e.preventDefault();return}else if(e.key==='End'){p.scrollTo(p.scrollWidth,p.scrollHeight);e.preventDefault();return}else return;e.preventDefault();p.scrollBy(x,y)}));
 const dialog=$('enlargement'),image=$('enlarged-image'),viewport=dialog.querySelector('.viewport');let opener,selected;
 const media={crop:['ch16-v2-filtration-control7a.png',721,'Source Figure 7A: young control TEM, complete selected field'],source7:['ch16-v2-filtration-source-figure7.png',1623,'Complete original Figure 7, including age/iron-overload panels and source 1 µm bar'],source6:['ch16-v2-filtration-source-figure6.png',1627,'Complete original Figure 6, endothelial-cell context and source labels']};
 function native(){image.style.width=selected[1]+'px';image.style.maxWidth='none'}
 document.querySelectorAll('[data-enlarge]').forEach(b=>b.addEventListener('click',()=>{opener=b;selected=media[b.dataset.enlarge];image.src=selected[0];image.alt=selected[2];$('enlargement-title').textContent=selected[2];native();dialog.showModal();viewport.scrollTo(0,0);viewport.focus()}));
 $('native').addEventListener('click',native);$('fit').addEventListener('click',()=>{image.style.width='100%';image.style.maxWidth=selected[1]+'px'});$('close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());
 window.FiltrationV2={stateFromPhase,renderFrame(ms){stop();return draw(Number(ms)/DURATION)},durationMs:DURATION};window.renderFrame=window.FiltrationV2.renderFrame;
 draw(0);requestAnimationFrame(frame);
})();
