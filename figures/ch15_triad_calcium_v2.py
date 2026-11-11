"""Rebuild source-preserving triad pair and a closed perturbation-pool lesson.
Only immutable public sourcePNG/JSON, template/JS and shared modal are inputs.
"""
from pathlib import Path
import hashlib,json,math,platform
from PIL import Image,__version__ as pillow_version
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch15-v2-triad-calcium';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'));src=A/s['input']['file'];assert sha(src)==s['input']['sha256'];im=Image.open(src).convert('RGB');assert list(im.size)==s['input']['pixels'];assert hashlib.sha256(im.tobytes()).hexdigest()==s['input']['rgb_sha256'];outputs=[src]
for c in s['crops']:
 p=A/c['file'];q=im.crop(tuple(c['rect']));q.save(p);assert sha(p)==c['sha256'];assert hashlib.sha256(q.tobytes()).hexdigest()==c['rgb_sha256'];outputs.append(p)
def state(u,release=True,uptake=True):
 kr=3 if release else 0;ku=1 if uptake else 0;k=kr+ku;c=kr/k*(1-math.exp(-k*min(u,1)))if k else 0
 if u>1:c*=math.exp(-ku*(u-1))
 return c,1-c
paths=[]
for kind,color,dash in [('cyt','#965e0d',''),('sr','#0b6680',''),('off','#8f4779','5 7')]:
 pts=[]
 for i in range(401):
  u=i/100;c,sr=state(u,uptake=kind!='off');v=sr if kind=='sr'else c;pts.append(f'{100+u/4*640:.3f},{370-v*280:.3f}')
 paths.append('<polyline fill="none" stroke="'+color+'" stroke-width="4" stroke-dasharray="'+dash+'" points="'+' '.join(pts)+'"/>')
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="Selected conserved perturbation-pool comparison"><rect width="800" height="450" fill="white"/><g font-family="Arial,sans-serif" font-size="24" fill="#111"><text x="30" y="30">Tracked perturbation · not free calcium</text><text x="100" y="65" font-size="21">Solid: uptake enabled · dotted: cytosol, uptake off</text><path d="M100 85V370H745" stroke="#555" fill="none"/><path d="M260 85V370" stroke="#777" stroke-dasharray="5 7"/><text x="45" y="377">0</text><text x="30" y="237">0.5</text><text x="45" y="97">1</text><text x="95" y="405">0</text><text x="255" y="405">1</text><text x="415" y="405">2</text><text x="575" y="405">3</text><text x="735" y="405">4</text><text x="100" y="440">Release command ends at u = 1</text><text x="580" y="440">Model u</text></g>'''+''.join(paths)+'</svg>'
plot=A/(P+'-print-model.svg');plot.write_text(svg+'\n',encoding='utf-8');outputs.append(plot)
rows=[]
for name,release,uptake in [('Release + uptake',True,True),('Release, uptake off',True,False),('No release',False,True)]:
 for u in [1,4]:
  c,sr=state(u,release,uptake);rows.append(f'<tr><td>{name}</td><td>{u}</td><td>{c:.4f}</td><td>{sr:.4f}</td></tr>')
t=R/'figures/ch15_triad_calcium_v2.template.html';h=A/(P+'-reference.html');h.write_text(t.read_text(encoding='utf-8').replace('<!-- MODEL_TABLE -->',''.join(rows)),encoding='utf-8');outputs.append(h)
r={'date':'2026-11-09','status':'Candidate; independent assembled source/native appearance and actual browser/print pending, no acceptance inferred','source_record':P+'-sources.json','source_record_sha256':sha(A/(P+'-sources.json')),'source_input':s['input'],'crops':s['crops'],'component_rights':s['rights'],'model':s['controlled_model'],'notation':'u dimensionless; krel=3,kup=1 constantcoefficients whenenabled. Never3 dividedbycoordinateu. c0=0 istrackedperturbation, neverzero basalCa.','print':s['print'],'review_basis':s['review_basis'],'reproduction':{'builder':'figures/ch15_triad_calcium_v2.py','builder_sha256':sha(__file__),'template':'figures/ch15_triad_calcium_v2.template.html','template_sha256':sha(t),'python':platform.python_version(),'pillow':pillow_version,'inputs':'Immutable public sourcePNG/JSON/template/JS/sharedmodal only; no work/network/sourceacquisition dependency'},'artifacts':{p.name:sha(p)for p in outputs+[A/(P+'.js'),A/'observed-image-dialog.css',A/'observed-image-dialog.js']},'pending':['ActualD/E NativeFit/containedpan/focus/sourcebar andlegend review','Actualthreewidth globalcontainment/controls/seek/presets/rate/reducedmotion/stateaudit','Actualtwofigureprintpagebreaks/182ppi density/sourcebar and235ppi segmentation/sourcelegend/key/credit','Canonical15 remains frozen: no integration or wholeECC/actomyosin acceptance inferred']}
(A/(P+'-provenance.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('NEW_TRIAD_GEOMETRY_AND_CONSERVED_PERTURBATION_MODEL_COMPOSED')
