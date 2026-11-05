/* Original deterministic teaching sequences. Presentation progress is not time. */
(function (root) {
  'use strict';
  const groups = ['O', 'A', 'B', 'AB'];
  const antigens = { O: [], A: ['A'], B: ['B'], AB: ['A', 'B'] };
  const targets = g => ['A', 'B'].filter(x => !antigens[g].includes(x));
  const clamp = x => Math.max(0, Math.min(1, x));
  const lerp = (a, b, p) => a + (b - a) * clamp(p);
  function encounter(donor, recipient, component) {
    if (!groups.includes(donor) || !groups.includes(recipient) ||
        !['red_cells', 'plasma'].includes(component)) throw Error('Invalid ABO input');
    const cellGroup = component === 'red_cells' ? donor : recipient;
    const plasmaGroup = component === 'red_cells' ? recipient : donor;
    const hits = antigens[cellGroup].filter(a => targets(plasmaGroup).includes(a));
    return { cellGroup, plasmaGroup, hits, compatible: hits.length === 0 };
  }
  function state(kind, p, params = {}) {
    p = clamp(p);
    if (kind === 'abo') {
      const e = encounter(params.donor, params.recipient, params.component);
      const approach = e.compatible ? 0 : clamp((p - 0.2) / 0.5);
      return { ...e, p, left: lerp(210, 285, approach),
        right: lerp(510, 435, approach), bound: !e.compatible && p >= 0.7 };
    }
    if (kind === 'lymph') {
      let x, y;
      if (p < 0.3) { x = 245; y = lerp(105, 205, p / 0.3); }
      else { x = lerp(245, 620, (p - 0.3) / 0.55); y = 205; }
      return { p, x, y, entryOpen: p < 0.34,
        valveOpen: p >= 0.3 && p < 0.85 };
    }
    if (kind === 'immune') {
      const enabled = params.costim === 'yes';
      return { p, recognition: p >= 0.2, costimulation: enabled && p >= 0.35,
        expansion: enabled && p >= 0.6, memory: enabled && p >= 0.85 };
    }
    throw Error('Unknown mechanism');
  }
  function initialize(panel) {
    const kind = panel.dataset.ch4;
    const q = s => panel.querySelector(s);
    const part = n => q(`[data-part="${n}"]`);
    const controls = q('[data-controls]');
    controls.innerHTML = '<button type="button" data-action="play" aria-pressed="false">Play</button>' +
      '<button type="button" data-action="replay">Replay</button>' +
      '<button type="button" data-action="back">Previous phase</button>' +
      '<button type="button" data-action="step">Next phase</button>' +
      '<label>Progress <input data-seek type="range" min="0" max="1000" value="0" step="1"></label>' +
      '<label>Speed <select data-speed><option value="0.5">0.5×</option>' +
      '<option value="1" selected>1×</option><option value="2">2×</option></select></label>';
    const play = q('[data-action="play"]');
    const seek = q('[data-seek]');
    const speed = q('[data-speed]');
    const status = q('[data-phase]');
    let progress = 0, running = false, previous = null, frame = null;
    function params() {
      return Object.fromEntries([...panel.querySelectorAll('[data-param]')]
        .map(el => [el.dataset.param, el.value]));
    }
    function pause() {
      running = false; previous = null;
      if (frame !== null) cancelAnimationFrame(frame);
      frame = null; play.textContent = 'Play'; play.setAttribute('aria-pressed', 'false');
    }
    function draw() {
      const par = params();
      const s = state(kind, progress, par);
      seek.value = String(Math.round(progress * 1000));
      if (kind === 'abo') {
        const ag = antigens[s.cellGroup];
        const colors = { A: '#f1c96a', B: '#8dceec' };
        part('cells').innerHTML = [s.left, s.right].map((cx, i) => {
          const facing = i === 0 ? 1 : -1;
          return `<circle cx="${cx}" cy="161" r="44" fill="#aa4956" stroke="#e5a1a8" stroke-width="3"/>` +
            `<ellipse cx="${cx}" cy="161" rx="24" ry="26" fill="#853e4d"/>` +
            ag.map((a, j) => {
              const yy = ag.length === 1 ? 161 : 147 + 28 * j;
              const xx = cx + facing * 44;
              return `<rect x="${xx - 10}" y="${yy - 10}" width="20" height="20" rx="3" fill="${colors[a]}"/>` +
                `<text x="${xx}" y="${yy + 5}" text-anchor="middle" style="fill:#14232e;font-size:14px">${a}</text>`;
            }).join('');
        }).join('');
        const hit = s.hits[0];
        const yy = ag.length === 2 ? (hit === 'A' ? 147 : 175) : 161;
        const alpha = s.compatible ? 0 : clamp((progress - 0.1) / 0.3);
        const leftTip = s.left + 54, rightTip = s.right - 54;
        // Two arms end on exposed antigen edges; no free-floating bridge claim.
        part('bridge').innerHTML = hit ?
          `<path d="M${leftTip} ${yy} L360 202 L${rightTip} ${yy} M360 202 V224" fill="none" stroke="#e5bf72" stroke-width="7" opacity="${alpha}"/>` : '';
        part('cell-label').textContent = `Cells: ${par.component === 'red_cells' ? 'donor' : 'recipient'} group ${s.cellGroup}; A/B antigens = ${ag.join(', ') || 'none'}`;
        part('antibody-label').textContent = `Plasma: ${par.component === 'red_cells' ? 'recipient' : 'donor'} group ${s.plasmaGroup}; targets = ${targets(s.plasmaGroup).join(', ') || 'none'}`;
        status.textContent = s.compatible ?
          'Empty A/B intersection: no opposing antibody target in this restricted model. Clinical compatibility is not established.' :
          `Opposing target ${s.hits.join(' and ')}: ${s.bound ? 'schematic bridged endpoint' : 'binding/approach sequence'}. Clumping and hemolysis are different outcomes; reaction kinetics are not modeled.`;
      } else if (kind === 'lymph') {
        part('parcel').setAttribute('cx', s.x); part('parcel').setAttribute('cy', s.y);
        part('entry-flap').setAttribute('d', s.entryOpen ? 'M205 155 L235 135' : 'M205 155 L255 155');
        part('valve-top').setAttribute('d', s.valveOpen ? 'M360 155 L388 194' : 'M360 155 L388 205');
        part('valve-bottom').setAttribute('d', s.valveOpen ? 'M360 255 L388 216' : 'M360 255 L388 205');
        const descriptions = [
          'Entry: a favorable tissue-to-lymph pressure difference opens the overlapping endothelial entry flap. The marker crosses only that opening.',
          'Entry closure and forward transport: the marker is now lymph. Vessel/tissue-generated pressure carries it toward the open collector valve.',
          'Collecting pathway: the marker passes between the valve leaflets into the downstream lumen. Node passage is omitted from this separated-scale path.',
          'Outlet: lymph joins venous blood at a favorable pressure difference. The outlet is an open junction, not passage through an intact venous wall.',
          'Reverse-pressure phase: the collecting valve closes after the marker has passed. Valves oppose backflow but do not supply pumping energy.'
        ];
        const phase = progress < 0.3 ? 0 : progress < 0.47 ? 1 :
          progress < 0.76 ? 2 : progress < 0.85 ? 3 : 4;
        status.textContent = descriptions[phase];
      } else {
        part('recognition').setAttribute('opacity', s.recognition ? '1' : '0');
        part('costimulation').setAttribute('opacity', s.costimulation ? '1' : '0');
        let descendants = '';
        if (s.expansion) {
          const n = s.memory ? 2 : 6;
          descendants = '<rect x="55" y="80" width="600" height="210" rx="12" fill="#14232e"/>' +
            `<text x="95" y="112">${s.memory ? 'Later state: surviving memory population' : 'Later state: selected clone expands'}</text>`;
          for (let i = 0; i < n; i++) {
            const cx = 125 + i * 88;
            descendants += `<circle cx="${cx}" cy="195" r="26" fill="#527b60" stroke="#b4d3a8" stroke-width="3"/>`;
          }
          descendants += '<text class="small" x="95" y="267">Symbol counts illustrate a state change; they are not measured cell counts.</text>';
        }
        part('clone').innerHTML = descendants;
        status.textContent = !s.recognition ? 'Local encounter: the matching conventional CD4 cell has not yet received the depicted recognition signal.' :
          par.costim === 'no' ? 'Peptide–MHC recognition without the selected costimulation does not advance to clonal expansion in this teaching case. Specific tolerance outcomes are not predicted.' :
          s.memory ? 'Effector contraction leaves a surviving memory population. These arbitrary phases do not estimate response duration or persistence.' :
          s.expansion ? 'Selected activated lymphocytes expand and differentiate. An unrelated receptor specificity is not converted into the selected clone.' :
          s.costimulation ? 'Matching recognition plus costimulation and suitable cytokine context supports activation. The two contacts are distinct receptor pairs.' :
          'The T-cell receptor recognizes peptide–MHC II; recognition alone does not establish full naive-cell activation.';
      }
    }
    function tick(now) {
      if (!running) return;
      if (previous !== null) progress = clamp(progress + Math.min(now - previous, 100) * Number(speed.value) / 12000);
      previous = now; draw();
      if (progress >= 1) pause(); else frame = requestAnimationFrame(tick);
    }
    function start() {
      if (progress >= 1) progress = 0;
      running = true; previous = null;
      play.textContent = 'Pause'; play.setAttribute('aria-pressed', 'true');
      frame = requestAnimationFrame(tick);
    }
    play.addEventListener('click', () => running ? pause() : start());
    q('[data-action="replay"]').addEventListener('click', () => { pause(); progress = 0; draw(); start(); });
    q('[data-action="back"]').addEventListener('click', () => { pause(); progress = clamp(progress - 0.2); draw(); });
    q('[data-action="step"]').addEventListener('click', () => { pause(); progress = clamp(progress + 0.2); draw(); });
    seek.addEventListener('input', () => { pause(); progress = Number(seek.value) / 1000; draw(); });
    speed.addEventListener('change', () => { pause(); draw(); });
    panel.querySelectorAll('[data-param]').forEach(el => el.addEventListener('change', () => { pause(); progress = 0; draw(); }));
    const preference = matchMedia('(prefers-reduced-motion: reduce)');
    preference.addEventListener('change', () => { pause(); draw(); });
    document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
    window.addEventListener('beforeprint', () => { pause(); progress = 0; draw(); });
    panel.ch4Controller = { seek(p) { pause(); progress = clamp(p); draw(); },
      getState() { return { progress, running, ...state(kind, progress, params()) }; } };
    draw(); // Always initial paused, including reduced-motion preference.
  }
  root.Ch04 = { encounter, state, initialize };
  if (typeof document !== 'undefined') document.querySelectorAll('[data-ch4]').forEach(initialize);
})(typeof window !== 'undefined' ? window : globalThis);
