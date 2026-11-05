"""MPFB core exterior reference, metres. Run Blender -b -t 4 --python this_file.
Output PNGs contain no internal anatomy. Separate SVGs are original schematics.
"""
from pathlib import Path
import bpy, math, json, hashlib
from mathutils import Vector, Matrix
from bl_ext.blender_org.mpfb.services.humanservice import HumanService
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'work/ch01-body'; ASSET=ROOT/'assets';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
macro={'gender':1.0,'age':0.5,'muscle':0.5,'weight':0.5,'height':0.5,'proportions':0.5,'race':{'asian':0.33,'caucasian':0.34,'african':0.33}}
body=HumanService.create_human(mask_helpers=True,macro_detail_dict=macro)
rig=HumanService.add_builtin_rig(body,'default',import_weights=True)
REALISM=ROOT/'sources/assets/body-realism/selected'
eyes=HumanService.add_mhclo_asset(str(REALISM/'eyes/low-poly/low-poly.mhclo'),body,asset_type='Eyes',subdiv_levels=2,material_type='MAKESKIN')
# Orient successive limb segments in world coordinates, retaining local bone roll.
for side,sign in [('L',1),('R',-1)]:
    for name in ['upperarm01','upperarm02','lowerarm01','lowerarm02']:
        p=rig.pose.bones[name+'.'+side]; bpy.context.view_layer.update()
        old=p.matrix.copy(); direction=Vector((sign*.20,0,-1)).normalized()
        rot=(old.to_3x3()@Vector((0,1,0))).rotation_difference(direction)
        p.matrix=Matrix.Translation(old.translation)@rot.to_matrix().to_4x4()@old.to_3x3().to_4x4()
        bpy.context.view_layer.update()
# Supination distributed along forearm; palms/ lateral thumbs verified by front preview.
for side,sign in [('L',1),('R',-1)]:
    for name in ['lowerarm01','lowerarm02']:
        p=rig.pose.bones[name+'.'+side];p.matrix=p.matrix@Matrix.Rotation(math.radians(-45)*sign,4,'Y');bpy.context.view_layer.update()
for p in body.data.polygons:p.use_smooth=True
sub=body.modifiers.new('Surface subdivision','SUBSURF');sub.levels=2;sub.render_levels=2
def texture_material(name,path,roughness,sss=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    image=n.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(path),check_existing=True);image.image.colorspace_settings.name='sRGB'
    uv=n.new('ShaderNodeTexCoord');l.new(uv.outputs['UV'],image.inputs['Vector']);l.new(image.outputs['Color'],p.inputs['Base Color'])
    p.inputs['Roughness'].default_value=roughness;p.inputs['Subsurface Weight'].default_value=sss
    p.inputs['Subsurface Radius'].default_value=(1,.45,.2);p.inputs['Subsurface Scale'].default_value=.0015
    return mat
mat=texture_material('Official CC0 skin atlas / illustrative optics',REALISM/'skins/middleage_asian_male/middleage_lightskinned_male_diffuse2.png',.49,.18)
n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=850;tex.inputs['Detail'].default_value=2
coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.00012;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);body.data.materials.clear();body.data.materials.append(mat)
eye_mat=texture_material('Official CC0 brown eyes / illustrative optics',REALISM/'eyes/materials/brown_eye.png',.22)
eye_mat.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.2
eye_mat.node_tree.nodes.get('Principled BSDF').inputs['Coat Roughness'].default_value=.12
eyes.data.materials.clear();eyes.data.materials.append(eye_mat)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=720;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.world=bpy.data.worlds.new('Studio world');scene.world.color=(.12,.12,.12);scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.5
def light(name,pos,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.9))-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-2,-3,3),350,2,(1,.91,.82));light('Fill',(2,-1,1.8),140,2,(.8,.9,1));light('Rim',(1,2,2.8),250,1.5,(.8,.9,1))
d=bpy.data.cameras.new('Orthographic reference');cam=bpy.data.objects.new('Orthographic reference',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=1.9
for name,pos in [('front',(0,-5,.86)),('side',(-5,0,.86))]:
    cam.location=pos;cam.rotation_euler=(Vector((0,0,.86))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(ASSET/f'ch01-body-{name}.png');bpy.ops.render.render(write_still=True)
# Inspect texture mapping and eye fit at a separate head scale; no invented internals.
scene.render.resolution_x=600;scene.render.resolution_y=600;d.ortho_scale=.34
for name,pos in [('head-front',(0,-5,1.60)),('head-side',(-5,-.04,1.60))]:
    cam.location=pos;target=(0,-.04,1.60) if name=='head-side' else (0,0,1.60);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{name}.png');bpy.ops.render.render(write_still=True)
scene.render.resolution_x=720;scene.render.resolution_y=1200;d.ortho_scale=1.9
cam.location=(0,-5,.86);cam.rotation_euler=(Vector((0,0,.86))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'body-orientation.blend'))
(OUT/'build-evidence.json').write_text(json.dumps({'blender':bpy.app.version_string,'mpfb':'2.0.18','macro':macro,'units':'metres','orientation':'model anterior -Y, left +X, superior +Z; verify render','pose':'upper/lower arm direction (+/-0.20,0,-1); forearm supination -45deg per segment mirrored; inspect final palms','render':{'engine':'Cycles CPU','samples':32,'threads':4,'resolution':[720,1200],'view_transform':'AgX','exposure_stops':-.5},'geometry':'MPFB core surface plus fitted official low-poly eyes; no organs; helper masking only, no body clipping','uv_layers':[u.name for u in body.data.uv_layers],'body_vertices':len(body.data.vertices),'eye_vertices':len(eyes.data.vertices),'fitting':'HumanService.add_mhclo_asset hm08 vertex attachments before pose','skin_source_sha256':hashlib.sha256((REALISM/'skins/middleage_asian_male/middleage_lightskinned_male_diffuse2.png').read_bytes()).hexdigest(),'material':'Official CC0 skin UV diffuse and fitted low-poly brown eyes; artistic Principled roughness/SSS; .12mm illustrative bump, no diffuse displacement','acceptance':'pending independent scientific and visual review'},indent=2))
print('BODY_RENDER_COMPLETE')


