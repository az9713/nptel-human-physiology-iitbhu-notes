"""Compose the standalone bilayer plate from an immutable public source crop.

Run: python figures/ch02_bilayer_reconstruction_v2.py
No network, private research inputs, resampling or anatomical annotation.
The source PDF was separately acquired; original extraction is documented in
the public sources record, not silently repeated by this public-only composer.
"""
from pathlib import Path
import hashlib
import json
import platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch02-v2-bilayer-reconstruction-'
SHARED = {
    'observed-image-dialog.css': 'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
    'observed-image-dialog.js': '5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = A / (PREFIX + 'sources.json')
    source = json.loads(source_path.read_text(encoding='utf-8'))['source']
    crop = A / source['crop']['file']
    if sha(crop) != source['crop']['sha256']:
        raise ValueError('Immutable publication crop changed')
    with Image.open(crop) as image:
        image.load()
        if image.size != (599, 253) or image.format != 'PNG':
            raise ValueError('Unexpected native crop dimensions/format')
    for name, expected in SHARED.items():
        if sha(A / name) != expected:
            raise ValueError('Shared dependency changed; re-review: ' + name)
    template = ROOT / 'figures/ch02_bilayer_reconstruction_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    record = {
        'status': 'PROVISIONAL; independent science/appearance, browser and print review pending',
        'date': '2026-11-09', 'source': source,
        'teaching_claim': 'Two source-identified leaflet-associated headgroup density bands of one bilayer in averaged Torpedo membrane map2.',
        'representation': 'Experimental averaged helical cryo-EM density cross-section, not a raw micrograph or generated anatomy.',
        'source_marks': {'O': 'upper outer/extracellular headgroup region',
                         'I': 'lower inner/cell-facing headgroup region',
                         'MX': 'inner-side acetylcholine-receptor helix',
                         'red_arrow': 'source pore locator; not flux'},
        'operations': 'Host composition and external reading key only; immutable source crop bytes unchanged.',
        'coverage_limits': ['Not human, intact normal tissue or live imaging',
                            'No calibrated publication image bar',
                            'No transport or individually resolved lipid positions',
                            'Separate raw observed leaflet-image acquisition remains unresolved'],
        'print_candidate': {'crop_width_mm': 100,
                            'output_ppi': 599 / (100 / 25.4),
                            'external_text_min_pt': 9.5,
                            'source_label_limit': 'Original O/I glyphs remain small; external key is readable but does not imply print acceptance.',
                            'actual_print_proof': 'PENDING'},
        'reproduction': {'builder': 'figures/ch02_bilayer_reconstruction_v2.py',
                         'template': 'figures/ch02_bilayer_reconstruction_v2.template.html',
                         'public_inputs': [source_path.name, crop.name] + list(SHARED),
                         'original_acquisition': source['acquisition_boundary'],
                         'builder_sha256': sha(Path(__file__)),
                         'template_sha256': sha(template),
                         'python': platform.python_version(), 'pillow': pillow_version,
                         'seed': 'N/A; deterministic byte composition'},
        'verification': {'source_integrity_and_dimensions': 'PASS integrity only',
                         'public_only_rebuild': 'See private layout-rebuild proof; no private inputs required',
                         'independent_anatomy_appearance': 'PENDING',
                         'responsive_enlargement_keyboard_focus': 'PENDING',
                         'actual_print': 'PENDING', 'chapter_integration_release': 'PENDING'},
        'shared_dependencies': SHARED,
        'artifacts': {f.name: sha(f) for f in [source_path, crop, host]},
    }
    (A / (PREFIX + 'provenance.json')).write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('BILAYER_RECONSTRUCTION_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
