"""Offline composition of unchanged source-marked MRI screen recordings."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch20-v2-placental-mri-';T=R/'figures/ch20_placental_mri_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));files=[]
for c in s['cases']:
    for r in [c['movie']]+c['stills']:
        p=A/r['file'];assert sha(p)==r['sha256'];files.append(p)
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files += [host,T,Path(__file__),A/(P+'sources.json')]+[A/n for n in ['observed-image-dialog.css','observed-image-dialog.js','observed-video-controls.css','observed-video-controls.js']]
record={'date':'2026-11-09','role':s['role'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'acquisition':'Original sourceMP4s acquired separately; all immutable movies/stills and exact source metadata are public composition inputs'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_claims':'Pending independent assembled retarget','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('PLACENTAL_MRI_BUILT')
