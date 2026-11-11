"""Recompose observed MRI gallery from immutable public inputs; Python 3.13/Pillow 11.
No private work/network/FFmpeg/remux/re-encoding dependency on composition rebuild.
Original MOV and separately verified container-only browser MP4 are immutable inputs.
"""
from pathlib import Path
import json,hashlib,platform
from PIL import Image,__version__ as pillow_version
R=Path(__file__).resolve().parents[1];A=R/'assets'
P='ch07-v2-breathing-observed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((A/(P+'-sources.json')).read_text(encoding='utf-8'))
for x in s['inputs']:
 p=A/x['file'];assert sha(p)==x['sha256'],p
 if x['role']=='decoded_frame':
  im=Image.open(p).convert('RGB');assert list(im.size)==[x['width'],x['height']];assert hashlib.sha256(im.tobytes()).hexdigest()==x['rgb_sha256']
proof=json.loads((A/s['remux']['proof_file']).read_text(encoding='utf-8'))
assert proof['all_48_decoded_rgb_frames_equal'] and proof['all_48_coded_packet_hashes_equal']
assert proof['timing']['all_pts_exact_equal'] and proof['timing']['max_abs_pts_error_s']==0
assert proof['frame_hashes']['source']==proof['frame_hashes']['derivative'] and len(proof['frame_hashes']['source'])==48
assert proof['source_sha256']==sha(A/(P+'.mov')) and proof['output_sha256']==sha(A/s['browser_primary_file'])
html=(R/'figures'/'ch07_breathing_observed_v2.template.html').read_text(encoding='utf-8');(A/(P+'-reference.html')).write_text(html,encoding='utf-8')
record=dict(date='2026-11-09',status='Candidate; independent review and actual browser/print acceptance pending',sources=P+'-sources.json',browser_primary_file=s['browser_primary_file'],remux=s['remux'],inputs=s['inputs'],modifications=s['modifications'],print=s['print'],coverage_gaps=s['gaps'],reproduction={'builder':'figures/ch07_breathing_observed_v2.py','template':'ch07_breathing_observed_v2.template.html','python':platform.python_version(),'pillow':pillow_version,'scope':'Exact public originalMOV/MP4remux/proof/decoded-frame/sourceJSON/template/shared-control inputs only; original acquisition and verified remux were separate. No private work/network/remux or reencoding on composition rebuild.'},controls={'video':'Native controls fallback; shared observed-video controls opt-in. Starts paused, metadata only, no autoplay/loop. Publisher file seconds distinct from physiology/acquisition. Shared reduced-motion preference change pauses playback.','display':'Native pixels/Fit player; focused contained keyboard pan. Native/Fit/Close poster modal with opener focus return.'},pending=['Distinct independent anatomy/timing/source and appearance/teaching review','Actual desktop/650/390 native/fit/pan/focus/play/seek/step/replay/end/reduced-motion and source format support','Actual PDF native-poster/source-label/external-key/credit/pagebreak legibility','Canonical chapter integration not performed'])
files=[A/x['file'] for x in s['inputs']]+[A/(P+'-sources.json'),A/(P+'-reference.html')]+[A/x for x in ['observed-image-dialog.css','observed-image-dialog.js','observed-video-controls.css','observed-video-controls.js']]
record['artifacts']={p.name:sha(p) for p in files}
(A/(P+'-provenance.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(P+' composed')
