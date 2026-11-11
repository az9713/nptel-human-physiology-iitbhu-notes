"""Offline, public-input-only assembly of term histology and independent quantitative lab."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch20-v2-villus-gas-';T=R/'figures/ch20_villus_gas_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));im=A/s['image']['file'];assert sha(im)==s['image']['sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__),im]+[A/n for n in [P+'sources.json',P+'model.js',P+'controls.js','observed-image-dialog.css','observed-image-dialog.js']]
record={'date':'2026-11-09','role':s['role'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_model':'Pending independent assembled review','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('VILLUS_GAS_BUILT')
