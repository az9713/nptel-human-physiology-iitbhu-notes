"""Compose unchanged licensed ovarian fields; all reproduction inputs are public assets."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch19-v2-follicle-observed-';T=R/'figures/ch19_follicle_observed_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'))
images=[A/r['file'] for r in s['records']]
for image,record in zip(images,s['records']):assert sha(image)==record['sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__),A/(P+'sources.json'),A/'observed-image-dialog.css',A/'observed-image-dialog.js']+images
record={'date':'2026-11-09','purpose':s['purpose'],'licence':s['licence'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'acquisition':'Original complete source JPEGs acquired separately from exact manual URI links; public immutable files and records suffice for composition, full manual remains private'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_native':'Pending independent assembled review','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('FOLLICLE_OBSERVED_BUILT')
