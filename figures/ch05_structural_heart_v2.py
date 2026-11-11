"""Source-preserving human structural-heart gallery; Python3.13/Pillow11.0.0.
Rebuild uses immutable public nativePNGs/sourceJSON/template/shared controls only.
Includes disclosed full PanelA and lower measurement-detail exact integer crops; no private acquisition, network, Blender or resampling.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch05-v2-structural-heart'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'))
for i in s['figures']:
 p=A/i['file'];assert sha(p)==i['sha256'];im=Image.open(p).convert('RGB');assert list(im.size)==i['dimensions'];assert hashlib.sha256(im.tobytes()).hexdigest()==i['rgb_sha256']
for i in s.get('derived_views',[]):
 source=A/i['source_file'];assert sha(source)==i['source_sha256']
 crop=Image.open(source).convert('RGB').crop(tuple(i['crop_rect_xyxy']))
 assert list(crop.size)==i['dimensions']
 assert hashlib.sha256(crop.tobytes()).hexdigest()==i['rgb_sha256']
 path=A/i['file'];crop.save(path);assert sha(path)==i['sha256']
shared={'observed-image-dialog.css':'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b','observed-image-dialog.js':'5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211'}
for n,h in shared.items():assert sha(A/n)==h
builder=Path(__file__);template=R/'figures/ch05_structural_heart_v2.template.html';host=A/(P+'-reference.html');host.write_bytes(template.read_bytes())
r=dict(date='2026-11-09',status='Candidate; independent anatomy/appearance, actual responsive/native-Fit/print review pending',sources=P+'-sources.json',teaching_purpose='Fixed human anterior/greatvesselRVOT, opened pulmonary/tricuspid apparatus and sectionalRVOT/RV/LV relationships; no livevalvephase or conduction.',images=s['figures'],derived_views=s.get('derived_views',[]),image_integrity='Three whole native source PNGs and full PanelA crop unchanged; exact lower PanelA crop added for print, with original W/M/E endpoints, sampling guides and5mm bar. Disclosed rectangles and identical RGB. No resampling/recolor/newleaders/arrow/scale.',independence=s['independence'],preparation=s['preparation'],source_cautions=s['source_cautions'],coverage_gaps=['Four complete chambers/mitral/aortic equivalent detail','Complete coronary tree and ambiguousSAA locator excluded','Normal livevalveopening/closure and hemodynamic phases','Conduction/ECG-mechanical registration'],controls='Native/Fit/Close; source1890px restored in explicitly height-clamped containedviewport, focus/keyboardpan sharedadapter and openerreturn. No outerdialog-only pan. Actualphone/allcorners test pending.',print={'figures':4,'widths_mm':[i['print_width_mm']for i in s['figures']+s.get('derived_views',[]) if i.get('print_width_mm') is not None],'output_ppi':[i['print_ppi']for i in s['figures']+s.get('derived_views',[]) if i.get('print_ppi') is not None],'external_key_min_pt':9.5,'credits_min_pt':9,'source_labels':'Original labels/bars unchanged; external readable key includingTV/RAVV distinction. Actual original glyph recognition must be checked in PDF.','plan':'Three whole sourcefigures plus one replacement lower-PanelA detail page on whitehtml/body, not a fifth plate. FullA retained web/native; print lowercrop640x850 at140mm/185.94mm height,116.1ppi source-limited enlargement. Actual4pagecount/glyph/bar/credit legibility pending root/B.'},reproduction={'builder':'figures/ch05_structural_heart_v2.py','template':'figures/ch05_structural_heart_v2.template.html','builder_sha256':sha(builder),'template_sha256':sha(template),'python':platform.python_version(),'pillow':pillow_version,'scope':'Deterministic composition using publicimmutablePNGs/sourceJSON/template and sharedmodal. Initial acquisition separate; no privatework/network/Blender requirement.'},shared_dependencies=shared,pending=['Independent anatomy/source-label and separate appearance/teaching review','Root desktop650390 Native/Fit/End/allcorners/focus/keyboard pan','Root actual4platePDF including PanelA native source glyph/bar/key/credit/pagebreaks','No acceptance inferred from source integrity; canonicalintegration separately recorded'])
r['artifacts']={p.name:sha(p)for p in [A/i['file']for i in s['figures']+s.get('derived_views',[])]+[A/(P+'-sources.json'),host]+[A/n for n in shared]};(A/(P+'-provenance.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('STRUCTURAL_HEART_GALLERY_COMPOSED')
