"""Deterministic public-input composition; Python3.13 stdlib only, no network."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

def digest(path):
    data = path.read_bytes()
    return {'file': path.relative_to(ROOT).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

def main():
    template = ROOT / 'figures/templates/ch11-v2-follicle-stages.html'
    output = ASSETS / 'ch11-v2-follicle-stages.html'
    output.write_bytes(template.read_bytes())
    files = [template, Path(__file__).resolve(), output,
             ASSETS / 'ch11-v2-follicle-stages-model.js',
             ASSETS / 'ch11-v2-follicle-stages.js',
             ASSETS / 'ch11-v2-follicle-observed-panel-a.png',
             ASSETS / 'ch11-v2-follicle-observed-sources.json']
    record = {
        'status': 'Local candidate; not visual acceptance',
        'date': '2026-11-09',
        'purpose': 'Observed follicular architecture with controlled explanatory states, no molecular tracking through H&E',
        'rebuild': 'python -B -X utf8 figures/ch11_follicle_stages_v2.py',
        'tool': 'CPython3.13 stdlib; browser native SVG/DOM/requestAnimationFrame',
        'inputs_outputs': [digest(path) for path in files],
        'image_rights': {'creator': 'Rosa et al.2022', 'doi': '10.1111/jcmm.17282',
                         'license': 'CC BY4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
                         'change': 'Existing exact H&E panel crop, separate optional structural SVG leaders/outlines; no source-pixel changes'},
        'mechanism_sources': [
            {'url': 'https://www.endotext.org/wp-content/uploads/pdfs/chapter-2-thyroid-hormone-synthesis-and-secretion.pdf',
             'revision': '2015-08-30', 'read_pdf_pages': [4,7,8,9,19,26,27,29,33,34,35],
             'acquired_pdf_sha256': '1e86ba095667a35f0cbfda2611a160e0e4c7a2561dcf79c6ae6bc0d962d3c980',
             'reuse': 'Reference only; no Endotext illustration reproduced'},
            {'url': 'https://www.jci.org/articles/view/42113', 'doi': '10.1172/JCI42113',
             'scope': 'Mouse basolateral Mct8 localization and knockout secretion experiment; not human H&E protein identification'}],
        'timing': {'kind': 'presentation', 'seconds': 21, 'states': 7,
                   'biological_mapping': None, 'source_image': 'fixed throughout'},
        'geometry': 'Three broad structural leaders/outlines; no cell segmentation, capillary, molecular geometry or source registration invented',
        'print': {'image_width_mm': 100, 'source_ppi': 176.022,
                  'exception': 'Source-limited 693px H&E field; no upscaling-generated detail. Actual print review required.'},
        'review': 'Every applicable V01-V20 requires exact final source/appearance/UI/print/reproduction evidence; no automatic PASS'
    }
    (ASSETS / 'ch11-v2-follicle-stages-provenance.json').write_text(
        json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'output': digest(output), 'files': len(files)}))

if __name__ == '__main__':
    main()
