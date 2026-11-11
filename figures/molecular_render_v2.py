"""Blender-only renderer for audited coordinate-derived molecular OBJ surfaces.

This creates a static scientific reconstruction, not molecular dynamics or an
optical photograph. Input coordinates remain in Angstrom units. Chain colours,
material and illumination are illustrative. No invented surface noise is added.
Run: blender -b -t 4 -P figures/molecular_render_v2.py -- --input DIR --output DIR
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--samples', type=int, default=48)
parser.add_argument('--width', type=int, default=1600)
parser.add_argument('--height', type=int, default=1400)
options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source = (ROOT/options.input).resolve()
out = (ROOT/options.output).resolve()
out.mkdir(parents=True, exist_ok=True)
paths = sorted(source.glob('*.obj'))
if not paths:
    raise ValueError('No audited OBJ surfaces in input directory')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = options.samples
scene.cycles.use_denoising = True
scene.cycles.seed = 17011
scene.render.resolution_x = options.width
scene.render.resolution_y = options.height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world = bpy.data.worlds.new('Molecular overview world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.025, .04, .065, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45

# Reproducible path tracing on the available device, with CPU fallback.
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    gpu_found = False
    for device in prefs.devices:
        device.use = device.type == 'CUDA'
        gpu_found = gpu_found or device.use
    if gpu_found:
        scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'


def linear(rgb):
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb)


def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*linear(rgb), 1)
    bsdf.inputs['Roughness'].default_value = .64
    bsdf.inputs['Metallic'].default_value = 0
    bsdf.inputs['IOR'].default_value = 1.38
    bsdf.inputs['Subsurface Weight'].default_value = .04
    bsdf.inputs['Subsurface Radius'].default_value = (1, .6, .4)
    bsdf.inputs['Subsurface Scale'].default_value = .1
    bsdf.inputs['Coat Weight'].default_value = 0
    return mat


palette = [(.67, .79, .84), (.88, .67, .48), (.49, .72, .64), (.75, .64, .82)]
objects = []
for index, path in enumerate(paths):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(path), forward_axis='Y', up_axis='Z')
    new = [x for x in bpy.data.objects if x not in before and x.type == 'MESH']
    if not new:
        raise ValueError(f'No mesh imported from {path.name}')
    mat = material(f'Illustrative chain colour {path.stem}', palette[index % len(palette)])
    for obj in new:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        # Smooth normals only. Vertex positions and structural gaps are retained.
        for face in obj.data.polygons:
            face.use_smooth = True
        obj['source_obj'] = path.name
        obj['source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        obj['coordinate_unit'] = 'angstrom; no geometry scale change'
        objects.append(obj)

points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
lower = Vector(tuple(min(p[i] for p in points) for i in range(3)))
upper = Vector(tuple(max(p[i] for p in points) for i in range(3)))
centre = (lower+upper)/2
span = max(upper-lower)
if not all(math.isfinite(v) for p in points for v in p) or span <= 0:
    raise ValueError('Nonfinite or degenerate molecular coordinates')


def aim(obj):
    obj.rotation_euler = (centre-obj.location).to_track_quat('-Z', 'Y').to_euler()


def area(name, relative, energy, size, colour):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy*span*span
    light.shape = 'DISK'
    light.size = size*span
    light.color = colour
    obj = bpy.data.objects.new(name, light)
    scene.collection.objects.link(obj)
    obj.location = centre+Vector(relative)*span
    aim(obj)


area('Broad neutral key', (-1.1, -1.2, 1.5), 100, 1.5, (1, .96, .91))
area('Soft cool fill', (1.3, -.3, .4), 45, 1.3, (.82, .91, 1))
area('Silhouette separation', (.3, 1.1, 1.2), 100, 1.0, (.92, .97, 1))
camera_data = bpy.data.cameras.new('Scientific overview camera')
camera = bpy.data.objects.new('Scientific overview camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.ortho_scale = span*1.24
camera_data.clip_end = span*20
camera.location = centre+Vector((1.0, -2.6, .65))*span
aim(camera)
scene['representation'] = 'Coordinate-derived surface; see preprocessing manifest for algorithm/radii/selection.'
scene['colour_and_material'] = 'Illustrative chain colours and material; not measured optical properties or literal molecular colours.'
scene['dynamics'] = 'None. One static experimental conformation; no inferred biological motion.'
scene['geometry_unit'] = 'Input Angstrom coordinates preserved. Blender lighting is a display convention.'

bpy.ops.wm.save_as_mainfile(filepath=str(out/'molecular-scene.blend'))
scene.render.filepath = str(out/'overview.png')
bpy.ops.render.render(write_still=True)
record = {
    'status': 'PROTOTYPE; native anatomy/appearance review pending',
    'blender': bpy.app.version_string,
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'input_obj_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'bounds_angstrom': {'lower': list(lower), 'upper': list(upper)},
    'render': {'samples': options.samples, 'seed': 17011, 'width': options.width, 'height': options.height},
    'camera': {'location': list(camera.location), 'target': list(centre), 'ortho_scale': camera_data.ortho_scale},
    'output_sha256': hashlib.sha256((out/'overview.png').read_bytes()).hexdigest(),
    'limitations': ['No measured optical colour/material', 'No biological motion', 'No inference of absent residues', 'No physiological membrane or ligand path added']
}
(out/'render-record.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print('MOLECULAR_RENDER_COMPLETE', out/'overview.png', flush=True)
