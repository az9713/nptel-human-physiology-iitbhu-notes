/* Original abstract teaching states; no anatomical kinematics or fitted laws. */
(function(root){
  'use strict';
  const clamp=x=>Math.min(1,Math.max(0,x));
  function phase(p){if(!Number.isFinite(p))throw new Error('finite phase required');return clamp(p);}
  function remodeling(p){
    p=phase(p);
    const removed=Math.min(1,p/.25), deposited=clamp((p-.4)/.4), mineralized=clamp((p-.8)/.2);
    const stage=p<.25?'Resorption':p<.4?'Reversal':p<.8?'Osteoid deposition':'Mineralization';
    return {p,stage,removed,deposited,mineralized,
      bone:10-removed+.9*deposited*mineralized,osteoid:.9*deposited*(1-mineralized)};
  }
  function loading(p){
    p=phase(p); const t=90*p,fluid=480*Math.exp(-t/30),solid=600-fluid;
    const angle=Math.PI/3*p,c=Math.cos(angle),s=Math.sin(angle);
    // Force vectors stay transverse to the ideal lever; no gravity inference.
    return {p,t,fluid,solid,angle,tendon:375,reaction:325,
      loadPoint:[.3*c,.3*s],tendonPoint:[.04*c,.04*s],
      loadForce:[50*s,-50*c],tendonForce:[-375*s,375*c],reactionForce:[325*s,-325*c]};
  }
  root.Ch14={remodeling,loading};
  if(typeof module!=='undefined')module.exports=root.Ch14;
  if(typeof document==='undefined')return;
  const kind=document.body.dataset.model;
  const seek=document.getElementById('seek'),play=document.getElementById('play'),speed=document.getElementById('speed');
  let p=0,playing=false,last=null;
  const ns='http://www.w3.org/2000/svg',svg=document.getElementById('scene');
  function node(tag,attrs,text){const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;svg.append(e);return e;}
  function text(x,y,t){return node('text',{x,y,fill:'#e7edf3','font-size':17},t);}
  function rect(x,y,w,h,color){return node('rect',{x,y,width:w,height:h,fill:color,rx:3});}
  function line(x1,y1,x2,y2,color,width=4){return node('line',{x1,y1,x2,y2,stroke:color,'stroke-width':width});}
  function arrow(x,y,dx,dy,color){line(x,y,x+dx,y+dy,color);const a=Math.atan2(dy,dx);line(x+dx,y+dy,x+dx-12*Math.cos(a-.45),y+dy-12*Math.sin(a-.45),color,3);line(x+dx,y+dy,x+dx-12*Math.cos(a+.45),y+dy-12*Math.sin(a+.45),color,3);}
  function render(){
    svg.replaceChildren();node('title',{},kind==='remodeling'?'Abstract remodeling ledger':'Separate transverse-force lever and held-load ledger');
    if(kind==='remodeling'){
      const q=remodeling(p); text(18,30,q.stage+' — compressed presentation phase, not biological days');
      rect(30,145,620,100,'#637b8b');
      rect(200,145,180,50*q.removed,'#0f202a');
      rect(200,195-45*q.deposited,180,45*q.deposited,'#e3ad63');
      rect(200,195-45*q.deposited*q.mineralized,180,45*q.deposited*q.mineralized,'#83c4b7');
      text(30,95,'Symbolic tissue surface — no cell shape or microscopic scale');
      text(30,285,'Gray: original mineralized tissue; amber: osteoid; green: newly mineralized');
      text(30,325,`Mineralized inventory: ${q.bone.toFixed(3)} selected units`);
      text(30,355,`Unmineralized osteoid: ${q.osteoid.toFixed(3)} selected units`);
      text(30,395,'Initial10; remove1; deposit0.9; final9.9. No cell-count or mass-density claim.');
      document.getElementById('state').textContent=`${q.stage}. Mineralized ${q.bone.toFixed(3)} units; osteoid ${q.osteoid.toFixed(3)}. The selected final deficit is0.1.`;
    }else{
      const q=loading(p),ox=135,oy=240,scale=550;
      const pt=a=>[ox+scale*a[0],oy-scale*a[1]];
      const end=pt(q.loadPoint),attach=pt(q.tendonPoint);
      text(18,28,'Panel A: prescribed abstract rotation; forces rotate with lever');
      line(ox,oy,...end,'#e6edf2',10);node('circle',{cx:ox,cy:oy,r:9,fill:'#e3ad63'});
      const forceScale=.2;
      arrow(...end,q.loadForce[0]*forceScale,-q.loadForce[1]*forceScale,'#e3ad63');
      arrow(...attach,q.tendonForce[0]*forceScale,-q.tendonForce[1]*forceScale,'#69d7c5');
      arrow(ox,oy,q.reactionForce[0]*forceScale,-q.reactionForce[1]*forceScale,'#cf9be8');
      text(18,55,'Pivot O; load arm d = 0.30 m; tendon arm r = 0.04 m');
      const armCaption=text(18,80,'Forces are perpendicular to the lever; attachment lengths are moment arms.');
      armCaption.setAttribute('textLength','650');
      armCaption.setAttribute('lengthAdjust','spacingAndGlyphs');
      text(ox-28,oy+5,'O');
      text(455,95,'Applied load 50 N');text(455,125,'Tendon 375 N');
      text(455,155,'Reaction 325 N').setAttribute('fill','#cf9be8');
      text(455,185,'Torque balance15N·m');text(455,215,'Angle is presentation only');
      text(18,330,'Panel B: separate held-load model — no anatomical contact geometry');
      rect(30,350,600*q.fluid/600,32,'#69d7c5');rect(30+q.fluid,350,q.solid,32,'#e3ad63');
      text(30,415,`Synthetic time ${q.t.toFixed(1)} s; total600 N`);
      text(30,445,`Fluid ${q.fluid.toFixed(3)} N; solid ${q.solid.toFixed(3)} N`);
      text(30,480,'No cartilage deformation, patient coefficients or knee trajectory predicted.');
      document.getElementById('state').textContent=`Independent held-load time ${q.t.toFixed(1)} seconds. Fluid ${q.fluid.toFixed(3)} newtons plus solid ${q.solid.toFixed(3)} equals600. Lever angle is a separate prescribed presentation coordinate.`;
    }
    seek.value=String(p*1000);
    document.getElementById('phase').textContent=`Phase ${(p*100).toFixed(1)}%`;
  }
  function pause(){playing=false;play.textContent='Play';play.setAttribute('aria-pressed','false');last=null;}
  play.addEventListener('click',()=>{if(playing)pause();else{if(p===1)p=0;playing=true;last=null;play.textContent='Pause';play.setAttribute('aria-pressed','true');}});
  seek.addEventListener('input',()=>{pause();p=Number(seek.value)/1000;render();});
  document.getElementById('replay').addEventListener('click',()=>{pause();p=0;render();});
  document.getElementById('previous').addEventListener('click',()=>{pause();p=clamp(p-.1);render();});
  document.getElementById('next').addEventListener('click',()=>{pause();p=clamp(p+.1);render();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');reduced.addEventListener('change',()=>{pause();render();});
  // Always paused initially, including reduced motion. Animation requires explicit Play.
  function tick(now){if(playing){if(last!==null)p=clamp(p+(now-last)/1000*Number(speed.value)/12);last=now;render();if(p===1)pause();}requestAnimationFrame(tick);}
  render();requestAnimationFrame(tick);
})(typeof globalThis!=='undefined'?globalThis:this);
