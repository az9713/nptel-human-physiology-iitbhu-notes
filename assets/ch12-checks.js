'use strict';
// Reproducible non-browser checks; actual UI and print inspection are separate.
const assert = require('node:assert/strict');
const m = require('./ch12-models.js');
for (let frame = 0; frame <= 1000; frame++) {
  const p = frame / 1000;
  const t = m.transit(p), h = m.hydrolysis(p), a = m.absorption(p);
  assert.equal(h.residues, 10);
  assert.equal(h.positions.length, 10);
  for (let i = 0; i < 10; i++) for (let j = i + 1; j < 10; j++) {
    assert.ok(Math.hypot(h.positions[i].x-h.positions[j].x,
      h.positions[i].y-h.positions[j].y) >= 44, 'residue marker collision');
  }
  if (p < 0.6) assert.equal(h.edges[7].opacity, 1, 'branch cut by amylase');
  if (p >= 0.65) assert.ok(h.edges.every(e => e.opacity === 0));
  const wall = t.wall.reduce((u,v) =>
    Math.abs(v.x-t.x) < Math.abs(u.x-t.x) ? v : u);
  assert.ok(200-18 > wall.top+9 && 200+18 < wall.bottom-9,
    'bolus overlaps tube wall');
  assert.ok(t.x >= 120 && t.x <= 700);
  for (const token of [a.glucose, a.fructose]) {
    if (token.y > 167 && token.y < 193) {
      assert.ok(Math.abs(token.x-240) <= 17 ||
        Math.abs(token.x-520) <= 17, 'apical crossing outside protein');
    }
    if (token.y > 377 && token.y < 403) {
      assert.ok(token.x >= 353 && token.x <= 417,
        'basolateral crossing outside GLUT2');
    }
  }
  assert.ok(Math.hypot(a.glucose.x-a.fructose.x,
    a.glucose.y-a.fructose.y) >= 26, 'sugar marker collision');
  for (const sodium of a.sodium) {
    if (sodium.y > 173 && sodium.y < 187) {
      assert.ok(sodium.x >= 217 && sodium.x <= 263,
        'sodium crossing outside SGLT1');
    }
    assert.ok(Math.hypot(sodium.x-a.glucose.x,
      sodium.y-a.glucose.y) >= 20, 'coupled markers overlap');
  }
}
assert.equal(m.transit(-1).phase, 0);
assert.equal(m.transit(2).phase, 1);
assert.equal(m.hydrolysis(0).edges[2].opacity, 1);
assert.equal(m.hydrolysis(.2).edges[2].opacity, 0);
console.log('PASS:1001 phases; luminal containment, correct membrane apertures, residue/marker separation, branch retention, endpoints. UI not tested.');
