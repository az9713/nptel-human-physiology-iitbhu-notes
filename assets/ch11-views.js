(function(){
'use strict';
const $=id=>document.getElementById(id), mode=document.body.dataset.view;
const play=$('play'),phase=$('phase'),scenario=$('scenario'),speed=$('speed'),out=$('readout');
let p=0,playing=false,last=null,trace=[],params;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function pause(){playing=false;play.textContent='Play';play.setAttribute('aria-pressed','false');last=null;}
function reset(){pause();p=0;phase.value='0';prepare();render();}
function prepare(){if(mode==='feedback'){params=[[1,.25,0],[.25,1,0],[1,1,1]][Number(scenario.value)];trace=Ch11.trajectory(...params);}}
function point(points,f){const q=Math.min(1,Math.max(0,f))*(points.length-1),i=Math.min(points.length-2,Math.floor(q)),w=q-i;return [points[i][0]*(1-w)+points[i+1][0]*w,points[i][1]*(1-w)+points[i+1][1]*w];}
function topologyPanels(kind,active,text){
 let svg=text(20,25,'Topology snapshots: colloid above; cell and basal blood-facing side below.','small');
 const names=kind==='secretion'?['1. Closed secretory vesicle','2. Apical fusion','3. Cargo in colloid']:['1. Apical invagination','2. Closed endocytic vesicle','3. Lysosomal proteolysis'];
 for(let i=0;i<3;i++){
 const left=20+i*330,right=left+300,cx=left+150,connected=kind==='secretion'?i===1:i===0;
 svg+='<g data-topology="'+kind+'-'+i+'" data-active="'+(i===active)+'"><rect x="'+left+'" y="45" width="300" height="490" rx="10" fill="#162b36" stroke="'+(i===active?'#f1ce70':'#61768a')+'" stroke-width="'+(i===active?5:1)+'"/>';
 svg+=text(left+12,80,names[i],'small');
 svg+='<rect x="'+(left+8)+'" y="100" width="284" height="130" fill="#493f28"/><rect x="'+(left+8)+'" y="230" width="284" height="210" fill="#233f47"/><rect x="'+(left+8)+'" y="440" width="284" height="75" fill="#3e283d"/>';
 svg+=text(left+20,128,'Colloid lumen','small')+text(left+20,425,'Follicular-cell cytosol','small')+text(left+20,495,'Blood / interstitium','small')+text(left+20,465,'Basal membrane','small');
 svg+='<path data-basal="intact" d="M'+(left+8)+' 440H'+(right-8)+'" stroke="#a9d5dc" stroke-width="6"/>';
 if(connected){
 svg+='<path data-lumen="connected" d="M'+(cx-35)+' 230V300C'+(cx-35)+' 350 '+(cx+35)+' 350 '+(cx+35)+' 300V230Z" fill="#493f28"/>';
 svg+='<path data-apical="continuous-invagination" d="M'+(left+8)+' 230H'+(cx-35)+'V300C'+(cx-35)+' 350 '+(cx+35)+' 350 '+(cx+35)+' 300V230H'+(right-8)+'" fill="none" stroke="#e2c58b" stroke-width="6"/>';
 svg+=text(left+15,205,'Apical membrane','small');
 }else{svg+='<path data-apical="resealed" d="M'+(left+8)+' 230H'+(right-8)+'" stroke="#e2c58b" stroke-width="6"/>';svg+=text(left+15,205,'Apical membrane','small');}
 if(kind==='secretion'){
 const cy=i===2?165:i===1?300:330;
 if(i===0)svg+='<circle data-compartment="secretory-lumen" cx="'+cx+'" cy="330" r="48" fill="#493f28" stroke="#e2c58b" stroke-width="6"/>';
 svg+='<circle data-cargo="Tg" data-contained-in="'+(i===0?'secretory-lumen':'colloid')+'" cx="'+cx+'" cy="'+cy+'" r="15" fill="#f1ce70"/>'+text(cx-11,cy+6,'Tg','small');
 if(i===0)svg+=text(left+30,395,'Membrane-enclosed lumen','small');
 }else if(i<2){
 const cy=i===0?300:330;
 if(i===1)svg+='<circle data-compartment="endocytic-lumen" cx="'+cx+'" cy="330" r="48" fill="#493f28" stroke="#e2c58b" stroke-width="6"/>';
 svg+='<circle data-cargo="Tg" data-contained-in="'+(i===0?'colloid':'endocytic-lumen')+'" cx="'+cx+'" cy="'+cy+'" r="15" fill="#f1ce70"/>'+text(cx-11,cy+6,'Tg','small');
 }else{
 svg+='<circle data-compartment="lysosomal-lumen" cx="'+cx+'" cy="330" r="65" fill="#563953" stroke="#d8a5d3" stroke-width="6"/>';
 svg+='<path data-cargo="Tg-fragments" data-contained-in="lysosomal-lumen" d="M'+(cx-35)+' 300l12 8m8-8l12 8" stroke="#f1ce70" stroke-width="6"/>';
 svg+='<path data-cargo="free-T3T4" data-contained-in="lysosomal-lumen" d="M'+(cx-10)+' 340l10-10 10 10-10 10Z" fill="#70d3e2"/>';
 svg+=text(left+30,405,'Separate lysosomal lumen','small');
 }
 svg+='</g>';
 }
 return svg+text(20,562,'Gold Tg cargo / fragments; cyan diamond = liberated T3/T4. Snapshots do not measure membrane-deformation time.','small');
}
function follicle(){
 const view=Number(scenario.value),stages=view===0?4:3,stage=Math.min(stages-1,Math.floor(p*stages)),f=Math.min(1,p*stages-stage);
 let drawing='',route=[],description='';
 const text=(x,y,s,cl='')=>'<text x="'+x+'" y="'+y+'" class="'+cl+'">'+s+'</text>';
 $('cargo').setAttribute('visibility','visible');$('cargo').setAttribute('fill',view===1?'#70d3e2':'#f1ce70');
 if((view===0&&stage===2)||(view===1&&stage<2)){
 const secretion=view===0,active=secretion?Math.min(2,Math.floor(3*f)):stage===0?(f<.5?0:1):2;
 $('drawing').innerHTML=topologyPanels(secretion?'secretion':'retrieval',active,text);$('cargo').setAttribute('visibility','hidden');
 const descriptions=secretion?'Tg is cargo inside a secretory vesicle. Apical membrane fusion opens the vesicle lumen to colloid; Tg does not cross an intact lipid bilayer.':stage===0?'An apical invagination encloses colloidal Tg. Fission leaves Tg inside a closed endocytic compartment, not free in cytosol.':'Endocytic cargo reaches the lysosomal lumen. Proteolysis liberates T3/T4 from Tg before the distinct hormone-export route. Membrane trafficking and processing are ordered teaching stages, not measured kinetics.';
 out.textContent='Stage '+(stage+1)+' / '+stages+'. Highlighted topology '+(active+1)+' / 3. '+descriptions;return;
 }
 if(view<2){
 drawing='<rect x="30" y="70" width="245" height="420" fill="#3e283d"/><rect x="285" y="70" width="310" height="420" fill="#233f47"/><rect x="605" y="70" width="365" height="420" fill="#493f28"/>';
 drawing+=text(55,40,'Blood / interstitium')+text(350,40,'Follicular cell')+text(680,40,'Colloid lumen');
 drawing+='<path d="M280 70V165M280 195V325M280 355V490" stroke="#a9d5dc" stroke-width="8"/>';
 drawing+='<path d="M600 70V165M600 195V490" stroke="#e2c58b" stroke-width="8"/>';
 drawing+='<rect x="266" y="165" width="28" height="30" rx="8" fill="#58979f"/><rect x="266" y="325" width="28" height="30" rx="8" fill="#58979f"/><rect x="586" y="165" width="28" height="30" rx="8" fill="#a38a53"/>';
 drawing+=text(120,155,'NIS: 2 Na⁺ / I⁻','small')+text(365,155,'Na/K ATPase supports gradient','small')+text(637,155,'Pendrin / apical route','small');
 drawing+=text(66,372,'T3/T4 export route','small')+text(65,392,'including MCT8','small')+text(300,525,'Basal membrane')+text(595,525,'Apical membrane');
 drawing+='<path d="M267 90V120" stroke="#d8a5d3" stroke-width="8"/>'+text(60,80,'TSH → receptor','small');
 drawing+=text(665,260,'Tg scaffold in colloid')+text(650,465,'TPO: apical/colloid context','small');
 if(view===0){
 if(stage===0){route=[[170,105],[257,105]];description='TSH binds an extracellular basal receptor. Signal transduction regulates the cell; TSH is not required to enter.';}
 if(stage===1){route=[[100,180],[280,180],[440,180],[600,180],[690,180]];description='Iodide enters through NIS with sodium-gradient coupling, then crosses an apical anion route. Marker is one route token, not a molecule census.';}
 if(stage===3){route=[[760,300],[760,300]];description='TPO-associated oxidation, iodination and coupling occur on luminal Tg: MIT/DIT count iodine atoms; products remain attached. No free-I2 pool is modeled.';drawing+=text(650,350,f<.33?'Tyrosyl residue → MIT':f<.66?'MIT / DIT residues':'Coupled T3/T4 on Tg');}
 }else{
 if(stage===2){route=[[440,340],[280,340],[100,340]];description='Cyan free T3/T4 leave basolaterally through hormone transport. The prior panel located proteolysis inside a lysosomal lumen; transfer from that lumen to the cytosolic export pool is not animated. No second vesicle membrane lies across this separate route. This is not peptide-vesicle exocytosis.';}
 }
 }else{
 drawing='<rect x="30" y="70" width="405" height="420" fill="#3e283d"/><rect x="445" y="70" width="525" height="420" fill="#233f47"/><path d="M440 70V285M440 315V490" stroke="#a9d5dc" stroke-width="8"/><rect x="426" y="285" width="28" height="30" rx="8" fill="#58979f"/>';
 drawing+='<circle cx="200" cy="210" r="25" fill="none" stroke="#d8a5d3" stroke-width="8"/>';drawing+=text(90,40,'Plasma')+text(640,40,'Target cell')+text(60,135,'TBG: reversible plasma carrier')+text(70,165,'Not thyroglobulin')+text(470,350,'Hormone transport','small');
 drawing+='<rect x="680" y="140" width="250" height="100" rx="15" fill="'+(stage===2?'#71603a':'#344854')+'"/>'+text(695,175,'Nuclear receptor')+text(695,210,'Gene regulation');
 if(stage===0){route=[[100,210],[200,210]];description='Free hormone binds a plasma carrier reversibly. Total = free + bound. This schematic does not assign a measured free fraction.';}
 if(stage===1){route=[[200,210],[300,300],[440,300],[560,300]];description='After dissociation, unbound hormone enters the target cell through transport machinery. Carrier TBG remains in plasma.';}
 if(stage===2){route=[[560,300],[560,300]];description='Intracellular availability, T4-to-T3 conversion and nuclear receptor action intervene before gene regulation. The highlighted nuclear panel is a separate mechanism view; nuclear transit is not animated.';drawing+=text(500,415,'T4 → T3: tissue conversion');}
 }
 const xy=point(route,f);$('drawing').innerHTML=drawing;$('cargo').setAttribute('cx',xy[0]);$('cargo').setAttribute('cy',xy[1]);out.textContent='Stage '+(stage+1)+' / '+stages+'. '+description;
}
function feedback(){const idx=Math.min(trace.length-1,Math.round(p*(trace.length-1))),r=trace[idx];const xx=t=>80+850*t/20,yy=v=>510-125*v;for(const [key,line,dot] of [['s','drive-line','drive-dot'],['h','hormone-line','hormone-dot']]){let d='';for(let i=0;i<=idx;i+=5)d+=(d?'L':'M')+xx(trace[i].t)+','+yy(trace[i][key]);if(idx%5)d+='L'+xx(r.t)+','+yy(r[key]);$(line).setAttribute('d',d);$(dot).setAttribute('cx',xx(r.t));$(dot).setAttribute('cy',yy(r[key]));}$('central-node').setAttribute('fill','hsl(43 45% '+(18+12*r.s)+'%)');$('gland-node').setAttribute('fill','hsl(190 45% '+(18+12*r.h)+'%)');const eq=Ch11.equilibrium(...params);out.textContent='τ = '+r.t.toFixed(2)+'; drive s = '+r.s.toFixed(6)+'; signal h = '+r.h.toFixed(6)+'. Equilibrium: s = '+eq.s.toFixed(6)+', h = '+eq.h.toFixed(6)+'. All values synthetic and normalized.';}
function render(){mode==='feedback'?feedback():follicle();}
play.addEventListener('click',()=>{if(playing)pause();else{if(p>=1)p=0;playing=true;last=null;play.textContent='Pause';play.setAttribute('aria-pressed','true');}});
$('replay').addEventListener('click',reset);phase.addEventListener('input',()=>{pause();p=Number(phase.value);render();});scenario.addEventListener('change',reset);reduced.addEventListener('change',pause);document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
for(const box of document.querySelectorAll('.scroll'))box.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){box.scrollLeft+=e.key==='ArrowRight'?70:-70;e.preventDefault();}});
function frame(now){if(playing){if(last!==null){p=Math.min(1,p+Math.min(.1,(now-last)/1000)*Number(speed.value)/18);phase.value=String(p);render();if(p===1)pause();}last=now;}requestAnimationFrame(frame);}
prepare();render();requestAnimationFrame(frame);
})();
