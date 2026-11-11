"""Offline composition from immutable licensed organoid media and exact source records."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch21-v2-organoid-observed-';T=R/'figures/ch21_organoid_observed_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));files=[]
for item in [s['original'],s['movie']]+s['stills']+s['proofs']:
    p=A/item['file'];assert sha(p)==item['sha256'],str(p);files.append(p)
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files += [host,T,Path(__file__),A/(P+'sources.json')]+[A/n for n in ['observed-image-dialog.css','observed-image-dialog.js','observed-video-controls.css','observed-video-controls.js']]
record={'date':'2026-11-09','role':s['role'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'inputs':'Original MOV, lossless WebM, full-field decoded PNGs, RGB/PTS proof and source JSON are immutable public composition inputs. Original acquisition and optional ffmpeg re-encoding are separate documented steps.'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_claims':'Pending independent assembled retarget','actual_browser_print':'Pending root; native codec, event playback and physical still visibility unverified'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('ORGANOID_OBSERVED_BUILT',sha(host))
