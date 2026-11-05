/* Original deterministic state rendering. Wall-clock deltas change presentation time only. */
'use strict';
(()=>{
 const M=window.Ch10,get=id=>document.getElementById(id),view=document.body.dataset.view;
 let time=0,playing=false,last=null;const trajectory=M.control(),end=100;
 const colors=['#79d9c5','#e8c17c','#bca5de'];
 const txt=(x,y,s,small=false)=>'<text x="'+x+'" y="'+y+'"'+(small?' class="small"':'')+'>'+s+'</text>';
 const line=(x1,y1,x2,y2,c='#547183',w=2)=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+c+'" stroke-width="'+w+'"/>';
 const rect=(x,y,w,h,c)=>'<rect x="'+x+'" y="'+y+'" width="'+Math.max(0,w)+'" height="'+Math.max(0,h)+'" rx="5" fill="'+c+'"/>';
 const f=x=>x.toFixed(6);
 function pause(){playing=false;last=null;get('play').textContent='Play';get('play').setAttribute('aria-pressed','false');}
 function state(t){return trajectory[Math.min(trajectory.length-1,Math.round(t/.05))];}
 function plot(series,ymax,label){
  let s=txt(30,192,label,true)+line(55,210,55,320)+line(55,320,955,320)+txt(18,217,String(ymax),true)+txt(32,324,'0',true)+txt(55,345,'0',true)+txt(885,345,'100 min',true);
  series.forEach((item,j)=>{const points=[];for(let t=0;t<=100;t+=.5)points.push((55+t*9)+','+(320-110*item.fn(t)/ymax));s+='<polyline points="'+points.join(' ')+'" fill="none" stroke="'+colors[j]+'" stroke-width="2.5"/>';});
  s+=line(55+time*9,205,55+time*9,320,'#f4d6a3');return s;
 }
 function render(){
  get('seek').value=time;let s='',report='';
  if(view==='transport'){
   const oxygen=M.exchange(time),glucose=M.exchange(time,{conductance:.1,external:10,consumption:.02}),insulin=M.exchange(time,{conductance:.08,external:0,consumption:0,source:.03});
   s+=rect(20,20,260,140,'#364f5e')+txt(35,46,'Maintained host reservoirs')+txt(35,76,'Oxygen 0.20 μmol/mL')+txt(35,106,'Glucose 10 μmol/mL')+txt(35,136,'Insulin external sink = 0');
   s+=rect(430,20,410,140,'#254652')+txt(455,46,'Protected graft region, V = 1 mL');
   [oxygen.c/.2,glucose.c/10,insulin.c/.375].forEach((v,j)=>{s+=rect(455,60+j*28,330*v,16,colors[j]);});
   s+=txt(850,75,'O₂ used')+txt(850,105,'Glucose used')+txt(850,135,'Insulin source');
   s+=line(400,15,400,65,'#83b7c2',8)+line(400,85,400,93,'#83b7c2',8)+line(400,113,400,121,'#83b7c2',8)+line(400,141,400,165,'#83b7c2',8);
   for(let j=0;j<3;j++){const y=75+j*28;s+=line(285,y,430,y,colors[j]);const x=j<2?285+145*((time/4)%1):430-145*((time/4)%1);s+='<circle cx="'+x+'" cy="'+y+'" r="5" fill="'+colors[j]+'"/>';}
   s+='<circle cx="335" cy="35" r="15" fill="#bc8e6b"/>'+txt(290,15,'Immune cell stays outside',true);
   s+=plot([{fn:t=>M.exchange(t).c/.2},{fn:t=>M.exchange(t,{conductance:.1,external:10,consumption:.02}).c/10},{fn:t=>M.exchange(t,{conductance:.08,external:0,consumption:0,source:.03}).c/.375}],1,'Fraction of reference: O₂ 0.20; glucose 10; insulin 0.375. Dots mark routes, not molecule counts.');
   report='t = '+f(time)+' model min. Oxygen '+f(oxygen.c)+' μmol/mL; input '+f(oxygen.input)+' = stored '+f(oxygen.stored)+' + outward back-transfer '+f(oxygen.back)+' + consumed '+f(oxygen.used)+' μmol. Glucose '+f(glucose.c)+' μmol/mL. Insulin '+f(insulin.c)+' illustrative amount units/mL; produced '+f(insulin.produced)+' = stored '+f(insulin.stored)+' + exported '+f(insulin.back)+'. Largest absolute amount residual '+Math.max(Math.abs(oxygen.residual),Math.abs(glucose.residual),Math.abs(insulin.residual)).toExponential(2)+'. No clinical insulin units.';
  }else if(view==='sensing'){
   const v=M.sensing(time),values=[v.blood,v.tissue,v.sensor];
   ['Blood reservoir','Interstitial fluid','Processed sensor'].forEach((name,j)=>{s+=rect(25+j*325,20,295,130,'#284652')+txt(40+j*325,48,name)+rect(40+j*325,65,260*values[j]/10,30,colors[j])+txt(40+j*325,124,f(values[j])+' mmol/L');});
   s+=plot([{fn:t=>M.sensing(t).blood},{fn:t=>M.sensing(t).tissue},{fn:t=>M.sensing(t).sensor}],10,'Glucose (mmol/L): green blood, gold tissue, purple sensor. Blood rise 10 min; fall 40 min.');
   report='t = '+f(time)+' model min. Blood '+f(v.blood)+', tissue '+f(v.tissue)+', processed sensor '+f(v.sensor)+' mmol/L. Processing observes tissue, never directly jumps to blood. Synthetic lag constants 5 and 2 min; no noise or calibration bias included. Reservoir forcing is externally maintained.';
  }else{
   const v=state(time);s+=rect(20,20,300,140,'#284652')+txt(35,47,'Glucose reservoir: '+f(v.g))+txt(35,75,'Delayed observation: '+f(v.s))+txt(35,103,'mmol/L; reservoir V = 1 L')+txt(35,133,'Disturbance: 20–40 min',true);
   s+=rect(345,20,295,140,'#284652')+txt(360,47,'Bounded command u [0,1]')+rect(360,65,260*v.u,25,colors[1])+txt(360,125,f(v.u)+' dimensionless');
   s+=rect(665,20,310,140,'#284652')+txt(680,47,'Delayed effector a [0,1]')+rect(680,65,270*v.a,25,colors[2])+txt(680,125,f(v.a)+' dimensionless');
   s+=plot([{fn:t=>state(t).g},{fn:t=>state(t).s}],12,'Glucose (mmol/L): green reservoir, gold observation. Command/effector bars are dimensionless.');
   report='t = '+f(v.t)+' model min (0.05-min solver grid). Input '+f(v.input)+' mmol; initial 5 + input = stored '+f(v.g)+' + basal removal '+f(v.basal)+' + added removal '+f(v.extra)+' mmol. Residual '+v.residual.toExponential(2)+'. u '+f(v.u)+'; a '+f(v.a)+'. Neither is insulin concentration or pump rate. Model balance does not establish safe control.';
  }
  get('drawing').innerHTML=s;get('result').textContent=report;
 }
 get('play').onclick=()=>{if(playing){pause();return;}if(time>=end)time=0;playing=true;last=null;get('play').textContent='Pause';get('play').setAttribute('aria-pressed','true');};
 get('replay').onclick=()=>{pause();time=0;render();};
 get('back').onclick=()=>{pause();time=Math.max(0,time-5);render();};get('next').onclick=()=>{pause();time=Math.min(end,time+5);render();};
 get('seek').oninput=()=>{pause();time=Number(get('seek').value);render();};
 get('viewport').addEventListener('keydown',event=>{if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();get('viewport').scrollLeft+=event.key==='ArrowRight'?80:-80;}if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();get('viewport').scrollTop+=event.key==='ArrowDown'?60:-60;}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});const motion=matchMedia('(prefers-reduced-motion: reduce)');motion.addEventListener('change',pause);
 function tick(now){if(playing){if(last!==null){time=Math.min(end,time+(now-last)/1000*5*Number(get('speed').value));render();if(time>=end)pause();}last=now;}requestAnimationFrame(tick);}
 window.Ch10View={renderAt(t){if(!Number.isFinite(t)||t<0||t>end)throw new RangeError('time outside [0,100]');pause();time=t;render();},state:()=>({time,playing,view})};
 render();requestAnimationFrame(tick);
})();
