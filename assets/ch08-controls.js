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
 const v=M.lung(phase,val('vt')), y=x=>270-x*38;
 s+=text(20,25,'Lung gas volume (L)')+text(610,300,'Maneuver presentation phase');
 for(let n=0;n<=6;n++)s+=line(70,y(n),650,y(n),'#3b5869')+text(30,y(n)+5,n.toString());
 const colors=['#5b7ba3','#96765e','#538f99','#759f74'];
 let levels=[0,v.rv,v.frc,v.frc+v.vt,v.tlc];
 ['RV','ERV','VT','IRV'].forEach((name,i)=>{s+=rect(720,y(levels[i+1]),80,(levels[i+1]-levels[i])*38,colors[i])+text(815,(y(levels[i])+y(levels[i+1]))/2+6,name+' '+f(levels[i+1]-levels[i]));});
 let points=[];for(let i=0;i<=200;i++){let p=i/200;points.push((70+p*580)+','+y(M.lung(p,val('vt')).value));}
 s+='<polyline points="'+points.join(' ')+'" fill="none" stroke="#78d6c4" stroke-width="3"/>';
 s+=line(70+phase*580,40,70+phase*580,270,'#f1c875');
 s+='<circle cx="'+(70+phase*580)+'" cy="'+y(v.value)+'" r="6" fill="#f1c875"/>';
 report='Phase '+f(phase)+'; volume '+f(v.value)+' L. IC '+f(v.ic)+'; FRC '+f(v.frc)+'; VC '+f(v.vc)+'; TLC '+f(v.tlc)+' L. TLC = IC + FRC = VC + RV. IRV 3, ERV 1.1 and RV 1.2 L are fixed; changing VT changes the coherent sums. Ordinary spirometry does not directly supply RV/FRC/TLC.';
}else if(view==='oxygen-accounting'){
 const hb=val('hb')*(1-.5*phase),c=M.content(hb,val('sat'),100),b=M.balance(c.total,c.total*(1-val('e')),val('q'));
 const scale=760/4500;
 s+=text(25,30,'Oxygen rates (mL/min); one common scale 0–4500');
 [['Incoming delivery',b.delivery,'#6ed9c3'],['Consumed',b.consumption,'#ecb975'],['Returning in venous blood',b.returned,'#8ca8df']].forEach((r,i)=>{let y=70+i*75;s+=text(25,y,r[0]+' '+f(r[1]))+rect(25,y+12,r[1]*scale,24,r[2]);});
 s+=text(25,295,'Content '+f(c.total)+' mL/dL; Hb '+f(hb)+' g/dL; pressure 100 mmHg');
 report='Sweep phase '+f(phase)+' (independent states). Hb '+f(hb)+' g/dL; saturation '+f(val('sat'))+'. Bound '+f(c.bound)+' + dissolved '+f(c.dissolved)+' = '+f(c.total)+' mL O₂/dL. Delivery '+f(b.delivery)+' = consumed '+f(b.consumption)+' + returning '+f(b.returned)+' mL/min. Content extraction fraction '+f(val('e'))+'; consumption/delivery '+(b.delivery>0?f(b.consumption/b.delivery):'undefined at zero delivery')+'.';
}else{
 const o=M.optical(val('red'),100,2,100),occ=M.occupancy(val('co'));
 s+=rect(20,50,135,85,'#416778')+text(30,80,'Red 660 nm')+text(30,112,'IR 940 nm')+rect(215,50,160,85,'#735b68')+text(235,98,'Tissue path')+rect(435,50,130,85,'#416778')+text(450,98,'Detector')+line(155,90,215,90,'#edbd79',5)+line(375,90,435,90,'#edbd79',5);
 s+=text(20,25,'Transmission schematic: illustrative geometry, not a tissue section');
 let red=[],ir=[];for(let i=0;i<=200;i++){let p=i/200;red.push((25+p*500)+','+(205-Math.sin(6*Math.PI*p)*val('red')*10));ir.push((25+p*500)+','+(270-Math.sin(6*Math.PI*p)*20));}
 s+='<polyline points="'+red.join(' ')+'" fill="none" stroke="#ef9e94" stroke-width="3"/><polyline points="'+ir.join(' ')+'" fill="none" stroke="#8bd8d2" stroke-width="3"/>'+text(550,205,'Red AC '+f(val('red')))+text(550,270,'IR AC 2; DC both 100')+line(25+phase*500,155,25+phase*500,295,'#f1c875');
 s+=text(700,65,'Separate Hb-site pool');let x=700;[[occ.oxy,'#71c9a6'],[occ.deoxy,'#829bce'],[occ.co,'#d7a765']].forEach(r=>{s+=rect(x,90,r[0]*220,35,r[1]);x+=r[0]*220;});s+=text(700,160,'Oxy '+f(100*occ.oxy)+'%')+text(700,190,'Deoxy '+f(100*occ.deoxy)+'%')+text(700,220,'CO '+f(100*occ.co)+'%');
 report='Pulse phase '+f(phase)+'; synthetic R '+f(o.r)+'. Illustrative 130−30R = '+f(o.illustrativePercent)+'% (not a device calibration). Hb pool separately assumes functional saturation 98%; oxy '+f(100*occ.oxy)+'%, deoxy '+f(100*occ.deoxy)+'%, CO '+f(100*occ.co)+'% of all sites. These fractions sum to 100%. Signals are NOT generated from this pool; no CO-specific optical reading is predicted. Conventional two-wavelength oximetry cannot exclude CO poisoning.';
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
const reduced=matchMedia('(prefers-reduced-motion: reduce)');reduced.addEventListener('change',pause);
function tick(now){if(playing){if(last!==null){phase=Math.min(1,phase+(now-last)/12000*val('speed'));render();if(phase>=1)pause();}last=now;}requestAnimationFrame(tick);}
render();requestAnimationFrame(tick);
})();
