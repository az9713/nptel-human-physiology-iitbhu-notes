/* UI clock is presentation time. D3 is seeked through a pure source-coordinate model. */
(() => {
  'use strict';
  const model = window.GasTransferModel;
  const $ = id => document.getElementById(id);
  if (!model) { $('status').textContent = 'Animation library unavailable. Read the static equivalent below.'; return; }
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let pressures = {o2:[100,40],co2:[40,46]};
  let time = 0, playing = false, speed = 1, last = null, raf = null;
  const steps = [0,2,4,6,8];
  const format = value => Object.is(value,-0) ? '0' : String(value);
  function draw() {
    const state = model.computeState(time,pressures);
    time = state.time;
    for (const gas of ['o2','co2']) {
      const s = state[gas];
      const show = s.visible && $('show-'+gas).checked;
      $('route-'+gas).setAttribute('d',s.path);
      $('route-'+gas).style.display = show ? '' : 'none';
      $('packet-'+gas).setAttribute('cy',s.y);
      $('packet-'+gas).style.display = show ? '' : 'none';
      $('pressure-'+gas).textContent = `${format(s.airPressure)} / ${format(s.bloodPressure)} mmHg`;
      $('delta-'+gas).textContent = `${s.delta > 0 ? '+' : ''}${format(s.delta)} mmHg`;
      $('direction-'+gas).textContent = s.direction;
      $('equilibrium-'+gas).hidden = s.visible;
      $('equilibrium-'+gas).textContent = s.equilibriumText;
    }
    $('seek').value = Math.round(time*1000);
    $('seek').setAttribute('aria-valuetext',`${time.toFixed(1)} illustration seconds; ${state.phase}`);
    $('clock').textContent = `${time.toFixed(1)} / 8 illustration s`;
    $('phase').textContent = state.phase;
    $('play').textContent = playing ? 'Pause' : 'Play';
    $('play').setAttribute('aria-pressed',String(playing));
    window.__gasTransferSnapshot = {...state,playing,speed,showO2:$('show-o2').checked,showCO2:$('show-co2').checked};
  }
  function pause() {
    playing = false; last = null;
    if (raf !== null) cancelAnimationFrame(raf);
    raf = null; draw();
  }
  function tick(now) {
    if (!playing) return;
    if (last !== null) time += Math.max(0,(now-last)/1000)*speed;
    last = now;
    if (time >= model.duration) { time = model.duration; playing = false; last = null; }
    draw();
    raf = playing ? requestAnimationFrame(tick) : null;
  }
  function play() {
    if (playing) return;
    if (time >= model.duration) time = 0;
    playing = true; last = null; draw(); raf = requestAnimationFrame(tick);
  }
  function seek(value) { pause(); time = Math.max(0,Math.min(model.duration,value)); draw(); }
  $('play').addEventListener('click',() => playing ? pause() : play());
  $('replay').addEventListener('click',() => { seek(0); if (!reduced.matches) play(); });
  $('previous').addEventListener('click',() => seek([...steps].reverse().find(x => x < time-.001) ?? 0));
  $('next').addEventListener('click',() => seek(steps.find(x => x > time+.001) ?? model.duration));
  $('seek').addEventListener('input',event => seek(Number(event.target.value)/1000));
  $('speed').addEventListener('change',event => { speed = Number(event.target.value); last = null; draw(); });
  for (const gas of ['o2','co2']) {
    $('preset-'+gas).addEventListener('change',event => {
      const pair = model.presets[gas][event.target.value];
      if (!pair) { $('status').textContent = 'Unknown pressure preset; previous pressures retained.'; return; }
      pressures = model.validatePressures({...pressures,[gas]:pair});
      seek(0);
      $('status').textContent = 'Pressure changed. The illustration resets; each gas follows its own pressure gradient.';
    });
    $('show-'+gas).addEventListener('change',draw);
  }
  $('fit').addEventListener('click',() => { $('micro-pan').classList.add('fit'); $('micro-pan').focus(); });
  $('detail').addEventListener('click',() => { $('micro-pan').classList.remove('fit'); $('micro-pan').focus(); });
  // Handle panning explicitly: browser defaults can scroll the page instead of
  // the focused overflow region in embedded readers. Do not intercept controls.
  $('micro-pan').addEventListener('keydown',event => {
    if (event.target !== event.currentTarget || event.altKey || event.ctrlKey || event.metaKey) return;
    const pan = event.currentTarget;
    const end = Math.max(0,pan.scrollWidth-pan.clientWidth);
    if (!end || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    event.preventDefault();
    const target = event.key === 'Home' ? 0 : event.key === 'End' ? end :
      pan.scrollLeft + (event.key === 'ArrowRight' ? 60 : -60);
    pan.scrollTo({left:Math.max(0,Math.min(end,target)),behavior:'instant'});
  });
  reduced.addEventListener('change',event => { if (event.matches) { pause(); $('status').textContent = 'Reduced motion: paused. Use the step or seek controls; Play remains an explicit choice.'; } });
  document.addEventListener('visibilitychange',() => { if (document.hidden && playing) pause(); });
  window.addEventListener('beforeprint',pause);
  // Deterministic export/review entry point. It is presentation time, not physiology.
  window.renderFrame = seconds => { seek(seconds); return window.__gasTransferSnapshot; };
  $('status').textContent = reduced.matches ? 'Reduced motion: starts paused. Step or seek to inspect the mechanism.' : 'Starts paused. The two gas examples progress together in presentation time.';
  draw();
})();
