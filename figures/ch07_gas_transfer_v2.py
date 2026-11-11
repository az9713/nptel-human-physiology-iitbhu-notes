"""Record source/code integrity of the authored animation; never accepts it."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
files = ['assets/ch07-v2-gas-transfer.html', 'assets/ch07-v2-gas-model.js',
         'assets/ch07-v2-gas-transfer.js', 'assets/vendor/d3-animate-libs.js',
         'assets/ch07-v2-barrier-tem.jpg']
record = {
    'status': 'PROVISIONAL; final V01-V20 checks pending',
    'purpose': 'Teach independent down-partial-pressure NET O2/CO2 transfer across observed tissue, equality and reversal; not gas content, kinetics or perfusion.',
    'microscopy': {'source': 'https://doi.org/10.3389/fphys.2023.1142221',
       'figure': '1A from original complete Figure1A/B', 'species': 'rat',
       'preparation': 'vascular-perfusion fixed; source describes blood-cell-free capillaries',
       'creator': 'Knudsen, Hummel, Wrede, Zimmermann, Perlman and Smith (2023)',
       'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
       'original_dimensions_px': [1059,540], 'display_crop_ltrb': [24,26,536,538],
       'modification': 'Source JPEG unchanged. SVG viewport crop omits source panel letters; internal source labels and 0.5 micrometre bar retained. Transparent symbolic gas packets/dashed routes added without white tissue-erasing halo.'},
    'mechanism_sources': ['https://doi.org/10.1002/cphy.c150028', 'https://doi.org/10.1152/japplphysiol.00318.2016'],
    'representation': {'coordinates': 'original TEM pixels, top-left origin',
       'O2_source_path': {'x':180, 'air_y':390, 'barrier_y':240, 'blood_y':165},
       'CO2_source_path': {'x':330, 'air_y':430, 'barrier_y':350, 'blood_y':180},
       'time': '8 illustration seconds, arbitrary piecewise linear presentation, not biological seconds',
       'flux': 'No molar flux, molecule count, diffusivity, conductance or kinetic prediction',
       'partial_pressures': 'Chosen fixed ideal-reservoir boundary conditions in mmHg; gas content, haemoglobin saturation and pH not computed',
       'equilibrium': 'Zero NET-transfer symbols at equal pressures; microscopic exchange continues for positive gas pressures. At zero pressure on both sides, the model specifies no gas and does not assert molecular exchange.',
       'spatial_limits': 'Route and symbol size are illustrative; no literal channel, pore, trajectory, fluid-film resolution or cell transit is claimed'},
    'library': {'repository':'https://github.com/az9713/animate-libs',
       'path':'plugins/animate-libs/skills/animate-libs/libs/d3.js',
       'git_blob':'93ab9daf94ecd8dd7788c1bdb00140045df6ff14',
       'sha256':'856c40d8d4f055dd6daca2120538cdfec476d28894b04e0db9ebb88080714ea2',
       'usage':'Pure d3.interpolateNumber; no D3 timers or randomness',
       'notices':'vendor/animate-libs-D3-NOTICE.txt'},
    'artifacts_sha256':{name:sha(ROOT/name) for name in files},
    'reproduction': 'Authored HTML/SVG/JS with local D3 and exact separately sourced JPEG. Deterministic computeState(time, pressures); renderFrame(time) seeks presentation state. Source model is not an empirical dynamic simulation.',
    'print_resolution': 'PanelA crop512px at designed105mm is about124ppi, a source-limited exception requiring actual print/detail review; original raster has no synthetic detail added.'
}
(ROOT/'assets/ch07-v2-gas-transfer-provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Recorded candidate source/code hashes; acceptance remains pending.')
