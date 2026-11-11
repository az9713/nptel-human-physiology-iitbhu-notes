/* Completed human maternal inventories. No biological time or image-derived counts. */
(function(root){'use strict';
const names=['Primordial follicle','Primary follicle','Multilayer preantral follicle','Antral follicle','Competent preovulatory follicle','After meiosis I, before release','Ovulated cumulus–oocyte complex','Conditional completion of meiosis II'];
function limit(branch){return branch?7:6;}
function state(index,branch=false){
 const i=Math.max(0,Math.min(limit(branch),Number.isFinite(index)?Math.round(index):0));
 return Object.freeze({index:i,name:names[i],status:i<4?'Primary oocyte; prophase I arrest':i===4?'Primary oocyte; before meiosis I completion':i<7?'Secondary oocyte; metaphase II arrest':'Maternal haploid product, before replication',chromosomes:i<5?46:23,chromatids:i<5?92:i<7?46:23,dnaC:i<5?4:i<7?2:1,ploidy:i<5?'2n':'n',conditional:i===7});
}
const api=Object.freeze({state,limit});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.OocyteInventory=api;
})(typeof window!=='undefined'?window:globalThis);
