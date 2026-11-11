"""Rebuild the hierarchy with sketched human figures and observed skin/microscopy.

The user explicitly replaced only photorealistic unclothed human figures with
sketches. See assets/ch01-body-sketch-provenance.json for prompts and limits.
Existing independent skin, histology and fibroblast imagery remains unchanged.
The template retains the native guided-tour, plane, print and accessibility UI.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def build():
    art = runpy.run_path(str(ROOT / 'figures/ch01_planes_v2.py'))['build'](ROOT)
    (ROOT / 'assets/ch01-scale-hierarchy.html').write_bytes(art['page'].encode('utf8'))


if __name__ == '__main__':
    build()
