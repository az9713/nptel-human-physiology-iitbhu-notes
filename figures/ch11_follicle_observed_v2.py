"""Compose one observed thyroid H&E panel from immutable public inputs, offline.

Run: python figures/ch11_follicle_observed_v2.py
Native PDF/JPEG extraction and initial crop verification were separate acquisition
steps. Unrelated full-figure panels remain private and are not rebuild inputs.
"""
from pathlib import Path
import hashlib
import json
import platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch11-v2-follicle-observed-'
SHARED = {
    'observed-image-dialog.css': 'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
    'observed-image-dialog.js': '5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = A / (PREFIX + 'sources.json')
    proof_path = A / (PREFIX + 'crop-proof.json')
    record = json.loads(source_path.read_text(encoding='utf-8'))
    source = record['sources'][0]
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    panel = A / source['file']
    assert sha(panel) == source['sha256'] == proof['derived_sha256']
    with Image.open(panel) as image:
        assert list(image.size) == source['dimensions'] == [693, 525]
        rgb_sha = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
    assert rgb_sha == source['decoded_rgb_sha256'] == proof['decoded_rgb_sha256']
    assert source['crop_rect_xyxy'] == proof['crop_rect_xyxy'] == [0, 0, 693, 525]
    assert proof['source_DCT_bytes_equal_extracted_JPEG']
    assert proof['crop_decoded_RGB_equal_named_Pillow_source_rect']
    assert not proof['cross_decoder_rgb_identity_claimed']
    for name, expected in SHARED.items():
        if sha(A / name) != expected:
            raise ValueError('Shared helper changed; re-review: ' + name)
    template = ROOT / 'figures/ch11_follicle_observed_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    inputs = [source_path, proof_path, panel]
    provenance = {
        'date': '2026-11-09', 'status': 'Local candidate; independent gallery appearance/source and actual browser/print review pending',
        'purpose': 'One observed human follicular structural reference: colloid profiles, epithelial rims and intervening stroma',
        'sources': record, 'operations': 'Immutable exact A crop composed without further image processing, anatomical overlays or new scale.',
        'limits': source['boundaries'],
        'print': {'panel_width_mm': 110, 'panel_height_mm': 525 / 693 * 110,
                  'file_ppi': 693 / (110 / 25.4), 'external_key_min_pt': 9.5, 'credit_min_pt': 9,
                  'source_limited_exception': source['print_candidate']['source_limited_exception'],
                  'actual_pdf_and_original_A_HE_bar_readability': 'PENDING root/B'},
        'reproduction': {'builder': 'figures/ch11_follicle_observed_v2.py', 'builder_sha256': sha(Path(__file__)),
                         'template': 'figures/ch11_follicle_observed_v2.template.html', 'template_sha256': sha(template),
                         'python': platform.python_version(), 'pillow': pillow_version,
                         'public_inputs': [f.name for f in inputs] + list(SHARED),
                         'private_network_dependencies': 'None for composition. Native published PDF/JPEG acquisition and exact crop were separately executed; original URLs/hashes and decoder boundary are recorded in public inputs.',
                         'seed': 'N/A; deterministic composition'},
        'shared_dependencies': SHARED,
        'verification': {'immutable_crop_hash_RGB': 'PASS integrity only', 'actual_browser_Native_Fit_pan_focus_responsive': 'PENDING',
                         'independent_gallery_source_appearance': 'PENDING', 'actual_print': 'PENDING',
                         'canonical_integration_release': 'PENDING'},
        'artifacts': {f.name: sha(f) for f in inputs + [host]},
    }
    (A / (PREFIX + 'provenance.json')).write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('FOLLICLE_OBSERVED_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
