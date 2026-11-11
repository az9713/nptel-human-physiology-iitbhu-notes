"""Recompose source-preserving anatomy and externally plotted saved balance states."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]; A=R/'assets'; P='ch17-v2-countercurrent'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
data=A/'ch17-countercurrent-data.json'
assert sha(data)=='25fe59fa85bef7e06673e56d5e6b2cd5235b2f52234e449247f2116dbfa1f422'
d=json.loads(data.read_text()); assert len(d['frames'])==201
def chart(f):
    z=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" role="img" aria-label="Concentration profiles at selected model state"><rect width="800" height="480" fill="white"/><g font-family="Arial,sans-serif" font-size="22" fill="#172834"><text x="130" y="35">Arbitrary osmoles per water unit</text>']
    for x in range(5):
        px=150+280*x/2; z.append(f'<path d="M{px},70V380" stroke="#ccd4d8"/><text x="{px-10}" y="420">{x/2:g}</text>')
    for j in range(4):z.append(f'<text x="28" y="{95+j*90}">Level {j}</text>')
    for k,c in [('d','#176696'),('a','#ac3457'),('inter','#357049')]:
        pts=' '.join(f'{150+280*v:.5f},{90+90*j}'for j,v in enumerate(f[k]));z.append(f'<polyline id="profile-{k}" points="{pts}" fill="none" stroke="{c}" stroke-width="5"/>')
    return ''.join(z)+'</g></svg>'
(A/(P+'-final-profiles.svg')).write_text(chart(d['frames'][-1]),encoding='utf-8')
t=R/'figures/ch17_countercurrent_v2.template.html';h=A/(P+'-reference.html')
f=d['frames'][-1];rows=''.join(f'<tr><th>{j}</th><td>{f["d"][j]:.6f}</td><td>{f["a"][j]:.6f}</td><td>{f["inter"][j]:.6f}</td></tr>'for j in range(4))
h.write_text(t.read_text(encoding='utf-8').replace('<!--FINAL_ROWS-->',rows),encoding='utf-8')
inputs=[data,A/'ch16-v2-renal-anatomy-nephron-c.png',A/'ch16-v2-renal-anatomy-sources.json']
r={'date':'2026-11-09','status':'Candidate; actual UI/PDF and final independent review pending','source_anatomy':'Li et al. 2024 DOI10.1364/BOE.515527, Figure6c exact published-PDF crop; prepared mouse tracing and optical morphology, not photographed intact wall. Optica OA noncommercial attribution terms, not CC BY. See immutable renal source record.','model':{'data_sha256':sha(data),'saved_states':201,'interpolation':False,'presentation_seconds':24,'scope':d['anatomical_scope'],'units':d['units'],'parameters':d['parameters'],'invariant':'M+B+O-F=12; M=sum of12 unit-water compartment concentrations; B removed to sink; O discharged; F supplied.','no_pump':'Exact uniform solution, reset common initial condition; F=O=0.2t, B=0, M=12; not midhistory intervention','max_saved_mass_residual':d['max_mass_residual']},'print':{'anatomy_width_mm':130,'source_ppi':715*25.4/130,'source_limited_exception':True,'profile_width_mm':145,'profile_axis_min_pt':22*145/800*72/25.4,'external_key_pt':9.5,'credit_pt':9,'proof_pending':True},'reproduction':{'builder':str(Path(__file__).relative_to(R)),'builder_sha256':sha(__file__),'template_sha256':sha(t),'offline':'Public inputs/template/JS only; no private work dependency'},'inputs':{p.name:sha(p)for p in inputs},'artifacts':{p.name:sha(p)for p in [h,A/(P+'.js'),A/(P+'-final-profiles.svg'),A/'observed-image-dialog.css',A/'observed-image-dialog.js']},'remaining_gaps':['No photoreal tubule wall or vascular exchange','No thin ascending limb, anatomical bend, inner-medullary urea or complete concentrating mechanism','Actual phone/keyboard/modal/print and appearance proof pending']}
(A/(P+'-provenance.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('COUNTERCURRENT_V2_COMPOSED')
