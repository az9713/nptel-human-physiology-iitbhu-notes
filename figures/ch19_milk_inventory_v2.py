"""Offline public-input composition. Static default graph remains with JavaScript disabled."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch19-v2-milk-inventory-';T=R/'figures/ch19_milk_inventory_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'));im=A/s['context']['file'];assert sha(im)==s['context']['sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__),im]+[A/n for n in [P+'sources.json',P+'model.js',P+'controls.js',P+'default.svg',s['context']['source_record'],'observed-image-dialog.css','observed-image-dialog.js']]
record={'date':'2026-11-09','purpose':s['purpose'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'static_graph':'Public editable model.js plot(2,0.2,0), exact SVG included in template and immutable default.svg'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_model':'Pending independent assembled review','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('MILK_INVENTORY_BUILT')
