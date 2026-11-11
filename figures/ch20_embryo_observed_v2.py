"""Offline composition from immutable public media, exact posters and source facts."""
from pathlib import Path
import hashlib
import json
from PIL import Image

R = Path(__file__).resolve().parents[1]
A = R / 'assets'
P = 'ch20-v2-embryo-observed-'
T = R / 'figures/ch20_embryo_observed_v2.template.html'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
s = json.loads((A / (P + 'sources.json')).read_text(encoding='utf-8'))
assert sha(A / s['media']['file']) == s['media']['sha256']
for item in s['posters']:
    p = A / item['file']
    im = Image.open(p)
    assert sha(p) == item['sha256']
    assert list(im.size) == item['dimensions']
    assert hashlib.sha256(im.convert('RGB').tobytes()).hexdigest() == item['decoded_rgb_sha256']
proof = json.loads((A / s['proof']).read_text())
assert proof['all_source_coordinate_cropped_RGB_frame_hashes_equal']
assert proof['frame_count_original'] == proof['frame_count_derivative'] == 665
assert proof['derivative_sha256'] == s['media']['sha256']
host = A / (P + 'reference.html')
host.write_bytes(T.read_bytes())
files = [host, T, Path(__file__), A / (P + 'sources.json'), A / s['media']['file'], A / s['proof']]
files += [A / item['file'] for item in s['posters']]
files += [A / f for f in ('observed-image-dialog.css', 'observed-image-dialog.js', 'observed-video-controls.css', 'observed-video-controls.js')]
p = {'date': '2026-11-09', 'sources': s,
     'operations': 'Lossless VP9 RGB codec derivative; full native decoded source frames, exact Well5 crop, no retouch or overlay.',
     'reproduction': {'builder': Path(__file__).relative_to(R).as_posix(), 'template': T.relative_to(R).as_posix(), 'private_network_required': False},
     'artifacts': {f.relative_to(R).as_posix(): sha(f) for f in files},
     'acceptance': {'current': False, 'assembled_source_appearance': 'Pending independent review', 'actual_browser_print': 'Pending root'}}
(A / (P + 'provenance.json')).write_text(json.dumps(p, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('EMBRYO_OBSERVED_BUILT')
