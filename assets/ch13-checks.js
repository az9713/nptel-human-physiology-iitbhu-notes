/* Run: node assets/ch13-checks.js. Pure-state/DOM-double checks, not browser QA. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const model = require('./ch13-models.js');
for (const time of [0,1]) {
  assert.throws(() => model.evolve([1e308,1e308,1e308,1e308],[1,1,1],time),
    /Total pool amount exceeds finite range/);
}
assert.throws(() => model.evolve([0,Number.MAX_VALUE,0,0],[1,1,1],2),
  /Propagation exceeds finite range/);
let samples = 0;
for (let i=0;i<=10000;i++) {
  const p=i/10000;
  for (const name of ['protein','lipid']) {
    const s=model[name](p);
    assert(Number.isFinite(s.x)&&Number.isFinite(s.y));
    let radius=name==='protein'?11:s.vesicle?20:s.identity==='TAG droplet'?25:11;
    if(Math.abs(s.x-250)<=radius) assert(s.y-radius>=163&&s.y+radius<=197);
    if(Math.abs(s.x-600)<=radius) assert(s.y-radius>=277&&s.y+radius<=323);
    if(name==='lipid'&&Math.abs(s.x-820)<=radius) {
      assert(s.y-radius>=298&&s.y+radius<=342);
      assert.equal(s.identity,'chylomicron');assert.equal(s.vesicle,false);
    }
    if(name==='lipid'&&s.x>600)assert.equal(s.vesicle,false);
    if(name==='protein'&&s.x>=600)assert.equal(s.identity,'amino acids');
    samples++;
  }
  const a=model.evolve([100,0,0,0],[1,1,1],6*p);
  const b=model.evolve([100,0,0,0],[0.2,1,1],6*p);
  for(const row of [a,b]) {
    assert(Math.min(...row)>=0);
    assert(Math.abs(row.reduce((x,y)=>x+y,0)-100)<1e-10);
  }
}
for(const t of [0,0.1,2,6,20]) {
  const values=[[0.2,1,1],[1,0.2,1],[1,1,0.2]].map(r=>model.evolve([100,0,0,0],r,t));
  assert(Math.max(...values.map(r=>r[3]))-Math.min(...values.map(r=>r[3]))<1e-10);
}
function fakeNode() {
  return {value:'1',textContent:'',disabled:false,children:[],events:{},attrs:{},
    setAttribute(k,v){this.attrs[k]=String(v);},
    appendChild(n){this.children.push(n);},
    replaceChildren(){this.children=[];},
    addEventListener(k,f){this.events[k]=f;}};
}
for(const mode of ['protein','lipid','failure']) {
  const ids=['scene','phase','seek','progress','play','motion-note','replay','previous','next','speed'];
  const nodes=Object.fromEntries(ids.map(k=>[k,fakeNode()]));
  const media={matches:false,addEventListener(k,f){this.change=f;}};
  let raf;
  const document={body:{dataset:{mode}},hidden:false,events:{},
    getElementById:id=>nodes[id],createElementNS:()=>fakeNode(),
    addEventListener(k,f){this.events[k]=f;}};
  const window={matchMedia:()=>media,requestAnimationFrame:f=>{raf=f;}};
  vm.runInNewContext(fs.readFileSync(require.resolve('./ch13-models.js'),'utf8'),
    {window,document,globalThis:window});
  assert.equal(nodes.play.textContent,'Play');
  nodes.next.events.click();assert(Number(nodes.seek.value)>0);
  nodes.previous.events.click();assert.equal(Number(nodes.seek.value),0);
  nodes.play.events.click();raf(0);raf(100);assert(Number(nodes.seek.value)>0);
  nodes.play.events.click();const paused=nodes.seek.value;raf(200);assert.equal(nodes.seek.value,paused);
  nodes.seek.value='700';nodes.seek.events.input();assert.equal(nodes.seek.value,'700');
  nodes.replay.events.click();assert.equal(nodes.seek.value,'0');
  nodes.speed.value='2';nodes.speed.events.change();nodes.play.events.click();
  raf(0);raf(100);assert(Number(nodes.seek.value)>=16);
  document.hidden=true;document.events.visibilitychange();assert.equal(nodes.play.textContent,'Play');
  media.matches=true;media.change();assert.equal(nodes.play.disabled,true);
  assert(nodes['motion-note'].textContent.includes('Reduced motion'));
  nodes.next.events.click();assert(Number(nodes.seek.value)>0);
}
console.log(`PASS: ${samples} schematic topology states; conservation, rate-order symmetry; control logic in DOM doubles for 3 modes. Actual browser/mobile/print QA remains separate.`);
