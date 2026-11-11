"""Build the observed axonal-transport lesson from retained source movies.

The source is Sajic et al., PLOS Biology (2013), DOI10.1371/journal.pbio.1001754,
Videos S1 (s004) and S2 (s005), CC BY4.0 as linked by the owning article.
Requires Python3, FFmpeg and ffprobe. No new download or source enhancement.
The explicit palette -> RGB24 -> GBR planar conversion is required: direct
palette -> GBR conversion failed decoded RGB equality and is not used.
"""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
HERE=Path(__file__).with_name('ch23_axonal_observed.template.html')


def run(*args):return subprocess.check_output(args,cwd=ROOT)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    results=[]
    conditions=[('stimulated','S1','s004',80,8,[0,40,79],['0 s','80 s','158 s'],608,129),
                ('resting','S2','s005',50,10,[0,25,49],['0 s','50 s','98 s'],468,131)]
    for condition,label,supp,frame_count,fps,frames,clocks,width,height in conditions:
        source=ASSETS/f'ch23-v2-transport-{condition}-source.avi'
        delivery=ASSETS/f'ch23-v2-transport-{condition}.webm'
        run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-map','0:v:0','-vf','format=rgb24,format=gbrp','-c:v','libvpx-vp9','-lossless','1','-pix_fmt','gbrp','-row-mt','1','-threads','2','-fflags','+bitexact','-flags:v','+bitexact','-an','-map_metadata','-1',str(delivery))
        decoded=[]
        for path in [source,delivery]:
            lines=run('ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-map','0:v:0','-vf','format=rgb24','-f','framemd5','-').splitlines()
            decoded.append([line.split(b',')[-1].strip().decode() for line in lines if line and not line.startswith(b'#')])
        assert len(decoded[0])==frame_count and decoded[0]==decoded[1],condition
        for i,frame in enumerate(frames):
            png=ASSETS/f'ch23-v2-transport-{condition}-frame-{frame:03d}.png'
            run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(png))
            if i==0:(ASSETS/f'ch23-v2-transport-{condition}-poster.png').write_bytes(png.read_bytes())
        probe=json.loads(run('ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)))
        results.append({'condition':condition,'supplement':'Video '+label,'supplement_id':supp,'supplement_url':'https://doi.org/10.1371/journal.pbio.1001754.'+supp,'source_file':source.name,'source_sha256':sha(source),'delivery_file':delivery.name,'delivery_sha256':sha(delivery),'native_dimensions':[width,height],'frames':frame_count,'file_fps':fps,'file_duration_seconds':frame_count/fps,'sampled_frames':frames,'visually_read_source_clocks':clocks,'decoded_rgb_frames_identical':True,'decoded_rgb_frame_md5':decoded[0]})
    record={'date':'2026-11-09','status':'LOCAL PRODUCTION; browser/native playback and final rubric acceptance pending','title':'Observed mitochondrial transport in adult mouse peripheral axons','authors':['Marija Sajic','Vincenzo Mastrolia','Chao Yu Lee','Diogo Trigo','Mona Sadeghian','Angelina J. Mosley','Norman A. Gregson','Michael R. Duchen','Kenneth J. Smith'],'article':'https://doi.org/10.1371/journal.pbio.1001754','publication_date':'2013-12-31','license':'CC BY4.0, the version explicitly linked by the owning article as accessed','license_url':'https://creativecommons.org/licenses/by/4.0/','source_context':'In vivo exposed/de-sheathed saphenous nerves of anaesthetised adult mice, mitochondria labelled with TMRM. VideoS1:50Hz proximal electrical stimulation with distal compound action-potential recording. VideoS2:naive animal without deliberate electrical stimulation. Independent examples, not a matched before/after pair.','appearance':'VideoS1 is a grayscale fluorescence export with the original arrow and clock; VideoS2 is a red-channel fluorescence export with original10µm bar and clock. These are modality/false-colour signals, not natural tissue colour.','orientation':'Foot/distal direction is right according to the source captions; proximal direction is left. No soma, terminal or entire nerve length is visible. No new metric bar is assigned to VideoS1.','time':'Source clocks visibly read0,80,158seconds atS1frames0,40,79 and0,50,98seconds atS2frames0,25,49. The article Methods reports1.97s per acquired frame; the export clocks round to2s increments. Controls expose encoded-file time, not exact acquisition time. At1x encoded playback, the rounded source clocks advance approximately16x(S1) or20x(S2).','modifications':'Full uncut source frames re-encoded into VP9 lossless RGB, with exact equality of every decoded RGB frame verified. No crop, scale, contrast change, retiming, synthetic interpolation, annotation, denoising or discarded frames. Three native PNG samples and a first-frame poster extracted from each original AVI.','teaching_scope':'Compare stationary and moving organelles and distinguish cargo movement from an electrical impulse. The movies do not resolve microtubule motors, prove every bright profile identity without source labelling, measure human physiology, show a voltage waveform or establish population statistics from these two examples.','print_resolution_exception':'Native movie fields608x129 and468x131pixels are preserved. Print panels may use a source-limited150mm width for legibility, approximately103and79ppi respectively; no invented upscaling/detail. External frame/clock labels remain text. Native PNG/full movie access provides the original pixels. Actual print-layout inspection is pending.','reproduction':{'script':'figures/ch23_axonal_observed.py','template':'figures/ch23_axonal_observed.template.html','dependencies':['Python3 standard library','FFmpeg with libvpx-vp9','ffprobe'],'inputs':'Retained original AVI files; no network reacquisition occurs during build.','tool_versions':{'ffmpeg':run('ffmpeg','-version').decode().splitlines()[0],'ffprobe':run('ffprobe','-version').decode().splitlines()[0]}},'conditions':results}
    (ASSETS/'ch23-v2-transport-provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
    (ASSETS/'ch23-v2-axonal-transport.html').write_bytes(HERE.read_bytes())
    print(json.dumps({'conditions':len(results),'identical_rgb_frames':sum(r['frames'] for r in results),'status':record['status']},indent=2))

if __name__=='__main__':build()
