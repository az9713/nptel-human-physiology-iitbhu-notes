"""Reproduce the complete immutable NC-ND source figure; composition only, no adaptation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch20-v2-gross-placenta-';T=R/'figures/ch20_gross_placenta_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));im=A/s['image']['file'];assert sha(im)==s['image']['sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__),im,A/(P+'sources.json'),A/'observed-image-dialog.css',A/'observed-image-dialog.js']
record={'date':'2026-11-09','role':s['role'],'rights':s['rights'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'original_source':'PDF separately acquired and whole JPEG raw stream extracted; exact public immutable figure sufficient to rebuild composition. Full PDF private.','adaptation':'None; complete source JPEG must not be cropped, retouched or annotated'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_native':'Pending independent assembled retarget','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('GROSS_PLACENTA_BUILT')
