"""Rebuild the observed cavity gallery from immutable public inputs only.

Python 3.13, Pillow 11.0.0, FFmpeg/ffprobe (versions captured in provenance).
No network/private work inputs, resampling, anatomical overlays or animation.
"""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PREFIX = 'ch01-v2-cranial-pleural-'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    source_path = A / (PREFIX + 'sources.json')
    sources = json.loads(source_path.read_text(encoding='utf-8'))
    for source in sources['sources']:
        path = A / source['file']
        if sha(path) != source['sha256']:
            raise ValueError(f"Immutable source changed: {source['id']}")
    mri = A / (PREFIX + 'mri.jpg')
    if Image.open(mri).size != (1443, 1448):
        raise ValueError('Unexpected MRI dimensions')
    video = A / (PREFIX + 'sliding.mp4')
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                           '-show_format', '-of', 'json', str(video)]))
    stream = next(s for s in probe['streams'] if s.get('codec_type') == 'video'
                  and not s.get('disposition', {}).get('attached_pic'))
    if (stream['width'], stream['height'], int(stream['nb_frames'])) != (1920, 1080, 197):
        raise ValueError('Unexpected video stream')
    # Poster is an actual decoded frame, zero-based index 98, not a composite.
    poster = A / (PREFIX + 'poster.png')
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video),
         '-map', '0:v:0', '-vf', 'select=eq(n\\,98)', '-frames:v', '1', str(poster)])
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
         '-map', '0:v:0', '-f', 'null', '-'])
    template = ROOT / 'figures/ch01_cranial_pleural_v2.template.html'
    host = A / (PREFIX + 'reference.html')
    host.write_bytes(template.read_bytes())
    shared = {'observed-image-dialog.css': 'fe4ddfd8ee5108943d2cf0b14ce376d66cb8392b7857b796875090272462211b',
              'observed-image-dialog.js': '5523431062e21f8cd36f63547b1eb79412c4d840fd912d7cd443809faedaf211'}
    for name, expected in shared.items():
        if sha(A / name) != expected:
            raise ValueError('Shared dialog changed; re-review dependency: ' + name)
    shared.update({name: sha(A / name) for name in ['observed-video-controls.js', 'observed-video-controls.css']})
    artifacts = [source_path, mri, video, poster, host]
    record = {
        'status': 'PROVISIONAL; independent review and actual browser/print proof pending',
        'date': '2026-11-08', 'sources': sources['sources'],
        'teaching_purpose': 'Cranial-to-upper-cervical context and an independent clinical pleural acoustic-interface observation.',
        'poster': {'file': poster.name, 'frame_index_zero_based': 98,
                   'file_time_seconds': 98 * 1001 / 24000,
                   'operation': 'Full-frame decoded PNG, no resize/color adjustment/new annotation.'},
        'video_operation': 'Unchanged publisher M4V bytes delivered with MP4 extension; no transcode, crop or timing change.',
        'surfaces': ['MRI inline/native dialog/direct original', 'Native video fallback and shared authored playback controls',
                     'Source-labelled decoded poster inline/print/direct PNG',
                     'Ordered text equivalent', 'Two print figures'],
        'coverage_gaps': ['Only upper cervical canal in MRI, not whole vertebral axis',
                          'No measured meningeal or CSF segmentation',
                          'Separate normal parietal/fluid/visceral leaflets unresolved',
                          'No registration between MRI and ultrasound'],
        'print': {'mri_width_mm': 120, 'mri_nominal_ppi': 1443 / (120 / 25.4),
                  'poster_width_mm': 170, 'poster_nominal_ppi': 1920 / (170 / 25.4),
                  'text_min_pt': 9.5, 'actual_print_proof': 'PENDING'},
        'reproduction': {'builder': 'figures/ch01_cranial_pleural_v2.py',
                         'template': str(template.relative_to(ROOT)).replace('\\', '/'),
                         'inputs': source_path.name + ' and hash-verified public MRI/video originals',
                         'python': platform.python_version(), 'pillow': pillow_version,
                         'ffmpeg': run(['ffmpeg', '-version']).splitlines()[0],
                         'ffprobe': run(['ffprobe', '-version']).splitlines()[0],
                         'builder_sha256': sha(Path(__file__)), 'template_sha256': sha(template),
                         'seed': 'N/A; no stochastic process'},
        'verification': {'native_source_hashes': 'PASS integrity only', 'full_video_decode': 'exit 0',
                         'independent_science_appearance_review': 'PENDING',
                         'desktop_650_390_native_fit_keyboard_focus': 'PENDING',
                         'actual_pdf': 'PENDING', 'chapter_integration_release': 'PENDING'},
        'artifacts': {f.name: sha(f) for f in artifacts}, 'shared_dependencies': shared,
    }
    (A / (PREFIX + 'provenance.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('CRANIAL_PLEURAL_REFERENCE_BUILT')


if __name__ == '__main__':
    main()
