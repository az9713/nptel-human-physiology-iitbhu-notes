"""Source-preserving adult ultrasound + mouse observed-nephron reconstruction.
Public inputs only; component-specific CC BY and Optica noncommercial terms.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch16-v2-renal-anatomy';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'))
for x in s['inputs']:
 p=A/x['file'];im=Image.open(p);assert sha(p)==x['sha256'] and list(im.size)==x['pixels'];assert hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()==x['rgb_sha256']
crop=A/(P+'-nephron-c.png');Image.open(A/(P+'-nephron-source.png')).crop(tuple(s['nephron']['crop_c'])).save(crop)
t=R/'figures/ch16_renal_anatomy_v2.template.html';h=A/(P+'-reference.html');h.write_bytes(t.read_bytes())
shared={n:sha(A/n)for n in ['observed-image-dialog.css','observed-image-dialog.js']}
p={'date':'2026-11-09','status':'Candidate; final source/anatomy/appearance/UI/print review pending, no acceptance inferred','source_record':P+'-sources.json','source_record_sha256':sha(A/(P+'-sources.json')),'component_rights':{'ultrasound':s['ultrasound']['rights'],'nephron':s['nephron']['rights']},'crop':{'file':crop.name,'source':P+'-nephron-source.png','rect':s['nephron']['crop_c'],'pixels':list(Image.open(crop).size),'operation':'Exact integer sourcepanel crop, no resampling or pixel/color modification'},'independence':s['independence'],'print':s['print'],'coverage_limits':s['coverage_limits'],'controls':'Contained Native/Fit/Close keyboardpan modal; focusreturn; target-only inline arrow60/Home/End/Page pan. Actual browser tests pending.','reproduction':{'builder':'figures/ch16_renal_anatomy_v2.py','builder_sha256':sha(__file__),'template':'figures/ch16_renal_anatomy_v2.template.html','template_sha256':sha(t),'python':platform.python_version(),'pillow':pillow_version,'inputs':'Immutable public acquired PNGs/sourceJSON/template/sharedmodal; no privatework or network dependency. SourcePDF acquisitions separately documented.'},'shared_dependencies':shared,'pending':['B actual source/rights and new layout','Root desktop650390 Native/Fit/pan and actual125ppi source-limited print legibility/pagebreaks','No molecular transporter or complete countercurrent coverage inferred']}
p['artifacts']={x.name:sha(x)for x in [h,crop]+[A/i['file']for i in s['inputs']]}
(A/(P+'-provenance.json')).write_text(json.dumps(p,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('OBSERVED_RENAL_ANATOMY_GALLERY_COMPOSED')
