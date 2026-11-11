/* Seven explanatory states; no mapping to biological time or live tissue motion. */
(function(root){
 'use strict';
 const stages=[
  {title:'Bring iodide into the polarized cell',region:'rim',side:'Basolateral side → follicular cell',cargo:'Iodide, coupled to inward Na⁺',mechanism:'NIS uses the Na⁺ electrochemical gradient to accumulate iodide. Na/K ATPase maintains that gradient; NIS is not itself an ATP-hydrolysing pump.',boundary:'The stromal side faces the blood supply in vivo. This section does not resolve a capillary or a NIS molecule.'},
  {title:'Supply the apical reaction compartment',region:'interface',side:'Follicular cell → colloid',cargo:'Iodide through apical anion-transport routes',mechanism:'Apical efflux delivers iodide to the follicular lumen. Pendrin is a proposed apical anion route; its in-vivo contribution is not established by the cited Endotext account. It is not an ATPase, and other routes must be considered.',boundary:'The luminal edge establishes epithelial polarity. No anion channel or individual ion is visible in this H&E section.'},
  {title:'Deliver the protein scaffold',region:'interface',side:'Secretory-vesicle lumen → colloid',cargo:'Cell-made thyroglobulin (Tg)',mechanism:'Tg enters the ER secretory pathway, is processed through Golgi and delivered in vesicles. Apical fusion connects the vesicle lumen to colloid; Tg does not cross an intact lipid bilayer.',boundary:'This light micrograph supplies follicular context. It does not resolve ER, Golgi or the fusion pore.'},
  {title:'Build and store hormone on Tg',region:'colloid',side:'Apical–colloid interface and luminal store',cargo:'Iodinated Tg with covalently linked hormone residues',mechanism:'TPO and H₂O₂ support iodination and coupling on Tg. MIT/DIT count iodine atoms on tyrosyl residues. The formed hormone remains attached to Tg in the colloid store.',boundary:'Pink staining identifies colloid morphology, not TPO activity, iodine content or hormone concentration. The reaction and storage are not spatially uniform events inferred from these pixels.'},
  {title:'Retrieve the luminal precursor',region:'interface',side:'Colloid → membrane-enclosed endocytic compartment',cargo:'Iodinated Tg',mechanism:'Apical endocytosis internalizes colloidal Tg. Cargo first remains in a membrane-enclosed lumen; it is not deposited as intact free Tg in the cytosol.',boundary:'The section does not show an endocytic event. No pit, vesicle size or macropinocytosis route is invented here.'},
  {title:'Release free hormone from the protein',region:'rim',side:'Intracellular endolysosomal processing',cargo:'Tg → liberated T3/T4 plus other breakdown products',mechanism:'Proteolysis cleaves hormone residues from Tg. Iodotyrosine deiodination recycles iodine separately. Liberated hormone must leave the lysosomal compartment before basal export.',boundary:'No lysosome is identified in H&E. The lysosomal membrane-transfer machinery is not assigned a fictitious transporter or trajectory.'},
  {title:'Export hormone toward the circulation',region:'rim',side:'Follicular cell → interstitium → blood',cargo:'Free T3/T4, subsequently reversibly bound in plasma',mechanism:'Basal export uses thyroid-hormone transport machinery. MCT8 involvement is supported by mouse localization and knockout experiments. This differs from the apical Tg-exocytosis route.',boundary:'TBG is a plasma carrier, distinct from Tg. The image does not show hormone release or identify MCT8 in this human specimen.'}
 ];
 const ledger=[
 ['Interstitium','I⁻ + inward Na⁺ gradient','NIS cotransport','Follicular-cell interior','I⁻ accumulated; gradient energy used'],
 ['Follicular-cell interior','I⁻','Apical anion transfer','Colloid','I⁻ supplied outside the cell'],
 ['Secretory-vesicle lumen','Tg enclosed by vesicle membrane','Apical fusion opens luminal continuity','Colloid','Tg extracellular; no intact-bilayer crossing'],
 ['Apical–colloid interface','Tyrosyl residues within Tg + iodide-derived iodine','Iodination and coupling','Colloid store','Hormone residues remain covalently attached to Tg'],
 ['Colloid','Iodinated Tg, extracellular','Endocytic enclosure','Intracellular endocytic lumen','Tg enclosed; not free in cytosol'],
 ['Endolysosomal lumen','Tg-bound hormone residues','Proteolytic cleavage','Endolysosomal processing products','Free T3/T4 distinct from Tg fragments'],
 ['Follicular-cell interior','Liberated T3/T4 after intracellular handling','Basal hormone export','Interstitium, then blood','Free hormone can reversibly bind plasma carriers']
 ];
 function state(seconds){
  const n=Number(seconds),time=Number.isFinite(n)?Math.max(0,Math.min(21,n)):0;
  const index=Math.min(6,Math.floor(time/3));
  return {...stages[index],ledger:ledger[index],index,time,phase:time===21?1:(time-index*3)/3};
 }
 const api={stages,duration:21,state};
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.ThyroidFollicleStages=api;
})(typeof window==='object'?window:globalThis);
