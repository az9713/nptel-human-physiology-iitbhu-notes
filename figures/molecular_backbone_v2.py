"""Same-frame3WGU C-alpha trace companion and labelled surface draft.

Host Python prepares exact coordinate segments/projection metadata and SVG only.
Blender --build-scene constructs an editable static scene; --render is explicit.
No secondary-structure assignment, missing-residue interpolation or dynamics.
"""
from pathlib import Path
import argparse,base64,hashlib,json,math,re,sys

ROOT=Path(__file__).resolve().parents[1]
CHAIN_INFO={'A':{'label':'A','name':'alpha','rgb':[.67,.79,.84]},'B':{'label':'B','name':'beta','rgb':[.88,.67,.48]},'G':{'label':'C','name':'FXYD','rgb':[.49,.72,.64]}}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,s):return [x*s for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def unit(a):return mul(a,1/norm(a))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]

def options():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='work/visual-v2/ch02/molecular/pump-sas-04-final')
    p.add_argument('--render-record',default='work/visual-v2/ch02/molecular/render-01-final/render-record.json')
    p.add_argument('--out',default='work/visual-v2/ch02/molecular/backbone-01')
    p.add_argument('--build-scene',action='store_true')
    p.add_argument('--render',action='store_true')
    p.add_argument('--samples',type=int,default=48)
    p.add_argument('--device',choices=['CPU','CUDA','OPTIX'],default='CPU')
    return p.parse_args(args)

def prepare(args):
    source=ROOT/args.source;record_path=ROOT/args.render_record;out=ROOT/args.out
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    atoms_path=source/'atoms-and-ligands.json'
    assert sha(atoms_path)==manifest['atoms_sha256']
    inventory=json.loads(atoms_path.read_text(encoding='utf-8'))
    record=json.loads(record_path.read_text(encoding='utf-8'))
    primary=record_path.parent/'overview.png';assert sha(primary)==record['output_sha256']
    forward=unit(sub(record['camera']['target'],record['camera']['location']))
    right=unit(cross(forward,[0,0,1]));up=unit(cross(right,forward))
    width,height=record['render']['width'],record['render']['height']
    camera_width=record['camera']['ortho_scale'];camera_height=camera_width*height/width
    def project(xyz):
        p=sub(xyz,record['camera']['target'])
        return [width*(.5+dot(p,right)/camera_width),height*(.5-dot(p,up)/camera_height)]
    chains=[];all_breaks=[]
    for chain,info in CHAIN_INFO.items():
        ca=[x for x in inventory['atoms'] if x['polymer'] and x['chain']==chain and x['atom']=='CA' and x['element']=='C']
        parsed=[]
        for atom in ca:
            match=re.fullmatch(r'(-?\d+)([A-Za-z]?)',atom['residue_id'])
            if not match:raise ValueError('Unsupported author residue ID '+atom['residue_id'])
            parsed.append((int(match.group(1)),match.group(2),atom))
        parsed.sort(key=lambda x:(x[0],x[1]))
        seen=set();segments=[];current=[];previous=None;distances=[]
        for number,insertion,atom in parsed:
            key=atom['residue_id'];assert key not in seen;seen.add(key)
            point={'author_residue':key,'residue':atom['residue'],'xyz_A':atom['xyz_A'],'projected_pixel':project(atom['xyz_A'])}
            reason=[]
            if previous is not None:
                distance=norm(sub(atom['xyz_A'],previous[2]['xyz_A']));distances.append(distance)
                if number!=previous[0]+1 or insertion or previous[1]:reason.append('nonconsecutive author residue numbering or insertion code')
                if distance>4.8:reason.append('C-alpha distance>4.8Angstrom')
                if reason:
                    segments.append(current);current=[]
                    all_breaks.append({'chain':chain,'after':previous[2]['residue_id'],'before':key,'distance_A':distance,'reasons':reason})
            current.append(point);previous=(number,insertion,atom)
        if current:segments.append(current)
        expected=next(x['modelled_residues'] for x in manifest['chains'] if x['author_chain']==chain)
        assert len(ca)==expected
        chains.append(dict(info,author_chain=chain,points=len(ca),segments=segments,segment_lengths=[len(s) for s in segments],min_adjacent_CA_A=min(distances),max_adjacent_CA_A=max(distances),selection='Exactly selected source C-alpha carbon atoms; no added residues or secondary-structure guessing.'))
    lo=record['bounds_angstrom']['lower'];hi=record['bounds_angstrom']['upper']
    bounds=manifest['rigid_orientation']['computed_hydrophobic_boundary_z_A']
    assert bounds==[-15.1,15.1]
    planes=[]
    for z in bounds:
        corners=[[lo[0]-8,lo[1]-8,z],[hi[0]+8,lo[1]-8,z],[hi[0]+8,hi[1]+8,z],[lo[0]-8,hi[1]+8,z]]
        planes.append({'z_A':z,'world_corners_A':corners,'projected_corners_pixel':[project(p) for p in corners],'identity':'OPM computed hydrophobic-orientation reference boundary; not measured complete bilayer leaflet.'})
    anchors=[{'chain':'A','name':'alpha','pixel':[850,1005],'role':'Broad visible blue subunit territory selected from actual existing native surface pixels; not a residue/site endpoint.','box':[55,1000,350,110]}, {'chain':'B','name':'beta','pixel':[715,245],'role':'Broad visible peach subunit territory; not an atom-specific claim.','box':[55,150,350,110]}, {'chain':'G','name':'FXYD','pixel':[760,530],'role':'Broad visible mint accessory-chain territory; partial modeled segment only.','box':[1180,500,365,110]}]
    data={'status':'PREPARATION ONLY; unreviewed static companion/draft','source':str(source.relative_to(ROOT)),'manifest_sha256':sha(source/'manifest.json'),'atoms_sha256':sha(atoms_path),'render_record_sha256':sha(record_path),'primary_png_sha256':sha(primary),'primary_png':str(primary.relative_to(ROOT)),'script_sha256':sha(Path(__file__)),'units':'Exact audited OPM-oriented Angstrom coordinates; no extra rotation/recentering/scaling.','chains':chains,'break_policy':'Break at residue-number gap/insertion ambiguity OR consecutive C-alpha distance>4.8A; no interpolation/extrapolation across missing regions. POLY segments connect only admitted adjacent C-alpha positions.','breaks':all_breaks,'camera':record['camera'],'render_dimensions':[width,height],'projection':{'method':'Orthographic horizontal-fit: right=normalize(forward cross worldZ), up=right cross forward; same camera location/target/ortho-scale/aspect as primary. Blender parity still requires actual scene audit.','right':right,'up':up,'forward':forward,'world_width_A':camera_width,'world_height_A':camera_height},'reference_planes':planes,'labels':anchors,'representation':'Piecewise-linear C-alpha trace, display tube radius0.20A; not visible protein wire, backbone bonds, ribbon secondary structure or full molecular surface.','orientation':'Positive z extracellular-facing; negative z cytoplasmic-facing, from audited OPM alignment. No membrane texture or biological thickness inferred.','limitations':['Static experimental conformation only; no ion path, pump cycle, kinetic rate or dynamics.','Protein-only incomplete deposited segments; no missing residues, glycan, lipid or ligands synthesized.','Per-chain SAS surface primary remains separately represented; overlap/crevices are not a pathway.','Manual label pixel anchors require actual composed review.']}
    (out/'backbone-geometry.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    make_surface_draft(data,primary,out)
    return data,out

def make_surface_draft(data,primary,out):
    encoded=base64.b64encode(primary.read_bytes()).decode()
    guides=[]
    for plane in data['reference_planes']:
        pts=' '.join(f'{x:.3f},{y+120:.3f}' for x,y in plane['projected_corners_pixel'])
        guides.append(f'<polygon points="{pts}" fill="none" stroke="#e7ca83" stroke-width="2.5" stroke-dasharray="12,9" opacity=".78"/>')
    labels=[]
    for a in data['labels']:
        x,y,w,h=a['box'];y+=120;px,py=a['pixel'];py+=120
        startx=x+w if x<500 else x
        char={'A':'α','B':'β','G':'FXYD'}[a['chain']]
        key=CHAIN_INFO[a['chain']]['label']
        labels.append(f'<path d="M{startx} {y+55}L{px} {py}" fill="none" stroke="#e8efed" stroke-width="3"/><circle cx="{px}" cy="{py}" r="5" fill="#f6d58a"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#17333f" stroke="#8da3aa"/><text x="{x+20}" y="{y+43}" font-size="34">{char} · author {a["chain"]}</text><text x="{x+20}" y="{y+85}" font-size="30">label asym {key}{"; partial" if a["chain"]=="G" else ""}</text>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="1770" viewBox="0 0 1600 1770" role="img" aria-labelledby="title desc"><title id="title">3WGU static molecular architecture: draft labels</title><desc id="desc">Existing coordinate-derived protein surface unchanged beneath broad subunit leaders and projected OPM hydrophobic reference rectangles. These are computed orientation guides, not literal bilayer leaflets. Alpha authorA, betaB, FXYD authorG/labelC; FXYD incomplete. No transport, ion path or motion.</desc><rect width="1600" height="1770" fill="#0b1822"/><g font-family="Arial,Helvetica,sans-serif" fill="#edf3ee"><text x="50" y="50" font-size="38">One Na-bound pig Na/K-ATPase assembly · PDB3WGU</text><text x="50" y="96" font-size="30">Static source-coordinate envelope; illustrative chain colors</text><image x="0" y="120" width="1600" height="1400" xlink:href="data:image/png;base64,{encoded}"/>{''.join(guides)}{''.join(labels)}<path d="M1510 310V1340M1497 330L1510 310L1523 330M1497 1320L1510 1340L1523 1320" fill="none" stroke="#c4d9d8" stroke-width="3"/><text x="1200" y="275" font-size="30">Extracellular-facing (+z)</text><text x="1180" y="1395" font-size="30">Cytoplasmic-facing (−z)</text><text x="50" y="1570" font-size="30">Dashed rectangles: computed OPM hydrophobic reference bounds z=±15.1Å.</text><text x="50" y="1617" font-size="30">No literal membrane, measured leaflet thickness or ion pathway is shown.</text><text x="50" y="1664" font-size="30">Protein-only1.4Å-probe envelope; missing residues and ligands are not rebuilt.</text><text x="50" y="1711" font-size="30">Draft composition; exact labels and reference projections await independent review.</text></g></svg>'''
    (out/'surface-labelled-draft.svg').write_text(svg,encoding='utf-8')

def build_scene(data,out,args):
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.seed=17011;scene.cycles.use_denoising=True
    scene.render.resolution_x,scene.render.resolution_y=data['render_dimensions'];scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.world=bpy.data.worlds.new('Same scientific navy world');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.04,.065,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
    def material(name,rgb):
        mat=bpy.data.materials.new(name);mat.use_nodes=True;b=mat.node_tree.nodes['Principled BSDF']
        rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Roughness'].default_value=.65;b.inputs['Metallic'].default_value=0
        return mat
    def curve(name,points,radius,mat,closed=False):
        geo=bpy.data.curves.new(name,'CURVE');geo.dimensions='3D';geo.resolution_u=1;geo.bevel_depth=radius;geo.bevel_resolution=2;geo.use_fill_caps=True
        spline=geo.splines.new('POLY');spline.points.add(len(points)-1)
        for p,xyz in zip(spline.points,points):p.co=(*xyz,1)
        spline.use_cyclic_u=closed;obj=bpy.data.objects.new(name,geo);scene.collection.objects.link(obj);obj.data.materials.append(mat)
        return obj
    for c in data['chains']:
        mat=material('Illustrative '+c['name'],c['rgb'])
        for i,segment in enumerate(c['segments']):
            if len(segment)>1:curve(f'CA author{c["author_chain"]} segment{i}',[p['xyz_A'] for p in segment],.20,mat)
            else:
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.20,location=segment[0]['xyz_A']);bpy.context.object.data.materials.append(mat)
    guide_mat=material('Computed hydrophobic boundary guides',(.8,.69,.42))
    for plane in data['reference_planes']:curve('OPM computed boundary z'+str(plane['z_A']),plane['world_corners_A'],.10,guide_mat,True)
    camdata=bpy.data.cameras.new('Exact primary camera');cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam
    camdata.type='ORTHO';camdata.ortho_scale=data['camera']['ortho_scale'];camdata.clip_end=4000
    cam.location=data['camera']['location'];target=Vector(data['camera']['target']);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    span=camdata.ortho_scale/1.24
    def light(name,offset,power,size,color):
        l=bpy.data.lights.new(name,'AREA');l.energy=power*span**2;l.shape='DISK';l.size=size*span;l.color=color;o=bpy.data.objects.new(name,l);scene.collection.objects.link(o);o.location=target+Vector(offset)*span;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
    light('Broad neutral key',(-1.1,-1.2,1.5),100,1.5,(1,.96,.91));light('Soft cool fill',(1.3,-.3,.4),45,1.3,(.82,.91,1));light('Silhouette separation',(.3,1.1,1.2),100,1,(.92,.97,1))
    scene.cycles.device='CPU'
    if args.device!='CPU':
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type=args.device;prefs.get_devices()
        for device in prefs.devices:device.use=device.type==args.device
        if not any(d.use for d in prefs.devices):raise RuntimeError('Requested device unavailable')
        scene.cycles.device='GPU'
    bpy.context.view_layer.update();parity=[]
    for p in data['reference_planes']:
        for world,expected in zip(p['world_corners_A'],p['projected_corners_pixel']):
            q=world_to_camera_view(scene,cam,Vector(world));actual=[q.x*data['render_dimensions'][0],(1-q.y)*data['render_dimensions'][1]]
            parity.append(max(abs(a-b) for a,b in zip(actual,expected)))
    if max(parity)>.02:raise RuntimeError('Projection/camera parity mismatch '+str(max(parity)))
    scene['representation']=data['representation'];scene['motion']='None';scene['source_manifest_sha256']=data['manifest_sha256']
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'backbone-scene.blend'))
    record={'status':'Static companion prototype; actual review pending','blender':bpy.app.version_string,'geometry_sha256':sha(out/'backbone-geometry.json'),'projection_max_error_pixels':max(parity),'camera_matches_primary':data['camera'],'scene_sha256':sha(out/'backbone-scene.blend'),'rendered':False}
    if args.render:
        scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'backbone.png');bpy.ops.render.render(write_still=True);record.update(rendered=True,output_sha256=sha(out/'backbone.png'))
    (out/'scene-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('BACKBONE_SCENE_COMPLETE',out)

if __name__=='__main__':
    args=options();data,out=prepare(args)
    if args.build_scene:build_scene(data,out,args)
    elif args.render:raise ValueError('--render requires explicit --build-scene')
    print('BACKBONE_PREPARED',out,'points',sum(c['points'] for c in data['chains']),'breaks',len(data['breaks']))
