'use strict';
// Deterministic original teaching construction. One state clock drives all views.
(() => {
  const el = id => document.getElementById(id);
  const model = el('model'), seek = el('seek'), play = el('play');
  let time = 0, running = false, lastFrame = null;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const modes = ['diffusion', 'pump', 'feedback'];
  if (modes.includes(location.hash.slice(1))) model.value = location.hash.slice(1);
  function diffuse(t, g) {
    const delta = 10 * Math.exp(-1.5 * g * t);
    return [20 / 3 + delta / 3, 20 / 3 - 2 * delta / 3];
  }
  function feedback(t, k) {
    const rate = 0.05 + k;
    return (1 - Math.exp(-rate * t)) / rate;
  }
  function line(values, left, base, scale) {
    return values.map((v, j) => `${left + j / 120 * (765-left)},${base-v*scale}`).join(' ');
  }
  function dot(id, x, y) { el(id).setAttribute('cx', x); el(id).setAttribute('cy', y); }
  function setRunning(value) {
    running = value;
    play.textContent = running ? 'Pause' : 'Play';
    play.setAttribute('aria-pressed', String(running));
    lastFrame = null;
  }
  function render() {
    const mode = model.value;
    for (const name of modes) el(`${name}-scene`).style.display = name === mode ? '' : 'none';
    // SVG hidden behavior differs across engines: display is explicit.
    for (const name of modes) el(`${name}-scene`).removeAttribute('hidden');
    el('diffusion-parameters').hidden = mode !== 'diffusion';
    el('feedback-parameters').hidden = mode !== 'feedback';
    seek.value = String(time);
    el('clock').textContent = `${time.toFixed(1)} ${mode === 'pump' ? 'presentation s' : 's'}`;
    el('motion-note').textContent = motion.matches ? 'Reduced motion preference detected: starts paused. Seek or Step forward for static phases; Play is optional.' : 'Starts paused. Seek or Step forward to inspect any phase; Replay resets to the initial state.';
    if (mode === 'diffusion') {
      const g = Number(el('conductance').value), vm = Number(el('voltage').value);
      const [co, ci] = diffuse(time, g);
      el('g-label').textContent = `${g.toFixed(2)} L/s`;
      el('v-label').textContent = `${vm} mV`;
      el('scene-title').textContent = 'Synthetic closed two-compartment diffusion';
      el('scene-desc').textContent = `Outside ${co.toFixed(3)}, inside ${ci.toFixed(3)} mmol/L. Total 20 mmol. Gold outside, cyan inside.`;
      for (const [name, c] of [['outside',co], ['inside',ci]]) {
        const fill = el(`${name}-fill`);
        fill.setAttribute('y', String(225-c*17)); fill.setAttribute('height', String(c*17));
        el(`${name}-value`).textContent = `${c.toFixed(3)} mmol/L`;
      }
      const points = Array.from({length:121}, (_, j) => diffuse(j/4, g));
      el('outside-curve').setAttribute('points', line(points.map(v=>v[0]),400,225,17));
      el('inside-curve').setAttribute('points', line(points.map(v=>v[1]),400,225,17));
      dot('outside-dot',400+365*time/30,225-17*co);
      dot('inside-dot',400+365*time/30,225-17*ci);
      el('flux-arrow').style.opacity = String(Math.min(1,Math.abs(g*(co-ci))));
      el('readout').textContent = `t=${time.toFixed(1)} s · total=${(2*co+ci).toFixed(6)} mmol · inward rate=${(g*(co-ci)).toFixed(3)} mmol/s`;
      el('explanation').textContent = 'Concentration difference drives neutral-solute diffusion. Both volumes are fixed and well mixed; no reactions, voltage effects, pumps or water movement. Full curves show the exact model prediction; dots mark the selected time.';
      // A deliberately separate energy check: voltage does not alter neutral diffusion.
      const dg = 8.31446261815324*310*Math.log(140/4) + 96485.33212*vm/1000;
      el('energy').textContent = `Separate ionic energy check (not the neutral diffusion trace): K⁺ inside/outside=140/4 mmol/L, 310 K, ${vm} mV. Inward ΔG=${(dg/1000).toFixed(3)} kJ/mol: ${dg>0?'outward transfer favored':dg<0?'inward transfer favored':'equilibrium'}. Voltage changes this check only.`;
    } else if (mode === 'pump') {
      const q = time/30;
      const na = Math.max(0,Math.min(1,(q-.12)/.28));
      const potassium = Math.max(0,Math.min(1,(q-.55)/.3));
      el('sodium-ions').setAttribute('transform',`translate(0 ${-180*na})`);
      el('potassium-ions').setAttribute('transform',`translate(0 ${180*potassium})`);
      const phase = q<.12 ? '1 · Bind three cytosolic Na⁺' : q<.4 ? '2 · ATP-linked phosphorylation and access change; Na⁺ released outside' : q<.55 ? '3 · Bind two extracellular K⁺' : q<.85 ? '4 · Dephosphorylation and return of inward access' : '5 · Release two K⁺ inside; one cycle complete';
      el('scene-title').textContent = 'Schematic Na/K ATPase cycle';
      el('scene-desc').textContent = phase;
      el('readout').textContent = phase;
      el('explanation').textContent = 'Gold: three sodium ions move from cytosol to extracellular fluid. Blue: two potassium ions return. One ATP is hydrolyzed per usual forward cycle. Particle positions indicate sequence only: they are not a molecular trajectory. The separate symporter spends an existing sodium gradient; it does not hydrolyze this ATP.';
      el('energy').textContent = 'Time maps to five teaching phases, not measured protein kinetics. Protein geometry and colors are schematic; the symmetric drawing does not imply equal biological dwell times.';
    } else {
      const k = Number(el('gain').value), x = feedback(time,k);
      el('k-label').textContent = `${k.toFixed(2)} /s`;
      el('scene-title').textContent = 'Synthetic negative feedback response to a sustained disturbance';
      el('scene-desc').textContent = `Deviation ${x.toFixed(3)} au; effector action ${(-k*x).toFixed(3)} au/s.`;
      const grid = Array.from({length:121}, (_, j) => j/4);
      el('uncontrolled-curve').setAttribute('points',line(grid.map(t=>feedback(t,0)),425,225,8.5));
      el('controlled-curve').setAttribute('points',line(grid.map(t=>feedback(t,k)),425,225,8.5));
      dot('controlled-dot',425+340*time/30,225-8.5*x);
      el('state-value').textContent = `Deviation x = ${x.toFixed(3)} au`;
      el('effector-value').textContent = `u = ${(-k*x).toFixed(3)} au/s`;
      el('readout').textContent = `t=${time.toFixed(1)} s · steady error=${(1/(.05+k)).toFixed(3)} au · time constant=${(1/(.05+k)).toFixed(3)} s`;
      el('explanation').textContent = 'dx/dt = 1 − (0.05 + k)x. A continuing positive disturbance raises deviation; negative effector action reduces that rise. The signal and trace share the same state. Gold is the comparison with feedback disabled; cyan uses the selected gain.';
      el('energy').textContent = 'A nonzero steady error is expected with proportional control under a maintained disturbance. This one-state model excludes delay, saturation, noise, adaptation and changing reference values; it is not calibrated to blood glucose or pressure.';
    }
  }
  play.addEventListener('click',()=>{if(time>=30)time=0;setRunning(!running);render();});
  el('replay').addEventListener('click',()=>{time=0;setRunning(false);render();});
  el('step').addEventListener('click',()=>{setRunning(false);time=Math.min(30,time+1);render();});
  seek.addEventListener('input',()=>{setRunning(false);time=Number(seek.value);render();});
  model.addEventListener('change',()=>{time=0;setRunning(false);render();});
  for (const id of ['conductance','voltage','gain']) el(id).addEventListener('input',()=>{setRunning(false);render();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)setRunning(false);});
  motion.addEventListener('change',()=>{setRunning(false);render();});
  function frame(now) {
    if(running) {
      if(lastFrame!==null)time=Math.min(30,time+(now-lastFrame)/1000*Number(el('speed').value));
      lastFrame=now;
      if(time>=30)setRunning(false);
      render();
    }
    window.requestAnimationFrame(frame);
  }
  render(); window.requestAnimationFrame(frame);
})();
