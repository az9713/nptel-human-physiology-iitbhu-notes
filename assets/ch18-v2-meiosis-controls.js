'use strict';
(()=>{
  const $=id=>document.getElementById(id),model=window.MeioticInventory;
  let index=0,playing=false,last=null,elapsed=0;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const bar=(id,value,max,unit)=>{
    $(id).style.width=(value/max*100)+'%';
    $(id).parentElement.setAttribute('aria-label',value+' '+unit+' on a 0 to '+max+' scale');
  };
  function render(){
    const s=model.state(index);
    $('state-title').textContent=s.name;$('state-event').textContent=s.event;
    $('seek').value=String(index);$('seek').setAttribute('aria-valuetext',s.name);
    $('chromosomes').textContent=s.chromosomes;$('chromatids').textContent=s.chromatids;
    $('dna').textContent=s.dna+'C';$('lineage-dna').textContent=s.lineageDNA+'C';
    $('cells').textContent=s.cells;$('ploidy').textContent=s.ploidy;
    $('lineage-chromosomes').textContent=s.lineageChromosomes;
    bar('chromosome-bar',s.chromosomes,92,'chromosomes per cell');
    bar('chromatid-bar',s.chromatids,92,'chromatids per cell');
    bar('dna-bar',s.dna,4,'C DNA per cell');bar('lineage-bar',s.lineageDNA,4,'C lineage DNA');
    document.querySelectorAll('[data-state]').forEach(row=>{row.classList.toggle('selected',Number(row.dataset.state)===index);row.setAttribute('aria-current',Number(row.dataset.state)===index?'step':'false')});
    $('play').textContent=playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(playing));
    $('previous').disabled=index===0;$('next').disabled=index===3;
  }
  function pause(){playing=false;last=null;elapsed=0;render()}
  function select(i){pause();index=model.state(i).index;render()}
  $('previous').onclick=()=>select(index-1);$('next').onclick=()=>select(index+1);
  $('seek').oninput=e=>select(Number(e.target.value));$('reset').onclick=()=>select(0);
  $('play').onclick=()=>{if(playing){pause();return}if(index===3)index=0;playing=true;last=null;elapsed=0;render()};
  function tick(now){
    if(playing){if(last!==null)elapsed+=Math.min(100,now-last);last=now;if(elapsed>=3000){elapsed-=3000;index++;if(index>=3){index=3;playing=false;last=null}render()}}
    requestAnimationFrame(tick);
  }
  reduced.addEventListener('change',pause);document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});window.addEventListener('beforeprint',pause);
  const d=$('enlargement'),im=$('enlarged-image'),vp=d.querySelector('.viewport'),op=$('enlarge');
  function native(){im.style.width='1419px';im.style.maxWidth='none'}
  op.onclick=()=>{native();d.showModal();vp.scrollLeft=0;vp.scrollTop=0;vp.focus()};
  $('native').onclick=native;$('fit').onclick=()=>{im.style.width='100%';im.style.maxWidth='1419px'};$('close').onclick=()=>d.close();d.addEventListener('close',()=>op.focus());
  render();requestAnimationFrame(tick);
})();
