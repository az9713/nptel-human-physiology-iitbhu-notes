"""Rebuild observed cortical crop and source-preserving brain rotation.

python figures/ch22_brain_surfaces.py --cortical-pdf ORIGINAL_CUREUS_PDF
Requires retained public MOV/TIFF, exact separately acquired PDF, Python3,
PyMuPDF, Pillow and FFmpeg/ffprobe. No network, source enhancement or AI art.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess
import fitz
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
PDF_SHA = '40c9b333d5ba94a88604f0afb5abaf68f245e4f2af67b7aa41ffa012d70f3d8d'
MOV_SHA = 'de451ab359f4f19133cfa2d2e803c77c4adf44ac51645fe17c4356144c4a1350'
TIFF_SHA = '93b261b66194c8de9eb08481d82f7593a4f3dda0ad75767548e4e72d6f242f63'
FIGURE_SHA = '4b178acc2262e7a63d4870940a72196686c07c361f49b2e1e12add0eca3a8261'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, cwd=ROOT)


def decoded_hashes(path):
    raw = run('ffmpeg', '-v', 'error', '-threads', '2', '-i', str(path), '-map', '0:v:0',
              '-pix_fmt', 'rgb24', '-f', 'framemd5', '-')
    return [line.rsplit(',', 1)[-1].strip() for line in raw.decode().splitlines()
            if line and not line.startswith('#')]


def build(pdf):
    original = A / 'ch22-v2-brain-case1-source.mov'
    tiff = A / 'ch22-v2-brain-case1-photo-source.tif'
    for path, expected in [(pdf, PDF_SHA), (original, MOV_SHA), (tiff, TIFF_SHA)]:
        if sha(path) != expected:
            raise ValueError('Unexpected acquired input: ' + path.name)
    document = fitz.open(pdf)
    source = document.extract_image(41)
    if hashlib.sha256(source['image']).hexdigest() != FIGURE_SHA or (source['width'], source['height']) != (2000, 1125):
        raise ValueError('Unexpected original Figure1 stream')
    crop_rect = (0, 0, 980, 1125)
    crop = Image.open(io.BytesIO(source['image'])).convert('RGB').crop(crop_rect)
    cortical = A / 'ch22-v2-brain-cortical-lateral.png'
    crop.save(cortical)
    photograph = A / 'ch22-v2-brain-case1-photo.png'
    with Image.open(tiff) as image:
        if image.mode != 'RGB' or image.size != (3624, 2491):
            raise ValueError('Unexpected source photograph format')
        image.save(photograph, icc_profile=image.info.get('icc_profile'))
        if Image.open(photograph).tobytes() != image.tobytes():
            raise ValueError('Photograph pixel conversion differs')
    video = A / 'ch22-v2-brain-case1.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-i', str(original), '-map', '0:v:0',
        '-c:v', 'copy', '-an', '-map_metadata', '-1', '-movflags', '+faststart', str(video))
    hashes = [decoded_hashes(path) for path in [original, video]]
    if hashes[0] != hashes[1] or len(hashes[0]) != 693:
        raise ValueError('Stream-copy delivery changed decoded source pixels')
    frames = []
    for frame in [0, 230, 460, 692]:
        output = A / f'ch22-v2-brain-case1-frame-{frame:03}.png'
        run('ffmpeg', '-v', 'error', '-y', '-i', str(original), '-vf',
            f'select=eq(n\\,{frame})', '-frames:v', '1', '-update', '1', str(output))
        frames.append({'frame': frame, 'file_time_seconds': frame / 30,
                       'path': 'assets/' + output.name, 'sha256': sha(output)})
    poster = A / 'ch22-v2-brain-case1-poster.png'
    poster.write_bytes((A / 'ch22-v2-brain-case1-frame-000.png').read_bytes())
    record = {
        'date': '2026-11-10', 'status': 'LOCAL; actual browser/print and independent new-family review pending',
        'cortical_source': {
            'article': 'https://doi.org/10.7759/cureus.8643', 'authors': 'Vigo,Cornejo,Nunez,Abla,RodriguezRubio',
            'publication_date': '2020-06-15', 'license': 'CC BY4.0, explicitly in acquired PDF page1',
            'pdf_url': 'https://pmc-oa-opendata.s3.amazonaws.com/PMC7366040.1/PMC7366040.1.pdf',
            'pdf_sha256': PDF_SHA, 'pdf_page_1based': 3, 'xref': 41,
            'original_figure_image_sha256': FIGURE_SHA, 'original_pixels': [2000, 1125],
            'figure': '1A only', 'crop_rectangle': list(crop_rect), 'pixels': [980, 1125],
            'path': 'assets/' + cortical.name, 'sha256': sha(cortical),
            'modifications': 'Isolated lateral brain panel crop, without resampling, recolouring, retouching or added labels. Other source panel is not delivered.',
            'specimen': 'Study used5embalmed/latex-injectedcadaverheads plus an additionalMRI-derivedhealthymalemodel. Specific age,sex,hemisphere side or normality of this photographedpanelA not assigned here.',
            'orientation_scale': 'FrontalpoleFPimageleft, superiorup; no metricbar supplied. Not registered to the separate MRI or PLOS specimen.',
            'unexpanded_source_label': 'UppercaseOPprinted in sourcephoto but not expanded in Figure1caption; retained without assigning an author-defined expansion. Caption-definedOp is parsopercularis.',
        },
        'photogrammetry_source': {
            'article': 'https://doi.org/10.1371/journal.pone.0219619',
            'authors': 'Shintaku,Yamaguchi,Toru,Kitagawa,Hirokawa,Yokota,Uchihara',
            'publication_date': '2019-07-10', 'license': 'CC BY4.0, linked by owning article',
            'case': 'Case1, source-described normal/nonpathological formalin-fixed right hemisphere',
            'movie_url': 'https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0219619.s001',
            'original_mov': {'path': 'assets/' + original.name, 'sha256': MOV_SHA},
            'mp4': {'path': 'assets/' + video.name, 'sha256': sha(video), 'codec': 'H264 streamcopy',
                     'pixels': [1440, 1080], 'frames': 693, 'fps': 30, 'file_duration_seconds': 23.1,
                     'decoded_rgb_frames_identical': True,
                     'decoded_rgb_framehash_sequence_sha256': hashlib.sha256('\n'.join(hashes[0]).encode()).hexdigest()},
            'original_photo_url': 'https://journals.plos.org/plosone/article/figure/image?download=&id=10.1371%2Fjournal.pone.0219619.g003&size=original',
            'original_tiff': {'path': 'assets/' + tiff.name, 'sha256': TIFF_SHA, 'pixels': [3624, 2491]},
            'photo_png': {'path': 'assets/' + photograph.name, 'sha256': sha(photograph), 'source_rgb_pixels_identical': True},
            'scale_time': 'Figure3captionassigns1cmtooriginalblackbar; no scale is supplied inS1Movie. Source/movie23.1seconds is camera presentation, not physiological time. Rotation changes axes; no fixedorientationoverlay added.',
            'geometry_appearance': 'Author photogrammetry from60–80photos, with source lighting/toneprocessing. Supportingplateflattening and absent internalgeometry are author-described limitations. Originalmesh/rawphotocollection not supplied here; no completephotogrammetryrebuildclaim.',
            'native_frame_samples': frames,
        },
        'rights': 'Separate CCBY4sourcecomponents; ©2020Vigoetal and©2019Shintakuetal. Exact source attribution beside each reference. No model/software licence is substituted for content rights.',
        'print': 'Corticalcrop80mm≈311ppi; Figure3photo130mm≈708ppi; movieposter120mm≈305ppi. SourcebaronlycalibratesFigure3photo. Actual print/layout inspection pending.',
        'reproduction': {'builder': 'figures/ch22_brain_surfaces.py', 'template': 'figures/ch22_brain_surfaces.template.html',
                         'pymupdf': fitz.VersionBind, 'pillow': pillow_version,
                         'ffmpeg': run('ffmpeg', '-version').decode().splitlines()[0],
                         'inputs': 'Retained publicMOV/TIFF and separately acquired exact originalCureusPDF supplied with--cortical-pdf; no network or private-path dependency.'},
    }
    (A / 'ch22-v2-brain-provenance.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    (A / 'ch22-v2-brain-surfaces.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'source_crop': list(crop.size), 'source_photo_rgb_identical': True,
                      'unchanged_decoded_video_frames': len(hashes[0]), 'status': record['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cortical-pdf', required=True, type=Path)
    build(parser.parse_args().cortical_pdf)
