"""Replace the frozen effect tail with source-contiguous live footage."""
from pathlib import Path
import importlib.util
import subprocess
import hashlib
import json

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
VIDEO=PROD/'assembly-v11/build/render/knockout-brain-matchcut-001-v11.mp4'
OUT=PROD/'assembly-v12/build/render/knockout-brain-matchcut-001-v12.mp4'
FIGHT=PROD.parent/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
spec=importlib.util.spec_from_file_location('media',PROD/'prepare_media.py')
media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)
def ff(args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    # At Blender output frame90 the source clock should continue from frame60.
    # Output140 at 24fps = 5.833333s; source60..104 lasts 36 delivery frames.
    ff(['-ss','2','-i',FIGHT,'-t','1.5','-filter_complex',media.layout()+';[v]fps=24,scale=1080:1920,setsar=1[out]',
        '-map','[out]','-frames:v','36','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'moving-tail.mp4'])
    graph=('[0:v]split=2[a][b];[a]trim=end_frame=140,setpts=PTS-STARTPTS[head];'
           '[1:v]setpts=PTS-STARTPTS[repair];[b]trim=start_frame=176,setpts=PTS-STARTPTS[rest];'
           '[head][repair][rest]concat=n=3:v=1:a=0[out]')
    ff(['-i',VIDEO,'-i',HERE/'moving-tail.mp4','-filter_complex',graph,'-map','[out]','-map','0:a:0',
        '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',OUT])
    def audio_hash(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
    assert audio_hash(VIDEO)==audio_hash(OUT)
    record={'artifact':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'audio_unchanged':True,
            'repair_interval':[140/24,176/24],'source_interval':[2,3.5],'frames_replaced':36,
            'observed_v11_freeze':[5.875,6.583333]}
    (HERE/'receipt.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))
if __name__=='__main__':main()
