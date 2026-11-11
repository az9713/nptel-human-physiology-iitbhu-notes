'use strict';
(function (root) {
  const states = [
    {name:'Before S phase', event:'No premeiotic DNA replication has yet been counted.', cells:1, ploidy:'2n', chromosomes:46, chromatids:46, dna:2},
    {name:'After S phase: primary spermatocyte', event:'DNA replication is complete; sister chromatids remain joined.', cells:1, ploidy:'2n', chromosomes:46, chromatids:92, dna:4},
    {name:'After meiosis I: secondary spermatocytes', event:'Homologues have separated; sister chromatids remain joined.', cells:2, ploidy:'n', chromosomes:23, chromatids:46, dna:2},
    {name:'After meiosis II: spermatids', event:'Sisters have separated; each single chromatid is now a daughter chromosome.', cells:4, ploidy:'n', chromosomes:23, chromatids:23, dna:1}
  ].map((s,index)=>Object.freeze({...s,index,lineageDNA:s.cells*s.dna,lineageChromosomes:s.cells*s.chromosomes,lineageChromatids:s.cells*s.chromatids}));
  function state(index) {
    if (!Number.isFinite(index)) throw new TypeError('A finite state index is required');
    return states[Math.max(0,Math.min(3,Math.floor(index)))];
  }
  const api=Object.freeze({state,states:Object.freeze(states)});
  root.MeioticInventory=api;
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
