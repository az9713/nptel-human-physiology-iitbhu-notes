"""Rebuild observed RBC/clot gallery from immutable public inputs only.

python figures/ch03_rbc_clot_v2.py
Pillow decodes the full original TIFF to pixel-identical grayscale PNG.
The previously validated lossless movie and event poster are immutable inputs;
this composer does not require the private AVI, network or FFmpeg re-encoding.
"""
from pathlib import Path
import hashlib
import json
import platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch03-v2-rbc-clot-'
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
    for source in sources:
        if sha(A / source['file']) != source['sha256']:
            raise ValueError('Immutable source changed: ' + source['id'])
    for name, expected in SHARED.items():
        if sha(A / name) != expected:
            raise ValueError('Shared dependency changed; re-review: ' + name)
    proof_path = A / (PREFIX + 'rgb-proof.json')
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    video = A / (PREFIX + 'retraction.webm')
    poster = A / (PREFIX + 'poster.png')
    assert sha(video) == proof['output_sha256']
    assert sha(poster) == proof['poster']['png_sha256']
    assert proof['all_120_decoded_rgb_frames_equal']
    assert len(proof['frame_hashes']['source']) == 120
    assert proof['frame_hashes']['source'] == proof['frame_hashes']['derivative']
    original = A / (PREFIX + 'rbc-original.tif')
    rbc = A / (PREFIX + 'rbc.png')
    with Image.open(original) as image:
        image.load()
        assert image.mode == 'L' and image.size == (899, 843) and image.n_frames == 1
        source_pixels = image.tobytes()
        image.save(rbc, format='PNG')
    with Image.open(rbc) as image:
        assert image.mode == 'L' and image.size == (899, 843)
        assert image.tobytes() == source_pixels
    with Image.open(poster) as image:
        assert image.size == (1640, 1072) and image.mode == 'RGB'
        assert hashlib.sha256(image.tobytes()).hexdigest() == proof['poster']['decoded_rgb_sha256']
    template = ROOT / 'figures/ch03_rbc_clot_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    artifacts = [source_path, original, rbc, video, poster, proof_path, host]
    record = {
        'status': 'PROVISIONAL local candidate; independent anatomy/appearance, browser codec/playback and print review pending',
        'date': '2026-11-09', 'sources': sources,
        'teaching_purpose': 'Qualitative biconcave human RBC morphology and independent observed fibrin redistribution during human PRP clot retraction.',
        'operations': {'rbc': 'Full original TIFF decoded to lossless PNG; identical L-mode pixels, no crop, resize or contrast transform.',
                       'movie': 'Previously validated immutable VP9 lossless RGB derivative copied unchanged; original AVI remains separately acquired private input.',
                       'poster': 'Unchanged full RGB source frame75; decoded pixels match validated source and derivative.'},
        'pixel_verification': {'rbc_original_png_decoded_pixels_equal': True,
                               'rbc_grayscale_pixel_sha256': hashlib.sha256(source_pixels).hexdigest(),
                               'poster_rgb_equal_record': True,
                               'movie_all_120_rgb_equal_proof': proof_path.name,
                               'movie_pts_max_rounding_s': proof['timing']['max_abs_pts_error_s']},
        'scientific_limits': ['Independent specimens/modalities; no complete normal-human differential',
                              'SEM donor health and calibration unavailable; not living colour/oxygenation/flow',
                              'Static PRP retraction assay without imposed flow; citrated collection plus exogenous thrombin',
                              'Panel clocks diverge; publisher-file seconds are not one experiment clock',
                              'Source reviewed-preprint assessment does not establish causal winding/swirl mechanism'],
        'print_candidate': {'rbc_width_mm': 110, 'rbc_output_ppi': 899 / (110 / 25.4),
                            'poster_width_mm': 145, 'poster_output_ppi': 1640 / (145 / 25.4),
                            'external_text_min_pt': 9.5, 'actual_pdf': 'PENDING', 'pagination_repair': 'Independent-observation scope integrated in first-page intro and provenance/RGB links beside SEM credit; print omits screen-only access footer. RBC110mm/poster145mm and source graphics unchanged; actual revised PDF pending root test.'},
        'reproduction': {'builder': 'figures/ch03_rbc_clot_v2.py',
                         'template': 'figures/ch03_rbc_clot_v2.template.html',
                         'builder_sha256': sha(Path(__file__)), 'template_sha256': sha(template),
                         'python': platform.python_version(), 'pillow': pillow_version,
                         'public_inputs': [source_path.name, original.name, video.name, poster.name, proof_path.name] + list(SHARED),
                         'private_network_dependencies': 'None for composition rebuild. Original source acquisition/derivative encode was separately performed and documented.',
                         'seed': 'N/A; deterministic composition'},
        'verification': {'source_hashes_and_decoded_image_equality': 'PASS integrity only',
                         'browser_vp9_profile1_readyState_playback': 'PENDING root test',
                         'responsive_enlargement_controls_seek_keyboard_focus': 'PENDING',
                         'independent_anatomy_appearance': 'PENDING',
                         'actual_print': 'PENDING', 'chapter_integration_release': 'PENDING'},
        'shared_dependencies': SHARED,
        'artifacts': {f.name: sha(f) for f in artifacts},
    }
    (A / (PREFIX + 'provenance.json')).write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('RBC_CLOT_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
