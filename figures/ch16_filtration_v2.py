"""Rebuild observed filtration wall / external controlled pressure lesson.
Inputs are immutable public full-figure PNGs and source JSON; no work/ inputs.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; P='ch16-v2-filtration'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'))
whole=A/(P+'-source-figure7.png'); crop=A/(P+'-control7a.png')
assert Image.open(whole).size==(1623,1696)
assert sha(whole)==s['pdf_extraction_audit'][1]['sha256']
assert sha(A/(P+'-source-figure6.png'))==s['pdf_extraction_audit'][0]['sha256']
im=Image.open(whole).convert('RGB').crop((169,102,890,621)); im.save(crop)
assert sha(crop)==s['crop']['sha256']
assert hashlib.sha256(im.tobytes()).hexdigest()==s['crop']['rgb_sha256']
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" role="img" aria-labelledby="anatomy-title anatomy-desc">
<title id="anatomy-title">Observed mouse filtration wall: two sides and resolved profiles</title><desc id="anatomy-desc">Unchanged source Figure 7A. Neutral leaders identify a capillary-side bright field below the dense curved glomerular basement membrane and podocyte foot-process profiles above it. The upper cleft is urinary-space side, not a proven connected capsular lumen. No pressure vector, pore, particle path or added scale bar.</desc>
<rect width="1000" height="800" fill="#111b23"/><image href="ch16-v2-filtration-control7a.png" x="140" y="130" width="721" height="519"/>
<g id="anatomical-labels" data-anatomy-label="true" font-family="Arial,sans-serif" font-size="30" fill="#f0f5f7" stroke="none">
<text x="35" y="52">Urinary-space side</text><text x="35" y="87" font-size="24">Subpodocyte-space profile</text>
<text x="590" y="52">Foot-process profiles</text><text x="590" y="87" font-size="24">Podocyte interfaces</text>
<text x="35" y="727">Capillary-lumen side</text><text x="662" y="727">GBM</text><text x="662" y="764" font-size="24">Dense curved band</text>
<g stroke="#f1f5f7" stroke-width="2.5" fill="none"><path d="M300 98L440 250"/><path d="M690 98L570 403"/><path d="M300 695L410 530"/><path d="M720 695L460 420"/></g>
<g fill="#f1f5f7"><circle cx="440" cy="250" r="4"/><circle cx="570" cy="403" r="4"/><circle cx="410" cy="530" r="4"/><circle cx="460" cy="420" r="4"/></g></g></svg>'''
svgpath=A/(P+'-anatomy.svg');svgpath.write_text(svg+'\n',encoding='utf-8')
t=ROOT/'figures/ch16_filtration_v2.template.html';host=A/(P+'-reference.html')
host.write_text(t.read_text(encoding='utf-8').replace('<!-- ANATOMY_SVG -->',svg),encoding='utf-8')
shared={n:sha(A/n) for n in ['observed-image-dialog.css','observed-image-dialog.js']}
r={'date':'2026-11-09','status':'Candidate; exact composition, anatomy, appearance and actual UI/print review pending; no acceptance inferred','source_record':P+'-sources.json','source_record_sha256':sha(A/(P+'-sources.json')),'model':s['controlled_model'],'crop':s['crop'],'anatomical_anchors_crop_pixels':s['anatomical_anchors_crop_pixels'],'limits':s['anatomical_limits'],'print':s['print'],'rights':'Source TEM CC BY 4.0; exact integer crop and external vector labels disclosed. No photograph relabelled as human or measured-pressure experiment.','reproduction':{'builder':'figures/ch16_filtration_v2.py','builder_sha256':sha(__file__),'template':'figures/ch16_filtration_v2.template.html','template_sha256':sha(t),'python':platform.python_version(),'pillow':pillow_version,'input_scope':'Public immutable source figure PNGs, source JSON, template and shared modal dependencies only; original PDF acquisition separately documented, no private work/network required'},'shared_dependencies':shared,'pending':['B actual leader endpoint/composition check','Root actual 390/650/desktop play/seek/step/pan/modal/reduced-motion checks','Actual 85mm source-limited 215ppi PDF and attached external key/credit/pagebreak checks','Gross kidney/nephron architecture and segment mechanisms remain separate unfinished work']}
r['artifacts']={p.name:sha(p)for p in [whole,A/(P+'-source-figure6.png'),crop,svgpath,host,A/(P+'.js')]}
(A/(P+'-provenance.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('OBSERVED_FILTRATION_LESSON_COMPOSED')
