"""Extract the entire unchanged human H&E cord plate. Python3/PyMuPDF1.27.1.
Run: python figures/ch22_cord_histology.py --pdf PATH_TO_EXACT_SOURCE_PDF
No network, private-path dependency, crop, rendering, resampling or enhancement.
"""
from pathlib import Path
import argparse,hashlib,json
import fitz
ROOT=Path(__file__).resolve().parents[1]
PDF_SHA='0ab590c3d1123622efe4de7855ec2f11af7a571c520e747a976d0148f1674bd1'
IMAGE_SHA='26d0b3952a3f53dff5109525d0b102a8e2a48a320e026baa1115523773fcb16c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(pdf):
    if sha(pdf)!=PDF_SHA:raise ValueError('Uninspected source PDF')
    d=fitz.open(pdf)
    assert len(d)==23 and 87 in {x[0] for x in d[5].get_images()}
    image=d.extract_image(87)
    assert image['ext']=='jpeg' and (image['width'],image['height'])==(1498,1968)
    assert hashlib.sha256(image['image']).hexdigest()==IMAGE_SHA
    out=ROOT/'assets/ch22-v2-cord-histology-figure1.jpeg'
    out.write_bytes(image['image'])
    record={'date':'2026-11-10','status':'LOCAL; author source/native review only; actual browser/print and distinct independent review pending','title':'Observed human cervical spinal-cord H&E sections','authors':'Lukas F. Reissig, Genova Carrero-Rojas, Udo Maierhofer and colleagues','article':'https://doi.org/10.1007/s00418-022-02154-5','publication_date':'2022-10-06','issue':'Histochemistry and Cell Biology 159:23–45 (January 2023)','source_pdf':{'url':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9899749.1/PMC9899749.1.pdf','sha256':PDF_SHA,'pages':23,'image_page_1based':6,'image_xref':87,'methods_page_1based':2,'license_page_1based':21},'source_image':{'path':out.relative_to(ROOT).as_posix(),'sha256':IMAGE_SHA,'pixels':[1498,1968],'complete_original_jpeg_stream':True},'license':'CC BY 4.0, source PDF page21 and owning publisher notice; no separate Figure1 exclusion','license_url':'https://creativecommons.org/licenses/by/4.0/','specimen':'Cervical segments C4–C6 from 15 human body donors, five different subjects per postmortem interval group24/48/72h; seven women/eight men, ages58–103, no history of neurological disorders. Exact illustrated age/sex/segment not assigned. Separate39-year-old2h thoracic organ donor is not Figure1a.','preparation':'4%PFA in0.1M phosphate buffer24h at4°C, sucrose cryoprotection, frozen,10µm cryosections, hematoxylin3min/eosin1min, dehydrated and DPX-mounted. Preparation/staining colours, not live tissue.','orientation_scale':'pr posterior roots at top-left, ar anterior roots lower-left, deep anterior fissure below supports posterior-up/anterior-down inference. No body side assigned. Caption assigns1000µm bar to a–c, printed at lower-right panelc. No invented calibration.','teaching_scope':'Observe full cervical cross-section grey/white relationship and compare postmortem preparation. b/c are different-donor half-sections, not registered stages in a living cord. No cell counts, tract map, central-canal patency or functional signal propagation inferred.','modifications':'None: complete source JPEG stream without crop, resampling, enhancement, recolouring, new labels or overlays.','print':'Intended110mm≈346ppi. Actual print composition and label/readability review pending.','reproduction':{'builder':'figures/ch22_cord_histology.py','template':'figures/ch22_cord_histology.template.html','tool':'PyMuPDF','version':fitz.VersionBind,'input':'Separately acquired source PDF supplied with--pdf and verified by SHA256.'}}
    (ROOT/'assets/ch22-v2-cord-histology-provenance.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
    (ROOT/'assets/ch22-v2-cord-histology.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'complete_source_image':True,'dimensions':[1498,1968],'sha256':sha(out)}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',type=Path,required=True);build(p.parse_args().pdf)
