(() => {
  'use strict';
  const mode = document.body.dataset.mode;
  let phase = 0, running = false, speed = 1, previous;
  const seek = document.getElementById('seek');
  const play = document.getElementById('play');
  const text = document.getElementById('state');
  function draw() {
    const s = Ch16.state(mode,phase);
    seek.value = phase;
    if (mode === 'routes') {
      document.querySelectorAll('[data-step]').forEach(el => {el.classList.toggle('active',Number(el.dataset.step) === s.step);});
      text.textContent = ['Orientation: renal corpuscles lie in cortex; loops and collecting ducts extend into medulla.','Vascular route: afferent → glomerular capillary lumen → efferent; retained cells stay vascular.','Filtration route: plasma water and permitted solutes cross the capillary wall into capsular space.','Tubular route: capsular space → proximal tubule → loop → distal tubule → collecting system.'][s.step];
    } else if (mode === 'filtration') {
      text.textContent = `Prescribed capsular pressure ${s.pbs.toFixed(2)} mmHg; net pressure ${s.nfp.toFixed(2)} mmHg; signed model filtration ${s.signedFlux.toFixed(2)} mL/min.`;
      document.getElementById('capsular').setAttribute('width',s.pbs*5);
      document.getElementById('net').setAttribute('width',s.nfp*5);
      document.getElementById('flux').textContent = `${s.signedFlux.toFixed(1)} mL/min`;
    } else {
      text.textContent = `Afferent resistance ${(1+phase).toFixed(2)}: flow ${s.afferent.q.toFixed(2)} arbitrary units, node pressure ${s.afferent.pgc.toFixed(2)} mmHg. Efferent resistance ${(1+phase).toFixed(2)}: flow ${s.efferent.q.toFixed(2)}, node pressure ${s.efferent.pgc.toFixed(2)} mmHg.`;
      for (const [id,v] of [['aq',s.afferent.q],['eq',s.efferent.q],['ap',s.afferent.pgc],['ep',s.efferent.pgc]]) document.getElementById(id).setAttribute('width',v*3);
    }
  }
  function stop() {running=false;play.textContent='Play';play.setAttribute('aria-pressed','false');}
  play.addEventListener('click',()=>{running=!running; previous=undefined;play.textContent=running?'Pause':'Play';play.setAttribute('aria-pressed',String(running));});
  document.getElementById('replay').addEventListener('click',()=>{stop();phase=0;draw();});
  document.getElementById('speed').addEventListener('change',e=>{speed=Number(e.target.value);});
  seek.addEventListener('input',()=>{stop();phase=Number(seek.value);draw();});
  function frame(now) {if(running){if(previous!==undefined) phase=Math.min(1,phase+(now-previous)/12000*speed);draw();if(phase>=1)stop();}previous=now;requestAnimationFrame(frame);}
  draw(); requestAnimationFrame(frame);
  // Initial state is always paused, including reduced-motion preferences.
})();
