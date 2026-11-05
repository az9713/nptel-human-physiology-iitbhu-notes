/* Original source-surface pilot. No physics engine or tissue appearance claim. */
'use strict';
(function(global){
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  function rotation(q){
    if(!Array.isArray(q)||q.length!==4||!q.every(Number.isFinite))throw Error('Invalid quaternion');
    const norm=Math.hypot(...q);if(Math.abs(norm-1)>2e-6)throw Error('Nonunit quaternion');
    const [x,y,z,w]=q.map(v=>v/norm);
    return [1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),
      2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),
      2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)];
  }
  function model(c0,pose){
    if(c0.length!==3||pose.c_mm.length!==3||![...c0,...pose.c_mm].every(Number.isFinite))throw Error('Invalid reference point');
    const r=rotation(pose.q_xyzw),t=pose.c_mm.map((v,i)=>v-r.slice(i*3,i*3+3).reduce((s,x,j)=>s+x*c0[j],0));
    return [r[0],r[3],r[6],0,r[1],r[4],r[7],0,r[2],r[5],r[8],0,...t,1];
  }
  const identity=()=>[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
  const point=(m,v)=>[0,1,2].map(i=>m[i]*v[0]+m[4+i]*v[1]+m[8+i]*v[2]+m[12+i]);
  const multiply=(a,b)=>Array.from({length:16},(_,k)=>{const col=Math.floor(k/4),row=k%4;return [0,1,2,3].reduce((s,j)=>s+a[j*4+row]*b[col*4+j],0);});
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const unit=v=>{const n=Math.hypot(...v);return v.map(x=>x/n);};
  const dot=(a,b)=>a.reduce((s,x,j)=>s+x*b[j],0);
  function savedIndex(frames,time){
    if(!Number.isFinite(time))throw Error('Finite load coordinate required');
    let index=0;while(index+1<frames.length&&frames[index+1].model_time<=time+1e-12)index++;return index;
  }
  function permitted(mesh,mode){return mode==='reference'||mesh.bone;}
  const Core={rotation,model,identity,point,multiply,savedIndex,permitted};
  global.KneeCore=Core;
  if(typeof document==='undefined')return;
  const $=id=>document.getElementById(id),canvas=$('surface');
  let meta,poses,gl,program,index=0,playing=false,last=null,loadClock=0;
  let yaw=35*Math.PI/180,pitch=16*Math.PI/180,zoom=1,center,radius;
  let mode='reference';const meshes=[],visible=new Set(),checkboxes=new Map();
  const status=message=>$('status').textContent=message;
  function stop(){playing=false;last=null;$('play').textContent='Play';$('play').setAttribute('aria-pressed','false');}
  async function local(name){const r=await fetch(name);if(!r.ok)throw Error('Local file unavailable: '+name);return r;}
  function shader(kind,source){const s=gl.createShader(kind);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
  function setup(){
    gl=canvas.getContext('webgl',{antialias:true,alpha:false,preserveDrawingBuffer:true});
    if(!gl)throw Error('WebGL unavailable. Use the source/pose files; browser pilot inspection is pending.');
    program=gl.createProgram();
    gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec3 position;attribute vec3 normal;uniform mat4 vp;uniform mat4 model;varying vec3 N;void main(){N=mat3(model)*normal;gl_Position=vp*model*vec4(position,1.0);}'));
    gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float;uniform vec3 color;varying vec3 N;void main(){float light=0.30+0.70*abs(dot(normalize(N),normalize(vec3(0.3,-0.4,0.86))));gl_FragColor=vec4(color*light,1.0);}'));
    gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
    gl.useProgram(program);gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);
  }
  function viewProjection(){
    const back=[Math.sin(yaw)*Math.cos(pitch),Math.cos(yaw)*Math.cos(pitch),Math.sin(pitch)];
    const worldUp=Math.abs(back[2])>.999?[0,1,0]:[0,0,1];
    const right=unit(cross(worldUp,back)),up=cross(back,right),eye=center.map((x,j)=>x+back[j]*radius*4);
    const view=[right[0],up[0],back[0],0,right[1],up[1],back[1],0,right[2],up[2],back[2],0,-dot(right,eye),-dot(up,eye),-dot(back,eye),1];
    const h=radius*1.12/zoom,w=h*canvas.width/canvas.height,near=.1,far=radius*10;
    const projection=[1/w,0,0,0,0,1/h,0,0,0,0,-2/(far-near),0,0,0,-(far+near)/(far-near),1];
    return multiply(projection,view);
  }
  function draw(){
    if(!gl)return;
    const rect=canvas.getBoundingClientRect(),dpr=Math.min(2,global.devicePixelRatio||1);
    const width=Math.max(1,Math.round(rect.width*dpr)),height=Math.max(1,Math.round(rect.height*dpr));
    if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;}
    gl.viewport(0,0,width,height);gl.clearColor(.043,.078,.125,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.uniformMatrix4fv(gl.getUniformLocation(program,'vp'),false,new Float32Array(viewProjection()));
    for(const mesh of meshes){
      if(!permitted(mesh,mode)||!visible.has(mesh.id))continue;
      const matrix=mode==='motion'?model(poses.initial_centers_mm[mesh.id],poses.frames[index].poses[mesh.id]):identity();
      gl.uniformMatrix4fv(gl.getUniformLocation(program,'model'),false,new Float32Array(matrix));
      gl.uniform3fv(gl.getUniformLocation(program,'color'),mesh.rgb);
      gl.bindBuffer(gl.ARRAY_BUFFER,mesh.vertices);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.indices);
      for(const [name,offset] of [['position',0],['normal',12]]){const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,24,offset);}
      gl.drawElements(gl.TRIANGLES,mesh.index_count,gl.UNSIGNED_SHORT,0);
    }
  }
  const NS='http://www.w3.org/2000/svg';
  function svgNode(tag,attrs,text=''){const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);n.textContent=text;$('plots').appendChild(n);return n;}
  function plot(){
    $('plots').querySelectorAll('[data-drawn]').forEach(n=>n.remove());
    const series=poses.time_matched_reported_csv_series,selected=series[index];
    const add=(tag,attrs,text)=>svgNode(tag,{'data-drawn':'true',...attrs},text);
    const configs=[['reported_tf_flexion_deg','Reported TF JCS flexion (degrees)',25,'#9bd9ec'],['reported_tf_flexion_moment_Nmm','Reported TF flexion moment (N mm)',205,'#e4bf65']];
    for(const [key,title,top,color]of configs){
      const min=Math.min(0,...series.map(r=>r[key])),max=Math.max(0,...series.map(r=>r[key])),span=Math.max(1,max-min);
      const x=t=>100+t/2*850,y=v=>top+120-(v-min)/span*95;
      add('text',{x:100,y:top+4},title);add('path',{d:`M100 ${top+22}V${top+120}H950`,class:'axis',fill:'none'});
      for(const t of [0,1,2]){add('text',{x:x(t)-4,y:top+145},String(t));add('path',{d:`M${x(t)} ${top+120}v5`,class:'axis'});}
      for(const v of [min,max])add('text',{x:8,y:y(v)+5},v.toFixed(1));
      add('polyline',{points:series.map(r=>`${x(r.model_time)},${y(r[key])}`).join(' '),fill:'none',stroke:color,'stroke-width':2});
      add('path',{d:`M${x(selected.model_time)} ${top+20}V${top+120}`,stroke:'#eef4f8','stroke-dasharray':'4 4'});
      add('circle',{cx:x(selected.model_time),cy:y(selected[key]),r:5,fill:color});
    }
    add('text',{x:360,y:385},'Simulation load coordinate (not human seconds)');
  }
  function update(){
    const frame=poses.frames[index],r=poses.time_matched_reported_csv_series[index];
    $('seek').value=index;
    $('sample').textContent=(mode==='reference'?'Static reference geometry. ':'Bones-only conditional model replay. ')+`Saved state ${index}/${poses.frames.length-1}; load coordinate ${frame.model_time.toFixed(6)}; `+(index===0?'constructed input reference (not logged).':`native step ${frame.native_step}.`);
    $('values').innerHTML='<table><caption>Reported source scalars at the selected saved load coordinate; no world-vector interpretation</caption><tr><th>TF JCS flexion / degrees</th><th>TF flexion moment / N mm</th><th>PF JCS flexion / degrees</th></tr><tr>'+[r.reported_tf_flexion_deg,r.reported_tf_flexion_moment_Nmm,r.reported_pf_flexion_deg].map(v=>'<td>'+v.toFixed(6)+'</td>').join('')+'</tr></table>';
    $('pivots').innerHTML='<table><tr><th>Bone</th><th>Native c(t), mm</th><th>Native normalized qx, qy, qz, qw</th></tr>'+Object.entries(frame.poses).map(([key,p])=>'<tr><th>'+key+'</th><td>'+p.c_mm.map(v=>v.toFixed(5)).join(', ')+'</td><td>'+p.q_xyzw.map(v=>v.toFixed(7)).join(', ')+'</td></tr>').join('')+'</table>';
    for(const mesh of meshes){const cb=checkboxes.get(mesh.id);cb.disabled=!permitted(mesh,mode);cb.checked=visible.has(mesh.id)&&permitted(mesh,mode);}
    $('surface-policy').textContent=mode==='reference'?'All selected surfaces stay in the original reference pose. Colors distinguish named structures, not tissue appearance.':'All 12 soft-tissue surfaces are hidden and disabled. Femur/patella use decoded rigid poses; tibia/fibula stay fixed.';
    status(mode==='reference'?'Static source reference \u2022 no simulation transform applied':'CONDITIONAL bones-only replay \u2022 soft tissues hidden \u2022 saved states only');
    plot();draw();
  }
  function setIndex(value){if(!Number.isInteger(value)||value<0||value>=poses.frames.length)throw Error('Invalid saved state');index=value;loadClock=poses.frames[index].model_time;update();}
  function home(){yaw=35*Math.PI/180;pitch=16*Math.PI/180;zoom=1;$('zoom').value=zoom;draw();}
  function orbit(dx,dy){yaw+=dx;pitch=clamp(pitch+dy,-1.5,1.5);draw();}
  async function init(){
    [meta,poses]=await Promise.all([local('ch14-knee-viewer-geometry.json').then(r=>r.json()),local('ch14-knee-viewer-poses.json').then(r=>r.json())]);
    if(meta.meshes.length!==16||poses.frames.length!==141||poses.frames.length!==poses.time_matched_reported_csv_series.length)throw Error('Unexpected source packet shape');
    for(let j=0;j<poses.frames.length;j++){
      const f=poses.frames[j],r=poses.time_matched_reported_csv_series[j];
      if(!Number.isFinite(f.model_time)||Math.abs(f.model_time-r.model_time)>1e-10||!Object.values(r).every(Number.isFinite))throw Error('Pose/plot load coordinates differ');
      for(const key of ['FMB','TBB','FBB','PTB'])model(poses.initial_centers_mm[key],f.poses[key]);
    }
    const buffer=await local(meta.binary).then(r=>r.arrayBuffer());
    // WebCrypto is optional on ordinary HTTP. Byte identity is supplied by the
    // reproducible pack; validate the digest in secure/loopback contexts too.
    if(global.crypto?.subtle){const bytes=await crypto.subtle.digest('SHA-256',buffer);const hex=Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');if(hex!==meta.binary_sha256)throw Error('Packed geometry digest mismatch');}
    setup();center=[0,1,2].map(i=>(meta.view_bounds_mm[0][i]+meta.view_bounds_mm[1][i])/2);radius=Math.hypot(...meta.view_bounds_mm[1].map((v,i)=>v-meta.view_bounds_mm[0][i]))/2;
    for(const item of meta.meshes){
      const vertexData=new Float32Array(buffer,item.vertex_offset,item.vertex_count*6),indexData=new Uint16Array(buffer,item.index_offset,item.index_count);
      if(!Array.from(vertexData).every(Number.isFinite))throw Error('Nonfinite packed surface');
      const mesh={...item,rgb:new Float32Array([1,3,5].map(i=>parseInt(item.color.slice(i,i+2),16)/255)),vertices:gl.createBuffer(),indices:gl.createBuffer()};
      gl.bindBuffer(gl.ARRAY_BUFFER,mesh.vertices);gl.bufferData(gl.ARRAY_BUFFER,vertexData,gl.STATIC_DRAW);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.indices);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indexData,gl.STATIC_DRAW);meshes.push(mesh);visible.add(item.id);
      const label=document.createElement('label'),cb=document.createElement('input'),swatch=document.createElement('span');cb.type='checkbox';cb.checked=true;swatch.className='swatch';swatch.style.background=item.color;
      label.append(cb,swatch,document.createTextNode(item.id+' \u2014 '+item.name+(item.id==='TBB'||item.id==='FBB'?' (fixed)':'')));$('legend').appendChild(label);checkboxes.set(item.id,cb);cb.addEventListener('change',()=>{if(cb.checked&&permitted(mesh,mode))visible.add(item.id);else visible.delete(item.id);update();});
    }
    $('mode').addEventListener('change',()=>{stop();mode=$('mode').value;$('playback').disabled=mode!=='motion';setIndex(0);});
    $('show-all').addEventListener('click',()=>{meshes.filter(m=>permitted(m,mode)).forEach(m=>visible.add(m.id));update();});
    $('bones-only').addEventListener('click',()=>{visible.clear();meshes.filter(m=>m.bone).forEach(m=>visible.add(m.id));update();});
    $('seek').max=poses.frames.length-1;$('seek').addEventListener('input',()=>{stop();setIndex(Number($('seek').value));});
    $('reset').addEventListener('click',()=>{stop();setIndex(0);});$('previous').addEventListener('click',()=>{stop();setIndex(Math.max(0,index-1));});$('next').addEventListener('click',()=>{stop();setIndex(Math.min(poses.frames.length-1,index+1));});
    $('play').addEventListener('click',()=>{if(mode!=='motion')return;if(playing){stop();return;}if(index===poses.frames.length-1)setIndex(0);playing=true;last=null;$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');requestAnimationFrame(tick);});
    $('home').addEventListener('click',home);$('left').addEventListener('click',()=>orbit(-.15,0));$('right').addEventListener('click',()=>orbit(.15,0));$('up').addEventListener('click',()=>orbit(0,.12));$('down').addEventListener('click',()=>orbit(0,-.12));$('zoom').addEventListener('input',()=>{zoom=Number($('zoom').value);draw();});
    document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{const v=button.dataset.view;if(v==='oblique'){home();return;}yaw=v==='x'?Math.PI/2:0;pitch=v==='z'?Math.PI/2:0;draw();}));
    let drag=null;canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});canvas.addEventListener('pointermove',e=>{if(drag){orbit((e.clientX-drag[0])*.008,(e.clientY-drag[1])*.008);drag=[e.clientX,e.clientY];}});
    canvas.addEventListener('keydown',e=>{const moves={ArrowLeft:[-.15,0],ArrowRight:[.15,0],ArrowUp:[0,.12],ArrowDown:[0,-.12]};if(moves[e.key]){e.preventDefault();orbit(...moves[e.key]);}else if(e.key==='0')home();else if(['+','=','-'].includes(e.key)){e.preventDefault();zoom=clamp(zoom+(e.key==='-'?-.1:.1),.55,2.5);$('zoom').value=zoom;draw();}});
    matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});global.addEventListener('resize',draw);
    canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stop();status('WebGL context lost. Reload to restore the source display.');});
    update();global.ch14KneeReady=true;global.ch14KneeViewer={getState:()=>({mode,index,model_time:poses.frames[index].model_time,playing,visible:meshes.filter(m=>visible.has(m.id)&&permitted(m,mode)).map(m=>m.id)})};
  }
  function tick(now){if(!playing)return;if(last!==null){loadClock=Math.min(2,loadClock+Math.min(.2,(now-last)/1000)*Number($('speed').value)*2/24);const next=savedIndex(poses.frames,loadClock);if(next!==index){index=next;update();}}last=now;if(loadClock>=2)stop();else requestAnimationFrame(tick);}
  init().catch(error=>{stop();status('Pilot cannot load: '+error.message);console.error(error);});
})(typeof window==='undefined'?globalThis:window);
