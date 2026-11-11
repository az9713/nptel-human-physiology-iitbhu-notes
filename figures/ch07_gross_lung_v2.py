"""Recompose whole acquired lung photograph without image transformation.

Public immutable WebP/sourceJSON/template/shared modal only; no private input,
network, Blender, encoding or image resampling required.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';P='ch07-v2-gross-lung'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'));x=s['input'];photo=A/x['file']
assert sha(photo)==x['sha256'];im=Image.open(photo);assert im.format=='WEBP' and list(im.size)==x['pixels']
assert hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()==x['rgb_sha256']
shared={'observed-image-dialog.css':'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b','observed-image-dialog.js':'5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211'}
for n,h in shared.items():assert sha(A/n)==h,n
template=ROOT/'figures/ch07_gross_lung_v2.template.html';host=A/(P+'-reference.html');host.write_bytes(template.read_bytes())
r={'date':'2026-11-09','status':'Candidate; source/anatomy, native appearance and actual browser/print review pending, no acceptance inferred',
 'source_record':P+'-sources.json','input':x,'acquisition':s['acquisition'],'source_caption':s['source_caption'],'panel_key':s['panel_key'],'preparation':s['cohort_preparation'],'context_limit':s['context_limit'],'scale_limit':s['scale_limit'],'print':s['print'],'coverage_gaps':s['coverage_gaps'],'independence':s['independence'],
 'controls':'Native/Fit/Close sourceimage modal; explicit inner contained-height region, shared target-region keyboardpan and openerfocusreturn. Source967×654 restored without adding pixels. Actual phone/allcorners tests pending.',
 'reproduction':{'builder':'figures/ch07_gross_lung_v2.py','template':'figures/ch07_gross_lung_v2.template.html','builder_sha256':sha(__file__),'template_sha256':sha(template),'python':platform.python_version(),'pillow':pillow_version,'scope':'Exact public acquiredWebP/sourceJSON/template/sharedmodal only. Acquisition separately browser-observed; no privatework/network/resampling on rebuild.'},'shared_dependencies':shared,
 'pending':['Independent source panel A/right B/left and fixed-specimen limit check','Native appearance/teaching proof; no new leader or measured-scale claim','Actual desktop650390 NativeFit/focus/End/allcorners/keyboardpan','Actual130mm PDF sourceA/B/fissures/externalkey/attachedcredit/readable189ppi exception/pagebreaks','No canonical Chapter7 integration']}
r['artifacts']={p.name:sha(p)for p in [photo,A/(P+'-sources.json'),host]+[A/n for n in shared]}
(A/(P+'-provenance.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('OBSERVED_GROSS_LUNG_GALLERY_COMPOSED',flush=True)
