"""Extract the complete unchanged BBB microscopy plate from the acquired PDF.

Run: python figures/ch25_barrier_observed.py --pdf PATH_TO_SOURCE_PDF
Input has a version-specific CC BY-NC-ND4.0 notice; never crop/adapt its art.
Python3 and PyMuPDF1.27.1. No networking, rendering, enhancement or re-encoding.
"""
from pathlib import Path
import argparse
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_SHA = 'd75bce16c33aadd59d30f254b83d93731ec84a32b40747a826cbf7f04c9b42be'
IMAGE_SHA = 'f2293c7a5d01a06eb9435b41df1e0f302cbac6beabff29e4ea285551c7bdca71'
PDF_URL = 'https://gu.hms.harvard.edu/sites/gu.hms.harvard.edu/files/images/Pfau_et_al-2024-Nature_Neuroscience.pdf'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(pdf):
    if sha(pdf.read_bytes()) != PDF_SHA:
        raise ValueError('Source PDF hash differs from inspected version')
    document = fitz.open(pdf)
    images = document[18].get_images(full=True)
    if len(images) != 1 or images[0][0] != 4397 or images[0][2:4] != (2162, 2686):
        raise ValueError('Expected single complete source plate')
    image = document.extract_image(4397)
    if image['ext'] != 'jpeg' or sha(image['image']) != IMAGE_SHA:
        raise ValueError('Extracted image differs from inspected source stream')
    assets = ROOT / 'assets'
    (assets / 'ch25-v2-barrier-observed-native.jpeg').write_bytes(image['image'])
    provenance = {
        'date': '2026-11-09', 'status': 'LOCAL; actual browser/print and independent review pending',
        'title': 'Observed cortical and median-eminence capillary ultrastructure',
        'authors': 'Sarah J. Pfau, Urs H. Langen and colleagues',
        'article': 'https://doi.org/10.1038/s41593-024-01743-y',
        'publication_date': '2024-08-29', 'figure': 'Extended Data Figure2, all panels unchanged',
        'source_pdf': {'url': PDF_URL, 'sha256': PDF_SHA, 'page_count': 41,
                       'image_page_1based': 19, 'caption_page_1based': 20,
                       'license_page_1based': 12, 'image_xref': 4397},
        'license': 'CC BY-NC-ND4.0, exact acquired author PDF; noncommercial unchanged reproduction only',
        'license_url': 'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'license_version_note': 'PMC HTML of the same article currently statesCCBY4.0. This asset is extracted from the acquired authorPDF that explicitly statesCCBY-NC-ND4.0; its exact notice is retained. No inference of broader rights for these bytes.',
        'source_image': {'path': 'assets/ch25-v2-barrier-observed-native.jpeg',
                         'sha256': IMAGE_SHA, 'dimensions': [2162, 2686],
                         'modifications': 'None. Complete original JPEG stream extracted without decode/re-encode, crop, annotation, colour change or resampling.'},
        'specimen': 'Study used8–14week mice; both sexes unless stated otherwise. Exact sex/strain of this displayed capillary not assigned. TEM tissue chemically perfusion-fixed, osmicated, resin-embedded,80nmsections, lead-citrate counterstain, JEOL1200EX with2kCCD.',
        'orientation_scale': 'Source section views only; no body orientation or registration inferred. Original1µm cortical/ME main-image bars,4µm panelc bars,20µm paneld bar retained. Insets have source bars without a new numerical calibration.',
        'appearance': 'Source pseudocolours: endothelialpurple, pericyteteal, astrocyteendfootcyan, fibroblastred, lumenwhite, neuropilyellow. Lower confocal signals CD31white/AQP4green. Not natural living colours.',
        'teaching_scope': 'Identify cortical lumen/endothelium/junction/pericyte/endfoot relationships, compare specialised medianeminence. Does not measure live permeability, glucose flux, transporter kinetics, basement-membrane composition or junction dynamics.',
        'print': 'Full plate160mmwide yields~343ppi; external reading key remains text. Actual PDF composition pending.',
        'reproduction': {'script': 'figures/ch25_barrier_observed.py',
                         'template': 'figures/ch25_barrier_observed.template.html',
                         'tool': 'PyMuPDF', 'version': fitz.VersionBind,
                         'inputs': 'Separately acquired original PDF, identified by source URL and exact hash. Supply --pdf; no embedded local personal path.'},
    }
    (assets / 'ch25-v2-barrier-observed-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf8')
    (assets / 'ch25-v2-barrier-observed.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'complete_source_image': True, 'source_bytes': len(image['image']), 'dimensions': [2162, 2686], 'status': provenance['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, type=Path)
    build(parser.parse_args().pdf)
