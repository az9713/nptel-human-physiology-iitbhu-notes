"""Offline composition. Immutable public source inputs; no private/network dependencies."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch19-v2-oocyte-'
T=R/'figures/ch19_oocyte_inventory_v2.template.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'sources.json')).read_text(encoding='utf-8'))
assert sha(A/s['context_file'])==s['context_sha256']
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__)]+[A/n for n in [P+'sources.json',P+'model.js',P+'controls.js',s['context_file'],s['context_source_record'],'observed-image-dialog.css','observed-image-dialog.js']]
record={'date':'2026-11-09','role':s['role'],'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'actual_browser_print':'Pending root','assembled_source_model':'Pending independent review'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('OOCYTE_INVENTORY_BUILT')
