/* Original nonmetric scientific reconstructions. Same renderer for static/control views. */
'use strict';
(function(g){
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const T=(x,y,s,size=20,c='#e6eff9',anchor='start')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${c}" text-anchor="${anchor}">${esc(s)}</text>`;
const R=(x,y,w,h,c,rx=8)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${c}" stroke="#a6c4d8"/>`;
const P=(d,c='#b8ddeb',width=4,arrow=true)=>`<path d="${d}" fill="none" stroke="${c}" stroke-width="${width}" ${arrow?'marker-end="url(#arrow)"':''}/>`;
const C=(x,y,r=9,c='#ffc766')=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${c}" stroke="#fff"/>`;
const box=(x,y,w,h,a,c='#25435d')=>R(x,y,w,h,c)+a.map((s,i)=>T(x+12,y+28+i*25,s,18)).join('');
function wrap(title,w,h,a){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="${esc(title)}"><style>text{font-family:system-ui,sans-serif}</style><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#dcecf5"/></marker></defs><rect width="${w}" height="${h}" fill="#102032"/>${T(30,42,title,26)}${a}</svg>`;}
function barrier(i){
let a=T(35,82,'Sectional topology: exaggerated thicknesses; no measured permeability',17);
a+=R(45,110,880,120,'#603b50')+T(65,147,'Blood lumen / plasma',22);
a+=R(45,230,408,100,'#255977',0)+R(467,230,458,100,'#255977',0);
a+=T(65,272,'Nonfenestrated endothelial cell',19)+T(485,272,'Adjacent endothelial cell',19);
a+=P('M460 230V330','#ffc766',9,false)+T(55,365,'Tight junction between cells',17)+P('M320 353L454 298','#ffc766',2,false);
a+=R(45,380,880,48,'#6b617a',0)+T(530,410,'Basement membrane (matrix)',17);
a+=R(110,388,260,30,'#875467')+T(132,410,'Pericyte in matrix',16);
a+=R(45,450,310,54,'#477252')+R(385,450,260,54,'#477252')+R(675,450,250,54,'#477252');
a+=T(65,483,'Astrocyte endfeet: supporting processes',19)+T(55,555,'Brain interstitium: extracellular fluid around neural cells',21);
a+=P('M660 180V546','#7fe2de',5)+T(680,185,'Glucose / GLUT1',18)+T(680,210,'membrane transport',16);
a+=R(643,227,34,17,'#7fe2de',0)+R(643,320,34,17,'#7fe2de',0);
a+=P('M375 180V546','#dfb3ed',4)+T(390,310,'O₂ diffusion',17);
a+=P('M460 170V220','#ffc766',3)+P('M448 223H472','#ffc766',5,false);
a+=T(55,603,'Between-cell passage is restricted; transport through cells is a distinct route.',18);
a+=T(55,638,'Endfeet do not replace endothelial junctions. Plexus blood–CSF barrier differs.',17);
a+=T(55,679,'Marker: selected route position only; presentation time is not physiological time.',17);
if(i!==null){let y=180+366*i/160;a+=C(660,y);}
return wrap('Blood–brain barrier: name both sides of the wall',1000,720,a);
}
function plot(data,keys,top,labels){
let a=P(`M80 ${top}V${top+170}H930`,'#90a9bd',2,false),colors=['#79dccc','#efb56a','#d8a4ee'];
for(const t of [0,2,4,6,8])a+=T(80+t/8*850,top+197,String(t),16,'#dce8f5','middle');
for(const v of [0,.5,1])a+=T(65,top+170-v*150,v,16,'#dce8f5','end');
keys.forEach((fn,j)=>{a+=P(data.states.map((s,n)=>(n?'L':'M')+(80+s.time/8*850)+' '+(top+170-fn(s)*150)).join(' '),colors[j],3,false);a+=T(80+j*290,top-15,labels[j],17,colors[j]);});
return a+T(415,top+226,'Artificial model time (not seconds)',17);
}
function recycling(i,data){const s=data.states[i],values=Object.values(s.recycling),names=[['E: extracellular','glutamate'],['A: astrocyte','glutamate'],['Q: astrocyte','glutamine'],['N: returned','neuronal pool']];let a=T(30,82,'Closed equal-rate skeleton bookkeeping; physiological cycle is open',18);
names.forEach((n,j)=>{let x=35+j*245;a+=box(x,112,210,110,[...n,values[j].toFixed(6)]);if(j<3)a+=P(`M${x+210} 169H${x+242}`);a+=R(x,245,210,100,'#192f43')+R(x,345-values[j]*100,210,values[j]*100,'#477c78',0);});
a+=T(40,380,'E→A uptake; A→Q glutamine synthetase; Q→N lumped export/uptake/reconversion',17);
['Extracellular K⁺ at active site','Astrocyte channels / pumps','Coupled K⁺ redistribution'].forEach((label,j)=>{const x=40+j*310;a+=R(x,398,280,42,Math.min(2,Math.floor(i/54))===j?'#6c5b3a':'#253b50')+T(x+9,425,label,15);if(j<2)a+=P(`M${x+280} 420H${x+308}`,'#efb56a',2);});
a+=plot(data,[r=>r.recycling.extracellular_glu,r=>r.slower.extracellular_glu],475,['E: imposed k=1','E: imposed k=0.25']);
a+=P(`M${80+s.time/8*850} 475V645`,'#fff',2,false)+T(40,730,'K⁺ stages: qualitative order only. Selected artificial model t='+s.time.toFixed(2),16);
return wrap('Glial recycling: transfers conserve represented inventory',1000,760,a);}
function photo(i,data){const s=data.states[i],names=[['Light activates','rhodopsin'],['Transducin / PDE','cGMP decreases'],['CNG closes','hyperpolarization'],['Glutamate','release decreases']];let a=T(30,83,'Biological direction; numerical trace is a synthetic first-order response',18);
names.forEach((n,j)=>{let x=35+j*245;a+=box(x,125,210,85,n,s.photo.light?'#3b5868':'#25435d');if(j<3)a+=P(`M${x+210} 168H${x+242}`);});
a+=T(40,265,'u: chosen unit input; y: closure; 1−y: open fraction / assumed release proxy',18);
a+=T(40,310,`Selected artificial t=${s.time.toFixed(2)}; closure=${s.photo.closure.toFixed(6)}; open/release=${s.photo.open_fraction.toFixed(6)}`,18);
a+=plot(data,[r=>r.photo.closure,r=>r.photo.release_proxy],420,['Closure y','Open / release proxy']);
a+=P('M80 590H186.25V440H505V590H930','#d8a4ee',3,false)+T(680,405,'Input u (steps)',17,'#d8a4ee');
a+=P(`M${80+s.time/8*850} 420V590`,'#fff',2,false)+T(40,710,'No biochemical rate calibration, molecular trajectories or perceptual-brightness law.',18);
return wrap('Light response: closure rises, then recovers after the pulse',1000,760,a);}
function field(i,data){let a=T(35,82,"Top-view convention: person's left is drawn left; no anatomical lengths",18);const selected=Math.min(3,Math.floor(i/41));
a+=box(110,110,270,55,['Left visual hemifield'],'#664a71')+box(620,110,270,55,['Right visual hemifield'],'#356674');
a+=T(230,220,'Left eye',21)+T(630,220,'Right eye',21)+T(420,252,'Nose / midline',17);
a+=R(150,265,250,115,'#25435d')+R(600,265,250,115,'#25435d');
a+=T(170,305,'Temporal',17)+T(300,305,'Nasal',17)+T(610,305,'Nasal',17)+T(740,305,'Temporal',17);
a+=T(210,345,'T',23)+T(340,345,'N',23)+T(640,345,'N',23)+T(780,345,'T',23);
const coords=[{x:220,to:270,d:'M220 365L230 490L270 590'},{x:650,to:270,d:'M650 365L540 440L460 490L270 590'},{x:350,to:730,d:'M350 365L460 440L540 490L730 590'},{x:790,to:730,d:'M790 365L780 490L730 590'}];
data.routes.forEach((r,j)=>{let c=r.field==='right'?'#79dccc':'#d8a4ee',v=coords[j],from=r.field==='right'?755:245;a+=P(`M${from} 166L${v.x} 265`,c,j===selected?5:2,false);a+=P(v.d,c,j===selected?7:3);});
a+=T(420,420,'Optic chiasm',19)+T(425,535,'Nasal fibers cross;',17)+T(425,560,'temporal stay ipsilateral',17);
a+=box(165,600,235,70,['Left LGN','right-field information'])+box(615,600,235,70,['Right LGN','left-field information']);
a+=P('M280 671V718')+P('M730 671V718')+box(165,725,235,55,['Left visual cortex'])+box(615,725,235,55,['Right visual cortex']);
const r=data.routes[selected];a+=T(35,824,`Highlight: ${r.field} field → ${r.eye} eye ${r.retina} retina → ${r.hemisphere} hemisphere`,18);
return wrap('Partial optic decussation: preserve field and eye identity',1000,850,a);}
function conduction(i){let p=i/160,a=T(35,85,'Matched causal sequence; no millisecond, length or patient calibration',18);for(const [j,y]of [260,450].entries()){a+=T(35,y-75,j?'One possible demyelinated block':'Intact myelinated axon',21)+P(`M100 ${y}H900`,'#e0c494',6,false);for(const x of [120,360,600,840])a+=C(x,y,8,'#dcecf5');for(const x of [145,385,625])if(!(j&&x===385))a+=R(x,y-30,190,60,'#3f6d7e');if(j){a+=P('M480 446V365','#efb56a',4)+T(420,352,'Current leak',18);if(p>.5)a+=T(350,y+65,'Selected branch: no distal regeneration',17,'#efb56a');}a+=C(120+720*(j?Math.min(p,.5):p),y,13);}
a+=T(35,590,'Regeneration at exposed nodes; current spreads under intact internodes.',19)+T(35,623,'Myelin loss can slow or block conduction. New myelin cannot revive a dead axon.',17);
return wrap('Myelin supports node-to-node propagation',1000,650,a);}
function context(){let a=T(30,84,'A. Eye section: optical entry and layered wall (separate schematic scales)',20);
a+='<ellipse cx="260" cy="270" rx="190" ry="145" fill="#264257" stroke="#d8cbb1" stroke-width="12"/><path d="M300 133A190 145 0 0 1 300 407" fill="none" stroke="#bd7891" stroke-width="13"/><path d="M305 149A170 128 0 0 1 305 391" fill="none" stroke="#7bd0bd" stroke-width="8"/>';
a+='<ellipse cx="157" cy="270" rx="28" ry="62" fill="#b9dfe3" stroke="#fff"/>';
a+=P('M25 270H130','#ffd27a',4)+T(18,244,'Light',18)+T(94,180,'Cornea',17)+P('M118 185L84 216','#aaa',2,false)+T(130,366,'Lens',18)+P('M158 350V333','#aaa',2,false);
a+=T(220,205,'Vitreous',18)+P('M440 280L540 305','#d8cbb1',17,false)+T(442,340,'Optic nerve',17);
a+=T(320,460,'Sclera / choroid / retina',18)+P('M360 437L405 367','#aaa',2,false);
a+=T(620,124,'Retinal layer order (separate scale)',20);
a+=box(650,160,215,58,['Ganglion cells'])+box(650,245,215,58,['Bipolar pathways'])+box(650,330,215,58,['Rods / cones'])+box(650,415,215,50,['RPE'],'#604856');
a+=P('M610 163V390','#ffd27a',4)+T(560,135,'Light',18)+P('M903 385V170','#79dccc',4)+T(918,230,'Signal',18)+T(918,255,'toward',17)+T(918,280,'ganglion',17);
a+=T(30,520,'B. Ear connectivity: air → membrane/ossicles → cochlear fluid → hair-cell signal',20);
const ear=[['Pinna / canal'],['Tympanic','membrane'],['Ossicles:','malleus/incus/stapes'],['Oval window','cochlea']];ear.forEach((v,j)=>{a+=box(30+j*292,555,250,80,v);if(j<3)a+=P(`M${280+j*292} 595H${320+j*292}`);});
a+=T(35,676,'Vestibular labyrinth: semicircular ducts (rotation); utricle/saccule (linear/tilt)',18);
a+=T(35,723,'C. Cochlear section (new scale, not a continuous zoom)',20);
a+=R(40,750,640,42,'#34475e',0)+T(55,778,'Scala vestibuli: perilymph',18);
a+=P('M40 796H680','#b0b4cd',3,false);
a+=R(40,800,640,120,'#3e6570',0)+T(55,826,'Scala media: endolymph above apical seal',18);
a+=R(430,851,250,69,'#243b53',0);
a+=R(490,851,48,69,'#677882',0)+R(582,851,48,69,'#677882',0);
a+=R(547,851,28,69,'#d1b377',0);
a+=P('M551 849V823 M560 849V819 M569 849V815','#efb56a',3,false);
a+=P('M430 850H680','#b4e5ce',5,false);
a+=P('M40 922H680','#efb56a',4,false);
a+=R(40,927,640,42,'#34475e',0)+T(55,954,'Scala tympani: perilymph',18);
a+=T(55,878,'Low-K⁺ basolateral fluid',18)+T(55,905,'(perilymph-like; within the organ)',16)+P('M365 889L475 889','#aaa',2,false);
a+=T(730,778,'Organ of Corti on basilar membrane',18)+P('M720 785L563 892','#aaa',2,false);
a+=T(730,821,'Apical seal / reticular lamina',18)+T(730,845,'Hair/support-cell tight junctions',16)+P('M718 827L644 850','#b4e5ce',2,false);
a+=T(730,891,'Supporting-cell context',18)+P('M719 896L618 901','#aaa',2,false);
a+=T(730,942,'Basilar membrane below the organ',18)+P('M719 936L670 922','#efb56a',2,false);
a+=T(40,1010,'Separate fluid compartments and cell surfaces; no metric dimensions or oscillation timing.',18);
return wrap('Separate anatomical contexts: optics, retinal layers and ear compartments',1200,1040,a);}
// Numerical cross-check API; controls still consume the saved Python table.
function boundedNumber(value,lower,upper,name){
if(typeof value!=='number')throw TypeError(name+' must be a real number');
if(!(value>=lower&&value<=upper)||!Number.isFinite(value))throw RangeError(name+' outside finite domain');
return value;}
function compensatedSum(values){let sum=0,c=0;for(const x of values){const t=sum+x;c+=Math.abs(sum)>=Math.abs(x)?(sum-t)+x:(x-t)+sum;sum=t;}return sum+c;}
function recyclingAmounts(time,rate=1,amount=1){
const t=boundedNumber(time,0,100,'time'),k=boundedNumber(rate,0,100,'rate'),total=boundedNumber(amount,0,1e6,'amount');
if(total>0&&total<1e-100)throw RangeError('positive amount must be at least 1e-100 for relative conservation');
const x=k*t,e=Math.exp(-x),a=x*e,q=x*x*e/2,n=Math.max(0,1-compensatedSum([e,a,q]));
const pools=[e,a,q,n].map(p=>total*p),balance=compensatedSum(pools);
if(pools.some(v=>!Number.isFinite(v)||v<0||v>total)||Math.abs(balance-total)>1e-12*Math.max(Math.abs(balance),total))throw RangeError('pool output cannot preserve relative conservation');
return Object.fromEntries(['extracellular_glu','astrocyte_glu','astrocyte_gln','returned_neuronal'].map((key,i)=>[key,pools[i]]));}
function render(mode,i,data){if(!Number.isInteger(i)||i<0||i>160)throw Error('Saved index must be0..160');if(!data||data.states.length!==161)throw Error('Expected161 shared states');return mode==='barrier'?barrier(i):mode==='recycling'?recycling(i,data):mode==='photo'?photo(i,data):mode==='field'?field(i,data):mode==='conduction'?conduction(i):(()=>{throw Error('Unknown mode')})();}
g.Ch25Render={boundedNumber,recyclingAmounts,barrier,recycling,photo,field,conduction,context,render,wrap,T,R,P,C,box};
if(typeof module!=='undefined')module.exports=g.Ch25Render;
})(globalThis);
