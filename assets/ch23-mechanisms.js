"use strict";
const $ = id => document.getElementById(id);
let data, mode = "voltage", position = 0, playing = false, lastTime = null;
const phaseSeconds = 4;
function current() {
  const phases = data.modes[mode].phases;
  const total = phases.length * phaseSeconds;
  const t = Math.min(position, total - 1e-8);
  const index = Math.floor(t / phaseSeconds);
  return {phases, total, index, fraction: (t % phaseSeconds) / phaseSeconds, phase: phases[index]};
}
function render() {
  const m = data.modes[mode], s = current(), f = s.fraction, p = s.phase;
  const [x1,y1] = p.from, [x2,y2] = p.to;
  const x = x1 + (x2-x1)*f, y = y1 + (y2-y1)*f;
  $("title").textContent = m.title;
  $("clock-note").textContent = "Presentation time only · phase " + (s.index+1) + " of " + s.phases.length;
  $("stage").setAttribute("viewBox",m.viewBox);
  $("base").setAttribute("href",m.image);
  const [, , w, h] = m.viewBox.split(" ").map(Number);
  $("base").setAttribute("width",w); $("base").setAttribute("height",h);
  $("token").setAttribute("cx",x.toFixed(2)); $("token").setAttribute("cy",y.toFixed(2));
  $("token-label").setAttribute("x",Math.min(w-120,Math.max(120,x)).toFixed(2));
  $("token-label").setAttribute("y",Math.max(78,y-35).toFixed(2));
  $("token-label").textContent=p.tag;
  $("stage-title").textContent=m.title+": "+p.label;
  $("stage-desc").textContent=p.detail;
  $("status").textContent=p.label+" · "+(s.index+1)+"/"+s.phases.length+" · "+position.toFixed(1)+"/"+s.total+" presentation seconds";
  $("description").textContent=p.detail;
  $("seek").value=String(Math.round(position/s.total*1000));
  $("play").textContent=playing?"Pause":"Play";
}
function setMode(value) {if(!data.modes[value]) return; mode=value; position=0; playing=false; lastTime=null; render();}
function frame(now) {if(playing){if(lastTime!==null){position=Math.min(current().total,position+(now-lastTime)/1000*Number($("speed").value));if(position>=current().total){playing=false;}}lastTime=now;render();}else lastTime=null;requestAnimationFrame(frame);}
const motionPreference=window.matchMedia?.("(prefers-reduced-motion: reduce)");
motionPreference?.addEventListener?.("change",()=>{playing=false;lastTime=null;if(data)render();});
fetch("ch23-data.json").then(r=>{if(!r.ok) throw Error("model data unavailable");return r.json();}).then(d=>{data=d;$("mode").addEventListener("change",e=>setMode(e.target.value));$("play").addEventListener("click",()=>{if(!playing && position>=current().total) position=0;playing=!playing;lastTime=null;render();});$("replay").addEventListener("click",()=>{position=0;playing=false;render();});$("prev").addEventListener("click",()=>{position=Math.max(0,(current().index-1)*phaseSeconds);playing=false;render();});$("next").addEventListener("click",()=>{position=Math.min((current().phases.length-1)*phaseSeconds,(current().index+1)*phaseSeconds);playing=false;render();});$("seek").addEventListener("input",e=>{position=Number(e.target.value)/1000*current().total;playing=false;render();});const q=new URLSearchParams(location.search).get("mode");setMode(q&&d.modes[q]?q:"voltage");$("mode").value=mode;requestAnimationFrame(frame);}).catch(e=>{$("status").textContent="Diagram unavailable: "+e.message;});
