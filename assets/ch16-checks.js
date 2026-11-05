/* Numerical and topology/controls contract checks; actual UI inspection separate. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const m = require('./ch16-models.js');
const close = (a,b) => assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
const f = m.flow(1200,1-625/1200,125);
close(f.rpf,625);close(f.cells,575);close(f.efferentPlasma,500);
close(f.efferentBlood+f.gfr,1200);close(f.ff,.2);
for(let i=0;i<=1000;i++) {
  const phase=i/1000;
  const s=m.state('filtration',phase);
  close(s.nfp,10-5*phase);close(s.signedFlux,125-62.5*phase);
  const r=m.state('resistance',phase);
  close(r.afferent.q,r.efferent.q);
  assert.ok(r.afferent.pgc<=55 && r.efferent.pgc>=55);
  assert.ok(m.state('routes',phase).step>=0 && m.state('routes',phase).step<=3);
}
close(m.state('resistance',1).afferent.pgc,40);
close(m.state('resistance',1).efferent.pgc,70);
close(m.pressure(55,20,30,0,6.25).signedFlux,31.25);
assert.ok(m.pressure(55,30,30,0,12.5).signedFlux<0);
for(const args of [[1200,-1,125],[1200,1,125],[1200,.5,700],[NaN,.5,125]]) assert.throws(()=>m.flow(...args));
for(const args of [[1,1,10,10],[1,1,9,10]]) assert.throws(()=>m.resistance(...args));
for(const value of [NaN,Infinity,-Infinity]) {
  for(let index=0;index<4;index++) {
    const args=[1,1,100,10];args[index]=value;
    assert.throws(()=>m.resistance(...args));
  }
}
for(const name of ['routes','filtration','resistance']) {
  const html=fs.readFileSync(path.join(__dirname,`ch16-${name}.html`),'utf8');
  for(const id of ['play','replay','speed','seek','state']) assert.ok(html.includes(`id="${id}"`));
  assert.ok(html.includes('class="static"'));
  assert.ok(html.includes('role="img"'));
}
const routes=fs.readFileSync(path.join(__dirname,'ch16-routes.html'),'utf8');
for(let i=0;i<4;i++) assert.ok(routes.includes(`data-step="${i}"`));
console.log('PASS:1001 states ×3 modes, conserved flows, pressure signs, one-kidney scaling, invalid domains and control/topology contracts. Browser rendering and interaction remain separate.');
