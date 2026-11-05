'use strict';
(async()=>{
const $=id=>document.getElementById(id),modes={barrier:['Selective endothelial transport','Qualitative route position; no molecular velocity, flux or physiological transport time.'],recycling:['Glial recycling and potassium redistribution','Three equal imposed transfer rates conserve represented skeleton amount. K⁺ is a distinct qualitative route. Artificial units, not a patient model.'],photo:['Light response and recovery','Biological signs with a synthetic first-order response. Artificial model time, not measured rod kinetics.'],field:['Partial optic crossing','Four route selections, not eye movement, measured conduction or a physiological clock.'],conduction:['Myelin and conduction','Matched symbolic propagation with one possible blocked branch. No temporal or metric calibration.']};
const candidate=new URLSearchParams(location.search).get('mode'),mode=Object.hasOwn(modes,candidate)?candidate:'barrier';
$('title').textContent=modes[mode][0];$('boundary').textContent=modes[mode][1];$('static').href=`ch25-${mode}.svg`;
let data,index=0,playing=false,last=null,clock=0;
function stop(){playing=false;last=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
function show(){const s=data.states[index];$('figure').innerHTML=Ch25Render.render(mode,index,data);$('seek').value=index;$('state').textContent=`Saved state ${index}/160; presentation progress ${(100*index/160).toFixed(1)}%`+(['photo','recycling'].includes(mode)?`; artificial model t=${s.time.toFixed(2)}`:'; sequence only');$('detail').textContent=mode==='recycling'?'Selected amounts: '+Object.entries(s.recycling).map(([k,v])=>k+'='+v.toFixed(6)).join('; '):mode==='photo'?`Input=${s.photo.light}; closure=${s.photo.closure.toFixed(6)}; open/release proxy=${s.photo.open_fraction.toFixed(6)}`:modes[mode][1];}
function seek(v){if(!Number.isInteger(v)||v<0||v>160)throw Error('Invalid saved index');index=v;clock=v;show();}
function tick(now){if(!playing)return;if(last!==null){clock=Math.min(160,clock+Math.min(.2,(now-last)/1000)*8*Number($('speed').value));const j=Math.floor(clock);if(j!==index){index=j;show();}}last=now;if(clock>=160)stop();else requestAnimationFrame(tick);}
try{const response=await fetch('ch25-data.json');if(!response.ok)throw Error('Shared states unavailable');data=await response.json();if(data.states.length!==161)throw Error('Unexpected shared-state count');show();
$('play').onclick=()=>{if(playing){stop();return;}if(index===160)seek(0);playing=true;last=null;$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');requestAnimationFrame(tick);};
$('reset').onclick=()=>{stop();seek(0);};$('prev').onclick=()=>{stop();seek(Math.max(0,index-1));};$('next').onclick=()=>{stop();seek(Math.min(160,index+1));};$('seek').oninput=()=>{stop();seek(Number($('seek').value));};
matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.ch25State=()=>({mode,index,playing,model_time:data.states[index].time});
}catch(error){stop();$('state').textContent=error.message+'; use the static counterpart.';}
})();
