(()=>{
 'use strict';
 const $=id=>document.getElementById(id),model=window.TbgBindingModel;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let phase=0,playing=false,last=null,raf=null,speed=1;
 const x=p=>90+580*p,yFree=v=>245-180*v/1.2,yOther=v=>535-180*v/20;
 function path(key,mapY){return Array.from({length:101},(_,i)=>{const p=i/100,s=model.compute(p,$('assumption').value);return `${i?'L':'M'}${x(p).toFixed(3)} ${mapY(s[key]).toFixed(3)}`;}).join(' ');}
 function draw(){
  const s=model.compute(phase,$('assumption').value);phase=s.phase;
  for(const key of ['capacity','free','bound','total'])$(key).textContent=s[key].toFixed(key==='capacity'?1:6);
  $('fraction').textContent=(100*s.freeFraction).toFixed(4)+'%';
  $('assumption-note').textContent=s.mode==='fixed-free'?'Free concentration is held at 1 by an idealized reservoir. Extra bound hormone comes from that reservoir; total hormone is not fixed.':'Total hormone is fixed at 10 in a closed sample. Additional capacity redistributes hormone between bound and free forms; no hormone is created.';
  $('curve-free').setAttribute('d',path('free',yFree));$('curve-bound').setAttribute('d',path('bound',yOther));$('curve-total').setAttribute('d',path('total',yOther));
  $('cursor-free').setAttribute('cx',x(phase));$('cursor-free').setAttribute('cy',yFree(s.free));
  $('cursor-bound').setAttribute('cx',x(phase));$('cursor-bound').setAttribute('cy',yOther(s.bound));
  $('cursor-total').setAttribute('cx',x(phase));$('cursor-total').setAttribute('cy',yOther(s.total));
  for(const id of ['guide-free','guide-other']){$(id).setAttribute('x1',x(phase));$(id).setAttribute('x2',x(phase));}
  $('seek').value=String(phase);$('seek').setAttribute('aria-valuetext',`${(100*phase).toFixed(1)} percent presentation phase; capacity ${s.capacity.toFixed(1)} model concentration units`);
  $('clock').textContent=`${(12*phase).toFixed(2)} / 12 presentation seconds`;
  $('play').textContent=playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(playing));
 }
 function pause(){playing=false;last=null;if(raf!==null)cancelAnimationFrame(raf);raf=null;draw();}
 function seek(value){pause();phase=Math.max(0,Math.min(1,value));draw();}
 function tick(now){if(!playing)return;if(last!==null)phase+=Math.max(0,(now-last)/1000)*speed/12;last=now;if(phase>=1){phase=1;playing=false;last=null;}draw();raf=playing?requestAnimationFrame(tick):null;}
 function play(){if(phase>=1)phase=0;playing=true;last=null;draw();raf=requestAnimationFrame(tick);}
 $('play').addEventListener('click',()=>playing?pause():play());$('replay').addEventListener('click',()=>seek(0));
 $('previous').addEventListener('click',()=>seek(phase-.25));$('next').addEventListener('click',()=>seek(phase+.25));
 $('seek').addEventListener('input',e=>seek(Number(e.target.value)));$('speed').addEventListener('change',e=>{speed=Number(e.target.value);last=null;draw();});$('assumption').addEventListener('change',()=>seek(0));
 reduced.addEventListener('change',()=>{if(reduced.matches)pause();});document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('beforeprint',pause);
 document.querySelectorAll('.pan').forEach(p=>p.addEventListener('keydown',e=>{if(e.target!==p||e.ctrlKey||e.altKey||e.metaKey)return;const k=e.key;if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(k))return;const mx=p.scrollWidth-p.clientWidth,my=p.scrollHeight-p.clientHeight;if(!mx&&!my)return;e.preventDefault();p.scrollTo({left:k==='Home'?0:k==='End'?mx:p.scrollLeft+(k==='ArrowRight'?60:k==='ArrowLeft'?-60:0),top:k==='Home'?0:k==='End'?my:p.scrollTop+(k==='ArrowDown'?60:k==='ArrowUp'?-60:0),behavior:'instant'});}));
 const dialog=$('enlargement'),image=$('enlarged-image'),viewport=dialog.querySelector('.viewport');let opener;
 document.querySelectorAll('[data-enlarge]').forEach(b=>b.addEventListener('click',()=>{opener=b;const source=$(b.dataset.enlarge);image.src=source.getAttribute('src');image.alt=source.alt;image.style.width='1600px';image.style.maxWidth='none';$('enlargement-title').textContent=b.dataset.enlarge==='overview-image'?'Whole TBG orientation — source-coordinate envelope':'Bound T4 and selected source-coordinate neighbours';dialog.showModal();viewport.scrollTop=0;viewport.scrollLeft=0;viewport.focus();}));
 $('native').addEventListener('click',()=>{image.style.width='1600px';image.style.maxWidth='none';});$('fit').addEventListener('click',()=>{const h=parseFloat(getComputedStyle(viewport).maxHeight);image.style.width=Math.min(viewport.clientWidth,Number.isFinite(h)?h*1600/1200:1600,1600)+'px';image.style.maxWidth='1600px';viewport.scrollTop=0;viewport.scrollLeft=0;});$('close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());window.addEventListener('beforeprint',()=>{if(dialog.open)dialog.close();});
 draw();
})();
