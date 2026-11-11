"""Offline regional MRI composition from immutable source-derived panels."""
from pathlib import Path
import hashlib
import json
from PIL import Image
R=Path(__file__).resolve().parents[1]
A=R/'assets'
P='ch18-v2-regional-mri-'
T=R/'figures/ch18_regional_mri_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'))
files=[A/(P+'sources.json')]
for item in s['files']:
    f=A/item['file']
    assert sha(f)==item['sha256']
    im=Image.open(f).convert('RGB')
    assert list(im.size)==item['dimensions']
    assert hashlib.sha256(im.tobytes()).hexdigest()==item['decoded_RGB_sha256']
    files.append(f)
host=A/(P+'reference.html')
host.write_bytes(T.read_bytes())
files += [host,T,Path(__file__),A/'observed-image-dialog.css',A/'observed-image-dialog.js']
p={'date':'2026-11-09','sources':s,'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},
   'artifacts':{f.relative_to(R).as_posix():sha(f) for f in files},'acceptance':{'current':False,'assembled_source_appearance':'Pending independent review','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(p,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('REGIONAL_MRI_BUILT')
