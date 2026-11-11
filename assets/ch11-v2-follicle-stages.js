(()=>{
 'use strict';
 const $=id=>document.getElementById(id),model=window.ThyroidFollicleStages;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let time=0,playing=false,last=null,raf=null,speed=1;
 function draw(){
  const s=model.state(time);time=s.time;
  for(const key of ['title','side','cargo','mechanism','boundary'])$('state-'+key).textContent=s[key];
  s.ledger.forEach((text,i)=>$('ledger-'+i).textContent=text);
  $('stage-number').textContent=`Stage ${s.index+1} of 7`;
  $('clock').textContent=`${time.toFixed(1)} / 21 presentation seconds`;
  $('seek').value=String(Math.round(time*1000));
  $('seek').setAttribute('aria-valuetext',`Stage ${s.index+1}: ${s.title}; ${time.toFixed(1)} presentation seconds`);
  $('play').textContent=playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(playing));
  $('progress').style.width=`${100*time/21}%`;
  document.querySelectorAll('[data-stage]').forEach(button=>{const active=Number(button.dataset.stage)===s.index;button.setAttribute('aria-current',active?'step':'false');});
  document.querySelectorAll('[data-region]').forEach(region=>region.classList.toggle('active',region.dataset.region===s.region));
  $('scene').setAttribute('data-state',String(s.index));
 }
 function pause(){playing=false;last=null;if(raf!==null)cancelAnimationFrame(raf);raf=null;draw();}
 function seek(value){pause();time=Math.max(0,Math.min(model.duration,value));draw();}
 function tick(now){if(!playing)return;if(last!==null)time+=Math.max(0,(now-last)/1000)*speed;last=now;if(time>=21){time=21;playing=false;last=null;}draw();raf=playing?requestAnimationFrame(tick):null;}
 function play(){if(time>=21)time=0;playing=true;last=null;draw();raf=requestAnimationFrame(tick);}
 $('play').addEventListener('click',()=>playing?pause():play());
 $('replay').addEventListener('click',()=>{seek(0);if(!reduced.matches)play();});
 $('previous').addEventListener('click',()=>seek(Math.max(0,(Math.ceil(time/3)-1)*3)));
 $('next').addEventListener('click',()=>seek(Math.min(21,(Math.floor(time/3)+1)*3)));
 $('seek').addEventListener('input',e=>seek(Number(e.target.value)/1000));
 $('speed').addEventListener('change',e=>{speed=Number(e.target.value);last=null;draw();});
 document.querySelectorAll('[data-stage]').forEach(button=>button.addEventListener('click',()=>seek(Number(button.dataset.stage)*3)));
 $('show-guides').addEventListener('change',()=>{$('scene').classList.toggle('no-guides',!$('show-guides').checked);});
 $('fit').addEventListener('click',()=>{$('image-pan').classList.add('fit');$('image-pan').focus();});
 $('native').addEventListener('click',()=>{$('image-pan').classList.remove('fit');$('image-pan').focus();});
 $('image-pan').addEventListener('keydown',event=>{
  if(event.target!==event.currentTarget||event.altKey||event.ctrlKey||event.metaKey)return;
  const pan=event.currentTarget,maxX=pan.scrollWidth-pan.clientWidth,maxY=pan.scrollHeight-pan.clientHeight;
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key)||(!maxX&&!maxY))return;
  event.preventDefault();const k=event.key;
  pan.scrollTo({left:k==='Home'?0:k==='End'?maxX:pan.scrollLeft+(k==='ArrowRight'?60:k==='ArrowLeft'?-60:0),top:k==='Home'?0:k==='End'?maxY:pan.scrollTop+(k==='ArrowDown'?60:k==='ArrowUp'?-60:0),behavior:'instant'});
 });
 reduced.addEventListener('change',e=>{if(e.matches){pause();$('status').textContent='Reduced motion: paused. Use stage buttons, step or seek; Play remains an explicit choice.';}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);
 $('status').textContent=reduced.matches?'Reduced motion: starts paused. Select a stage to inspect.':'Starts paused. The presentation advances explanatory stages, not live histology.';
 draw();
})();
