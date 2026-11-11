
(function(){
'use strict';
const duration=16, seek=document.getElementById('seek'), play=document.getElementById('play'), speed=document.getElementById('speed'), clock=document.getElementById('clock'), state=document.getElementById('state');
const cards=[0,1,2,3].map(i=>document.getElementById('stage-'+i));
const descriptions=[
'Body: ask how systems cooperate to preserve the cell’s environment.',
'Organ: ask how different tissues are arranged to perform a shared task.',
'Tissue: identify the superficial epithelial band and the deeper fibrous extracellular matrix.',
'Cell: identify the yellow-stained nucleus and red-stained mitochondrial structures in a primary human fibroblast.'
];
let time=0, running=false, previous=null, current=-1;
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
function setRunning(value){running=value;previous=null;play.textContent=value?'Pause tour':'Guided tour';play.setAttribute('aria-pressed',String(value));}
function renderFrame(t){
time=Math.max(0,Math.min(duration,Number.isFinite(t)?t:0));
const phase=Math.min(3,Math.floor(time/4));
cards.forEach((card,i)=>{card.classList.toggle('active',i===phase);card.querySelector('button').setAttribute('aria-pressed',String(i===phase));});
seek.value=String(time);clock.textContent=time.toFixed(1)+' / 16 s';seek.setAttribute('aria-valuetext',time.toFixed(1)+' seconds; '+['body','organ','tissue','cell'][phase]);
if(phase!==current){state.textContent=descriptions[phase];current=phase;}
return {time:time,phase:phase,presentationOnly:true,sourceFieldWidthMicrometres:phase===2?400:null};
}
window.renderFrame=renderFrame;
play.addEventListener('click',()=>{if(time>=duration)renderFrame(0);setRunning(!running);});
document.getElementById('replay').addEventListener('click',()=>{renderFrame(0);setRunning(!reduced.matches);});
seek.addEventListener('input',()=>{setRunning(false);renderFrame(Number(seek.value));});
document.querySelectorAll('[data-stage]').forEach(button=>button.addEventListener('click',()=>{setRunning(false);renderFrame(Number(button.dataset.stage)*4);}));
document.addEventListener('visibilitychange',()=>{if(document.hidden)setRunning(false);});
reduced.addEventListener('change',()=>{if(reduced.matches)setRunning(false);});
function frame(stamp){if(running){if(previous!==null)renderFrame(time+Math.min(.1,(stamp-previous)/1000)*Number(speed.value));previous=stamp;if(time>=duration)setRunning(false);}requestAnimationFrame(frame);}


