/* Chapter 6 original deterministic teaching models. No measured kinetics. */
(() => {
  'use strict';
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  function radiusState(phase) {
    const r = 0.8 + 0.4 * clamp(phase, 0, 1);
    return { r, q: r ** 4, resistance: r ** -4, pressure: 1 };
  }
  function controlState(t, pressure = 1.3) {
    const target = clamp(pressure, 0.7, 1.5);
    const resistance = t < 2 ? 1 : target + (1 - target) * Math.exp(-(t - 2) / 3);
    const p = t < 2 ? 1 : pressure;
    return { t, p, resistance, q: p / resistance, target };
  }
  function classicalState(phase) {
    const pc = 35 - 18 * clamp(phase, 0, 1);
    return { pc, piC: 25, piI: 1, pI: 0, drive: pc - 24 };
  }
  globalThis.Ch06Models = { radiusState, controlState, classicalState };
  if (typeof document === 'undefined' || !document.body.dataset.model) return;
  const mode = document.body.dataset.model;
  const $ = id => document.getElementById(id);
  let phase = 0;
  let playing = false;
  let last = 0;
  let speed = 1;
  let exchange = 'classical';
  let pressure = 1.3;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const f = x => x.toFixed(3);
  const line = (x1, y1, x2, y2, color = '#b4cad5', width = 2) =>
    '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" stroke="' + color + '" stroke-width="' + width + '"/>';
  const text = (x, y, s, small = false) => '<text x="' + x + '" y="' + y + '"' + (small ? ' class="small"' : '') + '>' + s + '</text>';
  function scene(content, desc) {
    $('scene').innerHTML = '<title id="scene-title">' + document.title + '</title><desc id="scene-desc">' + desc + '</desc>' + content;
  }
  function radiusDraw() {
    const s = radiusState(phase);
    let out = text(25, 29, 'Ideal lumen section') + text(25, 55, 'Radius ratio ' + f(s.r), true);
    out += '<circle cx="150" cy="175" r="' + (70 * s.r + 9) + '" fill="#598b97"/>';
    out += '<circle cx="150" cy="175" r="' + (70 * s.r) + '" fill="#5a2437"/>';
    out += line(150, 175, 150 + 70 * s.r, 175, '#f1d183', 3);
    out += text(103, 298, 'Fixed ΔP = 1', true);
    out += text(345, 28, 'Normalized flow and resistance at fixed pressure');
    out += text(350, 53, 'Q / Q₀', true) + line(418, 48, 448, 48, '#ebc96f', 4);
    out += text(495, 53, 'R / R₀', true) + line(563, 48, 593, 48, '#79cee0', 4);
    const x = r => 350 + (r - 0.8) / 0.4 * 450;
    const y = value => 285 - value / 2.6 * 200;
    out += line(350, 85, 350, 285) + line(350, 285, 800, 285);
    for (const value of [0, 1, 2]) out += text(320, y(value) + 5, String(value), true) + line(345, y(value), 350, y(value));
    for (const r of [0.8, 1, 1.2]) out += text(x(r) - 12, 310, String(r), true) + line(x(r), 285, x(r), 291);
    const points = fn => Array.from({ length: 81 }, (_, i) => {
      const r = 0.8 + i / 200;
      return x(r) + ',' + y(fn(r));
    }).join(' ');
    out += '<polyline points="' + points(r => r ** 4) + '" stroke="#ebc96f" fill="none" stroke-width="3"/>';
    out += '<polyline points="' + points(r => r ** -4) + '" stroke="#79cee0" fill="none" stroke-width="3"/>';
    out += line(x(s.r), 85, x(s.r), 285, '#dfe8ee', 1);
    out += '<circle cx="' + x(s.r) + '" cy="' + y(s.q) + '" r="6" fill="#ebc96f"/>';
    out += '<circle cx="' + x(s.r) + '" cy="' + y(s.resistance) + '" r="6" fill="#79cee0"/>';
    out += text(500, 339, 'Radius / baseline radius', true);
    scene(out, 'A single radius ratio sets the lumen and both fourth-power curves. Pressure is fixed.');
    $('state').textContent = 'r/r₀ = ' + f(s.r) + '; Q/Q₀ = ' + f(s.q) + '; R/R₀ = ' + f(s.resistance) + '. All states share the same fixed pressure drop. Phase is a parameter sweep, not a contraction clock.';
  }
  function exchangeDraw() {
    const stage = Math.min(2, Math.floor(phase * 3));
    if (exchange === 'classical') {
      const s = classicalState(phase);
      let out = text(28, 30, 'Classical fixed-compartment construction');
      out += '<rect x="100" y="88" width="675" height="88" rx="18" fill="#59283a" stroke="#91bec8" stroke-width="8"/>';
      out += text(125, 125, 'Plasma πc = 25 mmHg') + text(125, 152, 'Capillary Pc = ' + f(s.pc) + ' mmHg', true);
      out += text(105, 225, 'Bulk interstitium: Pi = 0; πi = 1 mmHg');
      out += line(640, 185, 640, 248, '#ebc96f', 6);
      out += text(670, 220, 'Outward +', true);
      out += text(105, 284, 'D = Pc − Pi − (πc − πi) = ' + f(s.drive) + ' mmHg');
      out += text(105, 316, 'σ = 1; flow still requires Kf. Phase moves from Pc 35 to 17, not biological time.', true);
      scene(out, 'Classical pressure inputs held fixed apart from capillary pressure. Signed net drive changes from plus eleven to minus seven.');
      $('state').textContent = 'Classical driving pressure ' + f(s.drive) + ' mmHg: ' + (s.drive >= 0 ? 'outward filtration' : 'inward absorption') + ' in this fixed-input construction. This view does not establish steady human exchange or a universal reabsorbed fraction.';
    } else {
      let out = text(25, 28, 'Revised interface: continuous-endothelium schematic, separate scales');
      out += '<rect x="100" y="59" width="700" height="83" fill="#59283a"/>';
      out += text(120, 91, 'Lumen / plasma: Pc, πc');
      out += '<rect x="100" y="161" width="330" height="85" rx="7" fill="#538e9b"/><rect x="470" y="161" width="330" height="85" rx="7" fill="#538e9b"/>';
      out += '<rect x="100" y="145" width="700" height="9" fill="#a5cf9b"/>';
      out += '<rect x="432" y="155" width="36" height="40" fill="#e4c77e" opacity="' + (stage === 1 ? '0.8' : '0.35') + '"/>';
      out += text(120, 195, 'Endothelial cell', true) + text(560, 195, 'Endothelial cell', true);
      out += '<path d="M100 259H800" stroke="#d8b989" stroke-width="3" stroke-dasharray="7 4"/>';
      out += text(560, 249, 'Basement-membrane matrix', true);
      out += text(120, 286, 'Bulk interstitium: Pi, πi') + text(120, 313, 'Not automatically equal to protected πg', true);
      out += line(450, 115, 450, 290, '#ebc96f', 4);
      out += '<path d="M442 280L450 294L458 280" fill="none" stroke="#ebc96f" stroke-width="3"/>';
      out += text(490, 130, 'Selective surface layer', true);
      out += text(490, 222, 'Protected region: πg', true);
      out += line(470, 178, 555, 215, '#e4c77e', 1);
      out += text(600, 318, 'Lymph removes tissue fluid', true);
      out += text(28, 342, 'Yellow arrow: one intercellular water route through surface layer and cleft; no lipid crossing.', true);
      scene(out, 'Luminal glycocalyx above two endothelial cells. A water route passes through the surface layer into an intercellular cleft, with a protected subglycocalyx region. Interstitium and lymph are distinct.');
      const states = [
        'Identify the selective surface layer: the relevant plasma protein difference is evaluated across a barrier, not across an unnamed entire tissue.',
        'Identify the protected subglycocalyx region πg. It can differ from bulk interstitial πi; filtration and diffusion couple this environment to flow.',
        'Identify tissue removal: lymphatic return supports fluid balance in many steadily filtering tissues. Transient reabsorption and specialized beds require their own conditions.'
      ];
      $('state').textContent = states[stage] + ' Presentation stage only: no numerical πg or predicted human flux kinetics.';
    }
  }
  function controlDraw() {
    const t = phase * 14;
    const s = controlState(t, pressure);
    let out = text(28, 29, 'One shared state: q = p / resistance ratio');
    const x = time => 95 + time / 14 * 700;
    const y = value => 285 - value / 2.2 * 205;
    out += line(95, 80, 95, 285) + line(95, 285, 795, 285);
    for (const value of [0, 1, 2]) out += text(59, y(value) + 5, String(value), true) + line(89, y(value), 95, y(value));
    for (const time of [0, 2, 5, 10, 14]) out += text(x(time) - 7, 310, String(time), true) + line(x(time), 285, x(time), 291);
    const colors = { p: '#e3b286', resistance: '#79cee0', q: '#ebc96f' };
    ['p', 'resistance', 'q'].forEach((key, index) => {
      const end = Math.max(0, Math.floor(t * 25));
      const points = Array.from({ length: end + 1 }, (_, i) => {
        const a = i / 25;
        return x(a) + ',' + y(controlState(a, pressure)[key]);
      }).join(' ');
      out += '<polyline points="' + points + '" fill="none" stroke="' + colors[key] + '" stroke-width="3"/>';
      out += line(130 + index * 230, 53, 155 + index * 230, 53, colors[key], 4);
      out += text(165 + index * 230, 58, key === 'p' ? 'Pressure ratio' : key === 'q' ? 'Flow ratio' : 'Resistance ratio', true);
      out += '<circle cx="' + x(t) + '" cy="' + y(s[key]) + '" r="5" fill="' + colors[key] + '"/>';
    });
    out += line(x(t), 80, x(t), 285, '#e9eff3', 1);
    out += text(350, 340, 'Synthetic time (s)', true);
    scene(out, 'Normalized pressure step with bounded first-order resistance adaptation and algebraically linked flow. Time and all controller parameters are synthetic.');
    $('state').textContent = 'Synthetic t = ' + f(t) + ' s; p = ' + f(s.p) + '; resistance ratio = ' + f(s.resistance) + '; q = ' + f(s.q) + '. ' + (pressure > 1.5 ? 'Target saturates at 1.5: final q = 1.333333, so stabilization is incomplete.' : 'Within the selected bounds the target resistance tends to pressure ratio, and q tends to 1.');
  }
  if (mode === 'exchange') {
    $('options').innerHTML = '<label>View <select id="view"><option value="classical">Classical arithmetic</option><option value="revised">Revised interface</option></select></label>';
    $('view').addEventListener('change', () => { exchange = $('view').value; phase = 0; pause(); draw(); });
    $('fallback').textContent = 'Classical endpoints: +11 and −7 mmHg. Revised interface: effective oncotic term uses plasma minus subglycocalyx pressure; the bulk interstitium is a distinct compartment. Arrows indicate routes, not measured flux magnitude.';
  } else if (mode === 'control') {
    $('options').innerHTML = '<label>Pressure step <select id="pressure"><option value="1.3">1 → 1.3, within target bounds</option><option value="2">1 → 2, target saturates</option></select></label>';
    $('pressure').addEventListener('change', () => { pressure = Number($('pressure').value); phase = 0; pause(); draw(); });
    $('fallback').textContent = 'Static check for step 1.3: at t=2, p/R/q=1.3/1/1.3; at t=5, 1.3/1.189636/1.092771; at t=11, 1.3/1.285064/1.011623. Step 2 tends to p/R/q=2/1.5/1.333333.';
  } else {
    $('fallback').textContent = 'Static check: radius ratios 0.8/1/1.2 yield flow ratios 0.4096/1/2.0736 and resistance ratios 2.441406/1/0.482253. These depend on fixed pressure, viscosity and length.';
  }
  function draw() {
    $('seek').value = String(phase * 100);
    $('phase').textContent = 'Progress ' + Math.round(phase * 100) + '%';
    if (mode === 'radius') radiusDraw();
    else if (mode === 'exchange') exchangeDraw();
    else controlDraw();
  }
  function pause() { playing = false; $('play').textContent = 'Play'; $('play').setAttribute('aria-pressed', 'false'); }
  function play() {
    if (phase >= 1) phase = 0;
    playing = true;
    last = performance.now();
    $('play').textContent = 'Pause'; $('play').setAttribute('aria-pressed', 'true');
  }
  $('play').addEventListener('click', () => playing ? pause() : play());
  $('replay').addEventListener('click', () => { phase = 0; pause(); draw(); });
  $('seek').addEventListener('input', () => { phase = Number($('seek').value) / 100; pause(); draw(); });
  $('previous').addEventListener('click', () => { phase = clamp(phase - 0.25, 0, 1); pause(); draw(); });
  $('next').addEventListener('click', () => { phase = clamp(phase + 0.25, 0, 1); pause(); draw(); });
  $('speed').addEventListener('change', () => { speed = Number($('speed').value); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  reduced.addEventListener('change', () => { pause(); draw(); });
  const viewport = document.querySelector('.viewport');
  viewport.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); viewport.scrollLeft += event.key === 'ArrowRight' ? 70 : -70;
    }
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) pause();
  }).observe(document.body);
  function tick(now) {
    if (playing) {
      phase = clamp(phase + Math.min(100, now - last) / 12000 * speed, 0, 1);
      draw(); if (phase >= 1) pause();
    }
    last = now;
    requestAnimationFrame(tick);
  }
  draw(); requestAnimationFrame(tick);
})();
