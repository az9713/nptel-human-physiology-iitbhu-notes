"""Build the bounded observed organelle reference; Pillow 11.0.0.

Public originals are immutable inputs on rebuild. First acquisition fallback is
private work; no private template/data is required once assets are delivered.
No generated anatomy, resampling, timing interpolation or GPU operation.
"""
from pathlib import Path
import hashlib, json, platform
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
S = ROOT / 'work/visual-v2/ch01-cell'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = [
    dict(id='er', acquired='nuclear-figure1-source/Fig1C.png', file='ch01-v2-cell-er-source.png', dimensions=[687,705], sha256='fd75d3af82e24b325c8db5c2c43e2d4b66c5e7326614223cd950d5500091311c', creator='Bragulat-Teixidor, Ishihara, Szucs and Otsuka (2024)', doi='10.1038/s44319-024-00175-w', url='https://link.springer.com/article/10.1038/s44319-024-00175-w', rights='Source research data CC0 unless separately credited; article figures CC BY 4.0. Attribution retained conservatively.', specimen='Interphase HeLa human cervical cancer cell line; high-pressure freezing, freeze substitution/resin, 250 nm tomographic section.', limitation='Outer nuclear membrane/ER continuity, not a connection into nucleoplasm. Source preparation shrinkage estimate about17%; no living dimensions inferred.'),
    dict(id='golgi', acquired='golgi-figure1-native.jpg', file='ch01-v2-cell-golgi-source.jpg', dimensions=[3395,2835], sha256='68eb997ae00277a5b064198d9266deb62e3f8d0d0b400d0170814e2d02577270', creator='Bykov et al. (2017)', doi='10.7554/eLife.32493', url='https://elifesciences.org/articles/32493', rights='CC BY 4.0; no Figure1 third-party exclusion found in owning caption.', specimen='Chlamydomonas reinhardtii; vitrified cellular cryo-FIB lamella and cryo-electron tomography.', limitation='Algal specimen, not human. A tomographic slice and B corresponding author segmentation share a volume. Source segmentation colors are annotations. Other studies are independent specimens.'),
    dict(id='granules', acquired='secretory-figure1-native.jpg', file='ch01-v2-cell-granules-source.jpg', dimensions=[709,942], sha256='9088edb2d1a46e3a8808123aa64c386eb87ee6bb695257f40673f05e430c068b', creator='Makam et al. (online2024; volume2025)', doi='10.1096/fba.2024-00131', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC11795275/', rights='CC BY 4.0; no Figure1 third-party exclusion found.', specimen='Rat INS-1 832/13 insulinoma cells; glutaraldehyde/paraformaldehyde fixation, osmium, uranyl contrast, dehydration/LR White, 50–100 nm sections.', limitation='Paper title references human beta cells, but these TEM panels are rat INS-1. Static profiles do not establish fusion kinetics or aqueous pore topology.'),
]
sources.append(dict(id='er-author', acquired='er-context/figure1-owning-native.png',
    file='ch01-v2-cell-er-author-source.png', dimensions=[1752,1295],
    sha256='7597531afe0b9f6af3c43446571313df2b42194e9b05d6723738439e1325c323',
    creator='Bragulat-Teixidor, Ishihara, Szucs and Otsuka (2024)',
    doi='10.1038/s44319-024-00175-w',
    url='https://link.springer.com/article/10.1038/s44319-024-00175-w/figures/1',
    rights='CC BY 4.0 article figure. Creative annotation/mesh elements are not covered by the associated-data CC0 waiver.',
    specimen='HeLa cells; high-pressure frozen, freeze-substituted resin preparation, 250 nm tomographic section.',
    limitation='Original raw/author-colored Figure1C locates the constricted ER-outerNE membrane connection. Source colors are annotations. No open aqueous neck, flow or nucleoplasmic connection demonstrated.'))
for s in sources:
    target = A / s['file']
    origin = target if target.exists() else S / s['acquired']
    assert sha(origin) == s['sha256'], s['id']
    assert list(Image.open(origin).size) == s['dimensions'], s['id']
    if origin != target: target.write_bytes(origin.read_bytes())
    s['bytes'] = target.stat().st_size
    s['modifications'] = 'None; original complete file bytes retained.'

crops = [
    dict(id='golgi-a', source='golgi', rect=[0,0,1620,1770], file='ch01-v2-cell-golgi-a.png', print_width_mm=80, disclosure='Publisher Figure1A; top-left panel, including A tag, author labels and original bar. Lower C-H panels omitted.'),
    dict(id='golgi-b', source='golgi', rect=[1630,0,3395,1770], file='ch01-v2-cell-golgi-b.png', print_width_mm=80, disclosure='Publisher Figure1B; top-right author segmentation including B tag. White gutter and lower C-H panels omitted; no new scale bar added.'),
    dict(id='granules', source='granules', rect=[0,0,709,670], file='ch01-v2-cell-granules.png', print_width_mm=130, disclosure='Figure1A-F only; bottom quantitative plots G/H omitted. All displayed source tags, arrows, outlines and500nm bars retained.'),
]
crops.append(dict(id='er-author-c', source='er-author', rect=[950,550,1330,1295],
    file='ch01-v2-cell-er-author.png', print_width_mm=60,
    disclosure='Published Figure1C: raw slice above, source author annotation below, C tag and original20nm bar retained. PanelsA/B/D omitted; no new leader, recoloring or resampling.'))
byid = {s['id']:s for s in sources}
for c in crops:
    source = Image.open(A / byid[c['source']]['file'])
    image = source.crop(tuple(c['rect']))
    image.save(A / c['file'], optimize=False)
    c.update(dimensions=list(image.size), sha256=sha(A/c['file']), bytes=(A/c['file']).stat().st_size, operation='Lossless PNG crop of original PNG or decoded native JPEG pixels; no resampling, recoloring, sharpening, invented detail or anatomical overlay.', native_ppi_at_print_width=image.width/(c['print_width_mm']/25.4))

template = (ROOT/'figures/ch01_cell_observed_v2.template.html').read_text(encoding='utf-8')
(A/'ch01-v2-cell-reference.html').write_text(template, encoding='utf-8')
record = dict(status='PROVISIONAL bounded observed structural reference; not all-rubric acceptance', date='2026-11-08', sources=sources, crops=crops,
    registration='Only Golgi A/B share a source tomogram. Other specimens/organisms/preparations/scales are independent; no continuous zoom or trafficking history.',
    source_context='ER original isolated raw source and published author-annotated Figure1C retained; full owning figure supplies context. Granule full source contains graphs G/H. Displayed studies are ER junction, algal Golgi and fixed rat granules only.',
    scope={'supported':['Source ER-outerNE membrane connection, no open aqueous neck claim','Algal Golgi slice and corresponding author segmentation','Fixed rat INS-1 granule profiles'], 'unfinished':['Complete whole-cell compartment inventory/map','Validated whole-cell plasma membrane boundary','Complete physiological secretion mechanism/animation','Direct human cargo-release and fusion-pore evidence']},
    temporal_companion='ch01-v2-secretory-observed.html: separate mouse RUSH cargo relocation and yeast GFP-Sec4 dynamics, not a stitched complete pathway or human release movie.',
    scale='Source bars retained: ER20nm, Golgi A/B200nm caption context, rat TEM500nm. No shared metric calibration or timebase.',
    print={'planned_widths_mm':{'er':60,'golgi_a':80,'golgi_b':80,'granules':130}, 'ppi':{'er':380/(60/25.4),'golgi_a':1620/(80/25.4),'golgi_b':1765/(80/25.4),'granules':709/(130/25.4)}, 'external_keys':'9.5pt minimum, white html/body, three print figures; actual revised PDF pending.'},
    tools={'python':platform.python_version(),'pillow':pillow_version}, reproduction='Public builder/template, four immutable original assets and shared modal CSS/JS; no private work dependency on rebuild. Pillow11.0.0 pins crop pixels.', rights='Source-specific CCBY4 notices/attribution retained; research-dataCC0 does not cover creative author annotations. Crops declared; no blanket book licence.',
    pending=['Independent structural-source/appearance review of exact final files','Root desktop650/390 native/Fit/pan/keyboard review','Actual revised three-figure PDF annotation/bar legibility','Unfilled whole-cell and full physiological secretion requirements'])
record['print']['planned_widths_mm']['er'] = 60
record['print']['ppi']['er'] = 380/(60/25.4)
record['print']['source_limited_exception'] = 'Author-annotated ER380px at60mm~161ppi; granules709px at130mm~139ppi. Native source-limited exceptions; no upsampling. Actual revised three-figure PDF proof pending.'
record['artifacts'] = {p.name:sha(p) for p in [A/s['file'] for s in sources]+[A/c['file'] for c in crops]+[A/'ch01-v2-cell-reference.html']}
record['artifacts'].update({f:sha(A/f) for f in ['observed-image-dialog.css','observed-image-dialog.js']})
(A/'ch01-v2-cell-provenance.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('CELL_OBSERVED_BUILT', len(record['artifacts']), 'artifacts')
