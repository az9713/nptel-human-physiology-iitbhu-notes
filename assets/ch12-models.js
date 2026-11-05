/* Original deterministic schematic mechanisms; no measured physiological clock. */
(function (root) {
  'use strict';
  const clamp = x => Math.max(0, Math.min(1, x));
  const lerp = (a, b, t) => a + (b - a) * clamp(t);
  const point = (x, y) => ({x, y});
  function transit(phase) {
    const p = clamp(phase), x = lerp(120, 700, p), center = x - 70;
    const wall = [];
    for (let q = 40; q <= 800; q += 5) {
      const narrowing = 28 * Math.exp(-(((q - center) / 38) ** 2));
      wall.push({x: q, top: 140 + narrowing, bottom: 260 - narrowing});
    }
    return {phase:p, x, center, wall, label:p < .33 ? 'Contraction behind; accommodation ahead' : p < .67 ? 'The constriction travels with propulsion' : 'Bolus remains inside the lumen'};
  }
  function hydrolysis(phase) {
    const p = clamp(phase);
    const initial = [[90,190],[180,190],[270,190],[360,190],[450,190],[540,190],[630,190],[720,190],[630,110],[720,110]];
    const split = [[90,250],[165,250],[240,250],[370,210],[445,210],[520,210],[595,210],[670,210],[595,110],[670,110]];
    const final = [[90,280],[165,280],[240,280],[370,280],[445,280],[520,280],[595,280],[670,280],[595,110],[670,110]];
    const a = clamp((p - .20) / .20), b = clamp((p - .65) / .25);
    const positions = initial.map((v,i) => {
      const s = [lerp(v[0],split[i][0],a),lerp(v[1],split[i][1],a)];
      return point(lerp(s[0],final[i][0],b),lerp(s[1],final[i][1],b));
    });
    const edges = [[0,1,'α-1,4'],[1,2,'α-1,4'],[2,3,'α-1,4'],[3,4,'α-1,4'],[4,5,'α-1,4'],[5,6,'α-1,4'],[6,7,'α-1,4'],[6,8,'α-1,6'],[8,9,'α-1,4']].map((e,i) => ({a:e[0],b:e[1],type:e[2],opacity:i===2?1-clamp((p-.12)/.08):1-clamp((p-.60)/.05)}));
    return {phase:p,positions,edges,residues:10,stage:p < .20 ? 'Amylase: selected internal α-1,4 bond cleavage' : p < .60 ? 'Linear fragment + branched remainder; α-1,6 retained' : p < .90 ? 'Brush-border α-glucosidases; isomaltase removes branch' : 'Ten free glucose residues; ready for uptake'};
  }
  function absorption(phase) {
    const p=clamp(phase), glucose=point(240,lerp(100,290,(p-.15)/.20)), fructose=point(520,lerp(100,290,(p-.40)/.20));
    // Entry paths pass through the protein apertures. Lateral repositioning
    // occurs only within cytosol; exit then crosses the GLUT2 aperture.
    if(p>.65){glucose.x=lerp(240,370,(p-.65)/.10);fructose.x=lerp(520,400,(p-.65)/.10);}
    if(p>.75){glucose.y=lerp(290,460,(p-.75)/.20);fructose.y=lerp(290,460,(p-.75)/.20);}
    const sodium=[point(220,lerp(75,270,(p-.15)/.20)),point(260,lerp(75,270,(p-.15)/.20))];
    const pump=clamp((p-.65)/.30);
    return {phase:p,glucose,fructose,sodium,pump,stage:p<.15?'Basolateral ATP-driven pump maintains sodium conditions':p<.40?'Apical SGLT1: glucose with two sodium ions':p<.65?'Apical GLUT5: fructose entry, a separate route':p<.75?'Cytosolic redistribution toward basolateral exit':p<.95?'Basolateral GLUT2: sugar exit to tissue':'Transferred sugars; sodium gradient requires ongoing maintenance'};
  }
  const api={clamp,transit,hydrolysis,absorption};
  root.Ch12=api;
  if(typeof module !== 'undefined') module.exports=api;
  if(typeof document==='undefined') return;
  const kind=document.body.dataset.model;
  if(!kind) return;
  const svg=document.getElementById('scene'), dynamic=document.getElementById('dynamic');
  const readout=document.getElementById('readout'), seek=document.getElementById('seek');
  let phase=0, playing=false, speed=1, previous=null;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  function circle(p,r,color,label='') {return `<circle cx="${p.x}" cy="${p.y}" r="${r}" fill="${color}" stroke="#111e27" stroke-width="2"/>${label?`<text x="${p.x}" y="${p.y+6}" text-anchor="middle" class="token">${label}</text>`:''}`;}
  function draw(){
    phase=clamp(phase); seek.value=String(Math.round(phase*1000));
    const s=api[kind](phase);
    if(kind==='transit'){
      const top=s.wall.map(q=>`${q.x},${q.top}`).join(' '), bottom=s.wall.map(q=>`${q.x},${q.bottom}`).join(' ');
      dynamic.innerHTML=`<polyline points="${top}" fill="none" stroke="#df9c9c" stroke-width="18"/><polyline points="${bottom}" fill="none" stroke="#df9c9c" stroke-width="18"/>${circle(point(s.x,200),18,'#f1cc7a')}<line x1="${s.x-12}" y1="200" x2="${s.x+12}" y2="200" stroke="#10212d" stroke-width="3"/><text x="40" y="330">Bolus center: ${s.x.toFixed(1)} schematic units; phase ${(100*phase).toFixed(0)}%</text>`;
      readout.textContent=s.label+'. Bolus and walls share the same phase; no physical transit time.';
    } else if(kind==='hydrolysis'){
      dynamic.innerHTML=s.edges.map(e=>`<line x1="${s.positions[e.a].x}" y1="${s.positions[e.a].y}" x2="${s.positions[e.b].x}" y2="${s.positions[e.b].y}" opacity="${e.opacity}" stroke="${e.type==='α-1,6'?'#e9a1db':'#8acede'}" stroke-width="5"/>`).join('')+s.positions.map((v,i)=>circle(v,22,'#f1cc7a',String(i+1))).join('')+`<text x="40" y="345">Residue identities 1–10 persist. Count: ${s.residues} glucose residues.</text>`;
      readout.textContent=s.stage+'. Blue links: α-1,4; pink link: α-1,6. Water participation is chemical, not explicitly drawn.';
    } else {
      dynamic.innerHTML=circle(s.glucose,13,'#f1cc7a','G')+circle(s.fructose,13,'#d7a6ef','F')+s.sodium.map(v=>circle(v,7,'#8bd3ed')).join('')+`<path d="M630 310V455m-9 -15 9 15 9 -15M690 455V310m-9 15 9 -15 9 15" stroke="#efab8c" stroke-width="${3+3*s.pump}" fill="none"/><text x="590" y="505">3 Na+ out / 2 K+ in</text>`;
      readout.textContent=s.stage+'. G = glucose (galactose uses the same principal entry route); F = fructose; blue dots = coupled Na+. Pump arrows denote continued maintenance, not a synchronized ion census.';
    }
    document.getElementById('phase').textContent=`Presentation phase ${(100*phase).toFixed(0)}%; ${playing?'playing':'paused'}`;
  }
  function pause(){playing=false;previous=null;document.getElementById('play').textContent='Play';draw();}
  document.getElementById('play').onclick=()=>{playing=!playing;if(playing&&phase===1)phase=0;previous=null;document.getElementById('play').textContent=playing?'Pause':'Play';draw();};
  document.getElementById('replay').onclick=()=>{pause();phase=0;draw();};
  seek.oninput=()=>{const requested=Number(seek.value)/1000;pause();phase=requested;draw();};
  document.getElementById('back').onclick=()=>{pause();phase-=.05;draw();};
  document.getElementById('next').onclick=()=>{pause();phase+=.05;draw();};
  document.getElementById('speed').onchange=e=>{speed=Number(e.target.value);};
  reduced.addEventListener('change',()=>pause());
  const scroller=document.getElementById('scene-scroll');
  scroller.onkeydown=e=>{if(e.target!==scroller)return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();scroller.scrollLeft+=e.key==='ArrowRight'?60:-60;}};
  function frame(now){if(playing){if(previous!==null)phase+=(now-previous)*speed/16000;previous=now;if(phase>=1){phase=1;pause();}else draw();}requestAnimationFrame(frame);}
  // Start settled for every user, including reduced-motion preference.
  root.Ch12Player={getState:()=>({phase,playing,speed}),seek:p=>{pause();phase=clamp(p);draw();}};
  draw();requestAnimationFrame(frame);
})(typeof globalThis!=='undefined'?globalThis:this);
