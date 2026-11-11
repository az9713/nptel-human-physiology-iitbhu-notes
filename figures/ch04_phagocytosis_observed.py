"""Reproduce an observed macrophage movie and native stills from retained original AVI.
Requires Python3, FFmpeg/libvpx-vp9 and ffprobe. No network, crop or enhancement.
"""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'
SOURCE_SHA='952c18d926186df91ea850b06c238b8771496b033f3c2672c582934d4eb4fe3a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*a):return subprocess.check_output(a,cwd=ROOT)
def frames(p):
    raw=run('ffmpeg','-v','error','-i',str(p),'-vf','format=rgb24','-f','framemd5','-').decode().splitlines()
    return [x.split(',')[-1].strip() for x in raw if x and not x.startswith('#')]
def timestamps(p):
    data=json.loads(run('ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(p)))
    return [float(x['best_effort_timestamp_time']) for x in data['frames']]
def build():
    source=A/'ch04-v2-phagocytosis-source.avi';delivery=A/'ch04-v2-phagocytosis.webm'
    assert sha(source)==SOURCE_SHA,'Wrong source AVI'
    probe=json.loads(run('ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(source)))
    assert len(probe['streams'])==1
    stream=probe['streams'][0]
    assert (stream['width'],stream['height'],int(stream['nb_read_frames']),stream['avg_frame_rate'])==(352,305,102,'7/1')
    run('ffmpeg','-v','error','-y','-i',str(source),'-map','0:v:0','-vf','format=rgb24,format=gbrp','-c:v','libvpx-vp9','-lossless','1','-pix_fmt','gbrp','-threads','2','-fflags','+bitexact','-flags:v','+bitexact','-an','-map_metadata','-1',str(delivery))
    original=frames(source);converted=frames(delivery);assert len(original)==102 and original==converted
    source_pts=timestamps(source);delivery_pts=timestamps(delivery)
    errors=[abs(a-b) for a,b in zip(source_pts,delivery_pts)];assert len(source_pts)==len(delivery_pts)==102 and max(errors)<.001
    samples=[]
    for n,clock in [(0,'00:00 min'),(51,'12:49 min'),(101,'25:23 min')]:
        target=A/f'ch04-v2-phagocytosis-frame-{n:03}.png'
        run('ffmpeg','-v','error','-y','-i',str(source),'-vf',f'select=eq(n\\,{n})','-frames:v','1',str(target))
        samples.append({'frame':n,'path':'assets/'+target.name,'sha256':sha(target),'source_clock_read_from_native_sample':clock,'source_file_time_seconds':source_pts[n]})
    (A/'ch04-v2-phagocytosis-poster.png').write_bytes((A/'ch04-v2-phagocytosis-frame-000.png').read_bytes())
    record={'date':'2026-11-10','status':'LOCAL; source/native author review only; actual UI/PDF and distinct independent review pending','article':'https://doi.org/10.1371/journal.pone.0356679','article_date':'2026-10-07','authors':['Celeste Dea','Paula Arias','Sol L. Moroni','Nicolas N. Rolandelli','Arlinet Kierbel'],'supplement':'S8 Video','supplement_doi':'https://doi.org/10.1371/journal.pone.0356679.s010','source_url':'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0356679.s010&type=supplementary','license':'CC BY 4.0, explicitly linked by the owning article; copyright2026Deaet al.','license_url':'https://creativecommons.org/licenses/by/4.0/','source':{'path':'assets/'+source.name,'sha256':SOURCE_SHA,'bytes':source.stat().st_size,'dimensions':[352,305],'frames':102,'fps':'7/1','video_streams':1,'audio_streams':0},'delivery':{'path':'assets/'+delivery.name,'sha256':sha(delivery),'bytes':delivery.stat().st_size,'codec':'VP9 lossless GBR planar','decoded_rgb_frame_md5':original,'source_pts_seconds':source_pts,'delivery_pts_seconds':delivery_pts,'max_timestamp_rounding_seconds':max(errors),'duration_seconds':102/7},'specimen':'RAW264.7 mouse macrophage cell line, PM-GFP plasma-membrane marker; bacteria-associated apoptotic-cell clusters. This is not the separate primary-human-cell experiment in the paper.','colour_key':{'grey':'PM-GFP-associated plasma-membrane signal','green':'Cell Trace-labelled apoptotic material','red':'mCherry-labelled Pseudomonas aeruginosa'},'orientation_scale':'Original optical field and source yellow arrows retained; no metric scale bar visible in inspected source frames, no source-based body axes or pixel calibration assigned.','time':'Time-lapse, not a camera rotation. Three source clocks transcribed in samples. Encoded seven frames/second is playback cadence, not a seven-Hz physiological process. No uniform acquisition interval inferred from export FPS.','limits':'Source-marker signals have finite optical resolution. No nanometre membrane bilayer, receptor, force, exact 3D closure, bacterial killing, general human uptake rate, NET formation or downstream adaptive mechanism is established by this view.','modifications':'Complete102frames converted from raw BGR AVI into RGB-lossless VP9 WebM. Every decoded RGB frame compared exactly. Millisecond container timestamps round by less than0.5ms. No crop, scale, recolouring, contrast change, denoising, new overlay, synthetic intermediate, discarded frames or audio removal (source has no audio).','samples':samples,'print':'Source-limited90mm figure width gives approximately99ppi; no artificial detail added. Intended readability and actual print composition remain pending.','reproduction':{'builder':'figures/ch04_phagocytosis_observed.py','template':'figures/ch04_phagocytosis_observed.template.html','input':'Separately acquired originalAVI retained publicly; exactSHA256 checked.','ffmpeg':run('ffmpeg','-version').decode().splitlines()[0],'ffprobe':run('ffprobe','-version').decode().splitlines()[0],'python':'3 standard library','threads':2,'deterministic_packaging':'FFmpeg bitexact flags, no random or time-dependent parameters'}}
    (A/'ch04-v2-phagocytosis-provenance.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
    (A/'ch04-v2-phagocytosis-observed.html').write_bytes(Path(__file__).with_suffix('.template.html').read_bytes())
    print(json.dumps({'status':'PASS:102sourceRGBframesidentical','samples':3,'max_pts_error_seconds':max(errors)}))
if __name__=='__main__':build()
