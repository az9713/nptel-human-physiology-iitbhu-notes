"""Offline two-lab composition from public data, editable templates and immutable SVG/image inputs."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((A/'ch13-v2-digestion-sources.json').read_text(encoding='utf-8'));record=json.loads((A/'ch12-v2-enteric-sources.json').read_text(encoding='utf-8'))
for x in record['sources']:
 if x['id'] in ['enterocyte','vessels']:assert sha(A/x['file'])==x['sha256']
files=[A/'ch13-v2-digestion-sources.json',A/'ch13-v2-chemical-records.json',A/'ch12-v2-enteric-sources.json',A/'ch12-v2-enteric-extraction-proof.json',A/'ch12-v2-enteric-mouse-enterocyte.png',A/'ch12-v2-enteric-mouse-vessels.jpg']
files +=[A/f for f in ['ch13-v2-digestion-model.js','ch13-v2-digestion-controls.js','ch13-v2-digestion.css','ch13-v2-glycylglycine.svg','ch13-v2-glycine.svg','ch13-v2-lipid-tag.svg','ch13-v2-lipid-products.svg','observed-image-dialog.css','observed-image-dialog.js']]
for kind in ['protein','lipid']:
 t=R/'figures'/('ch13_'+kind+'_mechanism_v2.template.html');host=A/('ch13-v2-'+kind+'-reference.html');host.write_bytes(t.read_bytes());files.extend([t,host])
files.append(Path(__file__))
p={'date':'2026-11-09','sources':source,'mechanisms':{'protein':'3dipeptides/6residues acrossentry,hydrolysis,AAexit;3waterconsumed,nouniversalHcount','lipid':'3long-chainacylequivalentcargoluminalhydrolysis/molecularuptake/reesterificationassembly/basalrelease/lactealentry;notparticlecount'},'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'private_network_required':False,'chemical_reconstruction':'PublicSMILESrecord+editableoriginalSVG. VectorcreationseparateRDKitstep;compositiondoesnotrequireRDKit.'},'artifacts':{f.relative_to(R).as_posix():sha(f) for f in files},'acceptance':{'current':False,'Bsource_state_staticprototype':'Scopedapprovalbeforemotion;exactprivatecriticreportsretained','actual_runtime_source_appearance_print':'PENDING root/B'}}
(A/'ch13-v2-digestion-provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('TWO_DIGESTION_MECHANISMS_BUILT')
