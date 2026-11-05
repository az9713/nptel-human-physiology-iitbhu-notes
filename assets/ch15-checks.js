/* Run with node assets/ch15-checks.js. No browser-interaction claim. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const m = require("./ch15-models.js");
for (const kind of ["nmj", "coupling", "sliding"]) {
  for (let i = 0; i <= 1000; i++) {
    const p=i/1000, s=m.state(kind,p);
    assert.deepEqual(s,m.state(kind,p));
    assert.equal(s.A,1.6);
    assert(Math.abs(s.thin[0][1]-s.thin[0][0]-1)<1e-12);
    assert(Math.abs(s.thin[1][1]-s.thin[1][0]-1)<1e-12);
    assert.equal(s.z[0],-s.z[1]);
    assert(s.H>=0 && s.O>=0 && s.index>=0 && s.index<=6);
    const left=s.thin[0];
    const intersection=Math.max(0,Math.min(left[1],.8)-Math.max(left[0],-.8));
    assert(Math.abs(intersection-s.O)<1e-12);
    if(kind==="nmj" && p>=5/7) {
      assert(Math.abs(s.ap[0]+s.ap[1]-860)<1e-9);
    }
    const svg=m.render(s);
    assert(svg.includes('viewBox="0 0 860 '+(kind==="sliding"?600:445)+'"'));
    assert(!svg.includes("NaN")&&!svg.includes("undefined"));
  }
  for(const p of [0,.25,.5,.75,1]) {
    const file=path.join(__dirname,"ch15-"+kind+"-phase-"+Math.round(p*100)+".svg");
    assert.equal(fs.readFileSync(file,"utf8"),m.render(m.state(kind,p)));
  }
}
const expected=[
  ["H-pump","terminal cytosol","vesicle lumen"],
  ["VAChT-H","vesicle lumen","terminal cytosol"],
  ["VAChT-ACh","terminal cytosol","vesicle lumen"],
  ["terminal-Ca","extracellular","terminal cytosol"],
  ["exocytosis","vesicle lumen","cleft"],
  ["RyR1","SR lumen","muscle cytosol"],
  ["SERCA","muscle cytosol","SR lumen"]
];
assert.deepEqual(m.edges,expected);
assert.throws(()=>m.state("nmj",-1),RangeError);
assert.throws(()=>m.state("nmj",NaN),RangeError);
for(let n=0;n<=10;n++) for(let i=0;i<=1000;i++){
  const L=2.2+1.4*i/1000;
  const force=m.activeForce(L,n);
  assert(force>=0 && force<=100+1e-10);
  if(n>0) assert(force>=m.activeForce(L,n-1)-1e-10);
  assert(Math.abs(force-n*m.activeForce(L,1))<1e-10);
}
assert(Math.abs(m.activeForce(2.6,6)-300/7)<1e-10);
assert.equal(m.activeForce(2.2,6),60);
assert.equal(m.activeForce(3.6,10),0);
assert.throws(()=>m.activeForce(2.0,6),RangeError);
assert.throws(()=>m.activeForce(2.6,6.5),RangeError);
for(const [a,b] of [[1,1.6],[.8,1.5],[1.2,1],[.4,2]]){
  const lo=Math.max(b,2*a),hi=b+2*a;
  for(let i=0;i<=200;i++){
    const L=i===200?hi:lo+(hi-lo)*i/200,g=m.geometry(L,a,b);
    assert(g.H<=g.A+1e-12 && g.I<=2*a+1e-12);
    const intersection=Math.max(0,Math.min(-L/2+a,b/2)-Math.max(-L/2,-b/2));
    assert(Math.abs(intersection-g.O)<1e-12);
  }
  const upper=m.geometry(hi,a,b);
  assert(Math.abs(upper.H-b)<1e-12 && Math.abs(upper.I-2*a)<1e-12);
  assert(Math.abs(upper.O)<1e-12);
  assert.throws(()=>m.geometry(lo-1e-8,a,b),RangeError);
  assert.throws(()=>m.geometry(hi+1e-8,a,b),RangeError);
}
for(const args of [[NaN,1,1.6],[Infinity,1,1.6],[-Infinity,1,1.6],
  [2.6,NaN,1.6],[2.6,1,Infinity],[2.6,0,1.6],[2.6,1,0],
  [3.8,1,1.6],[10,1,1.6]]){
  assert.throws(()=>m.geometry(...args),RangeError);
}
function group(svg,role){
  return svg.match(new RegExp('<g data-role="'+role+'">([\\s\\S]*?)</g>'))?.[1]||"";
}
function firstLine(svg){
  const line=svg.match(/<line\b[^>]*>/)?.[0];
  assert(line,"missing arrow shaft");
  return ["x1","y1","x2","y2"].map(k=>Number(line.match(new RegExp(k+'="([^"]+)"'))[1]));
}
// Flatten the actual emitted membrane path, independently of declared edges.
function segments(d){
  const tokens=d.match(/[A-Za-z]|-?\d+(?:\.\d+)?/g);
  const result=[];let x=0,y=0,i=0;
  function add(nx,ny){result.push([[x,y],[nx,ny]]);x=nx;y=ny;}
  while(i<tokens.length){
    const cmd=tokens[i++];
    if(cmd==="M"){x=Number(tokens[i++]);y=Number(tokens[i++]);}
    else if(cmd==="H")add(Number(tokens[i++]),y);
    else if(cmd==="V")add(x,Number(tokens[i++]));
    else if(cmd==="C"){
      const p=[x,y,...tokens.slice(i,i+6).map(Number)];i+=6;
      for(let j=1;j<=100;j++){
        const t=j/100,u=1-t;
        add(u*u*u*p[0]+3*u*u*t*p[2]+3*u*t*t*p[4]+t*t*t*p[6],
          u*u*u*p[1]+3*u*u*t*p[3]+3*u*t*t*p[5]+t*t*t*p[7]);
      }
    } else assert.fail("unexpected closed/unparsed membrane command: "+cmd);
  }
  return result;
}
for(let index=0;index<7;index++){
  const p=(index+.5)/7;
  const sr=m.render(m.state("coupling",p));
  assert.equal(Boolean(group(sr,"sr-release")),index===1);
  assert.equal(Boolean(group(sr,"cytosolic-calcium-state")),index>=2&&index<=5);
  assert.equal(Boolean(group(sr,"serca-return")),index===6);
  if(index===1)assert.deepEqual(firstLine(group(sr,"sr-release")),[520,145,520,220]);
  if(index===6)assert.deepEqual(firstLine(group(sr,"serca-return")),[720,245,720,150]);
  const nmj=m.render(m.state("nmj",p));
  assert(nmj.includes('data-role="reserve-vesicle"'));
  assert.equal(Boolean(group(nmj,"ach-release")),index===2);
  assert.equal(nmj.includes('data-role="primed-vesicle"'),index<2);
  if(index===2){
    assert(nmj.includes('data-role="open-lumen"'));
    assert(!nmj.match(/<circle[^>]*cx="430"/));
    const release=firstLine(group(nmj,"ach-release"));
    assert.deepEqual(release,[430,155,430,270]);
    const membrane=nmj.match(/data-role="terminal-membrane" d="([^"]+)"/)[1];
    const pieces=segments(membrane);
    assert.deepEqual(pieces[0][0],[80,200]);
    assert.deepEqual(pieces.at(-1)[1],[770,200]);
    for(const [[x1,y1],[x2,y2]] of pieces){
      if(x1===x2){assert(!(x1===430 && Math.max(y1,y2)>=155 && Math.min(y1,y2)<=270));}
      else{
        const t=(430-x1)/(x2-x1),y=y1+t*(y2-y1);
        assert(!(t>=0&&t<=1&&y>=155&&y<=270),"ACh path crosses closed membrane");
      }
    }
    // Both neck edges descend to membrane level, leaving the central pore open.
    assert(pieces.some(([[x1,y1],[x2,y2]])=>x1===410&&x2===410&&y1===200&&y2===185));
    assert(pieces.some(([[x1,y1],[x2,y2]])=>x1===450&&x2===450&&y1===185&&y2===200));
  }
  if(index>=3)assert(nmj.includes("Completed release"));
  if(index===5){
    assert(nmj.includes('data-role="sarcolemma" d="M80 300 H770"'));
    const ap=group(nmj,"ap-propagation");
    const fronts=[...ap.matchAll(/data-role="ap-front" cx="([^"]+)" cy="([^"]+)"/g)];
    assert.equal(fronts.length,2);assert(fronts.every(x=>Number(x[2])===300));
    const shafts=[...ap.matchAll(/<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/g)]
      .filter(x=>Math.abs(Number(x[1])-Number(x[3]))>20);
    assert.equal(shafts.length,2);assert(shafts.every(x=>Number(x[2])===300&&Number(x[4])===300));
  }
}
console.log("PASS: 3003 deterministic states, 15 exact SVG snapshots, 7 compartment edges");
console.log("PASS: 11011 force/recruitment states, domain, additivity and endpoints");
console.log("PASS: finite band-domain endpoints/nondefault/nonfinite checks; seven-state flux/pore/AP topology");
