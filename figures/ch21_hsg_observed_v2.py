"""Offline source-preserving clinical source plate composition; no private/network dependencies."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets';T=R/'figures/ch21_hsg_observed_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/'ch21-v2-hsg-observed-sources.json').read_text(encoding='utf-8'));im=A/s['file']['file'];assert sha(im)==s['file']['sha256'];host=A/'ch21-v2-hsg-observed-reference.html';host.write_bytes(T.read_bytes())
f=[im,A/'ch21-v2-hsg-observed-sources.json',T,host,Path(__file__),A/'observed-image-dialog.css',A/'observed-image-dialog.js'];p={'date':'2026-11-09','sources':s,'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'source_acquisition':'Separate original PDF raw image extraction; native identity in public source JSON'},'artifacts':{q.relative_to(R).as_posix():sha(q) for q in f},'acceptance':{'current':False,'source_native_final':'PendingB','actual_browser_print':'Pendingroot'}}
(A/'ch21-v2-hsg-observed-provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('CLINICAL_OBSERVED_BUILT')
