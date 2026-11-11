"""Private appearance fields, not recovered anatomy or measured surface height."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,zoom
import hashlib,json
R=Path(__file__).resolve().parents[1];W=R/'work/visual-v2/ch14/material-brief';O=R/'work/visual-v2/ch14/knee-material-04/fields';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for name,source,rights,seed,tile_mm in [('bone','bone-shaft.png','Wasiul Bahar, Anatomy of the Bone 285 (2024), CC BY-SA4.0; statistical map derivative; source prep/scale unknown',1404,(24,24)),('collagen','central-collagen.png','Peters et al. 2018 DOI10.1038/s41598-018-24258-6, CC BY4.0; statistical map derivative; no mapped ligament identity',1405,(6,24))]:
 p=W/'third-evidence'/source
 if not p.exists() and name=='collagen':
  candidates=list((W/'third-evidence').glob('*'));raise RuntimeError(str(candidates))
 im=np.asarray(Image.open(p).convert('RGB'),dtype=float)/255
 lum=im@np.array([.2126,.7152,.0722]);detail=lum-gaussian_filter(lum,4)
 # Estimate texture power only, then randomize all phases; no source marks retained.
 resized=zoom(detail,(512/detail.shape[0],512/detail.shape[1]),order=1)
 power=np.abs(np.fft.fft2(resized))**2
 fy=np.fft.fftfreq(512)[:,None]*512;fx=np.fft.fftfreq(512)[None,:]*512
 radius=np.sqrt(fx*fx+fy*fy);bins=np.floor(radius).astype(int)
 radial=np.bincount(bins.ravel(),weights=power.ravel())/np.maximum(1,np.bincount(bins.ravel()))
 if name=='bone':
  power=radial[bins]; band=(radius>=44)&(radius<=132)
 else:
  # Disclosed longitudinal statistical approximation; no specimen fibre map.
  power=gaussian_filter(power,2);band=(abs(fx)>=12)&(abs(fx)<=36)&(abs(fy)<=12)
 amplitude=np.sqrt(power*band)
 rng=np.random.default_rng(seed);white=rng.normal(size=(512,512));phase=np.fft.fft2(white);phase/=np.maximum(abs(phase),1e-12)
 field=np.fft.ifft2(amplitude*phase).real;field/=field.std();field=.5+.10*field
 clipped=np.clip(field,0,1);path=O/(name+'-height-statistical.png');Image.fromarray(np.round(clipped*65535).astype('uint16')).save(path)
 height=(clipped-.5)*.00006 # Bump distance60µm, strength1; selected RMS≈6µm
 gy,gx=np.gradient(height,tile_mm[1]/1000/512,tile_mm[0]/1000/512)
 records.append({'name':name,'input_crop':str(p.relative_to(R)),'input_sha256':sha(p),'rights':rights,'source_photo_is_not':'Measured albedo, height, roughness or calibrated physical texture scale','map_sha256':sha(path),'seed':seed,'pixels':[512,512],'tile_mm':tile_mm,'algorithm':'Luminance detrend sigma4 source pixels; statistical power spectrum, selected display-frequency band; isotropized bone or longitudinal collagen filter; all Fourier phases replaced by deterministic Gaussian-white phases; normalize std0.1 around0.5; uint16. No source marks projected.','normal_height_RMS_m':float(height.std()),'RMS_slope_radians_approx':float(np.sqrt(np.mean(gx*gx+gy*gy))),'clip_fraction':float(np.mean((field<0)|(field>1))),'bump_distance_m':.00006,'bump_strength':1,'anatomy_change':False})
(O/'field-record.json').write_text(json.dumps({'status':'Private statistical appearance controls, not source measurements','fields':records,'generator_sha256':sha(__file__)},indent=2)+'\n')
print('STATISTICAL_FIELDS_PREPARED')

