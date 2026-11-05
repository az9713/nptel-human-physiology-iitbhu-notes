/* One mechanical state drives volume, pressure, flow and valve indicators.
 * ECG is explicitly a separate prescribed timing annotation on the same clock.
 */
(function (root) {
  'use strict';
  const clamp = x => Math.max(0, Math.min(1, x));
  function cycle(x, stroke = 70, rout = .04) {
    if (![x, stroke, rout].every(Number.isFinite) || x < 0 || x > 1 ||
        stroke < 0 || stroke > 100 || rout <= 0) throw Error('Invalid model input');
    let v, p, qi = 0, qo = 0, phase;
    if (x < .4) {
      const u = x / .4;
      v = 50 + stroke * (1 - Math.cos(Math.PI * u)) / 2;
      qi = stroke * Math.PI * Math.sin(Math.PI * u) / (.64);
      p = 10 - .01 * qi; phase = 'filling';
    } else if (x < .5) {
      v = 50 + stroke; p = 10 + 70 * (x - .4) / .1;
      phase = 'isovolumic contraction';
    } else if (x < .8) {
      const u = (x - .5) / .3;
      v = 50 + stroke * (1 + Math.cos(Math.PI * u)) / 2;
      qo = stroke * Math.PI * Math.sin(Math.PI * u) / (.48);
      p = 80 + rout * qo; phase = 'ejection';
    } else {
      v = 50; p = 80 - 70 * (x - .8) / .2;
      phase = 'isovolumic relaxation';
    }
    return { x, v, p, qi, qo, phase, inlet: qi > 1e-8, outlet: qo > 1e-8 };
  }
  function regional(factor = 1) {
    if (!Number.isFinite(factor) || factor <= 0) throw Error('Invalid factor');
    const rg = 86 / 1.2, ra = 86 / .3, rh = 4 / 1.5 * factor;
    const rp = 1 / (1 / rg + 1 / ra), out = 90 / (rp + rh);
    const p = 5 + rh * out;
    return { p, gut: (95 - p) / rg, hepatic: (95 - p) / ra,
      out, kidney: 1, other: 2.75, total: 3.75 + out };
  }
  function ecg(x) {
    const g = (mu, sigma, a) => a * Math.exp(-0.5 * (((x - mu) / sigma) ** 2));
    return g(.31,.023,.12) - g(.402,.006,.16) + g(.42,.006,1) -
      g(.44,.008,.25) + g(.77,.043,.27);
  }
  root.Ch05 = { cycle, regional, ecg };
  if (typeof document === 'undefined') return;
  const q = id => document.getElementById(id);
  const requested = new URLSearchParams(location.search).get('view');
  const mode = ['heart','sync','regional'].includes(requested) ? requested : 'heart';
  q('heading').textContent = {heart:'Four chambers, pressure-driven left-sided valves',sync:'One clock, different electrical and mechanical quantities',regional:'Parallel regional beds and a portal series path'}[mode];
  q('stroke-label').hidden = q('resistance-label').hidden = mode === 'regional';
  q('hepatic-label').hidden = mode !== 'regional';
  q('alternative').textContent = mode === 'regional' ? 'Steady network: gut portal outflow and hepatic arterial inflow meet at the liver inlet. Their sum exits through hepatic veins; other regional branches return separately. Changing hepatic outflow resistance changes their shared inlet pressure and both inflows together. Progress reveals routes, not physiological transit.' : mode === 'sync' ? 'The electrical trace is synthetic, with P/QRS/T timing annotations. Ventricular activation precedes the selected pressure rise; mechanical filling/ejection comes from the prescribed cycle. Pressure, volume and valve state are computed together. No ion-channel or ECG forward model is solved.' : 'The chamber map is a topological section: right heart is shown on the left, left heart on the right. Lungs connect right-ventricular outflow to left-atrial inflow; systemic tissues connect left-ventricular outflow to right-atrial inflow. Only left-ventricular valve motion is modeled, and markers cross only designated valve apertures.';
  const txt = (x,y,t,small=false,extra='') => `<text x="${x}" y="${y}" ${small?'class="small"':''} ${extra}>${t}</text>`;
  const line = (d,c='#8fb5ca',w=3,extra='') => `<path d="${d}" fill="none" stroke="${c}" stroke-width="${w}" ${extra}/>`;
  const rect = (x,y,w,h,c,extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${c}" stroke="#a6bbc7" stroke-width="2" ${extra}/>`;
  const dot = (x,y,c='#e8bf68') => `<circle cx="${x}" cy="${y}" r="7" fill="${c}" stroke="#fff" stroke-width="1"/>`;
  function valve(x,y,open,horizontal=false) {
    const gap = open ? 18 : 0;
    if (horizontal) return line(`M${x-20} ${y-20} L${x+8} ${y-gap} M${x-20} ${y+20} L${x+8} ${y+gap}`,'#edce78',5);
    return line(`M${x-20} ${y-20} L${x-gap} ${y+8} M${x+20} ${y-20} L${x+gap} ${y+8}`,'#edce78',5);
  }
  function heart(s) {
    let h=txt(25,28,'Sectional route abstraction — anatomical right is viewer-left') +
      txt(25,53,'Four chambers; numerical pressure/volume and valve motion model the left ventricle only.',true);
    h += rect(75,105,180,100,'#264b66') + rect(75,270,180,125,'#264b66') +
      rect(440,105,180,100,'#663d48') + rect(440,270,180,125,'#663d48');
    // Chamber connectors have explicit open necks; no marker crosses an intact wall.
    h += '<rect x="145" y="198" width="40" height="80" fill="#264b66"/>' +
      '<rect x="510" y="198" width="40" height="80" fill="#663d48"/>';
    h += txt(95,146,'Right atrium') + txt(95,316,'Right ventricle') +
      txt(455,146,'Left atrium') + txt(455,316,'Left ventricle');
    h += line('M255 335 H325 V98','#8abde0',8) +
      line('M370 82 H530 V105','#df99a3',8) +
      rect(280,65,90,34,'#3e5664') + txt(290,89,'Lungs',true) +
      line('M620 335 H708 V500 H600','#df99a3',8) +
      line('M420 500 H30 V155 H75','#8abde0',8) +
      rect(420,475,180,50,'#3e5664') + txt(435,505,'Systemic tissues',true);
    h += txt(25,565,'Blue = relatively oxygen-poor; rose = relatively oxygen-rich. Colors are explanatory.',true);
    h += line('M620 335 H708','#df99a3',10);
    h += '<rect x="613" y="316" width="18" height="38" fill="#663d48"/>';
    h += valve(530,235,s.inlet) + valve(645,335,s.outlet,true);
    h += txt(444,246,'Mitral',true) + txt(641,379,'Aortic',true) +
      txt(95,244,'Tricuspid',true) + txt(272,359,'Pulmonary',true);
    h += txt(427,420,`V = ${s.v.toFixed(2)} mL; P = ${s.p.toFixed(2)} mmHg`,true) +
      txt(427,447,`LA reservoir 10; aortic reservoir 80 mmHg`,true);
    if(s.inlet) {const u=s.x/.4; h+=dot(530,205+65*u);}
    if(s.outlet) {const u=(s.x-.5)/.3;h+=dot(620+80*u,335);}
    return h;
  }
  function path(fn,x0,y0,w,h,scale) {
    return Array.from({length:301},(_,i)=>`${i?'L':'M'}${(x0+w*i/300).toFixed(2)} ${(y0-h*fn(i/300)/scale).toFixed(2)}`).join(' ');
  }
  function sync(s,stroke,rout) {
    let h=txt(25,28,'Conduction annotation + synthetic lead + conserved mechanical cycle') +
      txt(25,52,'No measured ECG or ion-channel fit; all mechanical indicators use the same state.',true);
    h+=rect(25,83,210,180,'#213c4c')+txt(44,111,'Conduction locations',true);
    const stage=s.x<.29?'Diastolic interval':s.x<.36?'SA / atria':s.x<.40?'AV delay':s.x<.47?'His / Purkinje':'Ventricular tissue';
    h+=line('M62 140 L130 169 L130 210 L90 241 M130 210 L184 241','#739aaf',5) +
      dot(62,140,s.x>=.29&&s.x<.36?'#efc368':'#54768b')+
      dot(130,169,s.x>=.36&&s.x<.4?'#efc368':'#54768b')+
      txt(82,145,'SA',true)+txt(148,172,'AV',true)+txt(139,207,'His',true)+txt(44,286,stage,true);
    const x0=300,w=420,base=150;
    h+=txt(x0,85,'Synthetic lead signal (mV)',true)+line(`M${x0} ${base} H720`,'#617f91',1)+
      line(path(ecg,x0,base,w,50,1),'#efce7c',2)+txt(421,110,'P',true)+txt(467,91,'QRS',true)+txt(621,112,'T',true);
    h+=txt(x0,208,'Ventricular pressure (mmHg)',true)+
      line(path(x=>cycle(x,stroke,rout).p,x0,310,w,85,130),'#e394a2',2)+
      line(`M${x0} ${310-85*80/130} H720`,'#6e8fa5',1)+txt(302,329,'0',true)+txt(694,329,'0.8 s',true)+
      txt(x0,365,'Ventricular volume (mL)',true)+
      line(path(x=>cycle(x,stroke,rout).v,x0,470,w,90,150),'#8acfe5',2);
    const cursor=x0+w*s.x;
    h+=line(`M${cursor} 90 V480`,'#dbe8ed',1,'stroke-dasharray="4 4"')+
      dot(cursor,base-50*ecg(s.x)) + dot(cursor,310-85*s.p/130) +dot(cursor,470-90*s.v/150)+
      txt(27,337,'Mechanical phase',true)+txt(27,364,s.phase,true)+
      txt(27,399,`Inlet ${s.inlet?'open':'closed'}`,true)+txt(27,425,`Outlet ${s.outlet?'open':'closed'}`,true)+
      txt(27,455,`Qin ${s.qi.toFixed(1)} mL/s`,true)+txt(27,480,`Qout ${s.qo.toFixed(1)} mL/s`,true);
    return h;
  }
  function regionView(p,factor) {
    const r=regional(factor);
    let h=txt(25,28,'Steady regional network: branch topology, not literal anatomical geometry')+
      txt(25,53,'Fixed reservoirs: arterial 95 mmHg, venous 5 mmHg. All values synthetic.',true);
    h+=rect(25,105,125,55,'#653b46')+txt(39,138,'Arterial')+
      rect(605,105,125,55,'#25495e')+txt(618,138,'Venous')+
      rect(287,95,180,65,'#344f5b')+txt(313,133,'Other tissues')+
      rect(287,205,180,65,'#344f5b')+txt(325,245,'Kidneys')+
      rect(220,335,160,65,'#534e41')+txt(236,375,'Gut / spleen')+
      rect(448,335,155,65,'#614b53')+txt(483,375,'Liver');
    const routes=[['M150 130 H287','#e09aa5'],['M467 130 H605','#8abed8'],['M150 130 H182 V237 H287','#e09aa5'],['M467 237 H572 V130 H605','#8abed8'],['M150 130 H182 V367 H220','#e09aa5'],['M380 367 H448','#adabc8'],['M150 130 H195 V306 H523 V335','#e09aa5'],['M603 367 H667 V160','#8abed8']];
    routes.forEach(([d,c],i)=>h+=line(d,c,4,`opacity="${p>i/9?.95:.3}"`));
    h+=txt(382,354,'Portal',true)+txt(382,287,'Hepatic artery',true)+txt(612,408,'Hepatic veins',true)+
      txt(25,447,`Liver inlet ${r.p.toFixed(3)} mmHg; portal ${r.gut.toFixed(3)} + artery ${r.hepatic.toFixed(3)} = out ${r.out.toFixed(3)} L/min`,true)+
      txt(25,478,`Other ${r.other.toFixed(3)} + kidney ${r.kidney.toFixed(3)} + liver out ${r.out.toFixed(3)} = total ${r.total.toFixed(3)} L/min`,true);
    return h;
  }
  let progress=0,running=false,last=null,frame=null;
  const params=()=>({stroke:Number(q('stroke').value),rout:Number(q('resistance').value),factor:Number(q('hepatic').value)});
  function pause(){running=false;last=null;if(frame!==null)cancelAnimationFrame(frame);frame=null;q('play').textContent='Play';q('play').setAttribute('aria-pressed','false');}
  function render(){
    const par=params(),s=cycle(progress,par.stroke,par.rout);
    q('scene').setAttribute('viewBox',mode==='heart'?'0 0 760 600':'0 0 760 520');
    q('drawing').innerHTML=mode==='heart'?heart(s):mode==='sync'?sync(s,par.stroke,par.rout):regionView(progress,par.factor);
    q('seek').value=String(Math.round(progress*1000));
    const message=mode==='regional'?'Route reveal only. At every progress value, the same steady junction calculation conserves flow. Altered downstream resistance changes liver inlet pressure and both incoming flows.':
      `Phase ${(progress*100).toFixed(1)}% (${(progress*.8).toFixed(3)} s): ${s.phase}. V ${s.v.toFixed(3)} mL; P ${s.p.toFixed(3)} mmHg; inlet ${s.inlet?'open':'closed'}; outlet ${s.outlet?'open':'closed'}. Flow Qin ${s.qi.toFixed(3)}, Qout ${s.qo.toFixed(3)} mL/s. Prescribed SV ${par.stroke} mL; CO ${(75*par.stroke/1000).toFixed(3)} L/min. Changing resistance changes required pressure, not the prescribed stroke volume.`;
    if(q('state').textContent!==message)q('state').textContent=message;
  }
  function tick(now){if(!running)return;if(last!==null)progress=clamp(progress+Math.min(now-last,100)*Number(q('speed').value)/12000);last=now;render();if(progress>=1)pause();else frame=requestAnimationFrame(tick);}
  function start(){if(progress>=1)progress=0;running=true;last=null;q('play').textContent='Pause';q('play').setAttribute('aria-pressed','true');frame=requestAnimationFrame(tick);}
  q('play').addEventListener('click',()=>running?pause():start());
  q('replay').addEventListener('click',()=>{pause();progress=0;render();start();});
  q('back').addEventListener('click',()=>{pause();progress=clamp(progress-.1);render();});
  q('step').addEventListener('click',()=>{pause();progress=clamp(progress+.1);render();});
  q('seek').addEventListener('input',()=>{pause();progress=Number(q('seek').value)/1000;render();});
  q('speed').addEventListener('change',()=>{pause();render();});
  ['stroke','resistance','hepatic'].forEach(id=>q(id).addEventListener('change',()=>{pause();progress=0;render();}));
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',()=>{pause();render();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  root.addEventListener('beforeprint',()=>{pause();progress=.45;render();});
  root.ch05Controller={seek(x){pause();progress=clamp(x);render();},getState(){return {progress,running,mode,...cycle(progress,params().stroke,params().rout)};}};
  render();
})(typeof window!=='undefined'?window:globalThis);
