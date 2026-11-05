"""Pack acquired native knee surfaces and saved rigid poses; no FE execution.
Run python -X utf8 figures/ch14_knee_pack.py [--preflight]
Core pack uses the standard library. Optional private software raster preflight
uses already-installed numpy/Pillow; it is not browser/WebGL production QA.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, math, struct, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
OUT = ROOT / 'work/ch14-knee-viewer'
BONES = {'PTB', 'FBB', 'TBB', 'FMB'}
NAMES = {'PTB':'Patella bone','FBB':'Fibula bone','TBB':'Tibia bone','FMB':'Femur bone',
 'FMC':'Femoral cartilage','PTC':'Patellar cartilage','TBC-L':'Lateral tibial cartilage',
 'TBC-M':'Medial tibial cartilage','MNS-L':'Lateral meniscus','MNS-M':'Medial meniscus',
 'ACL':'Anterior cruciate ligament','PCL':'Posterior cruciate ligament',
 'LCL':'Lateral collateral ligament','MCL':'Medial collateral ligament',
 'PTL':'Patellar ligament','QAT':'Quadriceps tendon'}
COLORS = {'FMB':'#e6dbb8','TBB':'#a3c8e0','FBB':'#75abb8','PTB':'#f1c493',
 'FMC':'#7ebaa4','PTC':'#65a891','TBC-L':'#79aa9d','TBC-M':'#8fc4b0',
 'MNS-L':'#c89aaf','MNS-M':'#ae7899','ACL':'#e4bf65','PCL':'#d7a251',
 'LCL':'#b5a5d3','MCL':'#9d8bc5','PTL':'#e89e82','QAT':'#d38772'}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def rotation(q):
 x,y,z,w=q
 return ((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),
         (2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),
         (2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)))
def transform(v,c0,pose):
 r=rotation(pose['q_xyzw']);c=pose['c_mm']
 return tuple(c[i]+sum(r[i][j]*(v[j]-c0[j]) for j in range(3)) for i in range(3))
def pack():
 source=load(ASSETS/'ch14-knee-source.json');archive=ASSETS/'ch14-knee-geometry.zip'
 assert sha(archive.read_bytes())==source['archive']['sha256']
 private=ROOT/'work/ch14-knee-kinematics';poses=load(private/'poses.json');checks=load(private/'provenance-checks.json')
 for name,digest in checks['input_hashes'].items():
  assert sha((ROOT/'work/ch14-knee-motion'/name).read_bytes())==digest, name
 assert len(poses['frames'])==141 and len(poses['time_matched_reported_csv_series'])==141
 for frame,row in zip(poses['frames'],poses['time_matched_reported_csv_series']):
  assert math.isfinite(frame['model_time']) and abs(frame['model_time']-row['model_time'])<1e-10
  assert all(math.isfinite(v) for v in row.values())
  for key,p in frame['poses'].items():
   assert all(math.isfinite(v) for v in p['c_mm']+p['q_xyzw'])
   assert abs(math.sqrt(sum(v*v for v in p['q_xyzw']))-1)<2e-6
 blob=bytearray();meshes=[];arrays={}
 with zipfile.ZipFile(archive) as z:
  for item in source['archive']['contents']:
   raw=z.read(item['path']);assert sha(raw)==item['sha256'];count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+count*50
   vertices=[];indices=[];lookup={};normal_sums=[]
   for j in range(count):
    values=struct.unpack_from('<12fH',raw,84+50*j);tri=[]
    for k in (3,6,9):
     v=values[k:k+3];assert all(math.isfinite(x) for x in v)
     if v not in lookup:lookup[v]=len(vertices);vertices.append(v);normal_sums.append([0.,0.,0.])
     tri.append(lookup[v])
    a,b,c=(vertices[k] for k in tri);u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    for k in tri:
     for axis in range(3):normal_sums[k][axis]+=normal[axis]
    indices.extend(tri)
   assert len(vertices)<65536
   while len(blob)%4:blob.append(0)
   vo=len(blob)
   for v,n in zip(vertices,normal_sums):
    length=math.sqrt(sum(x*x for x in n));normal=[x/length for x in n] if length else [0,0,1];blob.extend(struct.pack('<6f',*v,*normal))
   io=len(blob);blob.extend(struct.pack('<'+'H'*len(indices),*indices))
   key=item['structure'];bounds=[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]]
   meshes.append({'id':key,'name':NAMES[key],'bone':key in BONES,'color':COLORS[key],
    'vertex_offset':vo,'vertex_count':len(vertices),'index_offset':io,'index_count':len(indices),
    'triangles':count,'bounds_mm':bounds,'native_file':item['path'],'native_sha256':item['sha256']})
   arrays[key]=(vertices,indices)
 # Keep reference-space vertices exactly unchanged; only the camera uses a common center.
 points=[]
 for m in meshes:
  corners=list(itertools.product(*zip(*m['bounds_mm'])))
  points.extend(corners)
  if m['bone']:
   for f in poses['frames']:points.extend(transform(v,poses['initial_centers_mm'][m['id']],f['poses'][m['id']]) for v in corners)
 bounds=[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]
 display={'schema':'oks003-source-surface-viewer-v1','binary':'ch14-knee-viewer-meshes.bin',
  'binary_sha256':sha(blob),'layout':'little endian; vertices xyz+area-weighted surface normals float32, stride24; local indices uint16; no coordinate decimation/recentering',
  'meshes':meshes,'view_bounds_mm':bounds,'units':'mm','axes':'Native source XYZ; anatomical direction signs unverified',
  'registration':'CONDITIONAL: shared STL/FEBio reference registration not independently proven; Geometry_custom.feb absent',
  'surface_policy':'All 16 source surfaces only in static reference; rigid-bone replay hides all12 soft tissues',
  'source':{k:source[k] for k in ('title','creators','source_project','dataset_doi','primary_description','specimen','coordinate_units','license_evidence','coordinate_unit_source')},
  'native_archive_sha256':source['archive']['sha256'],
  'native_motion_input_sha256':checks['input_hashes'],
  'decoded_pose_sha256':sha((private/'poses.json').read_bytes()),'decoder_sha256':sha((ROOT/'code/ch14_knee_kinematics.py').read_bytes()),
  'decoder_convention_checks':checks['checks'],'pose_source':'Native FeBio_custom.log COM/quaternion; t0 constructed from input',
  'limits':poses['limits']+['No natural-color tissue material, contact/collision solution, force direction, deformation or experimental/patient validation.','Other MRI/SEM references are separate specimens, not registered to this geometry.','Surface normals are recomputed for artificial lighting; vertex coordinates and triangles unchanged.']}
 public={k:v for k,v in poses.items() if k not in ('schema',)};public['schema']='oks003-conditional-rigid-saved-states-v1'
 (ASSETS/'ch14-knee-viewer-meshes.bin').write_bytes(blob)
 (ASSETS/'ch14-knee-viewer-geometry.json').write_text(json.dumps(display,indent=2)+'\n',encoding='utf-8')
 (ASSETS/'ch14-knee-viewer-poses.json').write_text(json.dumps(public,separators=(',',':'))+'\n',encoding='utf-8')
 (ASSETS/'ch14-knee-viewer-LICENSE.txt').write_bytes((ASSETS/'ch14-knee-LICENSE.txt').read_bytes())
 OUT.mkdir(exist_ok=True,parents=True)
 (OUT/'pack-checks.json').write_text(json.dumps({'triangles':sum(m['triangles'] for m in meshes),'mesh_count':len(meshes),'bytes':len(blob),'native_vertices_preserved':True,'no_decimation':True,'bounds_mm':bounds,'mesh_vertices':{m['id']:m['vertex_count'] for m in meshes}},indent=2)+'\n')
 return display,public,arrays

def preflight(meta,poses,arrays,reference_still=False):
 import numpy as np
 from PIL import Image,ImageDraw
 # Deterministic software painter preview, not a browser/WebGL screenshot.
 yaw=math.radians(35);pitch=math.radians(16)
 forward=np.array([math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)])
 right=np.cross([0,0,1],forward);right/=np.linalg.norm(right);up=np.cross(forward,right)
 bounds=np.array(meta['view_bounds_mm']);center=bounds.mean(axis=0);radius=np.linalg.norm(bounds[1]-bounds[0])/2
 if reference_still:
  bounds=np.array([[min(m['bounds_mm'][0][i] for m in meta['meshes']) for i in range(3)],
                   [max(m['bounds_mm'][1][i] for m in meta['meshes']) for i in range(3)]])
  center=bounds.mean(axis=0);radius=np.linalg.norm(bounds[1]-bounds[0])/2
 def raster(index,static=False):
  image=Image.new('RGB',(900,770),'#101923');draw=ImageDraw.Draw(image);triangles=[]
  for m in meta['meshes']:
   if not static and not m['bone']:continue
   key=m['id'];vertices,idx=arrays[key];v=np.array(vertices)
   if not static:
    pose=poses['frames'][index]['poses'][key];v=(v-np.array(poses['initial_centers_mm'][key]))@np.array(rotation(pose['q_xyzw'])).T+np.array(pose['c_mm'])
   scale=(650 if reference_still else 570)/(2*radius)
   q=v-center;screen=np.column_stack((450+q@right*scale,380-q@up*scale));depth=q@forward
   color=np.array(tuple(int(m['color'][j:j+2],16) for j in (1,3,5)))
   tri=np.array(idx).reshape(-1,3)
   normals=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]);norm=np.linalg.norm(normals,axis=1);norm[norm==0]=1;light=np.abs(normals@np.array([.3,-.4,.86])/norm);shades=.30+.70*np.minimum(1,light)
   for face,d,shade in zip(tri,depth[tri].mean(axis=1),shades):triangles.append((d,screen[face],tuple((color*shade).astype(int))))
  for _,xy,color in sorted(triangles,key=lambda r:r[0]):draw.polygon([tuple(point) for point in xy],fill=color)
  f=poses['frames'][index];label='Reference pose: 16 segmented structures' if reference_still else ('STATIC: all16 reference surfaces' if static else f'BONES ONLY: saved load coordinate {f["model_time"]:.6f}')
  subtitle='Original source positions; illustrative colors, not tissue appearance' if reference_still else 'CONDITIONAL registration | artificial colors | software source preflight'
  draw.text((24,20),label,fill='white');draw.text((24,44),subtitle,fill='#e8bf70')
  draw.text((24,710),'Native source XYZ, no anatomical camera-axis signs assigned. No soft tissue motion.',fill='white')
  return image
 if reference_still:
  raster(0,True).save(ASSETS/'ch14-knee-reference.png')
  return
 raster(0,True).save(OUT/'static-reference.png')
 indices=[min(range(len(poses['frames'])),key=lambda j:abs(poses['frames'][j]['model_time']-t)) for t in (0,1,1.25,1.5,1.75,2)]
 frames=[raster(i) for i in indices]
 for i,frame in zip(indices,frames):frame.save(OUT/f'bones-step-{i:03d}.png')
 frames[0].save(OUT/'saved-state-preview.gif',save_all=True,append_images=frames[1:],duration=650,loop=0)
 (OUT/'preflight-samples.json').write_text(json.dumps({'method':'software painter/source-state preview; NOT browser rendering, motion playback or contact validation','indices':indices,'load_coordinates':[poses['frames'][i]['model_time'] for i in indices]},indent=2)+'\n')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preflight',action='store_true');parser.add_argument('--reference-still',action='store_true');args=parser.parse_args();m,p,a=pack()
 if args.preflight:preflight(m,p,a)
 if args.reference_still:preflight(m,p,a,True)
 print(json.dumps({'meshes':len(m['meshes']),'saved_frames':len(p['frames']),'packed_sha256':m['binary_sha256']}))
