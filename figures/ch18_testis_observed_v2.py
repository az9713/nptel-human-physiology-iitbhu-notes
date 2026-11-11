"""Offline source-preserving human testis plate composition; no private/network dependencies."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets';T=R/'figures/ch18_testis_observed_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/'ch18-v2-testis-observed-sources.json').read_text(encoding='utf-8'));im=A/s['file']['file'];assert sha(im)==s['file']['sha256'];host=A/'ch18-v2-testis-observed-reference.html';host.write_bytes(T.read_bytes())
f=[im,A/'ch18-v2-testis-observed-sources.json',T,host,Path(__file__),A/'observed-image-dialog.css',A/'observed-image-dialog.js'];p={'date':'2026-11-09','sources':s,'reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'source_acquisition':'Separate original PDF xref119 extraction and exact a/b crop; original hashes and crop rectangle in public source JSON'},'artifacts':{q.relative_to(R).as_posix():sha(q) for q in f},'acceptance':{'current':False,'source_native_final':'PendingB','actual_browser_print':'Pendingroot'}}
(A/'ch18-v2-testis-observed-provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('TESTIS_OBSERVED_BUILT')
