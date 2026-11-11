"""Build sketched anatomical-plane guides; do not restore retired body photographs.

The PNG illustrations were generated once using the prompts recorded in
assets/ch01-body-sketch-provenance.json. This deterministic builder changes only
vector guides/layout, never the PNG source pixels. No Pillow dependency.
"""
from pathlib import Path
import base64
import re


def build(root):
    root = Path(root)
    assets = root / 'assets'
    images = {view: base64.b64encode((assets / name).read_bytes()).decode('ascii')
              for view, name in [('front', 'ch01-body-sketch-anterior.png'),
                                 ('lateral', 'ch01-body-sketch-lateral.png')]}

    def plane(view, kind, prefix):
        title = {'sagittal': 'Median sagittal', 'frontal': 'Coronal / frontal', 'transverse': 'Transverse'}[kind]
        path = {'sagittal': 'M400 145V1170', 'frontal': 'M400 145V1170', 'transverse': 'M170 600H630'}[kind]
        desc = ('A clothed adult anatomical line drawing. ' +
                ('Anterior view; body right is screen-left.' if view == 'front' else
                 'Lateral illustrative view, face and anterior direction screen-right.') +
                ' The magenta dashed line projects an imaginary reference plane; no internal section or measured position is shown.')
        labels = ('<text x="25" y="655">Body right</text><text x="775" y="655" text-anchor="end">Body left</text>' if view == 'front' else
                  '<text x="25" y="590">Posterior</text><text x="620" y="590">Anterior</text>')
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1320" viewBox="0 0 800 1320" role="img" aria-labelledby="{prefix}-title {prefix}-desc"><title id="{prefix}-title">{title}: imaginary plane on an anatomical sketch</title><desc id="{prefix}-desc">{desc}</desc><rect width="800" height="1320" fill="white"/><g font-family="Arial,Helvetica,sans-serif" fill="#17313b" font-size="27"><text x="34" y="48" font-size="32" font-weight="600" class="header">{title}</text><text x="34" y="88" font-size="23">Clothed anatomical sketch · qualitative position</text><image x="40" y="120" width="720" height="1080" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{images[view]}"/>{labels}<g fill="none" stroke-linecap="round"><path class="guide-halo" d="{path}" stroke="white" stroke-width="9"/><path id="{prefix}-guide" class="active-guide" d="{path}" stroke="#a80069" stroke-width="5" stroke-dasharray="16,10"/></g><text x="34" y="1260" font-size="23">Imaginary guide; no internal section is revealed.</text><text x="34" y="1295" font-size="23">AI-generated teaching sketch · no measured scale.</text></g></svg>'''

    for name, view, kind in [('anterior', 'front', 'sagittal'), ('lateral', 'lateral', 'frontal'), ('transverse', 'front', 'transverse')]:
        (assets / ('ch01-v2-plane-' + name + '.svg')).write_bytes(plane(view, kind, 'static-' + name).encode('utf8'))
    combined = '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1220" viewBox="0 0 1800 1220" role="img" aria-labelledby="orientation-title orientation-desc"><title id="orientation-title">Anatomical planes on clothed line drawings</title><desc id="orientation-desc">Median sagittal and transverse guides use an anterior sketch; the coronal guide uses a separate lateral sketch facing right. These illustrative projections are not a measured or registered body.</desc><rect width="1800" height="1220" fill="white"/><text x="35" y="48" font-family="Arial,Helvetica,sans-serif" fill="#17313b" font-size="34">Three reference planes · anatomical sketches</text>'
    for i, (view, kind) in enumerate([('front', 'sagittal'), ('lateral', 'frontal'), ('front', 'transverse')]):
        combined += f'<g transform="translate({i * 600},90) scale(.75)">' + plane(view, kind, 'plate-' + str(i)) + '</g>'
    combined += '<g font-family="Arial,Helvetica,sans-serif" fill="#17313b" font-size="24"><text x="35" y="1128">Drawings explain orientation. Dashed guides are imaginary; they do not reveal internal anatomy.</text><text x="35" y="1174">Independent illustrative views, no common physical scale. Credits: ch01-v2-plane-credits.html</text></g></svg>'
    (assets / 'ch01-body-orientation.svg').write_bytes(combined.encode('utf8'))
    page = (root / 'figures/ch01_sketch_hierarchy.template.html').read_bytes().decode('utf8')
    page = page.replace('$SKETCH_FRONT_SVG$', plane('front', 'sagittal', 'interactive-front'))
    page = page.replace('$SKETCH_LATERAL_SVG$', plane('lateral', 'frontal', 'interactive-lateral'))
    start = page.index('<section id="planes"')
    end = page.index('</section>', start) + len('</section>')
    script_start = page.index('const planeType=')
    script_end = page.index('renderFrame(0);requestAnimationFrame(frame);', script_start)
    return {'page': page, 'html': page[start:end], 'script': page[script_start:script_end],
            'css': '.sketched-planes' + page.split('.sketched-planes', 1)[1].split('</style>', 1)[0]}


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
