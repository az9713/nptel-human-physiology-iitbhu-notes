/* Controlled original teaching views; no autonomous playback. */
'use strict';
(() => {
const view=document.body.dataset.view, M=window.Ch08;
const get=id=>document.getElementById(id), val=id=>Number(get(id).value);
let phase=0, playing=false, last=null;
const line=(x1,y1,x2,y2,color='#90aabd',width=2)=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+color+'" stroke-width="'+width+'"/>';
const text=(x,y,s)=>'<text x="'+x+'" y="'+y+'">'+s+'</text>';
const rect=(x,y,w,h,c)=>'<rect x="'+x+'" y="'+y+'" width="'+Math.max(0,w)+'" height="'+h+'" rx="4" fill="'+c+'"/>';
const f=x=>x.toFixed(3);
function pause(){playing=false;last=null;get('play').textContent='Play';get('play').setAttribute('aria-pressed','false');}
function render(){
get('seek').value=phase;
let s='',report='';
if(view==='lung-volumes'){
 const v=M.lung(phase,val('vt')), y=x=>270-x*32;
 s+=text(20,25,'Lung gas volume (L)')+text(70,330,'Maneuver presentation phase (0–1; not respiratory time)');
 for(let n=0;n<=7;n++)s+=line(70,y(n),650,y(n),'#3b5869')+text(30,y(n)+5,n.toString());
 s+=line(70,46,70,270)+line(70,270,650,270);
 for(let n=0;n<=5;n++){const x=70+116*n;s+=line(x,270,x,278)+'<text class="tick-label" x="'+x+'" y="300" text-anchor="middle">'+(n/5).toFixed(1)+'</text>';}
 const colors=['#5b7ba3','#96765e','#538f99','#759f74'];
 let levels=[0,v.rv,v.frc,v.frc+v.vt,v.tlc];
 ['RV','ERV','VT','IRV'].forEach((name,i)=>{s+=rect(720,y(levels[i+1]),80,y(levels[i])-y(levels[i+1]),colors[i])+text(815,(y(levels[i])+y(levels[i+1]))/2+6,name+' '+f(levels[i+1]-levels[i]));});
 let points=[];for(let i=0;i<=200;i++){let p=i/200;points.push((70+p*580)+','+y(M.lung(p,val('vt')).value));}
 s+='<polyline class="data-curve" points="'+points.join(' ')+'" fill="none" stroke="#78d6c4" stroke-width="3"/>';
 s+='<g class="phase-cursor">'+line(70+phase*580,40,70+phase*580,270,'#f1c875')+'</g>';
 s+='<circle class="state-dot" cx="'+(70+phase*580)+'" cy="'+y(v.value)+'" r="6" fill="#f1c875"/>';
 report='Phase '+f(phase)+'; volume '+f(v.value)+' L. IC '+f(v.ic)+'; FRC '+f(v.frc)+'; VC '+f(v.vc)+'; TLC '+f(v.tlc)+' L. TLC = IC + FRC = VC + RV. IRV 3, ERV 1.1 and RV 1.2 L are fixed; changing VT changes the coherent sums. Ordinary spirometry does not directly supply RV/FRC/TLC.';
}else if(view==='oxygen-accounting'){
 const hb=val('hb')*(1-.5*phase),c=M.content(hb,val('sat'),100),b=M.balance(c.total,c.total*(1-val('e')),val('q'));
 const scale=760/4500;
 s+=text(25,30,'Oxygen rates (mL/min); one common scale 0–4500');
 [['Incoming delivery',b.delivery,'#6ed9c3'],['Consumed',b.consumption,'#ecb975'],['Returning in venous blood',b.returned,'#8ca8df']].forEach((r,i)=>{let y=70+i*75;s+=text(25,y,r[0]+' '+f(r[1]))+rect(25,y+12,r[1]*scale,24,r[2]);});
 s+=line(25,278,785,278);
 [0,1000,2000,3000,4000,4500].forEach(n=>{const x=25+n*scale;s+=line(x,278,x,286)+'<text class="tick-label" x="'+x+'" y="309" text-anchor="middle">'+n+'</text>';});
 s+=text(25,339,'Common rate axis (mL O₂/min)');
 s+=text(25,373,'Content '+f(c.total)+' mL/dL; Hb '+f(hb)+' g/dL; pressure 100 mmHg');
 report='Sweep phase '+f(phase)+' (independent states). Hb '+f(hb)+' g/dL; saturation '+f(val('sat'))+'. Bound '+f(c.bound)+' + dissolved '+f(c.dissolved)+' = '+f(c.total)+' mL O₂/dL. Delivery '+f(b.delivery)+' = consumed '+f(b.consumption)+' + returning '+f(b.returned)+' mL/min (rates rounded to 0.001 mL/min). Content extraction fraction '+f(val('e'))+'; consumption/delivery '+(b.delivery>0?f(b.consumption/b.delivery):'undefined at zero delivery')+'.';
}else{throw new Error('Unsupported quantitative plot view: '+view);
}
get('drawing').innerHTML=s;get('result').textContent=report;
}
get('play').onclick=()=>{if(playing){pause();return;}if(phase>=1)phase=0;playing=true;get('play').textContent='Pause';get('play').setAttribute('aria-pressed','true');last=null;};
get('replay').onclick=()=>{pause();phase=0;render();};
get('back').onclick=()=>{pause();phase=Math.max(0,Math.round((phase-.2)*1000)/1000);render();};
get('next').onclick=()=>{pause();phase=Math.min(1,Math.round((phase+.2)*1000)/1000);render();};
get('seek').oninput=()=>{pause();phase=val('seek');render();};
document.querySelectorAll('.controls input:not(#seek)').forEach(el=>{el.oninput=()=>{pause();render();};});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
window.addEventListener('beforeprint',pause);
document.querySelectorAll('.viewport').forEach(panel=>panel.addEventListener('keydown',event=>{
 if(event.target!==panel||event.altKey||event.ctrlKey||event.metaKey)return;
 let x=panel.scrollLeft;
 if(event.key==='ArrowLeft')x-=60;else if(event.key==='ArrowRight')x+=60;
 else if(event.key==='Home')x=0;else if(event.key==='End')x=panel.scrollWidth-panel.clientWidth;else return;
 event.preventDefault();panel.scrollTo({left:Math.max(0,Math.min(panel.scrollWidth-panel.clientWidth,x)),behavior:'instant'});
}));
const reduced=matchMedia('(prefers-reduced-motion: reduce)');reduced.addEventListener('change',pause);
function tick(now){if(playing){if(last!==null){phase=Math.min(1,phase+(now-last)/12000*val('speed'));render();if(phase>=1)pause();}last=now;}requestAnimationFrame(tick);}
render();requestAnimationFrame(tick);
})();
