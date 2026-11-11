"""Inventory planned and actual visual surfaces; never infer visual acceptance.

Run from any directory: python tools/inventory_visuals.py
Outputs live in validation/visuals. All newly encountered items start PENDING.
Nested inline SVG, canvas, raster/vector assets, video and programmatic drawing
entry points are included, not just the manifest's planned figure count.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation' / 'visuals'
MEDIA = {'.svg', '.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff',
         '.mp4', '.webm', '.mov', '.gif', '.glb', '.gltf'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Surfaces(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.counts = {}

    def handle_starttag(self, tag, attributes):
        if tag not in {'img', 'svg', 'canvas', 'video', 'iframe', 'object'}:
            return
        attrs = dict(attributes)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        self.items.append({'tag': tag, 'ordinal': self.counts[tag],
                           'element_id': attrs.get('id'),
                           'source': attrs.get('src') or attrs.get('data'),
                           'label': attrs.get('alt') or attrs.get('aria-label')
                           or attrs.get('title'),
                           'poster': attrs.get('poster')})


def inventory():
    manifest = json.loads((ROOT / 'chapter-manifest.json').read_text('utf8'))
    planned, actual = [], []
    for chapter in manifest['chapters']:
        for kind in ('illustrations', 'animations'):
            for item in chapter.get(kind, []):
                planned.append({'chapter': chapter['number'], 'kind': kind,
                                'id': item['id'], 'path': item.get('path'),
                                'description': item.get('description'),
                                'visual_v2_status': 'pending'})
    files = {ROOT / c['file'] for c in manifest['chapters']}
    files.update(p for p in (ROOT / 'assets').rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts
                 and re.match(r'ch\d\d-', p.name))
    files.add(ROOT / 'assets' / 'secretory-traffic-pilot.html')
    for path in sorted(files):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        base = {'file': relative, 'file_sha256': digest(path),
                'visual_v2_status': 'pending', 'classification': 'unclassified'}
        if path.suffix.lower() in MEDIA:
            actual.append({**base, 'id': relative, 'kind': 'media-asset'})
        elif path.suffix.lower() == '.html':
            parser = Surfaces()
            parser.feed(path.read_text('utf8'))
            for surface in parser.items:
                actual.append({**base, **surface, 'kind': 'display-surface',
                               'id': relative + '#' + (surface['element_id']
                                      or f"{surface['tag']}-{surface['ordinal']}")})
        elif path.suffix.lower() == '.js':
            text = path.read_text('utf8')
            markers = [pattern for pattern in ('<svg', '<path', '<rect',
                       'createElementNS', 'getContext(', 'WebGLRenderer')
                       if pattern in text]
            if markers:
                actual.append({**base, 'id': relative, 'kind': 'drawing-code',
                               'markers': markers})
    result = {'schema': 'physiology-visual-inventory-v2',
              'rubric': 'spec/physiology-visual-rubric.md',
              'scope': 'Planned uses plus media, HTML surfaces and drawing code; '
                       'classification/visual inspection still required. '
                       'Runtime modes, crops and clinical relationships must '
                       'be expanded during review; file counts are not approval.',
              'planned_uses': planned, 'actual_surfaces': actual,
              'counts': {'planned_uses': len(planned),
                         'actual_surfaces': len(actual), 'accepted_v2': 0}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n', 'utf8')
    print(json.dumps(result['counts']))
    return result


if __name__ == '__main__':
    inventory()
