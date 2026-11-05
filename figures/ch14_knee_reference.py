"""Reproduce the published knee reference still using only public assets.

Run: python -X utf8 figures/ch14_knee_reference.py
Requires numpy and Pillow. No native motion logs or private audit files are read.
The shared painter is an illustrative projection, not a contact calculation.
"""
import hashlib
import json
import struct
from ch14_knee_pack import ASSETS, preflight


def main():
    meta = json.loads((ASSETS / 'ch14-knee-viewer-geometry.json').read_text(encoding='utf-8'))
    blob = (ASSETS / meta['binary']).read_bytes()
    if hashlib.sha256(blob).hexdigest() != meta['binary_sha256']:
        raise ValueError('Published geometry binary hash mismatch')
    arrays = {}
    for mesh in meta['meshes']:
        vertices = [struct.unpack_from('<3f', blob, mesh['vertex_offset'] + 24*i)
                    for i in range(mesh['vertex_count'])]
        indices = struct.unpack_from('<' + 'H'*mesh['index_count'], blob, mesh['index_offset'])
        if any(i >= len(vertices) for i in indices):
            raise ValueError('Invalid triangle index')
        arrays[mesh['id']] = (vertices, indices)
    # Static mode does not apply saved poses; this placeholder is never transformed.
    preflight(meta, {'frames': [{}]}, arrays, reference_still=True)
    output = ASSETS / 'ch14-knee-reference.png'
    print(json.dumps({'output': output.name, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'meshes': len(arrays), 'private_inputs': False}))


if __name__ == '__main__':
    main()
