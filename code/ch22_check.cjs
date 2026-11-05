'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process'),path=require('node:path');
const root=path.resolve(__dirname,'..'),a=require('../assets/ch22-model.js');let count=0;
const equal=(x,y)=>{assert.deepEqual(x,y);count++;};
equal(a.latency(),{branch:20,local:24,motor:34,effector:39,ascending:70,central:76});
equal(a.latency({ascendingVelocity:10}).central,126);equal(a.latency({ascendingVelocity:10}).effector,39);
for(const k of Object.keys(a.defaults)){
 const valid=k.endsWith('Velocity')?[.1,1,200]:k.endsWith('Length')?[0,1,10]:[0,1,100];
 for(const x of valid){const q=a.latency({[k]:x});assert(Object.values(q).every(Number.isFinite));assert(q.local>=q.branch&&q.motor>=q.local&&q.effector>=q.motor&&q.central>=q.ascending&&q.ascending>=q.branch);count++;}
 for(const x of [-1,NaN,Infinity,-Infinity,true,'1',null,undefined,k.endsWith('Velocity')?0:1001]){assert.throws(()=>a.latency({[k]:x}));count++;}
}
for(const q of [null,[],2,{unknown:1},JSON.parse('{"__proto__":1}'),{toString:1}]){assert.throws(()=>a.latency(q));count++;}
for(const mode of ['route','reflex'])for(let i=0;i<=100;i++){
 const s=a.state(i,mode),v=a.render(i,mode);assert(!v.includes('NaN')&&!v.includes('Infinity'));equal(v,a.render(i,mode));
 const ids=[...v.matchAll(/data-edge="([^"]+)"/g)].map(m=>m[1]);equal(ids,mode==='reflex'?['afferent','ascending','output','local-integration']:['afferent','ascending','output','central-output']);
 equal(s.localResponse,mode==='reflex'&&i>=39);equal(s.brainwardInformation,i>=(mode==='reflex'?70:45));equal(s.centralProcessingComplete,i>=(mode==='reflex'?76:60));
}
for(const x of [-1,101,NaN,Infinity,true,'1']){assert.throws(()=>a.state(x));count++;}assert.throws(()=>a.state(0,'unknown'));count++;
const saved=JSON.parse(fs.readFileSync(path.join(root,'assets/ch22-pathway-states.json'),'utf8'));equal(saved.arrivals,a.latency());equal(saved.frames,Array.from({length:101},(_,t)=>a.state(t,'reflex')));
for(const mode of ['route','reflex'])equal(fs.readFileSync(path.join(root,'assets/ch22-'+mode+'.svg'),'utf8'),a.render(100,mode));
// A branch change cannot retime the unchanged motor path; a common-input change must retime both.
for(let i=1;i<=80;i++){let v=.1+i*2,q=a.latency({ascendingVelocity:v});equal(q.effector,39);let p=a.latency({afferentLength:i/10});assert(Math.abs((p.effector-39)-(p.central-76))<1e-10);count++;}
const cases=Array.from({length:101},(_,i)=>({afferentLength:i/10,afferentVelocity:.1+i*1.9,motorLength:(100-i)/10,motorVelocity:200-i,ascendingLength:i/20,ascendingVelocity:100,localDelay:i,effectorDelay:100-i,centralDelay:i/2}));
const py="import sys,json,runpy; a=runpy.run_path('code/ch22_pathways.py'); print(json.dumps([a['latency'](p) for p in json.load(sys.stdin)],allow_nan=False))";
const out=cp.spawnSync('python',['-X','utf8','-c',py],{cwd:root,input:JSON.stringify(cases),encoding:'utf8'});assert.equal(out.status,0,out.stderr);equal(JSON.parse(out.stdout),cases.map(p=>a.latency(p)));
for(const id of ['branch','local','brain']){let [x,y]=a.nodes[id],r=id==='brain'?44:34;assert(x-r>=300&&x+r<=820&&y-r>=105&&y+r<=555);count++;}assert(a.nodes.muscle[0]-34>820);count++;
console.log(count+' bounded state/domain/branch/renderer/geometry checks passed; 101 nondefault Python/JS object-parity cases included. Actual browser controls remain separate.');
