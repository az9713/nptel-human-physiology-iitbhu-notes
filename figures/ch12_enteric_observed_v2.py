"""Offline deterministic composition from immutable public source images/JSON. Initial acquisition/extraction separate, fully recorded; no private paths needed."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]; A=R/'assets'
PREF='ch12-v2-enteric-'
T=R/'figures'/'ch12_enteric_observed_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((A/(PREF+'sources.json')).read_text(encoding='utf-8'))
for s in record['sources']:
 p=A/s['file'];assert sha(p)==s['sha256'];im=Image.open(p);assert list(im.size)==s['dimensions'];assert hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()==s['decoded_rgb_sha256']
shared=['observed-image-dialog.css','observed-image-dialog.js']
assert sha(A/shared[0])=='fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b'
assert sha(A/shared[1])=='5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211'
host=A/(PREF+'reference.html');host.write_bytes(T.read_bytes())
inputs=[A/(PREF+'sources.json'),A/(PREF+'extraction-proof.json')]+[A/s['file'] for s in record['sources']]
p={'date':'2026-11-09','scope':'Observed structural candidate; not complete digestive mechanism','sources':record,'operations':'Compose immutable complete images/exact source crop; no local pixel transformation.','reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'initial_acquisition':'Separate owning primary PDF/catalogue acquisition; exact extraction/crop recorded in source JSON.'},'artifacts':{x.relative_to(R).as_posix():sha(x) for x in inputs+[host,T,Path(__file__)]+[A/s for s in shared]},'acceptance':{'current':False,'actual_browser_PDF':'PENDING root','independent_source_appearance':'PENDING B'}}
(A/(PREF+'provenance.json')).write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(host.name,'BUILT')
