"""Offline public-input-only composition of controlled epithelial accounting."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets';T=R/'figures/ch12_epithelial_transport_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((A/'ch12-v2-enteric-sources.json').read_text(encoding='utf-8'))
s=next(x for x in source['sources'] if x['id']=='enterocyte');assert sha(A/s['file'])==s['sha256']
host=A/'ch12-v2-epithelial-reference.html';host.write_bytes(T.read_bytes())
files=[T,Path(__file__),host,A/'ch12-v2-epithelial-model.js',A/'ch12-v2-epithelial-controls.js',A/'ch12-v2-enteric-sources.json',A/s['file']]
p={'date':'2026-11-09','purpose':'Separate fixed SEM context plus original idealized transport bookkeeping; no molecule tracked across source pixels','source':s,'mechanism':{'glucose_galactose':'3arbitrary sugar equivalents,2Na per sugar coupled entry viaSGLT1;conditionalbasalGLUT2exit','fructose':'3arbitrary sugar equivalents GLUT5entry/GLUT2exit,no directlycoupledNaATP','clock':'12presentationseconds,notphysiological;linearphaseinterpolation,notkinetics','conservation':'3sugar equivalents;Gbranch6coupledNa,Fbranch0;otherNaturnoveromitted','pump':'Separateconcurrent3Naout2KinperATPcontext,notanimatedscheduledcycles','scope':'Carrieridentityliterature-based,notresolvedSEM;independentepithelium/blood/lymph observationsunregistered'},'scientific_basis':[{'url':'https://pubmed.ncbi.nlm.nih.gov/8599647/','role':'humanSGLT1 coupling experiment inexpression system'},{'url':'https://doi.org/10.1096/fj.15-272195','role':'mouseGLUT5absorption/trafficking'},{'url':'https://pubmed.ncbi.nlm.nih.gov/8405848/','role':'ratbasolateralGLUT2sugartransport'}],'reproduction':{'private_network_required':False,'builder':'figures/ch12_epithelial_transport_v2.py','template':T.relative_to(R).as_posix()},'artifacts':{x.relative_to(R).as_posix():sha(x) for x in files},'acceptance':{'source_state_static_prototype':'Bscopedcompositionapproved;exactprivatecriticrecordretainedseparately','actual_runtime_PDF':'PENDING root','current':False}}
(A/'ch12-v2-epithelial-provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('EPITHELIAL_TRANSPORT_BUILT')
