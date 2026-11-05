/* Original schematic states and positive compartment model. No measured kinetics. */
(function (root) {
  'use strict';
  const clamp = p => Math.max(0, Math.min(1, p));
  const lerp = (a, b, p) => a + (b - a) * p;
  function route(points, p) {
    p = clamp(p);
    const z = p * (points.length - 1);
    const i = Math.min(points.length - 2, Math.floor(z));
    const f = z - i;
    return {x: lerp(points[i][0], points[i + 1][0], f),
      y: lerp(points[i][1], points[i + 1][1], f), segment: i};
  }
  function protein(p) {
    const point = route([[90,180],[170,180],[250,180],[360,180],
      [430,230],[510,300],[600,300],[710,300]], p);
    return {...point, p: clamp(p), identity: p < 1 / 7 ? 'protein' :
      p < 3.5 / 7 ? 'di/tripeptide' : 'amino acids',
      compartment: point.x < 250 ? 'lumen' : point.x < 600 ?
        'enterocyte' : 'interstitium / blood route',
      stage: Math.min(7, Math.floor(clamp(p) * 8))};
  }
  function lipid(p) {
    const point = route([[90,180],[140,180],[180,180],[250,180],
      [350,180],[440,250],[560,300],[600,300],[730,320],
      [820,320],[880,320]], p);
    const z = clamp(p) * 10;
    return {...point, p: clamp(p), identity: z < 1 ? 'TAG droplet' :
      z < 2 ? 'hydrolysis products' : z < 3 ? 'mixed-aggregate cargo' :
      z < 5 ? 'molecular cargo' : 'chylomicron',
      vesicle: z >= 5 && z < 7,
      compartment: point.x < 250 ? 'lumen' : point.x < 600 ?
        'enterocyte' : point.x < 820 ? 'interstitium' : 'lacteal',
      stage: Math.min(10, Math.floor(z))};
  }
  function evolve(state, rates, time) {
    if (state.length !== 4 || rates.length !== 3 ||
      [...state, ...rates, time].some(x => !Number.isFinite(x) || x < 0)) {
      throw new Error('Finite nonnegative pools, rates and time required');
    }
    let value = [...state];
    const inventory = value.reduce((sum, amount) => sum + amount, 0);
    if (!Number.isFinite(inventory)) {
      throw new Error('Total pool amount exceeds finite range');
    }
    const q = Math.max(...rates);
    if (!q || !time) return value;
    if (q * time > 10000) throw new Error('Teaching range exceeded');
    const steps = Math.max(1, Math.ceil(q * time));
    const z = q * time / steps;
    const k = rates.map(x => x / q);
    for (let j = 0; j < steps; j++) {
      let term = [...value], weight = Math.exp(-z), sum = weight;
      let result = term.map(x => x * weight);
      for (let order = 1; order < 100; order++) {
        const d = k.map((x, i) => x * term[i]);
        term = [term[0]-d[0],term[1]+d[0]-d[1],
          term[2]+d[1]-d[2],term[3]+d[2]];
        weight *= z / order;
        sum += weight;
        result = result.map((x, i) => x + weight * term[i]);
        if (weight < 1e-16) break;
      }
      const tail = Math.max(0, 1-sum);
      value = result.map((x, i) => x + tail * term[i]);
      if (value.some(x => !Number.isFinite(x))) {
        throw new Error('Propagation exceeds finite range');
      }
    }
    return value;
  }
  const proteinPhases = [
    'Protein in lumen: acid unfolding and protease cleavage are distinct.',
    'Luminal proteolysis produces amino acids and di/tripeptides.',
    'Peptide and H+ cross the apical PEPT1 opening.',
    'Imported peptide reaches cytosol; brush-border and intracellular enzymes differ.',
    'Intracellular peptide hydrolysis releases amino acids.',
    'Amino acids approach the basolateral exit route.',
    'Amino acids cross basolateral transport into interstitium.',
    'Intestinal capillaries receive amino acids for portal delivery to liver.'
  ];
  const lipidPhases = [
    'Emulsified TAG droplet: physical subdivision precedes molecular uptake.',
    'Lipase with colipase generates fatty acids and MAG at an interface.',
    'Mixed aggregates solubilize products; they are not bilayer vesicles.',
    'Cargo molecules cross apically; the luminal aggregate does not enter intact.',
    'Intracellular processing: long-chain cargo supports ER TAG re-esterification.',
    'ApoB-48-associated chylomicron assembly and secretory trafficking.',
    'A monolayer lipoprotein particle travels inside a bilayer secretory vesicle.',
    'Vesicle fuses at the enterocyte basolateral membrane; cargo is released.',
    'Released chylomicron moves through interstitial tissue, outside the enterocyte.',
    'Chylomicron enters a separate lacteal boundary; no vesicle–vessel fusion.',
    'Lymph drains through thoracic duct to systemic venous blood.'
  ];
  const api = {protein, lipid, evolve, route};
  root.Ch13 = api;
  if (typeof module !== 'undefined') module.exports = api;
  if (typeof document === 'undefined') return;
  const mode = document.body.dataset.mode;
  if (!['protein','lipid','failure'].includes(mode)) return;
  const $ = id => document.getElementById(id);
  const svg = $('scene');
  const ns = 'http://www.w3.org/2000/svg';
  const add = (name, attrs, content) => {
    const el = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
    if (content) el.textContent = content;
    svg.appendChild(el);
    return el;
  };
  const text = (x,y,s,size=17,fill='#e8edf3') => add('text',
    {x,y,'font-size':size,fill},s);
  const line = (x1,y1,x2,y2,color='#7897ac',width=3) => add('line',
    {x1,y1,x2,y2,stroke:color,'stroke-width':width});
  const circle = (x,y,r,fill,stroke='none',width=2) => add('circle',
    {cx:x,cy:y,r,fill,stroke,'stroke-width':width});
  function boundaries() {
    add('rect',{x:0,y:75,width:250,height:310,fill:'#172536'});
    add('rect',{x:250,y:75,width:350,height:310,fill:'#17342f'});
    add('rect',{x:600,y:75,width:220,height:310,fill:'#282a3a'});
    add('rect',{x:820,y:75,width:120,height:310,fill:'#153b42'});
    text(60,100,'LUMEN');text(340,100,'ENTEROCYTE');
    text(630,100,'INTERSTITIUM');text(835,100,mode==='lipid'?'LYMPH':'TISSUE',15);
    // Membranes have actual gaps, not a painted-over impermeable wall.
    for (const x of [247,253]) {
      line(x,110,x,163,'#81cfbf');line(x,197,x,380,'#81cfbf');
    }
    for (const x of [597,603]) {
      line(x,110,x,277,'#81cfbf');line(x,323,x,380,'#81cfbf');
    }
    text(212,135,'apical',14);text(539,135,'basolateral',13);
    if (mode==='lipid') {
      line(817,110,817,298,'#6fc9e2');line(817,342,817,380,'#6fc9e2');
      line(823,110,823,298,'#6fc9e2');line(823,342,823,380,'#6fc9e2');
      text(834,355,'lacteal',15);
      text(295,155,'ER re-esterification',15);
      text(390,278,'assembly → Golgi',15);
      text(20,365,'Shorter-chain FA → epithelium → portal blood (route preference)',15);
    } else {
      text(20,125,'pepsin / pancreatic proteases',14);
      text(20,145,'enteropeptidase → trypsin',14);
      text(260,155,'PEPT1 + H+',15);text(350,258,'cytoplasmic cleavage',15);
      text(605,347,'capillary → portal vein',15);
      text(20,365,'NHE3 apical: Na+ in / H+ out',15);
    }
  }
  function drawFailure(p) {
    const time = 6*p;
    const names = ['P: substrate','A: products','E: cell','B: delivered'];
    const base = evolve([100,0,0,0],[1,1,1],time);
    const impaired = evolve([100,0,0,0],[0.2,1,1],time);
    text(20,40,`Closed system; teaching time τ = ${time.toFixed(2)}`);
    text(20,68,'Selected coefficients: baseline (1,1,1); reduced hydrolysis (0.2,1,1)',16);
    text(20,102,'Bar length: conserved-equivalent amount, 0–100',15);
    for (let i=0;i<4;i++) {
      const y=135+i*69;
      text(20,y+14,names[i],16);
      add('rect',{x:180,y,width:6*base[i],height:18,fill:'#72d2bd'});
      add('rect',{x:180,y:y+23,width:6*impaired[i],height:18,fill:'#e5b570'});
      text(795,y+14,base[i].toFixed(3),15,'#72d2bd');
      text(795,y+37,impaired[i].toFixed(3),15,'#e5b570');
    }
    for (let tick=0;tick<=100;tick+=20) {
      const x=180+6*tick;line(x,412,x,419);text(x-7,438,String(tick),13);
    }
    line(180,412,780,412);
    $('phase').textContent=`Baseline total ${base.reduce((a,b)=>a+b,0).toFixed(6)}; `+
      `impaired total ${impaired.reduce((a,b)=>a+b,0).toFixed(6)}. `+
      'Green: baseline; amber: reduced hydrolysis. Synthetic coefficients; no diagnosis.';
  }
  let position=0, playing=false, last=null;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  function render() {
    svg.replaceChildren();
    add('title',{},mode==='failure'?'Conserved pool comparison':
      `${mode} processing; lumen left, tissue right; abstract compartments`);
    if (mode==='failure') drawFailure(position);
    else {
      boundaries();
      const state=api[mode](position);
      text(20,35,`${state.identity}; currently ${state.compartment}`,18);
      if (mode==='protein') {
        const color=state.identity==='amino acids'?'#f0c379':'#8db9ed';
        circle(state.x,state.y-6,5,color);circle(state.x,state.y+6,5,color);
        if (state.identity!=='amino acids') line(state.x,state.y-6,state.x,state.y+6,color,3);
        if (position>1/7 && position<3/7) circle(state.x-11,state.y,3,'#ffffff');
        text(20,408,'Na+/K+ pump BASOLATERAL: 3 Na+ out / 2 K+ in per ATP',16);
        $('phase').textContent=proteinPhases[state.stage];
      } else {
        if (position<0.1) circle(state.x,state.y,25,'#c79047','#f6cc83');
        else if(position<0.5) {
          if(position>=0.2 && position<=0.4) {
            circle(180,180,22,'none','#a9dfe6',3);
            text(80,230,'aggregate stays luminal',13);
          }
          circle(state.x,state.y-6,5,'#f0c379');
          circle(state.x,state.y+6,5,'#f0c379');
        } else {
          if(state.vesicle) {
            circle(state.x,state.y,20,'none','#a7c4db',2);
            circle(state.x,state.y,17,'none','#a7c4db',2);
          }
          circle(state.x,state.y,10,'#b8793b','#f3d07c',3);
          circle(state.x+8,state.y-6,3,'#e0a9e9');
        }
        text(20,408,'Gold particle surface: monolayer; double outer ring: carrier vesicle',16);
        $('phase').textContent=lipidPhases[state.stage];
      }
    }
    $('seek').value=String(Math.round(position*1000));
    $('progress').textContent=`${Math.round(position*100)}% presentation sequence`;
    $('play').textContent=playing?'Pause':'Play';
    $('play').setAttribute('aria-pressed',String(playing));
  }
  function stop() {playing=false;last=null;}
  function reducedChanged() {
    if(reduced.matches)stop();
    $('play').disabled=reduced.matches;
    $('motion-note').textContent=reduced.matches?
      'Reduced motion: use phase steps or the seek slider; continuous play disabled.':
      'No autoplay. Presentation duration is not physiological time.';
    render();
  }
  $('play').addEventListener('click',()=>{
    if(reduced.matches)return;
    playing=!playing;if(playing&&position>=1)position=0;last=null;render();
  });
  $('replay').addEventListener('click',()=>{stop();position=0;render();});
  const phases=mode==='lipid'?10:mode==='protein'?7:6;
  for(const [id,d] of [['previous',-1],['next',1]]) {
    $(id).addEventListener('click',()=>{
      stop();position=clamp((Math.round(position*phases)+d)/phases);render();
    });
  }
  $('seek').addEventListener('input',()=>{stop();position=Number($('seek').value)/1000;render();});
  $('speed').addEventListener('change',()=>{last=null;});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();render();}});
  reduced.addEventListener('change',reducedChanged);
  function frame(now) {
    if(playing) {
      if(last!==null)position=clamp(position+Math.min(now-last,100)/12000*Number($('speed').value));
      last=now;if(position>=1)stop();render();
    }
    window.requestAnimationFrame(frame);
  }
  reducedChanged();window.requestAnimationFrame(frame);
})(typeof window==='undefined'?globalThis:window);
