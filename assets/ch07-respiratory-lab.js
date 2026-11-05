'use strict';
// Equations shared with code/ch07_respiration.py. No external requests or dependencies.
(function () {
  const $ = id => document.getElementById(id);
  const requested = new URLSearchParams(location.search).get('view');
  const view = ['mechanics','barrier','binding'].includes(requested) ? requested : 'mechanics';
  $(view).hidden = false;
  const titles = {mechanics:'Ventilation: one volume, flow and pressure state',barrier:'Airways and the alveolar gas barrier',binding:'Hemoglobin: equilibrium affinity explorer'};
  $('heading').textContent = titles[view];
  let progress = 0, playing = false, last = null, frame = null;
  const duration = view === 'mechanics' ? 4 : 12;
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  function mechanics(t, R=2, C=.1) {
    const angle = 2*Math.PI*((t/4)%1), v=.25*(1-Math.cos(angle));
    const flow=.5*Math.PI/4*Math.sin(angle), alveolar=-R*flow, recoil=5+v/C;
    return {volume:2.5+v,flow,alveolar,pleural:alveolar-recoil,transpulmonary:recoil};
  }
  function saturation(p,p50=26,n=2.7) { return p === 0 ? 0 : 1/(1+(p50/p)**n); }
  // Exposed pure functions facilitate parity checks; UI state remains private.
  window.ch07Model = Object.freeze({mechanics,saturation});
  function path(points) {return points.map((p,i)=>(i?'L':'M')+p.map(x=>x.toFixed(3)).join(',')).join(' ');}
  function poly(samples,fn,x,y) {return path(Array.from({length:samples+1},(_,i)=>[x(i/samples),y(fn(i/samples))]));}
  function pause() {
    playing=false;last=null;if(frame!==null)cancelAnimationFrame(frame);frame=null;
    $('play').textContent='Play';$('play').setAttribute('aria-pressed','false');$('state').textContent='Paused';
  }
  function renderMechanics() {
    const R=+$('resistance').value,C=+$('compliance').value,s=mechanics(4*progress,R,C);
    $('rvalue').textContent=R.toFixed(1)+' cmH₂O·s/L';$('cvalue').textContent=C.toFixed(2)+' L/cmH₂O';
    const plots=[{name:'Volume (L)',lo:2.5,hi:3,y:70,key:'volume',color:'#9fd79c'},
      {name:'Inward flow (L/s)',lo:-.5,hi:.5,y:230,key:'flow',color:'#82d8ff'},
      {name:'Pressure (cmH₂O)',lo:-17,hi:3,y:400,key:'alveolar',color:'#f3a88f'}];
    $('mech-plots').innerHTML=plots.map(d=>{
      const y=v=>d.y+110*(d.hi-v)/(d.hi-d.lo),x=p=>410+350*p;
      return `<text x="365" y="${d.y-13}">${d.name}</text><line class="axis" x1="410" x2="760" y1="${d.y+110}" y2="${d.y+110}"/><text class="small" x="365" y="${d.y+8}">${d.hi}</text><text class="small" x="365" y="${d.y+115}">${d.lo}</text><path fill="none" stroke="${d.color}" stroke-width="3" d="${poly(160,p=>mechanics(4*p,R,C)[d.key],x,y)}"/>`+(d.key==='alveolar'?`<path fill="none" stroke="#cda9eb" stroke-width="3" d="${poly(160,p=>mechanics(4*p,R,C).pleural,x,y)}"/><text class="small" x="430" y="550">Alveolar: coral · Pleural: violet</text>`:'');
    }).join('');
    $('time-cursor').setAttribute('x1',410+350*progress);$('time-cursor').setAttribute('x2',410+350*progress);
    const expansion=(s.volume-2.5)/.5;
    $('diaphragm').setAttribute('d',`M40 ${330+25*expansion}Q170 ${270+80*expansion} 300 ${330+25*expansion}`);
    $('lung-left').setAttribute('transform',`translate(${ -5*expansion} 0) scale(${1+.04*expansion} ${1+.1*expansion})`);
    $('lung-right').setAttribute('transform',`translate(${ -5*expansion} 0) scale(${1+.04*expansion} ${1+.1*expansion})`);
    $('ribs').setAttribute('transform',`translate(${-7*expansion} 0) scale(${1+.05*expansion} 1)`);
    const zero=Math.abs(s.flow)<1e-9;
    $('phase-label').textContent=zero?(expansion>.5?'Maximum-volume endpoint':'Baseline endpoint'):(s.flow>0?'Inspiration: volume rising':'Expiration: volume falling');
    $('flow-direction').textContent=zero?'No bulk airflow':(s.flow>0?'Airway opening → alveolus':'Alveolus → airway opening');
    $('readout').textContent=`t = ${(4*progress).toFixed(2)} s; V = ${s.volume.toFixed(3)} L; q = ${s.flow.toFixed(3)} L/s; P_alv = ${s.alveolar.toFixed(3)} cmH₂O; P_pl = ${s.pleural.toFixed(3)} cmH₂O; P_L = ${s.transpulmonary.toFixed(3)} cmH₂O. ${zero?'Zero flow does not require zero pleural pressure.':''}`;
  }
  function renderBarrier() {
    $('mucus').setAttribute('cx',480-400*progress);
    const transfer=Math.max(0,Math.min(1,(progress-.25)/.75));
    $('oxygen').setAttribute('cy',300+250*transfer);$('carbon').setAttribute('cy',550-250*transfer);
    $('redcell').setAttribute('cx',150+300*progress);
    $('readout').textContent=progress<.25?'Presentation stage: conducting clearance and a change of anatomical scale. Mucus is transported toward the pharynx; alveoli have a different epithelium.':'Presentation stage: oxygen moves from alveolar air across the permeable layered barrier into blood; carbon dioxide moves oppositely under its own gradient. Red cells move along the capillary, not across its wall. Progress and speed are explanatory choices, not physiological time.';
  }
  function renderBinding() {
    const p=120*progress,p50=+$('p50').value,x=p=>80+620*p/120,y=s=>380-340*s;
    $('p50value').textContent=p50.toFixed(1)+' mmHg';
    let markup='';
    for(let i=0;i<=4;i++){const px=x(i*30);markup+=`<line class="grid" x1="${px}" x2="${px}" y1="40" y2="380"/><text x="${px-10}" y="410">${i*30}</text>`;}
    for(let i=0;i<=4;i++){const py=y(i/4);markup+=`<line class="grid" x1="80" x2="700" y1="${py}" y2="${py}"/><text x="30" y="${py+5}">${i*25}%</text>`;}
    markup+='<text x="80" y="25">Equilibrium saturation</text><text x="405" y="435">Oxygen partial pressure p (mmHg)</text>';
    for(const [half,n,color] of [[26,2.7,'#82d8ff'],[p50,2.7,'#f3a88f'],[3,1,'#a9db9d']])markup+=`<path fill="none" stroke="${color}" stroke-width="3" d="${poly(240,u=>saturation(120*u,half,n),u=>x(120*u),y)}"/>`;
    $('binding-plot').innerHTML=markup;
    $('pressure-cursor').setAttribute('x1',x(p));$('pressure-cursor').setAttribute('x2',x(p));
    for(const [id,half]of [['baseline-dot',26],['compare-dot',p50]]){$(id).setAttribute('cx',x(p));$(id).setAttribute('cy',y(saturation(p,half)));}
    const sb=saturation(p),sc=saturation(p,p50),sm=saturation(p,3,1);
    $('hemes').innerHTML=Array.from({length:4},(_,i)=>`<circle cx="${595+(i%2)*55}" cy="${450+Math.floor(i/2)*28}" r="11" fill="#82d8ff" fill-opacity="${.12+.88*sb}" stroke="#e1f4ff"/>`).join('');
    $('readout').textContent=`Pressure parameter p = ${p.toFixed(1)} mmHg. Baseline Hb ${(100*sb).toFixed(2)}%; comparison Hb ${(100*sc).toFixed(2)}%; illustrative myoglobin ${(100*sm).toFixed(2)}%. Mean baseline occupancy = ${(4*sb).toFixed(2)} oxygen molecules per tetramer. Presentation progress is not reaction time.`;
  }
  function render(){ $('seek').value=String(Math.round(progress*1000)); if(view==='mechanics')renderMechanics();else if(view==='barrier')renderBarrier();else renderBinding(); }
  function tick(now){if(!playing)return;if(last!==null)progress=Math.min(1,progress+(now-last)/1000*+$('speed').value/duration);last=now;render();if(progress>=1){pause();return;}frame=requestAnimationFrame(tick);}
  $('play').addEventListener('click',()=>{if(playing){pause();return;}if(progress>=1)progress=0;playing=true;last=null;$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');$('state').textContent='Playing';frame=requestAnimationFrame(tick);});
  $('replay').addEventListener('click',()=>{pause();progress=0;render();});
  $('step').addEventListener('click',()=>{pause();progress=Math.min(1,progress+.025);render();});
  $('seek').addEventListener('input',()=>{pause();progress=+$('seek').value/1000;render();});
  for(const id of ['resistance','compliance','p50'])$(id).addEventListener('input',()=>{pause();render();});
  $('speed').addEventListener('change',pause);
  document.querySelectorAll('[data-pressure]').forEach(b=>b.addEventListener('click',()=>{pause();progress=+b.dataset.pressure/120;render();}));
  media.addEventListener('change',pause);document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  $('cilia').innerHTML=Array.from({length:36},(_,i)=>`<path d="M${55+i*12} 168l-5 -17" stroke="#a1c6d0" stroke-width="2"/>`).join('');
  render();
})();
