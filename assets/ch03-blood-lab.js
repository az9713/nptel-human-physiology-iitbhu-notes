'use strict';
// The single state variable p is presentation progress, not physiological time.
const ui = Object.fromEntries(['mode', 'play', 'replay', 'previous', 'next',
  'speed', 'seek', 'phase', 'drawing', 'explanation', 'alternative',
  'progress-label', 'scene-title', 'scene-desc'].map(id => [id, document.getElementById(id)]));
const motion = matchMedia('(prefers-reduced-motion: reduce)');
let p = 0;
let playing = false;
let last = null;
const phases = {
  epo: [
    ['Reduced tissue oxygen availability', 'The renal stimulus concerns local oxygen supply relative to use. Cell count alone is not the sensor input.'],
    ['Kidney → EPO signal', 'Kidneys increase an erythropoietic hormone signal; the pulse shown is an explanatory marker, not a measured hormone concentration.'],
    ['EPO → marrow precursors', 'Responsive erythroid precursors increase production and mature. Mature circulating red cells do not divide to replenish themselves.'],
    ['More red cells enter circulation', 'Increased production can restore a depleted population if marrow and required nutrients are available. The cell icons are not a count scale.'],
    ['Feedback toward the original stimulus', 'Improved oxygen transport can reduce the renal oxygen-supply imbalance. No gain, delay or recovery curve is fitted here.']
  ],
  injury: [
    ['Intact blood-facing barrier', 'Endothelium separates circulating platelets from underlying collagen-rich matrix. Blood continues flowing through the lumen.'],
    ['Injury → platelet adhesion', 'Exposed matrix with VWF supports platelet capture through GPIb–IX–V; collagen receptors support activation and stable attachment.'],
    ['Activation and interplatelet aggregation', 'Activated αIIbβ3 binds bridging ligands such as fibrinogen. ADP, thromboxane and thrombin amplify recruitment.'],
    ['Surface coagulation → fibrin reinforcement', 'TF–VIIa initiation and IXa–VIIIa amplification support Xa–Va-dependent thrombin generation; thrombin generates fibrin and XIIIa crosslinks it. This overlaps platelet recruitment.'],
    ['Platelet contraction and tissue repair', 'Platelet force compacts the fibrin-supported clot. The drawing reduces its width as an explanatory geometric change, not a constitutive mechanics prediction.'],
    ['Regulated fibrinolysis', 'tPA helps generate plasmin from plasminogen; plasmin cleaves fibrin. Repair and controlled breakdown can overlap rather than waiting for one universal start time.']
  ],
  targets: [
    ['Platelet response', 'Antiplatelet interventions affect activation or aggregation. The highlighted route is a mechanism category, not a drug-selection recommendation.'],
    ['Heparin → antithrombin → Xa / IIa inhibition', 'Antithrombin is a serpin inhibitor. Heparin enhances its inhibitory action; this is not direct thrombin inhibition by heparin or fibrin cleavage.'],
    ['Warfarin → vitamin K recycling', 'VKORC1-related recycling supports functionally active II, VII, IX, X and proteins C/S. This is a production/maturation mechanism, not instantaneous removal of existing factors.'],
    ['EDTA / citrate → specimen calcium availability', 'Collection additives alter the laboratory specimen. Potassium EDTA tubes are not calcium-disodium edetate lead-chelation preparations.'],
    ['Plasmin → existing fibrin cleavage', 'Fibrinolysis acts on the clot substrate. Preventing new coagulation and breaking down existing fibrin are distinct operations.']
  ]
};
function phaseIndex(mode, progress) {
  return Math.min(phases[mode].length - 1, Math.floor(progress * phases[mode].length));
}
function text(x, y, content, size = 17, color = '#edf4f6') {
  return `<text x="${x}" y="${y}" style="font-size:${size}px;fill:${color}">${content}</text>`;
}
function rect(x, y, w, h, fill, rx = 10) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`;
}
function arrow(x1, y1, x2, y2, color = '#d1b46f') {
  return `<path d="M${x1} ${y1}L${x2} ${y2}" fill="none" stroke="${color}" stroke-width="3"/><circle cx="${x2}" cy="${y2}" r="5" fill="${color}"/>`;
}
function epoScene(i) {
  const nodes = [
    [30, 100, 'Renal tissue', 'O₂ supply/use'],
    [255, 100, 'EPO signal', 'Blood plasma'],
    [480, 100, 'Bone marrow', 'Erythroid precursors'],
    [705, 100, 'Circulation', 'Red-cell population']
  ];
  let out = text(25, 35, 'Causal sequence: human erythropoiesis; compartments shown separately', 19);
  nodes.forEach(([x, y, a, b], n) => {
    out += rect(x, y, 165, 95, i === Math.min(n, 3) ? '#526947' : '#294b5b');
    out += text(x + 12, y + 33, a) + text(x + 12, y + 65, b, 15);
    if (n < 3) out += arrow(x + 170, y + 45, x + 215, y + 45);
  });
  out += arrow(785, 220, 785, 270, '#76c8bd') + arrow(785, 270, 115, 270, '#76c8bd') + arrow(115, 270, 115, 215, '#76c8bd');
  out += text(225, 303, 'Improved transport reduces the original renal stimulus', 19, '#97e2d4');
  if (i === 1 || i === 2) {
    const x = i === 1
      ? 210 + 220 * ((p * 5) % 1)
      : 435 + 40 * ((p * 5) % 1);
    out += `<circle cx="${x}" cy="145" r="9" fill="#ead086"/>`;
  }
  for (let n = 0; n < (i >= 3 ? 5 : 2); n++) {
    out += `<ellipse cx="${726 + n * 26}" cy="215" rx="10" ry="6" fill="#e0787e"/>`;
  }
  return out;
}
function injuryScene(i) {
  const local = p * 6 - Math.floor(p * 6);
  const contraction = i >= 4 ? (i === 4 ? local : 1) : 0;
  const width = 230 - 65 * contraction;
  const center = 450;
  let out = text(25, 30, 'Vessel-wall sectional schematic: lumen above, tissue below', 19);
  out += rect(20, 65, 860, 180, '#452b3c', 0);
  out += rect(20, 245, 860, 90, '#4c4a37', 0);
  out += text(35, 323, 'Subendothelial tissue / exposed matrix', 18);
  out += text(35, 92, 'Blood flow →', 17);
  for (let n = 0; n < 6; n++) {
    const x = 45 + ((n * 145 + p * 450) % 800);
    out += `<ellipse cx="${x}" cy="120" rx="19" ry="10" fill="#d56373"/>`;
  }
  out += rect(20, 237, i === 0 ? 860 : 315, 17, '#78b6c1', 2);
  if (i > 0) out += rect(565, 237, 315, 17, '#78b6c1', 2);
  if (i >= 1) {
    out += `<path d="M340 262L370 247L400 263L430 247L460 263L490 247L520 263L550 247" fill="none" stroke="#e0c079" stroke-width="5"/>`;
    out += text(335, 293, 'Matrix + VWF', 17);
  }
  if (i >= 1 && !(i === 5 && p >= 0.999)) {
    const number = i === 1 ? 3 : 9;
    const opacity = i === 5 ? Math.max(0, 1 - local) : 1;
    for (let n = 0; n < number; n++) {
      const x = center - width / 2 + 20 + (n % 5) * width / 5;
      const y = 222 - Math.floor(n / 5) * 27;
      out += `<ellipse cx="${x}" cy="${y}" rx="16" ry="10" fill="#ddc065" opacity="${opacity}"/>`;
      if (i >= 2 && n > 0) out += `<path d="M${x - 24} ${y}L${x - 13} ${y}" stroke="#95d2e0" stroke-width="3" opacity="${opacity}"/>`;
    }
  }
  if (i >= 3) {
    const fraction = i === 5 ? (p >= 0.999 ? 0 : 1 - local) : 1;
    for (let n = 0; n < 7 * fraction; n++) {
      const x = center - width / 2 + n * width / 7;
      out += `<path d="M${x} 230L${center + width / 2 - n * width / 7} 172" stroke="#e1a38b" stroke-width="3"/>`;
    }
    out += text(580, 167, i === 5 ? 'tPA → plasmin → cleavage' : 'Thrombin → fibrin → XIIIa links', 17);
    out += text(580, 197, i === 4 ? 'Platelet force compacts network' : 'Reinforcement ≠ platelet capture', 16);
  }
  if (i === 5) out += rect(335, 237, 230 * Math.min(1, local + (p >= 0.999 ? 1 : 0)), 17, '#78b6c1', 2);
  return out;
}
function targetScene(i) {
  const labels = [
    ['Platelets', 'Activation / αIIbβ3 bridges', 'Antiplatelet category'],
    ['Coagulation enzymes', 'AT inhibits Xa and IIa', 'Heparin enhances AT'],
    ['Vitamin K cycle', 'Functional II / VII / IX / X, C / S', 'Warfarin affects recycling'],
    ['Specimen calcium', 'Calcium-dependent assembly', 'EDTA / citrate in tube'],
    ['Existing fibrin', 'Plasmin cleaves fibers', 'Fibrinolysis category']
  ];
  let out = text(25, 28, 'Sequential reveal compares targets; row order is not treatment timing', 19);
  labels.forEach(([a, b, c], n) => {
    out += rect(20, 46 + n * 58, 860, 49, n === i ? '#536444' : '#274856', 7);
    out += text(35, 77 + n * 58, a, 17) + text(250, 77 + n * 58, b, 16) + text(610, 77 + n * 58, c, 16);
  });
  return out;
}
function render() {
  const mode = ui.mode.value;
  const i = phaseIndex(mode, p);
  const [heading, explanation] = phases[mode][i];
  ui.phase.textContent = `${i + 1}/${phases[mode].length}: ${heading}`;
  ui.explanation.textContent = explanation;
  ui['scene-title'].textContent = heading;
  ui['scene-desc'].textContent = explanation;
  ui.alternative.textContent = `Complete static sequence: ${phases[mode].map(a => a[0]).join(' → ')}.`;
  ui.drawing.innerHTML = mode === 'epo' ? epoScene(i) : mode === 'injury' ? injuryScene(i) : targetScene(i);
  ui.seek.value = p;
  ui['progress-label'].textContent = `${Math.round(p * 100)}%`;
  ui.play.textContent = playing ? 'Pause' : 'Play';
  ui.play.setAttribute('aria-pressed', String(playing));
}
function pause() { playing = false; last = null; render(); }
ui.play.onclick = () => {
  if (p >= 1) p = 0;
  playing = !playing;
  last = null;
  render();
};
ui.replay.onclick = () => { p = 0; pause(); };
ui.mode.onchange = () => { p = 0; pause(); };
ui.seek.oninput = () => { p = Number(ui.seek.value); pause(); };
ui.previous.onclick = () => {
  const count = phases[ui.mode.value].length;
  p = Math.max(0, (phaseIndex(ui.mode.value, p) - 1) / count);
  pause();
};
ui.next.onclick = () => {
  const count = phases[ui.mode.value].length;
  p = Math.min(1, (phaseIndex(ui.mode.value, p) + 1) / count);
  pause();
};
motion.addEventListener('change', pause);
function frame(now) {
  if (playing) {
    if (last !== null) p = Math.min(1, p + Math.min(0.1, (now - last) / 1000) * Number(ui.speed.value) / 24);
    last = now;
    if (p >= 1) playing = false;
    render();
  } else last = null;
  requestAnimationFrame(frame);
}
render();
requestAnimationFrame(frame);
