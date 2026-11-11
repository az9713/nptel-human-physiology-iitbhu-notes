"""Offline composition of microscopy context and quantitative inventory controls."""
from pathlib import Path
import json
import hashlib
R=Path(__file__).resolve().parents[1]
A=R/'assets'
T=R/'figures/ch18_meiosis_inventory_v2.template.html'
P='ch18-v2-meiosis-'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tissue=json.loads((A/'ch18-v2-testis-observed-sources.json').read_text(encoding='utf-8'))
assert sha(A/tissue['file']['file'])==tissue['file']['sha256']
host=A/(P+'reference.html')
host.write_bytes(T.read_bytes())
names=['ch18-v2-testis-observed-sources.json',tissue['file']['file'],P+'sources.json',P+'model.js',P+'controls.js','observed-image-dialog.css','observed-image-dialog.js']
files=[host,T,Path(__file__)]+[A/n for n in names]
p={'date':'2026-11-09','purpose':'Human completed meiotic inventory: quantitative graph, not chromosome anatomy or measured motion',
   'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},
   'artifacts':{f.relative_to(R).as_posix():sha(f) for f in files},
   'acceptance':{'current':False,'actual_browser_print':'Pending root','assembled_model_review':'Pending independent reviewer'}}
(A/(P+'provenance.json')).write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
print('MEIOSIS_INVENTORY_BUILT')
