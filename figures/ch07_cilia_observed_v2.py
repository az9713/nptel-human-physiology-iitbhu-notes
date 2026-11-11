"""Compose observed-airway gallery from immutable public inputs, no network.

Run: python figures/ch07_cilia_observed_v2.py
AVI acquisition and lossless VP9 conversion were performed separately and
verified with all-frame RGB hashes. This composer does not require private
AVI inputs or repeat their encoding; supplied public proofs state that boundary.
"""
from pathlib import Path
import hashlib
import json
import platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch07-v2-cilia-'
SHARED = {
    'observed-image-dialog.css': 'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
    'observed-image-dialog.js': '5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211',
    'observed-video-controls.js': '1136584777fdb340619dab2527e02e647c95d12fa4a5d8af847148a60f42341f',
    'observed-video-controls.css': '55144b39d16e8f1096f0cf1d534c817076d1b8c1e137320291f9e8a46b852c9b',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = A / (PREFIX + 'sources.json')
    sources = json.loads(source_path.read_text(encoding='utf-8'))['sources']
    inputs = [source_path]
    movies = {}
    for source in sources:
        path = A / source['file']
        if sha(path) != source['sha256']:
            raise ValueError('Immutable source changed: ' + source['id'])
        inputs.append(path)
        if source['id'] == 'sem':
            with Image.open(path) as image:
                image.load()
                assert image.size == (2900, 3657)
            continue
        role = source['id']
        proof_path, poster = A / source['proof_file'], A / source['poster_file']
        assert sha(proof_path) == source['proof_sha256']
        assert sha(poster) == source['poster_sha256']
        proof = json.loads(proof_path.read_text(encoding='utf-8'))
        assert proof['output_sha256'] == sha(path)
        assert proof['source_sha256'] == source['original_sha256']
        assert proof['all_frames_rgb_equal']
        assert proof['frame_hashes']['source'] == proof['frame_hashes']['derivative']
        assert len(proof['frame_hashes']['source']) == source['frames']
        assert proof['decode']['source']['returncode'] == 0
        assert proof['decode']['derivative']['returncode'] == 0
        with Image.open(poster) as image:
            assert list(image.size) == source['dimensions'] and image.mode == 'RGB'
            assert hashlib.sha256(image.tobytes()).hexdigest() == proof['poster']['rgb_sha256']
        inputs.extend([proof_path, poster])
        movies[role] = {
            'all_frames_rgb_equal': True, 'frames': source['frames'],
            'proof': proof_path.name, 'poster': proof['poster'],
            'max_pts_rounding_s': proof['timing']['max_abs_pts_error_s'],
            'stream': proof['probes']['derivative'],
        }
    for name, expected in SHARED.items():
        if sha(A / name) != expected:
            raise ValueError('Shared dependency changed; re-review: ' + name)
    template = ROOT / 'figures/ch07_cilia_observed_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    record = {
        'status': 'PROVISIONAL partial observation; S1 transport retired after failed appearance review; full airway/mucus coverage pending',
        'date': '2026-11-09', 'sources': sources,
        'purpose': 'Prepared bronchial ciliated morphology and separate human-culture ciliary motion; no direct mucus-transport demonstration or continuous whole-airway zoom.',
        'scientific_limits': [
            'SEM species/preparation/clinical context unreported; not assigned human',
            'Reconstituted human bronchial ALI culture is not normal intact airway',
            'S2 acquired2.5s at40fps, delivered5s at20fps; separate panels at initial,+24h,and3days after mucus wash',
            'The retired S1 movie failed intended-size mucus-transport legibility and is absent from the reader. S2 does not replace that transport evidence.',
            'No synthetic anatomical direction, periciliary thickness, normal clearance rate or causal hydrodynamic-mechanism proof',
        ],
        'operations': 'Whole SEM original unchanged; validated lossless S2 browser movie and original decoded-frame poster copied unchanged. Failed S1 assets retained in private quarantine, not a reader dependency. No anatomical overlays/crops/resampling or invented clocks.',
        'movie_verification': movies,
        'print_candidate': {'sem_width_mm': 100, 'sem_ppi': 2900 / (100 / 25.4),
                            'S2_poster_width_mm': 160, 'S2_ppi': 1337 / (160 / 25.4),
                            'external_key_min_pt': 9.5, 'actual_pdf': 'PENDING'},
        'reproduction': {
            'builder': 'figures/ch07_cilia_observed_v2.py',
            'template': 'figures/ch07_cilia_observed_v2.template.html',
            'builder_sha256': sha(Path(__file__)), 'template_sha256': sha(template),
            'python': platform.python_version(), 'pillow': pillow_version,
            'public_inputs': [f.name for f in inputs] + list(SHARED),
            'private_network_dependencies': 'None for composition. Original AVI acquisition and lossless encoding are separately documented inputs, not silently repeated by the composer.',
            'seed': 'N/A; deterministic composition',
        },
        'verification': {
            'immutable_input_hashes_and_poster_pixels': 'PASS integrity only',
            'all_movie_rgb_frames': 'PASS pinned FFmpeg equality in linked records; no browser colour-management claim',
            'browser_vp9_readyState_playback': 'PENDING current S2-only retest',
            'responsive_native_fit_pan_seek_focus': 'PENDING',
            'independent_anatomy_appearance': 'PENDING',
            'actual_print': 'PENDING current S2-only retest', 'canonical_integration_release': 'PENDING',
        },
        'shared_dependencies': SHARED,
        'artifacts': {f.name: sha(f) for f in inputs + [host]},
    }
    (A / (PREFIX + 'provenance.json')).write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('CILIA_OBSERVED_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
