"""Source-grounded erythrocyte geometry/material prototype; NOT accepted art.

Blender 5.2: blender -b -t 4 -P figures/rbc_visual_v2.py -- --output work/visual-v2/rbc
One Blender unit represents one micrometre. This renders the axisymmetric
Evans/Fung profile as reproduced in Alimohamadi et al., PLoS Comput Biol (2020),
doi:10.1371/journal.pcbi.1007890, Eq6. It does not solve membrane mechanics,
oxygenation, flow, osmotic response or an observed cell's optical properties.
The material/camera are illustrative and require actual visual comparison.
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
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='work/visual-v2/rbc')
parser.add_argument('--samples', type=int, default=64)
parser.add_argument('--width', type=int, default=1440)
parser.add_argument('--height', type=int, default=1080)
parser.add_argument('--views', default='oblique,edge,top')
options = parser.parse_args(args)
OUT = ROOT / options.output
OUT.mkdir(parents=True, exist_ok=True)

RADIUS = 3.91
C0, C2, C4 = 0.81, 7.83, -4.39


def profile(theta):
    s, c = math.sin(theta), math.cos(theta)
    return RADIUS * s, .5 * c * (C0 + C2*s*s + C4*s**4)


def erythrocyte():
    # Single closed manifold: opposite dimple centres are actual vertices,
    # not duplicate ring vertices or an open torus.
    rings, sides = 128, 256
    vertices = [(0, 0, C0/2)]
    for i in range(1, rings):
        r, z = profile(math.pi*i/rings)
        for j in range(sides):
            phi = 2*math.pi*j/sides
            vertices.append((r*math.cos(phi), r*math.sin(phi), z))
    bottom = len(vertices)
    vertices.append((0, 0, -C0/2))
    faces = []
    for j in range(sides):
        faces.append((0, 1+j, 1+(j+1) % sides))
    for i in range(rings-2):
        a, b = 1+i*sides, 1+(i+1)*sides
        for j in range(sides):
            k = (j+1) % sides
            faces.append((a+j, b+j, b+k, a+k))
    a = 1+(rings-2)*sides
    for j in range(sides):
        faces.append((bottom, a+(j+1) % sides, a+j))
    mesh = bpy.data.meshes.new('Evans–Fung closed biconcave profile')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    cell = bpy.data.objects.new('Human RBC mean-profile reconstruction', mesh)
    bpy.context.collection.objects.link(cell)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return cell


def srgb(values):
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values)


def membrane_material():
    material = bpy.data.materials.new('Illustrative haemoglobin-red hydrated cell')
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*srgb((.54, .095, .075)), 1)
    bs.inputs['Metallic'].default_value = 0
    bs.inputs['Roughness'].default_value = .38
    bs.inputs['IOR'].default_value = 1.36
    bs.inputs['Subsurface Weight'].default_value = .28
    bs.inputs['Subsurface Radius'].default_value = (1, .28, .17)
    bs.inputs['Subsurface Scale'].default_value = .16
    bs.inputs['Coat Weight'].default_value = .06
    bs.inputs['Coat Roughness'].default_value = .3
    # Deliberately no invented pores, hairs, craters, membrane proteins or
    # visible nuclei. Subtle material variation does not alter source geometry.
    tex = nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 22
    tex.inputs['Detail'].default_value = 2
    rough = nodes.new('ShaderNodeMapRange')
    rough.inputs['To Min'].default_value = .34
    rough.inputs['To Max'].default_value = .42
    links.new(tex.outputs['Fac'], rough.inputs['Value'])
    links.new(rough.outputs[0], bs.inputs['Roughness'])
    return material


def point_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def light(name, location, power, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.shape, data.size = power, 'DISK', size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_at(obj, (0, 0, 0))


def mesh_audit(cell):
    mesh = cell.data
    edge_counts = {}
    signed_volume, area = 0., 0.
    for face in mesh.polygons:
        indices = list(face.vertices)
        for a, b in zip(indices, indices[1:]+indices[:1]):
            key = tuple(sorted((a, b)))
            edge_counts[key] = edge_counts.get(key, 0)+1
        a = mesh.vertices[indices[0]].co
        for k in range(1, len(indices)-1):
            b, c = mesh.vertices[indices[k]].co, mesh.vertices[indices[k+1]].co
            signed_volume += a.dot(b.cross(c))/6
            area += (b-a).cross(c-a).length/2
    nonmanifold = sum(count != 2 for count in edge_counts.values())
    assert nonmanifold == 0 and signed_volume > 0
    assert abs(2*max(v.co.x for v in mesh.vertices)-7.82) < 1e-4
    assert 90 < signed_volume < 100 and 130 < area < 140
    return {'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
            'nonmanifold_edges': nonmanifold, 'diameter_um': 2*RADIUS,
            'dimple_thickness_um': C0, 'volume_um3': signed_volume,
            'area_um2': area,
            'max_thickness_um': 2*max(v.co.z for v in mesh.vertices)}


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1e-6
cell = erythrocyte()
cell.data.materials.append(membrane_material())
audit = mesh_audit(cell)
scene.render.engine = 'CYCLES'
scene.cycles.samples = options.samples
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 3
scene.cycles.transmission_bounces = 2
device = 'CPU'
try:
    preferences = bpy.context.preferences.addons['cycles'].preferences
    preferences.compute_device_type = 'OPTIX'
    preferences.get_devices()
    gpu = [d for d in preferences.devices if d.type == 'OPTIX']
    for d in preferences.devices:
        d.use = d in gpu
    if gpu:
        scene.cycles.device = 'GPU'
        device = ','.join(d.name for d in gpu)
except Exception:
    scene.cycles.device = 'CPU'
scene.render.resolution_x, scene.render.resolution_y = options.width, options.height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
world = bpy.data.worlds.new('Neutral studio for morphology reconstruction')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.13, .17, .21, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = .35
scene.world = world
light('Large soft key', (-5, -5, 9), 1450, 7, (1, .91, .87))
light('Broad neutral fill', (5, 0, 5), 900, 6, (.85, .93, 1))
light('Gentle edge', (0, 5, 6), 1100, 5, (1, .8, .72))
camera = bpy.data.objects.new('Orthographic morphology camera', bpy.data.cameras.new('camera'))
bpy.context.collection.objects.link(camera)
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.4
camera.data.lens = 60
camera.data.clip_start, camera.data.clip_end = .01, 1000
views = {'oblique': (7, -12, 10), 'edge': (0, -15, 2.4), 'top': (0, -.01, 16)}
outputs = []
for view in options.views.split(','):
    camera.location = views[view]
    point_at(camera, (0, 0, 0))
    scene.render.filepath = str(OUT / (view+'.png'))
    bpy.ops.render.render(write_still=True)
    outputs.append({'file': view+'.png', 'sha256': hashlib.sha256((OUT/(view+'.png')).read_bytes()).hexdigest(),
                    'camera_position': list(camera.location)})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'rbc-prototype.blend'))
(OUT / 'render-record.json').write_text(json.dumps({
    'status': 'prototype, anatomy/appearance inspection pending',
    'source': 'https://doi.org/10.1371/journal.pcbi.1007890', 'equation': 6,
    'shape': 'Evans–Fung axisymmetric mean-profile reconstruction, not a measured individual cell',
    'coordinate_unit': 'micrometre', 'coefficients_um': [C0, C2, C4],
    'radius_um': RADIUS, 'mesh_audit': audit, 'outputs': outputs,
    'blender': bpy.app.version_string, 'device': device,
    'samples': options.samples, 'appearance': 'Illustrative red hydrated material; optical values unmeasured. No pores/nucleus/organelles invented.',
    'limitations': ['No membrane mechanics or blood-flow solution', 'Not a SEM/fluorescence/visible-light experimental observation',
                    'No oxygen binding or biological time is encoded', 'Material craft is not anatomical or photorealism acceptance']
}, indent=2)+'\n', 'utf8')
print('RBC_PROTOTYPE_RENDERED', json.dumps(audit), flush=True)
