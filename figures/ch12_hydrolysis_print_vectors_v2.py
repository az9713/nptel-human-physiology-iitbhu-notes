"""Optional regeneration of print-only chemical layouts from the public molecular facts.

RDKit 2025.09.6 / CoordGen; original screen vectors and mechanism state are untouched.
The composition builder consumes these editable vectors without requiring RDKit.
"""
from pathlib import Path
import hashlib
import json
from rdkit import Chem, rdBase
from rdkit.Chem import rdDepictor, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D
R=Path(__file__).resolve().parents[1]
A=R/'assets'
facts=json.loads((A/'ch12-v2-hydrolysis-compounds.json').read_text(encoding='utf-8'))
facts=facts.get('records',facts)
records=[]
for name,w,h,rotation,width_mm in [('maltotriose',450,750,90,80),('maltotetraose',450,750,90,80),('isomaltose',500,260,90,70),('D-glucose',300,260,0,42)]:
    entry=facts[name]
    m=Chem.MolFromSmiles(entry['SMILES'])
    canonical=Chem.MolToSmiles(m,isomericSmiles=True)
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(m)
    d=rdMolDraw2D.MolDraw2DSVG(w,h)
    o=d.drawOptions()
    o.rotate=rotation
    o.fixedFontSize=28
    o.padding=.04
    d.DrawMolecule(m)
    d.FinishDrawing()
    assert Chem.MolToSmiles(m,isomericSmiles=True)==canonical
    assert rdMolDescriptors.CalcMolFormula(m)==entry['MolecularFormula']
    path=A/f'ch12-v2-hydrolysis-{name}-print.svg'
    path.write_text(d.GetDrawingText(),encoding='utf-8')
    records.append({'name':name,'CID':entry['CID'],'canonical_isomeric_SMILES':canonical,
        'formula':rdMolDescriptors.CalcMolFormula(m),'CIP_centres':Chem.FindMolChiralCenters(m,includeUnassigned=True),
        'rotation_degrees':rotation,'canvas':[w,h],'fixed_font_size_svg_units':28,
        'print_width_mm':width_mm,'nominal_font_points':28*width_mm/w*72/25.4,
        'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
record={'date':'2026-11-09','rdkit':rdBase.rdkitVersion,'purpose':'Print-only coordinate/layout derivatives; same source molecular graphs and stereochemistry, labels remain upright after coordinate rotation.',
        'original_screen_vectors_changed':False,'mechanism_changed':False,'records':records}
(A/'ch12-v2-hydrolysis-print-layout.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('HYDROLYSIS_PRINT_VECTORS_BUILT')
