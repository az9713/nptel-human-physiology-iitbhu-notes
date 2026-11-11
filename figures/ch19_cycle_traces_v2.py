"""Offline composition of an original pure quantitative teaching graph."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch19-v2-cycle-traces-';T=R/'figures/ch19_cycle_traces_v2.template.html';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=A/(P+'reference.html');host.write_bytes(T.read_bytes())
files=[host,T,Path(__file__)]+[A/(P+n) for n in ['sources.json','model.js','controls.js','default.svg']]
record={'date':'2026-11-09','role':'Independent synthetic hormone functions on separate arbitrary scales; no anatomical rendering or coupled feedback','reproduction':{'builder':Path(__file__).relative_to(R).as_posix(),'template':T.relative_to(R).as_posix(),'private_network_required':False,'default_vector':'Public model.js plot(0), SVG preserved in template and default.svg'},'artifacts':{p.relative_to(R).as_posix():sha(p) for p in files},'acceptance':{'current':False,'source_model':'Pending independent assembled review','actual_browser_print':'Pending root'}}
(A/(P+'provenance.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('CYCLE_TRACES_BUILT')
