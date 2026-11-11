"""Reproduce source-movie PNG samples and the Chapter24 observed-synapse host.

Inputs are the unchanged, separately acquired MP4s listed in the provenance.
Python3 and FFmpeg/ffprobe are required. No networking or enhancement occurs.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
PREFIX = 'ch24-v2-ribbon-'
EXPECTED = {
    'live': {'sha256': 'c7a8993e893cc4af5009801efac7e05fa03e3d9841b39e3d2e31da6b8a884b12', 'dimensions': [1024, 512], 'frames': 66,
             'fps': '7/1', 'samples': [0, 33, 65], 'source_number': 1},
    'space': {'sha256': 'b993b6d35c1c9d0e3f3e3a9c1b8c79fbc4f744daab379c2e4cc469dffd00fc2f', 'dimensions': [268, 256], 'frames': 36,
              'fps': '3/1', 'samples': [0, 18, 35], 'source_number': 2},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, cwd=ROOT)


def build():
    movies = []
    for name, expected in EXPECTED.items():
        source = ASSETS / f'{PREFIX}{name}.mp4'
        if sha(source) != expected['sha256']:
            raise ValueError(f'Unexpected source bytes: {source.name}')
        probe = json.loads(run('ffprobe', '-v', 'error', '-count_frames',
                               '-show_streams', '-show_format', '-of', 'json', str(source)))
        streams = probe['streams']
        if len(streams) != 1 or streams[0]['codec_type'] != 'video':
            raise ValueError('Expected one video stream and no audio')
        stream = streams[0]
        actual = ([stream['width'], stream['height']], int(stream['nb_read_frames']), stream['avg_frame_rate'])
        if actual != (expected['dimensions'], expected['frames'], expected['fps']):
            raise ValueError(f'Unexpected decoded media properties: {actual}')
        samples = []
        for frame in expected['samples']:
            output = ASSETS / f'{PREFIX}{name}-frame-{frame:03}.png'
            run('ffmpeg', '-v', 'error', '-y', '-i', str(source), '-vf',
                f'select=eq(n\\,{frame})', '-frames:v', '1', '-update', '1', str(output))
            samples.append({'frame': frame, 'path': 'assets/' + output.name, 'sha256': sha(output)})
        poster = ASSETS / f'{PREFIX}{name}-poster.png'
        poster.write_bytes((ASSETS / f'{PREFIX}{name}-frame-000.png').read_bytes())
        movies.append({
            'path': 'assets/' + source.name, 'sha256': sha(source), 'bytes': source.stat().st_size,
            'source_url': 'https://static-movie-usa.glencoesoftware.com/mp4/10.7554/654/ec84ed6561d16d58962df102f376ae5f90f2ea72/'
                          f'elife-13245-media{expected["source_number"]}.mp4',
            'source_video_number': expected['source_number'], 'codec': stream['codec_name'],
            'dimensions': expected['dimensions'], 'frames': expected['frames'], 'fps': expected['fps'],
            'file_duration_seconds': float(stream['duration']), 'samples': samples,
            'poster': {'path': 'assets/' + poster.name, 'sha256': sha(poster)},
        })
    provenance = {
        'date': '2026-11-09', 'status': 'LOCAL; browser playback/layout/print and independent acceptance pending',
        'title': 'Observed vesicle-associated fluorescence at retinal ribbon synapses',
        'article': 'https://doi.org/10.7554/eLife.13245', 'version_of_record_date': '2016-02-29',
        'authors': ['Thirumalini Vaithianathan', 'Diane Henry', 'Wendy Akmentin', 'Gary Matthews'],
        'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'specimen': 'Isolated adult zebrafish retinal bipolar neurons; transgenic fish >3 months, both sexes. Methods: Animals; Patch-clamp recordings and imaging.',
        'geometry': 'Native optical fields and source scale bars retained, without overlays or inferred registration. Video1 has two fluorescence channels; Video2 is a confocal z-stack reconstruction.',
        'appearance': 'Label-associated green/red signals, not natural tissue colours or optically resolved vesicle membranes. Inspect source preparation and finite optical sampling before inferring structures.',
        'time': 'Video1: 3.77 s between images, 66 encoded frames at7fps; 65 intervals span245.05s, matching the source rounded245s. One file second corresponds to26.39s between acquisition samples at1x. Video2 camera rotation carries no physiological time mapping.',
        'limits': 'Neither movie resolves the full Ca/SNARE/fusion sequence, a postsynaptic response, a human synapse, or complete membrane/cleft topology. No particle trajectories, transport rates or fusion probabilities are inferred here.',
        'modifications': 'MP4 files unchanged byte-for-byte. Native PNG samples extracted without crop, enhancement, retiming or synthetic frames.',
        'print_exception': 'Source-limited150mm time-lapse panels (~173ppi) and60mm rotation panel (~113ppi); no hallucinated resolution. Actual PDF/layout inspection pending.',
        'reproduction': {'script': 'figures/ch24_ribbon_observed.py', 'template': 'figures/ch24_ribbon_observed.template.html',
                         'python': '3 standard library', 'ffmpeg': run('ffmpeg', '-version').decode().splitlines()[0],
                         'ffprobe': run('ffprobe', '-version').decode().splitlines()[0],
                         'inputs': 'Separately acquired unchanged public MP4 files, retained in assets.'},
        'movies': movies,
    }
    (ASSETS / f'{PREFIX}provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf8')
    (ASSETS / 'ch24-v2-ribbon-observed.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'source_movies': len(movies), 'native_samples': 6, 'status': provenance['status']}))


if __name__ == '__main__':
    build()
