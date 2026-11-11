"""Deterministic offline composition of separately generated coordinate renders.

This composes public PNG/model inputs; editable atom/mesh/Blender producers and
scenes remain in the local studio paths declared in the input manifest. It does
not silently rerender, acquire coordinates, or fit any binding data.
"""
from pathlib import Path
import hashlib,json,platform
from PIL import Image,__version__ as pillow_version

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'

def item(path):
    data=path.read_bytes()
    return {'file':path.relative_to(ROOT).as_posix(),'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest()}

def main():
    inputs=json.loads((ASSETS/'ch11-v2-tbg-inputs.json').read_text(encoding='utf-8'))
    for entry in inputs['renders']:
        path=ASSETS/entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        image=Image.open(path).convert('RGB')
        assert list(image.size)==[1600,1200]
        assert hashlib.sha256(image.tobytes()).hexdigest()==entry['decoded_rgb_sha256']
    template=ROOT/'figures/templates/ch11-v2-tbg-binding-reference.html'
    html=ASSETS/'ch11-v2-tbg-binding-reference.html'
    html.write_bytes(template.read_bytes())
    paths=[template,html,Path(__file__).resolve(),ASSETS/'ch11-v2-tbg-inputs.json',
           ASSETS/'ch11-v2-tbg-sources.json',ASSETS/'ch11-v2-tbg-pocket-atoms.json',
           ASSETS/'ch11-v2-tbg-binding-model.js',ASSETS/'ch11-v2-tbg-binding.js']
    record={'status':'Local candidate; all applicable V01-V20 evidence required',
            'date':'2026-11-09','rebuild':'python -B -X utf8 figures/ch11_tbg_plate_v2.py',
            'tools':{'python':platform.python_version(),'Pillow':pillow_version},
            'composition':'Copies the editable HTML template, verifies immutable PNG byte/RGB identity and binds model/controller/source inputs; no network or private dependency for this composition rebuild.',
            'creation_boundary':'Blender renders were produced separately from exact archived2CEO/CCD coordinates. Editable local source/mesh/scene/code paths and hashes are in inputs; composition equality is not a claim that this script rerenders the atoms.',
            'inputs':inputs,'artifacts':[item(p) for p in paths],
            'time':'12-second linear parameter comparison of equilibrium states; not binding kinetics/carrier synthesis/patient trajectory',
            'source_structure':'Static bound molecule, unchanged when the selected population-equilibrium assumption changes',
            'plot_axes':{'capacity':[90,180],'free_concentration':[0,1.2],'bound_total_concentration':[0,20],'units':'Synthetic common concentration unit; no measured TBG affinity or patient data'},
            'print':'Two intentional coherent pages: structural reference then both exact equilibrium assumptions. Actual PDF inspection required.'}
    (ASSETS/'ch11-v2-tbg-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(item(html)))

if __name__=='__main__':
    main()
