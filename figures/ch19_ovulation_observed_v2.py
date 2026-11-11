"""Offline composition of unchanged ovulation movie and exact source-coordinate stills."""
from pathlib import Path
import hashlib
import json
from PIL import Image
R=Path(__file__).resolve().parents[1]
A=R/'assets'
P='ch19-v2-ovulation-observed-'
T=R/'figures/ch19_ovulation_observed_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'))
assert sha(A/s['media']['file'])==s['media']['sha256']==s['primary']['original_download']['sha256']
files=[A/(P+'sources.json'),A/s['media']['file']]
for item in s['posters']:
    im=Image.open(A/item['file']).convert('RGB')
    assert sha(A/item['file'])==item['sha256']
    assert hashlib.sha256(im.tobytes()).hexdigest()==item['decoded_rgb_sha256']
    detail=item['print_detail']
    crop=Image.open(A/detail['file']).convert('RGB')
    assert sha(A/detail['file'])==detail['sha256']
    assert hashlib.sha256(crop.tobytes()).hexdigest()==detail['decoded_rgb_sha256']
    assert crop.tobytes()==im.crop(tuple(detail['crop_rect_xyxy'])).tobytes()
    files += [A/item['file'],A/detail['file']]
host=A/(P+'reference.html')
host.write_bytes(T.read_bytes())
files += [host,T,Path(__file__)]+[A/n for n in ('observed-image-dialog.css','observed-image-dialog.js','observed-video-controls.css','observed-video-controls.js')]
p={'date':'2026-11-09','sources':s,'operations':'Unchanged original MP4; exact decoded stills and declared left-context crops, no retouch or new labels.',
   'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},
   'artifacts':{f.relative_to(R).as_posix():sha(f) for f in files},
   'acceptance':{'current':False,'source_native':'B scoped pre-host pass','assembled_review':'Pending independent reviewer','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('OVULATION_OBSERVED_BUILT')
