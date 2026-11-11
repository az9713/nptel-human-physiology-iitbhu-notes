"""Offline reproduction from already acquired unchanged MP4 and source manifest."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

def item(path):
    data = path.read_bytes()
    return {'file': path.relative_to(ROOT).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

def main():
    movie = ASSETS / 'ch09-v2-glut4-redistribution.mp4'
    frames = []
    for index in [0,66,131]:
        out = ASSETS / f'ch09-v2-glut4-redistribution-frame-{index:04}.png'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),
                        '-vf',f'select=eq(n\\,{index})','-frames:v','1','-update','1','-y',str(out)],check=True)
        frames.append(out)
    template = ROOT / 'figures/templates/ch09-v2-glut4-reference.html'
    html = ASSETS / 'ch09-v2-glut4-reference.html'
    html.write_bytes(template.read_bytes())
    version = subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    sources = json.loads((ASSETS / 'ch09-v2-glut4-sources.json').read_text(encoding='utf-8'))
    record = {'status': 'Local candidate; all applicable rubric evidence required',
              'date': '2026-11-09','builder': item(Path(__file__).resolve()),
              'rebuild': 'python -B -X utf8 figures/ch09_glut4_observed_v2.py',
              'tools': {'python':'3.13','ffmpeg':version},
              'source': sources, 'artifacts': [item(x) for x in [template,html,movie,*frames,
                  ASSETS/'observed-video-controls.js',ASSETS/'observed-video-controls.css']],
              'frame_extraction': 'Full frames0/66/131 decoded by pinned FFmpeg, PNG lossless; no resampling or colour/contrast changes',
              'acquisition_boundary': 'Original MOV separately acquired from actual publisher supplement link; exact packet hashes/PTS/durations match unchanged remuxed MP4. Offline rebuild requires this already acquired MP4, never a private source path or network.',
              'print': {'endpoint_width_mm':80,'native_ppi':161.6075,
                        'source_limited_exception':'509px source; smaller image, no hallucinated upscaling. Actual print legibility remains to be verified.'}}
    (ASSETS/'ch09-v2-glut4-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(item(html)))

if __name__ == '__main__':
    main()
