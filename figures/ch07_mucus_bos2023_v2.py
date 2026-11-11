"""Deterministic observed-Bos2023 gallery from immutable public inputs.

No private-work/network/FFmpeg/video-encoding dependency for composition rebuild.
Acquisition, rights verification and native-frame extraction are separate records.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';P='ch07-v2-mucus-bos2023'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'))
for x in s['inputs']:
 p=A/x['file'];assert sha(p)==x['sha256'],p
 if x['role']=='decoded_frame':
  im=Image.open(p).convert('RGB');assert im.size==(x['width'],x['height'])
  assert hashlib.sha256(im.tobytes()).hexdigest()==x['rgb_sha256']
timing=json.loads((A/(P+'-timing-proof.json')).read_text())
assert timing['stream_start_time_s']==.05 and [x['container_pts_s']for x in timing['samples']]==[.05,7.55,15.05]
proof=A/(P+'-decode-framemd5.txt')
assert len([x for x in proof.read_text().splitlines() if x and not x.startswith('#')])==301
assert s['media']==dict(codec='H264',width=1572,height=2048,frames=301,fps='20/1',duration_s=15.05,last_frame_pts_s=15.05,audio=False,full_decode_errors=0,start_time_s=.05)
shared={'observed-image-dialog.css':'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
 'observed-image-dialog.js':'5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211',
 'observed-video-controls.js':'1136584777fdb340619dab2527e02e647c95d12fa4a5d8af847148a60f42341f',
 'observed-video-controls.css':'55144b39d16e8f1096f0cf1d534c817076d1b8c1e137320291f9e8a46b852c9b'}
for n,h in shared.items():assert sha(A/n)==h,n
template=ROOT/'figures/ch07_mucus_bos2023_v2.template.html';host=A/(P+'-reference.html');host.write_bytes(template.read_bytes())
record={'date':'2026-11-09','status':'Candidate; independent source/appearance and actual browser/print review pending, no acceptance inferred',
 'source_record':P+'-sources.json','inputs':s['inputs'],'source_movie':s['source_movie'],'native_modifications':s['modifications'],
 'timing':s['timing'],'print':{**s['print'],'width_mm':80,'height_mm':2048/1572*80,'ppi':1572/80*25.4,'exception':'No below300ppi raster exception required at80mm; individual cilia remain unresolved.','intent':'Current standalone candidate: one wholeposter80mm with compactprintspacing; body/key9.5pt,credit9pt. Root/B actualonepagephysicalbundlelegibility pending.','source_record_print_scope':'SourceJSON retains original100mm design intent; currentstandalone template/provenance overrides to80mm. CanonicalChapter7poster100mm unchanged.'},'coverage_gaps':s['gaps'],'independence':s['independence'],
 'controls':{'playback':'Native controls fallback; shared authored controls opt-in. Starts paused/preloadmetadata/noautoplay/noloop. File seconds only. Shared reduced-motion change/pagehide/beforeprint pauses.',
 'video_display':'Fit player contains entire tall source; Native pixels restores1572×2048 in explicit bounded-height scrolling region. Shared target-region arrows/Home/End.',
 'image_display':'Three source-indexed Native/Fit/Close dialogs, explicit bounded-height inner viewport, keyboardpan/openerfocusreturn. No pagewide source overflow.'},
 'reproduction':{'builder':'figures/ch07_mucus_bos2023_v2.py','template':'figures/ch07_mucus_bos2023_v2.template.html','builder_sha256':sha(__file__),'template_sha256':sha(template),'python':platform.python_version(),'pillow':pillow_version,
 'scope':'Public immutable originalMP4/fullnativeposters/decodeproof/sourceJSON/template/sharedadapters only; no private work, network or encoding required to recompose. Initial acquisition/frame extraction separate.'},
 'shared_dependencies':shared,'pending':['Distinct independent source/specimen/rights/timing review','Native appearance/teaching inspection; no invisible cilia/goblet-cause claim','Actual desktop650390 MP4decode/paused/play/seek/step/replay/end/reducedmotion/NativeFit/focus/pan tests','Actual whitePDF oneposter/sourcekey/timing/credit/pagebreak proof','No canonical Chapter7 integration performed']}
record['artifacts']={p.name:sha(p)for p in [A/x['file']for x in s['inputs']]+[A/(P+'-sources.json'),host]+[A/n for n in shared]}
(A/(P+'-provenance.json')).write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('BOS2023_OBSERVED_GALLERY_COMPOSED',flush=True)
