/* Focused shared-state/topology/static identity checks; no browser claim. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),R=require('../assets/ch25-render.js');
const data=JSON.parse(fs.readFileSync(path.join(root,'assets/ch25-data.json'),'utf8'));
let maxBalance=0,maxParity=0;
for(const [t,k,m] of [[0,1,1e-100],[2,1,1e-100],[100,100,1e-100],[2,.25,3.7],[3,0,2],[3,2,0]]){const pools=Object.values(R.recyclingAmounts(t,k,m)),sum=pools.reduce((a,b)=>a+b,0);assert(pools.every(v=>v>=0&&v<=m));assert(Math.abs(sum-m)<=1e-12*m);}
for(const args of [[2,1,5e-324],[2,1,1e-323],[2,1,1e-101],[1e300,1,1],[1,1e300,1],[1,1,1e300],[10n**1000n,1,1],[1,10n**1000n,1],[1,1,10n**1000n],[NaN,1,1],[1,Infinity,1],[1,1,true]])assert.throws(()=>R.recyclingAmounts(...args));
for(const i of [0,1,20,40,79,80,81,100,160]){
const s=data.states[i],t=i/20;assert.equal(s.time,t);
for(const [name,k]of [['recycling',1],['slower',.25]]){
const x=k*t,e=Math.exp(-x),a=x*e,q=x*x*e/2,n=Math.max(0,1-e-a-q),actual=Object.values(s[name]);
maxBalance=Math.max(maxBalance,Math.abs(actual.reduce((a,b)=>a+b,0)-1));
const checked=Object.values(R.recyclingAmounts(t,k,1));
actual.forEach((v,j)=>{assert(Math.abs(v-checked[j])<1e-14);assert(Number.isFinite(v)&&v>=0&&v<=1);maxParity=Math.max(maxParity,Math.abs(v-[e,a,q,n][j]));});
}
const y=t<1?0:t<4?1-Math.exp(-(t-1)):(1-Math.exp(-3))*Math.exp(-(t-4));
assert(Math.abs(y-s.photo.closure)<1e-14);assert.equal(s.photo.open_fraction,s.photo.release_proxy);
for(const mode of ['barrier','recycling','photo','field','conduction'])assert(!/NaN|undefined|Infinity/.test(R.render(mode,i,data)));
}
assert(maxBalance<1e-14&&maxParity<1e-14);
assert(data.states[40].recycling.extracellular_glu<data.states[40].slower.extracellular_glu);
assert.equal(data.states[80].photo.light,0);assert(data.states[80].photo.closure>data.states[100].photo.closure);
for(const r of data.routes){assert.equal(r.crosses,r.retina==='nasal');assert.notEqual(r.field,r.hemisphere);}
assert.equal(new Set(data.routes.map(r=>r.eye+':'+r.retina)).size,4);
for(const bad of [-1,161,NaN,Infinity,.5])assert.throws(()=>R.render('photo',bad,data));
assert.throws(()=>R.render('unknown',0,data));
for(const [mode,index]of [['barrier',80],['recycling',40],['photo',80],['field',50],['conduction',125]])assert.equal(R.render(mode,index,data),fs.readFileSync(path.join(root,`assets/ch25-${mode}.svg`),'utf8'));
assert.equal(R.context(),fs.readFileSync(path.join(root,'assets/ch25-eye-ear.svg'),'utf8'));
const h=fs.readFileSync(path.join(root,'chapter-25-glia-barriers-sensation.html'),'utf8');
const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);assert.equal(ids.length,new Set(ids).size);
assert.equal((h.match(/<details class="solution">/g)||[]).length,6);
for(const n of [1,2,3,4,5,6,7,8])assert(ids.includes('ch25-s'+n));
for(const m of h.matchAll(/(?:src|href)="((?:assets|code)\/ch25[-_][^"]+)"/g))assert(fs.existsSync(path.join(root,m[1].split('?')[0])));
console.log(JSON.stringify({status:'PASS',selected_indices:9,maxBalance,maxParity,routes:4,static_exports:6,solutions:6,unique_ids:ids.length,no_browser_claim:true},null,2));
// Isolated control wiring check. This does not parse/render browser SVG or prove UI.
(async()=>{
const vm=require('vm');
for(const mode of ['barrier','recycling','photo','field','conduction']){
const nodes={},events={},frames=[];
const get=id=>nodes[id]??=( {textContent:'',innerHTML:'',value:id==='speed'?'1':'0',setAttribute(k,v){this[k]=v;}} );
const ctx={URLSearchParams,location:{search:'?mode='+mode},Ch25Render:R,
document:{hidden:false,getElementById:get,addEventListener(k,f){events[k]=f;}},
fetch:async()=>({ok:true,json:async()=>data}),matchMedia:()=>({addEventListener(k,f){events.reduce=f;}}),
requestAnimationFrame:f=>frames.push(f),window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/ch25-mechanisms.js'),'utf8'),ctx);
await new Promise(resolve=>setImmediate(resolve));
assert.equal(ctx.window.ch25State().index,0);assert.equal(ctx.window.ch25State().playing,false);
get('next').onclick();assert.equal(ctx.window.ch25State().index,1);
get('seek').value='160';get('seek').oninput();assert.equal(ctx.window.ch25State().index,160);
get('play').onclick();assert.equal(ctx.window.ch25State().index,0);assert(ctx.window.ch25State().playing);
frames.shift()(0);frames.shift()(200);assert(ctx.window.ch25State().index>0);
events.reduce();assert.equal(ctx.window.ch25State().playing,false);
get('reset').onclick();assert.equal(ctx.window.ch25State().index,0);
get('prev').onclick();assert.equal(ctx.window.ch25State().index,0);
assert(get('figure').innerHTML.includes('<svg'));assert(!/NaN|undefined/.test(get('state').textContent));
}
console.log('PASS isolated5-mode initial/seek/step/replay/play/reduced-motion/reset control wiring; no browser rendering claim');
})().catch(e=>{console.error(e);process.exitCode=1;});
