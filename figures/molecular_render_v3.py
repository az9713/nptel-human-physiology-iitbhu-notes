"""Private material/light appearance pilot for the unchanged audited 3WGU surfaces.

This creates a static scientific reconstruction, not molecular dynamics or an
optical photograph. Input coordinates remain in Angstrom units. Chain colours,
material and illumination are illustrative. No invented surface noise is added.
One still only. No public output overwrite. Use factory startup, disabled autoexec and python-exit-code1.
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
parser.add_argument('--input', default='work/visual-v2/ch02/molecular/pump-sas-04-final')
parser.add_argument('--output', default='work/visual-v2/ch02/molecular/render-02-material-pilot')
parser.add_argument('--samples', type=int, default=48)
parser.add_argument('--width', type=int, default=1600)
parser.add_argument('--height', type=int, default=1400)
options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source = (ROOT/options.input).resolve()
out = (ROOT/options.output).resolve()
allowed = (ROOT/'work/visual-v2/ch02/molecular/render-02-material-pilot').resolve()
if out != allowed or options.samples != 48 or (options.width,options.height)!=(1600,1400):
    raise ValueError('Only the one bounded private1600x1400 pilot is authorized')
if (out/'overview.png').exists():
    raise FileExistsError('Pilot exists; no automatic rerender/overwrite')
out.mkdir(parents=True, exist_ok=True)
legacy_record_path=ROOT/'work/visual-v2/ch02/molecular/render-01-final/render-record.json'
legacy=json.loads(legacy_record_path.read_text(encoding='utf-8'))
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
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = -.5
scene.view_settings.gamma = 1.0
scene.world = bpy.data.worlds.new('Molecular overview world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.018, .023, .028, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .12

# Root-authorized isolated CPU pilot only; do not enumerate/change GPU devices.
scene.cycles.device='CPU'


def linear(rgb):
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb)


def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes=mat.node_tree.nodes
    nodes.clear()
    diffuse=nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value=(*linear(rgb),1)
    diffuse.inputs['Roughness'].default_value=.25
    output=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(diffuse.outputs['BSDF'],output.inputs['Surface'])
    return mat


# Distinct illustrative chain identities, not measured optical atom colours.
# Diffuse-only Oren-Nayar: no glossy, subsurface, coat, noise, bump or displacement.
palette = [(.63,.67,.70),(.13,.30,.46),(.85,.48,.12)]
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


area('Directional neutral key', (-1.1,-1.2,1.5),55,.65,(1,1,1))
area('Restrained neutral fill', (1.3,-.3,.4),12,1.1,(1,1,1))
area('Neutral silhouette light', (.3,1.1,1.2),65,.7,(1,1,1))
camera_data = bpy.data.cameras.new('Scientific overview camera')
camera = bpy.data.objects.new('Scientific overview camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.ortho_scale = span*1.24
camera_data.clip_end = span*20
camera.location = centre+Vector((1.0, -2.6, .65))*span
aim(camera)
# Bind unchanged coordinate source, imported bounds and exact camera to v2.
assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths} == legacy['input_obj_sha256']
assert list(lower)==legacy['bounds_angstrom']['lower'] and list(upper)==legacy['bounds_angstrom']['upper']
assert list(camera.location)==legacy['camera']['location']
assert list(centre)==legacy['camera']['target']
assert camera_data.ortho_scale==legacy['camera']['ortho_scale']
assert all(len(o.modifiers)==0 for o in objects)
scene['representation'] = 'Coordinate-derived surface; see preprocessing manifest for algorithm/radii/selection.'
scene['colour_and_material'] = 'Illustrative chain colours and material; not measured optical properties or literal molecular colours.'
scene['dynamics'] = 'None. One static experimental conformation; no inferred biological motion.'
scene['geometry_unit'] = 'Input Angstrom coordinates preserved. Blender lighting is a display convention.'

bpy.ops.wm.save_as_mainfile(filepath=str(out/'molecular-scene.blend'))
scene.render.filepath = str(out/'overview.png')
bpy.ops.render.render(write_still=True)
record = {
    'status': 'PRIVATE material/light pilot; not visual acceptance',
    'blender': bpy.app.version_string,
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'input_obj_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'bounds_angstrom': {'lower': list(lower), 'upper': list(upper)},
    'render': {'samples': options.samples, 'seed': 17011, 'width': options.width, 'height': options.height},
    'camera': {'location': list(camera.location), 'target': list(centre), 'ortho_scale': camera_data.ortho_scale},
    'output_sha256': hashlib.sha256((out/'overview.png').read_bytes()).hexdigest(),
    'material_parameters': {'shader':'Diffuse BSDF/Oren-Nayar', 'roughness':.25, 'palette_srgb_author_A_B_G':palette, 'palette_linear':[linear(c) for c in palette], 'glossy':False,'subsurface':False,'coat':False,'noise_bump_displacement':False},
    'lighting': {o.name:{'type':o.data.type,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'energy':o.data.energy,'size':o.data.size,'color':list(o.data.color)} for o in scene.objects if o.type=='LIGHT'},
    'world': {'color':list(scene.world.node_tree.nodes['Background'].inputs['Color'].default_value),'strength':scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value},
    'display': {'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma,'denoising':scene.cycles.use_denoising},
    'legacy_record_sha256':hashlib.sha256(legacy_record_path.read_bytes()).hexdigest(),
    'geometry_camera_checks':'SourceOBJhashes, importedbounds, camera location/target/orthoscale exactly equal legacyrecord; no geometry modifiers; only diffuse materials/palette/light/display changed.',
    'limitations': ['No measured optical colour/material', 'No biological motion', 'No inference of absent residues', 'No physiological membrane or ligand path added']
}
(out/'render-record.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print('MOLECULAR_V3_PRIVATE_PILOT_COMPLETE', out/'overview.png', flush=True)
