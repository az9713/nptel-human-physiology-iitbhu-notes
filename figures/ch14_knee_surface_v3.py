"""One private signal/sampling diagnostic; unchanged source geometry/camera."""
from pathlib import Path
import bpy,numpy as np,json,hashlib,time
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'work/visual-v2/ch14/knee-material-04';F=O/'fields';S=R/'work/visual-v2/ch14/knee-material-03/all-tissue-reference.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'preview.png').exists():raise RuntimeError('Preserve single diagnostic; no overwrite')
t0=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
def geometry_hash(ob):return hashlib.sha256(np.asarray([tuple(v.co)for v in ob.data.vertices],dtype='<f4').tobytes()+np.asarray([tuple(p.vertices)for p in ob.data.polygons],dtype='<i4').tobytes()).hexdigest()
before={ob.name:geometry_hash(ob)for ob in scene.objects if ob.type=='MESH'}
camera_before={'matrix':[list(v)for v in scene.camera.matrix_world],'ortho':scene.camera.data.ortho_scale}
layer=bpy.context.view_layer
for name,typ in [('StatisticalHeight','VALUE'),('MaterialRoughness','VALUE'),('PerturbedNormal','COLOR')]:
 a=layer.aovs.add();a.name=name;a.type=typ
params={
'bone':dict(rgb=(.56,.49,.36),rough=(.40,.56),sss=.035,scale=.00020,coat=0),
'cartilage':dict(rgb=(.68,.65,.57),rough=(.16,.25),sss=.10,scale=.00025,coat=.12),
'meniscus':dict(rgb=(.45,.40,.34),rough=(.27,.39),sss=.04,scale=.00018,coat=.03),
'collagen':dict(rgb=(.65,.47,.36),rough=(.24,.40),sss=.035,scale=.00018,coat=.03)}
audit=[]
for ob in [o for o in scene.objects if o.type=='MESH']:
 kind='bone'if ob.name in ['FMB','TBB','FBB','PTB']else'cartilage'if ob.name in ['FMC','PTC','TBC-L','TBC-M']else'meniscus'if ob.name.startswith('MNS')else'collagen'
 s=params[kind];m=bpy.data.materials.new(ob.name+' statistical surface04');m.use_nodes=True;tr=m.node_tree;tr.nodes.clear();N=tr.nodes;L=tr.links.new
 out=N.new('ShaderNodeOutputMaterial');p=N.new('ShaderNodeBsdfPrincipled');L(p.outputs[0],out.inputs[0])
 for name,value in [('Base Color',(*s['rgb'],1)),('Subsurface Weight',s['sss']),('Subsurface Scale',s['scale']),('Subsurface Radius',(1,.75,.45)),('IOR',1.37 if kind=='cartilage' else 1.45),('Specular IOR Level',.4),('Coat Weight',s['coat']),('Coat Roughness',.09)]:p.inputs[name].default_value=value
 tex=N.new('ShaderNodeTexCoord');coord=tex.outputs['Object'];axes=None
 if kind=='collagen':
  xyz=np.asarray([v.co[:]for v in ob.data.vertices]);_,ev=np.linalg.eigh(np.cov(xyz.T));a=Vector(ev[:,-1]);b=Vector(ev[:,-2]);axes=[list(a),list(b)];comb=N.new('ShaderNodeCombineXYZ')
  for j,(basis,tile)in enumerate([(b,.006),(a,.024)]):
   dot=N.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';L(coord,dot.inputs[0]);dot.inputs[1].default_value=basis;scale=N.new('ShaderNodeMath');scale.operation='DIVIDE';L(dot.outputs['Value'],scale.inputs[0]);scale.inputs[1].default_value=tile;L(scale.outputs[0],comb.inputs[j])
  vector=comb.outputs[0]
  geo=N.new('ShaderNodeNewGeometry');dot=N.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[0].default_value=a;L(geo.outputs['Normal'],dot.inputs[1]);mul=N.new('ShaderNodeVectorMath');mul.operation='SCALE';L(geo.outputs['Normal'],mul.inputs[0]);L(dot.outputs['Value'],mul.inputs['Scale']);sub=N.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[0].default_value=a;L(mul.outputs[0],sub.inputs[1]);normal=N.new('ShaderNodeVectorMath');normal.operation='NORMALIZE';L(sub.outputs[0],normal.inputs[0]);L(normal.outputs[0],p.inputs['Tangent']);p.inputs['Anisotropic IOR Level' if 'Anisotropic IOR Level' in p.inputs else 'Anisotropic'].default_value=.55
 else:
  scale=N.new('ShaderNodeVectorMath');scale.operation='SCALE';L(coord,scale.inputs[0]);scale.inputs['Scale'].default_value=1/.024;vector=scale.outputs[0]
 if kind in ['bone','collagen']:
  im=N.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(F/(kind+'-height-statistical.png')),check_existing=True);im.image.colorspace_settings.name='Non-Color';im.extension='REPEAT';im.interpolation='Linear';im.projection='FLAT'if kind=='collagen'else'BOX';im.projection_blend=.25;L(vector,im.inputs['Vector']);height=im.outputs['Color'];distance=.00006
 else:
  noise=N.new('ShaderNodeTexNoise');L(coord,noise.inputs['Vector']);noise.inputs['Scale'].default_value=3000;noise.inputs['Detail'].default_value=2;height=noise.outputs['Fac'];distance=.000004 if kind=='cartilage' else .000012
 rough=N.new('ShaderNodeMapRange');L(height,rough.inputs['Value']);rough.inputs['To Min'].default_value=s['rough'][0];rough.inputs['To Max'].default_value=s['rough'][1];L(rough.outputs[0],p.inputs['Roughness'])
 bump=N.new('ShaderNodeBump');L(height,bump.inputs['Height']);bump.inputs['Distance'].default_value=distance;bump.inputs['Strength'].default_value=1;L(bump.outputs['Normal'],p.inputs['Normal'])
 # No coarse cloudy color signal. Fine fields affect normal and roughness only.
 for name,signal,socket in [('StatisticalHeight',height,'Value'),('MaterialRoughness',rough.outputs[0],'Value'),('PerturbedNormal',bump.outputs['Normal'],'Color')]:
  aov=N.new('ShaderNodeOutputAOV');aov.name=name;aov.aov_name=name;L(signal,aov.inputs[socket])
 ob.data.materials.clear();ob.data.materials.append(m);audit.append({'object':ob.name,'class':kind,'PCA_axes':axes,'selected_bump_distance_m':distance,'geometry_hash_before':before[ob.name]})
for ob in [o for o in scene.objects if o.type=='MESH']:assert geometry_hash(ob)==before[ob.name]
assert camera_before=={'matrix':[list(v)for v in scene.camera.matrix_world],'ortho':scene.camera.data.ortho_scale}
scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False;layer.cycles.denoising_store_passes=True;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1600;scene.render.resolution_y=1333;scene.render.resolution_percentage=100
tr=bpy.data.node_groups.new('Private surface diagnostic compositor','CompositorNodeTree');scene.compositing_node_group=tr;tr.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=tr.nodes.new('CompositorNodeRLayers');den=tr.nodes.new('CompositorNodeDenoise');tr.links.new(rl.outputs['Image'],den.inputs['Image']);tr.links.new(rl.outputs['Denoising Normal'],den.inputs['Normal']);tr.links.new(rl.outputs['Denoising Albedo'],den.inputs['Albedo']);comp=tr.nodes.new('NodeGroupOutput');tr.links.new(den.outputs[0],comp.inputs['Image'])
for name,socket in [('raw','Image'),('height','StatisticalHeight'),('roughness','MaterialRoughness'),('normal','PerturbedNormal')]:
 output=tr.nodes.new('CompositorNodeOutputFile');output.directory=str(O);output.file_name=name;output.format.media_type='IMAGE';output.format.file_format='PNG';output.format.color_depth='16';output.file_output_items.new('RGBA','Image');tr.links.new(rl.outputs[socket],output.inputs['Image'])
scene.render.filepath=str(O/'preview.png');blend=O/'diagnostic.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.render.render(write_still=True)
record={'status':'Private diagnostic; actual source/native/root/B review required; no acceptance','source_scene_sha256':sha(S),'source_scene':'Exact all16 reference meshes/camera from private test03; no input source or historical output edited','geometry_unchanged':before,'camera':camera_before,'materials':params,'objects':audit,'statistical_fields':json.loads((F/'field-record.json').read_text()),'appearance_scope':'Statistical normal/roughness fields, not recovered specimen microstructure/optics; no source photo projection, macro pores/vessels/fascicles or geometry change. PCA long/across axis not true collagen map. Bone SA4 derivative field notice remains separate.','render':{'device':'CPU','threads':4,'samples':48,'pixels':[1600,1333],'runtime_s':time.perf_counter()-t0,'blender':bpy.app.version_string,'tone':'Unchanged Khronos PBR Neutral/exposure-.45','raw_and_denoised':'Same single48spp sample frame; compositor denoise with albedo/normal, raw PNG retained; diagnostics tonemapped PNG are visual signals, not numeric recovered anatomy'},'outputs':{p.name:sha(p)for p in O.glob('*.png')},'scene_sha256':sha(blend),'script_sha256':sha(__file__)}
(O/'render-record.json').write_text(json.dumps(record,indent=2)+'\n');print('CH14_TEST04_ONE_DIAGNOSTIC_COMPLETE',flush=True)
