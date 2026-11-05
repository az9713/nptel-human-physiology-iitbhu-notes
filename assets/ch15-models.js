/* Original deterministic teaching maps. No physiological clock or fitted rates. */
(function (scope) {
  "use strict";
  const nmj = [
    "Nerve action potential reaches terminal.",
    "Calcium enters terminal cytosol from extracellular fluid.",
    "Primed vesicle fuses: lumen opens to extracellular cleft.",
    "Cleft ACh activates muscle nAChRs: mixed-cation current.",
    "Graded EPP can trigger nearby voltage-gated sodium channels.",
    "Muscle AP fronts spread away from the endplate in both directions.",
    "AChE hydrolyzes cleft ACh; choline can be reused."
  ];
  const coupling = [
    "T-tubule depolarization changes CaV1.1 voltage-sensor state.",
    "RyR1 opens: calcium moves SR lumen → muscle cytosol.",
    "Calcium binds troponin C; thin-filament regulation permits cycling.",
    "ATP binds myosin: detachment from actin.",
    "ATP hydrolysis: detached head becomes primed with ADP + Pi.",
    "Attachment/product-release transitions support force; ADP leaves.",
    "Release subsides; SERCA spends ATP to move calcium cytosol → SR."
  ];
  const edges = Object.freeze([
    ["H-pump", "terminal cytosol", "vesicle lumen"],
    ["VAChT-H", "vesicle lumen", "terminal cytosol"],
    ["VAChT-ACh", "terminal cytosol", "vesicle lumen"],
    ["terminal-Ca", "extracellular", "terminal cytosol"],
    ["exocytosis", "vesicle lumen", "cleft"],
    ["RyR1", "SR lumen", "muscle cytosol"],
    ["SERCA", "muscle cytosol", "SR lumen"]
  ]);
  function geometry(length, a=1, b=1.6) {
    // Finite noninterfering band domain; excludes filament-free gaps.
    if(![length,a,b].every(Number.isFinite)||a<=0||b<=0||
      length<Math.max(b,2*a)||length>b+2*a) {
      throw new RangeError("finite a,b>0; max(b,2a) <= L <= b+2a");
    }
    return {L:length,a,b,A:b,I:length-b,H:Math.max(0,length-2*a),
      O:Math.max(0,Math.min(a,(b+2*a-length)/2)),
      z:[-length/2,length/2],
      thin:[[-length/2,-length/2+a],[length/2-a,length/2]]};
  }
  function activeForce(length, recruited=6) {
    if(!Number.isFinite(length)||length<2.2||length>3.6||
      !Number.isInteger(recruited)||recruited<0||recruited>10) {
      throw new RangeError("L in [2.2,3.6] µm; integer recruited in [0,10]");
    }
    const overlap=Math.max(0,Math.min(1,(3.6-length)/2));
    return (recruited/10)*100*Math.min(1,overlap/.7);
  }
  function state(kind, phase, recruited=6) {
    if (!Number.isFinite(phase) || phase < 0 || phase > 1) {
      throw new RangeError("phase must be in [0,1]");
    }
    const index = Math.min(6, Math.floor(phase * 7));
    const L = 2.6 - 0.4 * phase;
    return {
      kind, phase, index, ...geometry(L), recruited, q:recruited/10,
      force:activeForce(L,recruited),
      ap: [-1, 1].map(sign => 430 + sign * 330 *
        Math.max(0, Math.min(1, (phase - 5 / 7) * 7)))
    };
  }
  function line(x1,y1,x2,y2,color,width=4) {
    return '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+
      '" stroke="'+color+'" stroke-width="'+width+'"/>';
  }
  function text(x,y,s,size=18) {
    return '<text x="'+x+'" y="'+y+'" font-size="'+size+
      '" fill="#e5edf5">'+s+'</text>';
  }
  function box(x,y,w,h,label,active) {
    return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+
      '" rx="8" fill="'+(active?'#195c58':'#152332')+
      '" stroke="#68c9bd"/>'+text(x+12,y+29,label);
  }
  function arrow(x1,y1,x2,y2,color) {
    const ang=Math.atan2(y2-y1,x2-x1), len=11;
    return line(x1,y1,x2,y2,color)+line(x2,y2,
      x2-len*Math.cos(ang-.5),y2-len*Math.sin(ang-.5),color)+
      line(x2,y2,x2-len*Math.cos(ang+.5),y2-len*Math.sin(ang+.5),color);
  }
  function render(s) {
    let body="";
    if(s.kind==="nmj") {
      const membrane=s.index===2?
        "M80 200 H410 V185 C380 170 385 130 430 130 C475 130 480 170 450 185 V200 H770":
        "M80 200 H770";
      body='<rect x="80" y="50" width="690" height="150" fill="#195c58"/>'+
        '<rect x="80" y="200" width="690" height="100" fill="#152332"/>'+
        '<rect x="80" y="300" width="690" height="115" fill="#19505a"/>'+
        '<path d="M80 200 V50 H770 V200" fill="none" stroke="#68c9bd" stroke-width="2"/>'+
        text(100,80,"Nerve-terminal cytosol",18)+
        text(100,185,"Terminal plasma membrane",15)+
        text(100,235,"Extracellular cleft",18)+text(100,345,"Muscle cytosol",18)+
        text(90,35,"Motor endplate belongs to muscle; separate cell membranes",19)+
        '<circle data-role="reserve-vesicle" cx="675" cy="115" r="22" fill="#2a3d51" stroke="#f5c47a" stroke-width="3"/>'+
        text(550,85,"Closed reserve vesicle",15)+
        '<path data-role="terminal-membrane" d="'+membrane+'" fill="none" stroke="#68c9bd" stroke-width="4"/>'+
        '<path data-role="sarcolemma" d="M80 300 H770" stroke="#69d7c5" stroke-width="6"/>'+
        text(100,282,"Muscle sarcolemma / endplate",15)+
        text(100,390,"Cytosolic muscle calcium is a later, separate signal",17);
      if(s.index<2)body+='<circle data-role="primed-vesicle" cx="430" cy="145" r="25" fill="#2a3d51" stroke="#f5c47a" stroke-width="4"/>'+
        text(465,150,"Primed vesicle lumen",16);
      if(s.index===1)body+='<g data-role="terminal-calcium-entry">'+
        arrow(725,240,725,160,"#fcbd70")+'</g>'+text(640,245,"Ca²⁺",18);
      if(s.index===2)body+='<path data-role="open-lumen" d="M410 200 V185 C380 170 385 130 430 130 C475 130 480 170 450 185 V200 Z" fill="#152332" stroke="none"/>'+
        '<path data-role="omega-profile" d="'+membrane+'" fill="none" stroke="#68c9bd" stroke-width="4"/>'+
        '<g data-role="ach-release">'+arrow(430,155,430,270,"#fcbd70")+'</g>'+
        text(480,155,"Open lumen → cleft pore",16)+text(470,257,"ACh exits through pore",16);
      if(s.index>=3)body+=text(350,180,"Completed release; fused membrane flattened",15);
      if(s.index===3||s.index===4)body+='<g data-role="ion-current">'+
        arrow(430,291,430,350,"#69d7c5")+'</g>'+
        text(475,345,"nAChR ion current → EPP",16)+
        '<circle cx="430" cy="273" r="5" fill="#fcbd70"/>'+text(470,260,"Cleft ACh",16);
      if(s.index===5)body+='<g data-role="ap-propagation">'+s.ap.map(x=>
        '<circle data-role="ap-front" cx="'+x+'" cy="300" r="10" fill="#f5c47a"/>').join("")+
        (s.ap[0]<410?arrow(420,300,s.ap[0],300,"#f5c47a"):"")+
        (s.ap[1]>450?arrow(440,300,s.ap[1],300,"#f5c47a"):"")+'</g>';
      if(s.index===6)body+=text(350,260,"AChE: ACh → choline + acetate",17);
    } else if(s.kind==="coupling") {
      body=box(35,50,210,160,"T-tubule lumen",s.index===0)+
        text(48,115,"Extracellular space",16)+
        text(48,145,"CaV1.1 in membrane",16)+
        box(330,50,470,100,"SR lumen: stored calcium",s.index===1)+
        box(330,205,470,80,"Muscle cytosol",s.index===2||s.index===6)+
        text(40,33,"Skeletal triad coupling — compartment map, not scale anatomy",19)+
        arrow(250,110,325,110,"#69d7c5")+text(251,92,"coupling",14)+
        line(130,345,720,345,"#69d7c5",7)+text(140,328,"Actin (thin filament)",17)+
        line(410,408,410,377,"#f5c47a",8);
      if(s.index===1)body+='<g data-role="sr-release">'+
        arrow(520,145,520,220,"#f5c47a")+'</g>'+text(550,185,"RyR1 release",17);
      if(s.index>=2&&s.index<=5)body+='<g data-role="cytosolic-calcium-state">'+
        '<circle cx="510" cy="260" r="5" fill="#f5c47a"/><circle cx="530" cy="250" r="5" fill="#f5c47a"/>'+
        text(550,268,"Elevated cytosolic Ca²⁺",16)+'</g>';
      if(s.index===6)body+='<g data-role="serca-return">'+
        arrow(720,245,720,150,"#f5c47a")+'</g>'+text(550,185,"SERCA + ATP",17);
      const hx=s.index===3||s.index===4?450:430;
      const hy=s.index===3||s.index===4?377:350;
      body+=line(410,377,hx,hy,"#f5c47a",7)+
        '<circle cx="'+hx+'" cy="'+hy+'" r="10" fill="#f5c47a"/>'+
        text(500,408,s.index===3?"ATP: detached":
          s.index===4?"ADP + Pi: primed":
          s.index===5?"Force-bearing/product release":"Myosin motor state",17);
    } else {
      const map=x=>430+190*x;
      body=text(40,32,"Fixed filament lengths; prescribed sliding (µm)",20)+
        line(map(s.z[0]),70,map(s.z[0]),205,"#e4e9ef",7)+
        line(map(s.z[1]),70,map(s.z[1]),205,"#e4e9ef",7)+
        text(map(s.z[0])-8,55,"Z")+text(map(s.z[1])-8,55,"Z")+
        line(map(-.8),145,map(.8),145,"#f5c47a",13)+
        line(map(s.thin[0][0]),120,map(s.thin[0][1]),120,"#69d7c5",6)+
        line(map(s.thin[1][0]),170,map(s.thin[1][1]),170,"#69d7c5",6)+
        line(430,90,430,205,"#e4e9ef",2)+text(420,225,"M")+
        text(50,265,"A="+s.A.toFixed(2)+"   total I="+s.I.toFixed(2)+
          "   H="+s.H.toFixed(2)+"   overlap/side="+s.O.toFixed(2),19)+
        text(50,294,"Recruited "+s.recruited+"/10; q="+s.q.toFixed(1)+
          "; selected active force="+s.force.toFixed(2)+" N",18)+
        line(80,405,760,405,"#9caec2",2)+line(80,325,80,405,"#9caec2",2)+
        text(30,322,"L / µm",16)+text(35,338,"2.6",14)+text(35,408,"2.2",14)+
        line(80,545,760,545,"#9caec2",2)+line(80,445,80,545,"#9caec2",2)+
        text(30,441,"Active force / N",16)+text(30,452,"100",14)+
        text(45,548,"0",14)+text(625,580,"phase 0 → 1",16);
      const pts=[], ov=[];
      for(let i=0;i<=100;i++){
        const p=i/100, st=state("sliding",p,s.recruited),x=80+680*p;
        pts.push(x+","+(405-(st.L-2.2)*175));
        ov.push(x+","+(545-st.force));
      }
      body+='<polyline fill="none" stroke="#69d7c5" stroke-width="3" points="'+pts.join(" ")+'"/>'+
        '<polyline fill="none" stroke="#f5c47a" stroke-width="3" points="'+ov.join(" ")+'"/>'+
        line(80+680*s.phase,325,80+680*s.phase,545,"#e4e9ef",2)+
        text(310,322,"Teal: prescribed L; amber: selected force law",16);
    }
    const height=s.kind==="sliding"?600:445;
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 '+height+'" role="img" aria-label="'+
      (s.kind==="sliding"?"Fixed-length filament sliding":s.kind==="nmj"?nmj[s.index]:coupling[s.index])+
      '"><rect width="860" height="'+height+'" fill="#0d1723"/>'+body+'</svg>';
  }
  const api={state,render,geometry,activeForce,edges,nmj,coupling};
  if(typeof module!=="undefined") module.exports=api;
  scope.Ch15=api;
  if(typeof document==="undefined") return;
  document.querySelectorAll(".ch15-model").forEach((figure,n)=>{
    const kind=figure.dataset.model, canvas=figure.querySelector(".ch15-canvas");
    const controls=figure.querySelector(".ch15-controls"),output=figure.querySelector(".ch15-state");
    controls.innerHTML='<button type="button" data-play>Play</button>'+
      '<button type="button" data-reset>Replay</button>'+
      '<label>Speed <select aria-label="Playback speed"><option value=".5">0.5×</option>'+
      '<option value="1" selected>1×</option><option value="2">2×</option></select></label>'+
      '<label for="ch15-seek-'+n+'">Phase</label><input id="ch15-seek-'+n+
      '" type="range" min="0" max="1000" step="1" value="0">'+
      '<button type="button" data-step>Next phase</button>';
    if(kind==="sliding") controls.insertAdjacentHTML("beforeend",
      '<label>Recruited units <select data-recruit aria-label="Recruited units">'+
      Array.from({length:11},(_,i)=>'<option value="'+i+'"'+(i===6?' selected':'')+'>'+
        i+'/10</option>').join("")+'</select></label>');
    let phase=0,playing=false,last=null,raf=null;
    const play=controls.querySelector("[data-play]"), seek=controls.querySelector("input");
    const speed=controls.querySelector("select");
    const recruit=controls.querySelector("[data-recruit]");
    function draw(){
      const s=state(kind,phase,recruit?Number(recruit.value):6);
      canvas.innerHTML=render(s);seek.value=Math.round(phase*1000);
      output.textContent=kind==="sliding"?
        "Selected L="+s.L.toFixed(3)+" µm; overlap/side="+s.O.toFixed(3)+
        " µm; active force="+s.force.toFixed(3)+" N; "+s.recruited+"/10 units.":
        (s.index+1)+"/7. "+(kind==="nmj"?nmj:coupling)[s.index];
      play.textContent=playing?"Pause":"Play";play.setAttribute("aria-pressed",String(playing));
    }
    function stop(){playing=false;last=null;if(raf!==null)cancelAnimationFrame(raf);raf=null;}
    function tick(now){
      if(!playing)return;
      if(last!==null)phase=Math.min(1,phase+(now-last)*Number(speed.value)/10000);
      last=now;if(phase===1)stop();draw();
      if(playing)raf=requestAnimationFrame(tick);
    }
    function start(){if(phase===1)phase=0;playing=true;last=null;draw();raf=requestAnimationFrame(tick);}
    play.addEventListener("click",()=>{if(playing){stop();draw();}else start();});
    controls.querySelector("[data-reset]").addEventListener("click",()=>{stop();phase=0;start();});
    seek.addEventListener("input",()=>{stop();phase=Number(seek.value)/1000;draw();});
    if(recruit)recruit.addEventListener("change",()=>{stop();draw();});
    controls.querySelector("[data-step]").addEventListener("click",()=>{
      stop();phase=Math.min(1,(Math.floor(phase*7+1e-8)+1)/7);draw();
    });
    const reduced=matchMedia("(prefers-reduced-motion: reduce)");
    reduced.addEventListener("change",()=>{if(reduced.matches){stop();draw();}});
    document.addEventListener("visibilitychange",()=>{if(document.hidden){stop();draw();}});
    draw();
  });
})(typeof globalThis==="undefined"?this:globalThis);
