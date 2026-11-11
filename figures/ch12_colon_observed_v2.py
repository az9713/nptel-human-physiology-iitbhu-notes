"""Offline composition of unchanged source movie and native decoded posters."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch12-v2-colon-observed-';T=R/'figures/ch12_colon_observed_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));assert sha(A/s['media']['file'])==s['media']['sha256']
for f in s['posters']:
 p=A/f['file'];assert sha(p)==f['sha256'];im=Image.open(p);assert list(im.size)==f['dimensions'];assert hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()==f['decoded_rgb_sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[A/(P+'sources.json'),A/s['media']['file'],A/(P+'decode-framemd5.txt')]+[A/x['file'] for x in s['posters']]+[A/x for x in ['observed-image-dialog.css','observed-image-dialog.js','observed-video-controls.css','observed-video-controls.js']]+[host,T,Path(__file__)]
p={'date':'2026-11-09','sources':s,'operations':'No movie transformation; full decoded native stills; all1620frames decoded without error.','reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},'artifacts':{x.relative_to(R).as_posix():sha(x) for x in files},'acceptance':{'current':False,'independent_source_native':'ScopedBsource/nativeapproved;actualcomposedhostunreviewed','actual_browser_print':'PENDING root'}}
(A/(P+'provenance.json')).write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('COLON_OBSERVED_BUILT')
