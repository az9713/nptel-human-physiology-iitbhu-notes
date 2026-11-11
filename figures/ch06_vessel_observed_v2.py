"""Compose vascular microscopy gallery from immutable public crops, offline.

Run: python figures/ch06_vessel_observed_v2.py
Original acquisition/cropping was separately executed and recorded. Full publisher
figures remain private; this composer verifies supplied crops and proof records.
"""
from pathlib import Path
import hashlib
import json
import platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch06-v2-vessel-observed-'
SHARED = {
    'observed-image-dialog.css': 'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
    'observed-image-dialog.js': '5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = A / (PREFIX + 'sources.json')
    proof_path = A / (PREFIX + 'crop-proof.json')
    sources = json.loads(source_path.read_text(encoding='utf-8'))
    proofs = json.loads(proof_path.read_text(encoding='utf-8'))
    by_file = {proof['file']: proof for proof in proofs['crops']}
    inputs = [source_path, proof_path]
    for source in sources['sources']:
        path = A / source['file']
        proof = by_file[path.name]
        if sha(path) != source['sha256'] or sha(path) != proof['derivative_sha256']:
            raise ValueError('Immutable crop changed: ' + path.name)
        with Image.open(path) as image:
            assert list(image.size) == source['dimensions']
            rgb_hash = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
        assert rgb_hash == proof['decoded_rgb_sha256'] == proof['source_rect_rgb_sha256']
        assert proof['equal'] and proof['crop_rect_xyxy'] == source['crop_rect_xyxy']
        assert proof['source_figure_sha256'] == source['source_figure_sha256']
        inputs.append(path)
    for name, expected in SHARED.items():
        if sha(A / name) != expected:
            raise ValueError('Shared helper changed; re-review: ' + name)
    template = ROOT / 'figures/ch06_vessel_observed_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    record = {
        'date': '2026-11-09',
        'status': 'Local candidate; independent source/anatomy/appearance and actual browser/PDF checks pending',
        'purpose': 'Human regional artery–vein wall organisation and separate mouse baseline capillary luminal ultrastructure',
        'sources': sources,
        'operations': 'Immutable exact source crops copied into a standalone gallery; no pixel transformation or new anatomical leaders.',
        'scientific_limits': [
            'Postmortem human organ-donor cohort includes hypertension/diabetes; photographed donor identities not supplied.',
            'Arterial field has no separately resolved printed I; no invented intima locator.',
            'Mouse lanthanum-stained deposits are preparation-dependent, not a living hydrated glycocalyx thickness.',
            'No full revised Starling mechanism, measured fluid flux or unified specimen/scale claimed.',
        ],
        'print_layout': {
            'wall_crop_width_mm': 165, 'wall_file_ppi': 2350 * 25.4 / 165,
            'capillary_panel_width_mm': 75,
            'capillary_file_ppi': {'brain': 820 * 25.4 / 75, 'heart': 825 * 25.4 / 75, 'lung': 820 * 25.4 / 75},
            'external_key_min_pt': 9.5, 'layout': 'Human study first page; mouse study begins a new page; rights attached to each study.',
            'limits': 'File-to-layout ratios do not establish optical resolution or visual acceptance. Actual PDF remains pending.',
        },
        'reproduction': {
            'builder': 'figures/ch06_vessel_observed_v2.py', 'builder_sha256': sha(Path(__file__)),
            'template': str(template.relative_to(ROOT)).replace('\\', '/'), 'template_sha256': sha(template),
            'python': platform.python_version(), 'pillow': pillow_version,
            'public_inputs': [f.name for f in inputs] + list(SHARED),
            'private_network_dependencies': 'None for composition. Original publisher downloads and initial exact crop check were separate acquisition steps; their original URLs/hashes are in sources and crop proof.',
            'seed': 'N/A; deterministic composition',
        },
        'verification': {'immutable_crop_hashes_pixels': 'PASS integrity only',
                         'independent_anatomy_appearance': 'PENDING', 'actual_browser_native_fit_pan_focus': 'PENDING',
                         'actual_print': 'PENDING', 'canonical_integration_release': 'PENDING'},
        'shared_dependencies': SHARED,
        'artifacts': {f.name: sha(f) for f in inputs + [host]},
    }
    (A / (PREFIX + 'provenance.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('VESSEL_OBSERVED_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
