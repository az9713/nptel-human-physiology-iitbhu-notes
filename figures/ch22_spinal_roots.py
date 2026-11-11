"""Extract unchanged spinal-root source photographs and compose the reader host.

python figures/ch22_spinal_roots.py --pdf EXACT_SOURCE_PDF
Python3/PyMuPDF1.27.1; no network, source enhancement, crop or re-encoding.
"""
from pathlib import Path
import argparse
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = 'b3ac09928e53c9ed00bd073ab765f1e7312241e97e5f383d8a758092535b565c'
FIGURES = [(7, 6, 124, 2892, 1919, '4706eb39b917397bcb067e422b8aaca98154258c533b163a312dcf61ba16c246'),
           (8, 7, 139, 2892, 1914, '8f2891f538b62ffea185f1a3a024941a54dfd0b46e24f00ecd7941e8d493e6fc')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(pdf):
    if sha(pdf) != SOURCE_SHA:
        raise ValueError('Source PDF differs from inspected input')
    document = fitz.open(pdf)
    records = []
    for number, page, xref, width, height, expected in FIGURES:
        if xref not in {x[0] for x in document[page].get_images()}:
            raise ValueError('Source image not present on expected page')
        image = document.extract_image(xref)
        if image['ext'] != 'jpeg' or (image['width'], image['height']) != (width, height):
            raise ValueError('Unexpected source stream')
        if hashlib.sha256(image['image']).hexdigest() != expected:
            raise ValueError('Source image bytes differ')
        output = ROOT / 'assets' / f'ch22-v2-spinal-roots-figure{number}.jpeg'
        output.write_bytes(image['image'])
        records.append({'source_figure': number, 'pdf_page_1based': page + 1, 'xref': xref,
                        'path': 'assets/' + output.name, 'sha256': sha(output),
                        'pixels': [width, height], 'complete_original_jpeg_stream': True})
    record = {
        'date': '2026-11-10', 'status': 'LOCAL; actual browser/print and independent new-family review pending',
        'authors': ['Carolyn Enochs', 'Alice Li', 'Quinn Fan', 'Sara Richmond', 'Erin Paton', 'George Prada III'],
        'title': 'Novel Full-Length Dissection of the Sympathetic Chain and Spinal Cord From T1-L1 in a Human Cadaver',
        'article': 'https://doi.org/10.7759/cureus.102671', 'publication_date': '2026-01-30',
        'source_pdf_url': 'https://pmc-oa-opendata.s3.amazonaws.com/PMC12950620.1/PMC12950620.1.pdf',
        'source_pdf_sha256': SOURCE_SHA, 'source_pdf_pages': 10,
        'license': 'CC BY4.0, explicitly in source PDF first-page notice',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'specimen_preparation': 'One 75-year-old male, embalmed/formalin-fixed human cadaver; paper reports scoliosis. Posterior elements/ribs removed, vertebral bodies reduced and dura incised. Prepared tissue colours; neither intact living anatomy nor full external human figure.',
        'orientation_scale': 'Both source captions describe horizontalposterior/proneview with head outofframe to imageleft. No source metricbar; instruments not used ascalibration. No newcordsegment/vertebrallevelalignment inferred.',
        'figure7': 'SourceSC/DR/VR/DRG/PSC/GR/WR/VB/T5–T7labels. T6dorsalandventralrootfibres explicitlytransectedforexposure; do not imply all pathways intact. Whitearrows areauthoredleaders, not nerveimpulse directions.',
        'figure8': 'SourceDLdenticulateligament/duramater/SC/CE/DR/VR/VBlabels andDRGarrowheads. Captionkey DR(a)=T11,DR(b)=T12,VR(a)=T12,VR(b)=L1; sameletter doesnotidentify pairedroots. VRpassesunderDL inthisdissectedview. No transversehorns/intactCSFspaces shown.',
        'modifications': 'None. Complete original JPEG streams, no crop, recolour, overlay, new labels, filtering or resampling.',
        'print': 'Each completefigure170mmwide≈432ppi; externalsourcekey9.5pt. Actual PDF/label/credit placement pending.',
        'reproduction': {'builder': 'figures/ch22_spinal_roots.py', 'template': 'figures/ch22_spinal_roots.template.html',
                         'tool': 'PyMuPDF', 'version': fitz.VersionBind,
                         'inputs': 'Separately acquired original PDF supplied with--pdf and exact input hash; no private-path or network dependency.'},
        'figures': records,
    }
    assets = ROOT / 'assets'
    (assets / 'ch22-v2-spinal-roots-provenance.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    (assets / 'ch22-v2-spinal-roots.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'complete_source_figures': len(records), 'status': record['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, type=Path)
    build(parser.parse_args().pdf)
