"""HRA native-mesh organ material/composition pilots, Blender 5.2; NOT accepted art.

No anatomical deformation, fabricated fine structure, texture synthesis, section
caps, body-size rescaling or physiological animation. Detail mode hides explicitly
listed source components; it is component isolation, never a measured section.
All outputs remain under work/visual-v2/organs. Use --render explicitly.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'work/visual-v2/research'
CONFIG={
 'heart':dict(file='3d-vh-m-heart.glb',version='1.3',ref='heart-male',
   purpose='Inspect the source valve/papillary/septal assembly and chamber meshes without inventing chordae or a coronary tree.',
   absent=['coronary tree','chordae tendineae','measured valve motion'],
   details=['valve','papillary','septum']),
 'kidney':dict(file='3d-vh-m-kidney-l.glb',version='1.3',ref='kidney-male-left',
   purpose='Inspect source renal pyramids, columns and papilla-labelled meshes after hiding opaque capsule/cortical envelopes.',
   absent=['nephrons','calyces','renal vessels','urine-flow model'],
   details=['pyramid','papilla','column','hilum']),
 'lung':dict(file='3d-vh-m-lung.glb',version='1.4',ref='lung-male',
   purpose='Inspect actual lobar/segmental bronchial and cartilage meshes; do not substitute for alveoli or gas exchange.',
   absent=['alveoli','diaphragm','trachea','continuous main-bronchial path'],
   details=['bronchus','bronchi','cartilage']),
 'eye':dict(file='3d-vh-m-eye-l.glb',version='1.3',ref='eye-male-left',
   purpose='Inspect source lens, iris, retina and ciliary structures after hiding source outer envelopes/fluids; no retinal layers are reconstructed.',
   absent=['retinal cellular layers','optic chiasm','accommodation dynamics'],
   details=['retina','fovea','macula','optic_disc','iris','ciliary','lens','suspensory','ora_serrata','trabecular','schlemms']),
}

def parse():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument('--organ',choices=list(CONFIG),required=True)
    p.add_argument('--mode',choices=['full','detail'],default='detail')
    p.add_argument('--material',choices=['clay','tissue'],default='clay')
    p.add_argument('--render',action='store_true')
    p.add_argument('--samples',type=int,default=64)
    p.add_argument('--width',type=int,default=1440)
    p.add_argument('--height',type=int,default=1200)
    p.add_argument('--azimuth',type=float,default=-70)
    p.add_argument('--elevation',type=float,default=18)
    p.add_argument('--device',choices=['CPU','OPTIX'],default='CPU')
    p.add_argument('--tag',default='pilot01')
    return p.parse_args(args)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bbox(objects):
    points=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    return Vector([min(p[i] for p in points) for i in range(3)]),Vector([max(p[i] for p in points) for i in range(3)])
def srgb(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def tissue(name,rgba,rough=.48,sss=.06,transmission=0,ior=1.4):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    s=mat.node_tree.nodes['Principled BSDF']
    s.inputs['Base Color'].default_value=(*[srgb(v) for v in rgba],1)
    s.inputs['Metallic'].default_value=0
    s.inputs['Roughness'].default_value=rough
    s.inputs['IOR'].default_value=ior
    s.inputs['Subsurface Weight'].default_value=sss
    s.inputs['Subsurface Radius'].default_value=(1,.45,.25)
    s.inputs['Subsurface Scale'].default_value=.0006
    s.inputs['Transmission Weight'].default_value=transmission
    # No generated pores, vasculature, repeated noise or detail absent from source.
    return mat

def materials(organ):
    return {
     'clay':tissue('Neutral gray geometry inspection ONLY',(.53,.55,.55),.72,0),
     'muscle':tissue('Muted muscle material hypothesis',(.43,.23,.21),.5,.10),
     'fibrous':tissue('Fibrous tissue material hypothesis',(.76,.70,.61),.46,.05),
     'renal':tissue('Renal parenchyma material hypothesis',(.48,.28,.25),.53,.08),
     'medulla':tissue('Renal medulla material hypothesis',(.57,.36,.32),.56,.06),
     'lung':tissue('Pulmonary tissue material hypothesis',(.58,.40,.39),.58,.10),
     'cartilage':tissue('Cartilage material hypothesis',(.78,.74,.67),.48,.04),
     'airway':tissue('Airway wall material hypothesis',(.64,.49,.43),.51,.05),
     'sclera':tissue('Sclera material hypothesis',(.84,.81,.73),.40,.035),
     'retina':tissue('Retinal material hypothesis',(.62,.36,.27),.44,.045),
     'iris':tissue('Iris material hypothesis',(.31,.23,.16),.56,.015),
     'uvea':tissue('Uveal material hypothesis',(.24,.12,.10),.49,.025),
     'transparent':tissue('Ocular clear material hypothesis',(.95,.98,.98),.055,0,1,1.376),
    }

def assign(o,m,organ):
    n=o.name.lower()
    if organ=='heart':key='fibrous' if 'valve' in n else 'muscle'
    elif organ=='kidney':key='fibrous' if 'capsule' in n else ('medulla' if any(t in n for t in ('pyramid','papilla','medulla')) else 'renal')
    elif organ=='lung':key='cartilage' if 'cartilage' in n else ('airway' if any(t in n for t in ('bronchus','bronchi')) else 'lung')
    else:
        key=('transparent' if any(t in n for t in ('lens','cornea','humor')) else 'iris' if any(t in n for t in ('iris','pupil')) else 'retina' if any(t in n for t in ('retina','macula','fovea','optic_disc')) else 'sclera' if any(t in n for t in ('sclera','conjunctiva','ligament')) else 'uvea')
    o.data.materials.clear();o.data.materials.append(m[key])
    # Smooth existing surfaces only. No subdivision changes measured geometry.
    for poly in o.data.polygons:poly.use_smooth=True
    return key

def aim(obj,target):obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()

def run():
    args=parse();cfg=CONFIG[args.organ]
    out=ROOT/'work/visual-v2/organs'/args.organ/f'{args.tag}-{args.mode}-{args.material}'
    out.mkdir(parents=True,exist_ok=True)
    path=SOURCE/cfg['file'];cw=SOURCE/(cfg['file']+'.crosswalk.csv')
    crosswalk={row['node_name']:row for row in csv.DictReader(cw.open(encoding='utf-8-sig'))}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    mesh=[o for o in scene.objects if o.type=='MESH']
    source_bounds=bbox(mesh)
    mats=materials(args.organ);inventory=[]
    for i,o in enumerate(mesh,1):
        keep=args.mode=='full' or any(t in o.name.lower() for t in cfg['details'])
        o.hide_render=not keep;o.hide_viewport=not keep;o.hide_set(not keep);o.pass_index=i
        key=assign(o,mats,args.organ)
        if args.material=='clay':
            key='clay';o.data.materials.clear();o.data.materials.append(mats[key])
        lo,hi=bbox([o])
        inventory.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),source_crosswalk=crosswalk.get(o.name),matrix_world=[list(r) for r in o.matrix_world],bounds=[list(lo),list(hi)],visible_in_mode=keep,material_category=key,material_name=o.data.materials[0].name))
    visible=[o for o in mesh if not o.hide_render]
    if not visible:raise RuntimeError('No actual source meshes match detail selection')
    lo,hi=bbox(visible);center=(lo+hi)/2;extent=max(hi-lo)
    world=bpy.data.worlds.new('Neutral dark reference world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.046,.054,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;scene.world=world
    for name,offset,power,size in [('Large soft key',(-1.3,-1.4,1.7),600,.95),('Neutral fill',(1.4,-.6,.35),260,1.3),('Soft rim',(.6,1.1,1.2),380,.9)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power*extent**2;data.shape='DISK';data.size=size*extent
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=center+Vector(offset)*extent;aim(obj,center)
    camdata=bpy.data.cameras.new('Source-coordinate inspection camera');cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam
    az=math.radians(args.azimuth);el=math.radians(args.elevation)
    direction=Vector((math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)))
    cam.location=center+direction*extent*4;aim(cam,center)
    camdata.type='ORTHO';camdata.clip_start=extent*.001;camdata.clip_end=extent*100
    scene.render.resolution_x=args.width;scene.render.resolution_y=args.height;scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    # Fit all actual visible world-bounds corners in camera coordinates, not a
    # guessed nominal organ radius.12% margin surrounds both dimensions.
    inv=cam.matrix_world.inverted();corners=[inv@(o.matrix_world@Vector(p)) for o in visible for p in o.bound_box]
    spanx=max(p.x for p in corners)-min(p.x for p in corners);spany=max(p.y for p in corners)-min(p.y for p in corners)
    camdata.ortho_scale=max(spany,spanx/(args.width/args.height))*1.24
    for _ in range(3):
        bpy.context.view_layer.update()
        projected=[world_to_camera_view(scene,cam,o.matrix_world@Vector(p)) for o in visible for p in o.bound_box]
        factor=max(max(abs(p.x-.5)*2,abs(p.y-.5)*2) for p in projected)*1.12
        camdata.ortho_scale*=factor
    scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.seed=42;scene.cycles.use_animated_seed=False
    scene.cycles.use_denoising=False
    scene.cycles.device='CPU'
    if args.device=='OPTIX':
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for d in prefs.devices:d.use=d.type=='OPTIX'
        if not any(d.use for d in prefs.devices):raise RuntimeError('Requested OPTIX unavailable')
        scene.cycles.device='GPU'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=-2.2
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
    scene.render.film_transparent=False
    scene.render.filepath=str(out/'preview.png')
    bpy.context.view_layer.update()
    for row,o in zip(inventory,mesh):
        if o.hide_render:continue
        projected=[world_to_camera_view(scene,cam,o.matrix_world@Vector(p)) for p in o.bound_box]
        row['projected_bounds']=[[min(p[i] for p in projected) for i in range(3)],[max(p[i] for p in projected) for i in range(3)]]
        row['bbox_inside_frame']=all(0<=p.x<=1 and 0<=p.y<=1 and camdata.clip_start<p.z<camdata.clip_end for p in projected)
        # Occlusion visibility estimates must be interpreted as a sparse audit,
        # not proof that all diagnostic structures are readable in the final PNG.
        hits=0;tested=0;deps=bpy.context.evaluated_depsgraph_get()
        stride=max(1,len(o.data.vertices)//48)
        for vert in list(o.data.vertices)[::stride][:48]:
            target=o.matrix_world@vert.co;origin=target+direction*extent*5
            hit,loc,norm,idx,hitobj,mat=scene.ray_cast(deps,origin,-direction,distance=extent*10)
            tested+=1
            if hit and hitobj.original==o:hits+=1
        row['sparse_camera_visibility']={'vertex_samples':tested,'first_hit_same_object':hits,'fraction':hits/tested if tested else None,'warning':'Sparse vertex-ray estimate only; edges, transparent ocular surfaces and small structures need actual image inspection.'}
    report=dict(status='PROVISIONAL unreviewed render pilot',blender=bpy.app.version_string,organ=args.organ,mode=args.mode,teaching_brief=cfg['purpose'],source=str(path.relative_to(ROOT)),source_sha256=sha(path),crosswalk_sha256=sha(cw),source_record=f'https://purl.humanatlas.io/ref-organ/{cfg["ref"]}/v{cfg["version"]}',license='CC BY 4.0; retain owning source metadata and named creators',source_bounds_xyz=[list(p) for p in source_bounds],units='Imported glTF meter convention; no specimen metric calibration asserted. No geometry rescaling.',orientation='Preserved Blender glTF import transform. Camera angles are source-coordinate values, NOT certified anatomical anterior/posterior views.',view_parameters=vars(args),camera=dict(location=list(cam.location),matrix_world=[list(r) for r in cam.matrix_world],ortho_scale=camdata.ortho_scale,clip_start=camdata.clip_start,clip_end=camdata.clip_end),hidden_objects=[o.name for o in mesh if o.hide_render],missing_anatomy=cfg['absent'],objects=inventory,appearance='Material hypotheses only. Untextured source meshes. No microscopic detail invented. Heart comparison reference is independent autopsy photograph assets/ch05-heart-reference-autopsy.jpg; kidney/lung/eye gross photographic comparison pending.',presentation='Static reference pilot. Any future camera orbit represents presentation, never physiology.',limitations=['Internal component isolation removes enclosing meshes without adding cut faces; it is not a measured tissue section.','Heart chambers require shell-versus-blood-pool topology verification.','Kidney source names and metadata papilla-position description require reconciliation.','Lung crosswalk has label/ID anomalies; no clinical segment labels approved.','Projected bounds/raycast audit cannot certify anatomy, appearance or teaching legibility.'])
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
    report['scene_sha256']=sha(out/'scene.blend')
    if args.render:
        bpy.ops.render.render(write_still=True);report['preview_sha256']=sha(out/'preview.png')
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('ORGAN_V2_COMPLETE',args.organ,args.mode,'rendered='+str(args.render),str(out))

if __name__=='__main__':run()
