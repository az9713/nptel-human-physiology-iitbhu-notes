"""Static HRA heart: unchanged geometry, procedural illustrative tissue.

Blender 5.2: --factory-startup -b -t 4 --python figures/ch05_heart_render.py
Add -- --final for two 1200px/80spp stills (default 640px/32spp preview).
Source is privately retained under sources/assets/hra-heart-male/.
"""
from pathlib import Path
import hashlib
import json
import sys
import struct
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT/'work/ch05-heart'
WORK.mkdir(parents=True, exist_ok=True)
ASSETS = ROOT/'assets'
SOURCE = ROOT/'sources/assets/hra-heart-male/VH_M_Heart.glb'
EXPECTED = '1889d452b0781b9c35d8b4464c58e3ef60c26f9d7611b88e25c903ff80dbca44'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
FINAL = '--final' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
meshes = [o for o in scene.objects if o.type == 'MESH']

def bounds(obs):
    p = [o.matrix_world @ Vector(v) for o in obs for v in o.bound_box]
    return Vector([min(v[i] for v in p) for i in range(3)]), Vector([max(v[i] for v in p) for i in range(3)])

inventory = []
def mesh_digest(o):
    h=hashlib.sha256()
    for v in o.data.vertices: h.update(struct.pack('<3f',*v.co))
    for p in o.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    return h.hexdigest()
hidden_terms = ('valve','papillary','septum','brachiocephalic','common_carotid','subclavian','descending_aorta','inferior_vena_cava_b')
for o in meshes:
    o.hide_render = any(t in o.name for t in hidden_terms)
    o.hide_viewport = o.hide_render
    inventory.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.polygons),
        'source_materials':[m.name if m else None for m in o.data.materials],
        'matrix_world':[list(r) for r in o.matrix_world], 'visible':not o.hide_render,
        'vertex_polygon_sha256':mesh_digest(o)})
    # Vertex positions and polygon indices are never changed. Smooth shading
    # interpolates normals only; it does not weld the segmented surfaces.
    for p in o.data.polygons: p.use_smooth = True
visible = [o for o in meshes if not o.hide_render]
lo, hi = bounds(visible)
center = (lo+hi)/2
extent = max(hi-lo)

def tissue(name, low, high, rough, sss):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Metallic'].default_value=0
    bs.inputs['IOR'].default_value=1.38
    bs.inputs['Subsurface Weight'].default_value=sss
    bs.inputs['Subsurface Radius'].default_value=(1,.42,.23)
    bs.inputs['Subsurface Scale'].default_value=.0006
    tc=n.new('ShaderNodeTexCoord')
    broad=n.new('ShaderNodeTexNoise'); broad.inputs['Scale'].default_value=125
    broad.inputs['Detail'].default_value=3
    l.new(tc.outputs['Position'],broad.inputs['Vector']) if 'Position' in tc.outputs else l.new(tc.outputs['Object'],broad.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(*low,1)
    ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=(*high,1)
    l.new(broad.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    micro=n.new('ShaderNodeTexNoise'); micro.inputs['Scale'].default_value=4200; micro.inputs['Detail'].default_value=2
    l.new(tc.outputs['Object'],micro.inputs['Vector'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.13; bump.inputs['Distance'].default_value=.000035
    l.new(micro.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    rr=n.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value=rough-.05; rr.inputs['To Max'].default_value=rough+.05
    l.new(micro.outputs['Fac'],rr.inputs['Value']); l.new(rr.outputs[0],bs.inputs['Roughness'])
    return m

muscle=tissue('Illustrative myocardium; optical parameters unmeasured',(.14,.038,.027),(.32,.12,.078),.48,.10)
vessel=tissue('Illustrative vessel wall; no oxygenation color code',(.24,.12,.087),(.43,.26,.18),.48,.07)
coronary=tissue('Illustrative small vessels; no artery-vein color distinction',(.22,.066,.045),(.36,.15,.10),.46,.06)
for o, rec in zip(meshes,inventory):
    m=muscle if 'heart1' in rec['source_materials'] else vessel
    if any(s in o.name.lower() for s in ('coronary','interventricular','marginal','circumflex','descending_artery','diagonal','cardiac_vein','vein_of_')) and 'septum' not in o.name: m=coronary
    o.data.materials.clear(); o.data.materials.append(m)

world=bpy.data.worlds.new('Neutral dark background'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.031,.038,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
scene.world=world
def aim(o): o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
lights=[]
for name,offset,power,size in [('Broad key',(-1.5,-1.8,1.7),330,.95),('Fill',(1.4,-.8,.6),115,1.1),('Rim',(.6,1.1,1.3),200,.8)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=power*extent**2; d.shape='DISK'; d.size=size*extent
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=center+Vector(offset)*extent; aim(o)
    lights.append({'name':name,'offset_extent':offset,'energy_watts':d.energy,'size':d.size})
d=bpy.data.cameras.new('Orthographic reference camera'); camera=bpy.data.objects.new('Orthographic reference camera',d)
scene.collection.objects.link(camera); scene.camera=camera
d.type='ORTHO'; d.ortho_scale=extent*1.16; d.clip_start=extent*.001; d.clip_end=extent*100
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=80 if FINAL else 32
scene.cycles.use_denoising=True; scene.cycles.seed=17
scene.render.resolution_x=scene.render.resolution_y=1200 if FINAL else 640
scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-1.15
views={'anterior-oblique':(.2,-3,.35),'left-anterior-oblique':(2.7,-1.2,.35)}
outputs=[]
for name,offset in views.items():
    camera.location=center+Vector(offset)*extent; aim(camera)
    out=(ASSETS/f'ch05-heart-render-{name}.png') if FINAL else (WORK/f'preview-{name}.png')
    scene.render.filepath=str(out); bpy.ops.render.render(write_still=True)
    outputs.append({'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_world':list(camera.location),'camera_offset_extent':offset})
scene['source_attribution']='Kristen Browne (2021), HRA Heart Male v1.0, DOI 10.48539/hbm384.fdpd.646, CC BY 4.0'
scene['appearance']='Procedural illustrative tissue, unmeasured optical parameters; no photo-quality claim'
assert all(mesh_digest(o)==r['vertex_polygon_sha256'] and [list(x) for x in o.matrix_world]==r['matrix_world'] for o,r in zip(meshes,inventory))
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'ch05-heart-private.blend'))
record={'source':{'title':'3D Reference Organ for Heart, Male v1.0','creator':'Kristen Browne','year':2021,'doi':'https://doi.org/10.48539/hbm384.fdpd.646','url':'https://cdn.humanatlas.io/hra-releases/v1.0/models/VH_M_Heart.glb','license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','sha256':EXPECTED},
 'geometry':'Source meshes retained as imported by Blender glTF importer; imported vertices, polygon indices, placement and parent transforms unchanged throughout scene construction. No custom weld, remesh, caps, cuts, added fat, reconstructed anatomy or deformation. Smooth normals only. Imported inventory has 294478 polygons, while the earlier raw glTF accessor review counted 294496 triangles; import-level difference is not independently classified.',
 'orientation':'Landmark-inferred, not source-certified: +X left, -Y anterior, +Z superior. Views are qualified anterior-oblique interpretations.',
 'units':'glTF meter convention; metric scale_length=1; no rescaling. Specimen scale not independently calibrated; no physical scale bar.',
 'visible_bounds_xyz':[list(lo),list(hi)],'mesh_inventory':inventory,
 'render':{'blender':bpy.app.version_string,'engine':'Cycles','device':'CPU','samples':scene.cycles.samples,'size':[scene.render.resolution_x,scene.render.resolution_y],'seed':17,'denoise':True,'view_transform':'AgX','look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'orthographic_scale':d.ortho_scale,'clip':[d.clip_start,d.clip_end],'lights':lights},
 'appearance':'Restrained multiscale procedural color, roughness, 35-micrometer shader bump and 0.6-mm SSS scale are illustrative choices, not measured tissue optics. No vessel oxygenation color code. No texture displacement.',
 'limits':['RA and SVC source patches/seams remain unchanged.','No inference of hidden lumen connectivity, valve motion or hemodynamics.','Source segmentation omits external fat covering seen in the separate autopsy photograph.','Render is an anatomical illustration, not a clinical image or photographic replica.'],
 'outputs':outputs,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
target=ASSETS/'ch05-heart-render-provenance.json' if FINAL else WORK/'preview-provenance.json'
target.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('CH05_HEART_RENDER_COMPLETE', 'final' if FINAL else 'preview')
