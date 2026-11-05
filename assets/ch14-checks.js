'use strict';
const assert=require('node:assert/strict');
const {remodeling,loading}=require('./ch14-models.js');
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} versus ${b}`);
const cross=(p,f)=>p[0]*f[1]-p[1]*f[0];
let oldFluid=Infinity;
for(let i=0;i<=1000;i++){
  const p=i/1000,r=remodeling(p),l=loading(p);
  assert.ok(r.bone>=9 && r.bone<=10 && r.osteoid>=0);
  near(r.bone+r.osteoid,10-r.removed+.9*r.deposited);
  near(l.fluid+l.solid,600); assert.ok(l.fluid<=oldFluid);oldFluid=l.fluid;
  near(cross(l.loadPoint,l.loadForce),-15);
  near(cross(l.tendonPoint,l.tendonForce),15);
  near(Math.hypot(...l.loadPoint),.3);near(Math.hypot(...l.tendonPoint),.04);
  // Pivot reaction balances vector force at every prescribed orientation.
  near(l.loadForce[0]+l.tendonForce[0]+l.reactionForce[0],0);
  near(l.loadForce[1]+l.tendonForce[1]+l.reactionForce[1],0);
  near(Math.hypot(...l.reactionForce),325);
  // Geometric arrow-shaft/head bounds for the enlarged loading viewBox.
  // Text glyphs, responsive layout and actual rendering still need browser QA.
  for(const [point,force] of [[[0,0],l.reactionForce],[l.loadPoint,l.loadForce],[l.tendonPoint,l.tendonForce]]){
    const x=135+550*point[0],y=240-550*point[1];
    const dx=.2*force[0],dy=-.2*force[1],a=Math.atan2(dy,dx);
    const points=[[x,y],[x+dx,y+dy],
      [x+dx-12*Math.cos(a-.45),y+dy-12*Math.sin(a-.45)],
      [x+dx-12*Math.cos(a+.45),y+dy-12*Math.sin(a+.45)]];
    for(const [px,py] of points)assert.ok(px>=0 && px<=700 && py>=85 && py<=315);
  }
}
near(remodeling(0).bone,10);near(remodeling(1).bone,9.9);near(remodeling(1).osteoid,0);
near(loading(0).fluid,480);near(loading(1).t,90);
assert.deepEqual(remodeling(-1),remodeling(0));assert.deepEqual(loading(2),loading(1));
assert.throws(()=>loading(NaN));assert.throws(()=>remodeling(Infinity));
console.log('PASS:1001 states; tissue accounting, load sharing, lever torque/vector balances, geometric constraints, endpoints and invalid phases');
