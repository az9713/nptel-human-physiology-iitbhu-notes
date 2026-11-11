"""Observed source-native junction and independently selected passive circuit.
Public immutable sourceJPEG/JSON, template/JS only; no work/network dependency.
"""
from pathlib import Path
import hashlib,json,math
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'assets';P='ch15-v2-nmj-epp';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'));src=A/s['input']['file'];assert sha(src)==s['input']['sha256'];im=Image.open(src).convert('RGB');assert list(im.size)==s['input']['pixels'];assert hashlib.sha256(im.tobytes()).hexdigest()==s['input']['rgb_sha256'];crop=A/s['crop']['file'];im.crop(tuple(s['crop']['rect'])).save(crop);assert sha(crop)==s['crop']['sha256']
def points(g):
 inf=-90/(1+g);tau=10/(1+g);cross=-tau*math.log((-55-inf)/(-90-inf))if inf>-55 else None;pre=[];post=[]
 for i in range(301):
  t=i/10;v=inf+(-90-inf)*math.exp(-t/tau);p=f'{100+t/30*640:.3f},{365-(v+95)/65*290:.3f}';(post if cross is not None and t>=cross else pre).append(p)
 if cross is not None and cross<30:
  p=f'{100+cross/30*640:.3f},{365-40/65*290:.3f}';pre.append(p);post.insert(0,p)
 return ' '.join(pre),' '.join(post)
curves=[]
for g,color in [(1,'#185c82'),(.5,'#985a14')]:
 pre,post=points(g);curves.append(f'<polyline points="{pre}" stroke="{color}" stroke-width="4" fill="none"/><polyline points="{post}" stroke="{color}" stroke-width="4" stroke-dasharray="5 7" fill="none"/>')
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="Selected passive endplate comparison"><rect width="800" height="450" fill="white"/><g font-family="Arial,sans-serif" font-size="24" fill="#111"><text x="35" y="32">Membrane potential, Vm (mV)</text><path d="M100 65V365H745" stroke="#555" fill="none"/><path d="M100 186.54H740" stroke="#555" stroke-dasharray="8 7"/><text x="32" y="349">−90</text><text x="32" y="194">−55</text><text x="32" y="81">−30</text><text x="94" y="399">0</text><text x="300" y="399">10</text><text x="512" y="399">20</text><text x="724" y="399">30</text><text x="460" y="436">Model time · ms</text><text x="260" y="70" fill="#185c82">1 µS: τ5 ms, V∞−45 mV</text><text x="260" y="103" fill="#985a14">0.5 µS: τ6.667 ms, V∞−60 mV</text></g>{''.join(curves)}</svg>'''
plot=A/(P+'-print-comparison.svg');plot.write_text(svg+'\n',encoding='utf-8');t=R/'figures/ch15_nmj_epp_v2.template.html';h=A/(P+'-reference.html');h.write_bytes(t.read_bytes())
r={'date':'2026-11-09','status':'Candidate; final independent appearance/source-composition and actual UI/print pending, no acceptance inferred','source_record':P+'-sources.json','source_record_sha256':sha(A/(P+'-sources.json')),'input':s['input'],'crop':s['crop'],'model':s['controlled_model'],'source_limit':s['source_anatomy_limit'],'review_basis':'B exactnative/source/equation precode approval, signedcurrent wording corrected; work/visual-v2/ch15/nmj-source/review-independent-precode.md','print':s['print'],'reproduction':{'builder':'figures/ch15_nmj_epp_v2.py','builder_sha256':sha(__file__),'template':'figures/ch15_nmj_epp_v2.template.html','template_sha256':sha(t),'scope':'Public immutable sourceJPEG/JSON/template/JS/sharedmodal only; no work/network or source acquisition on rebuild'},'artifacts':{p.name:sha(p)for p in [src,crop,plot,h,A/(P+'.js'),A/'observed-image-dialog.css',A/'observed-image-dialog.js']},'pending':['Actual390650desktop containment/pan/NativeFit/focus/controls/rate/reducedmotion and state audit','Actual90mm192ppi sourceannotation/bar/externalkey/credit and two coherent printfigures','Broad presynapticfusion/NMJpropagation/excitation-contraction mechanism remains separate unfinished scope']}
(A/(P+'-provenance.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('NATIVE_NMJ_AND_PASSIVE_RESPONSE_COMPOSED')
