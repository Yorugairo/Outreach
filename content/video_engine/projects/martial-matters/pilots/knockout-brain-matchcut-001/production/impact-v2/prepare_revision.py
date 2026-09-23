"""Prepare the continuous replay effect and its audio for the existing player."""
from pathlib import Path
import argparse
import json
import subprocess

HERE = Path(__file__).resolve().parent
PRODUCTION = HERE.parent
PROJECT = PRODUCTION.parent
REPO = next(p for p in HERE.parents if (p/'content/video_engine/scripts/render_episode.py').exists())
FIGHT = PROJECT/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
SOUND = REPO/'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound'

def run(args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

def edit_manifest():
    edit=json.loads((PRODUCTION/'edit.json').read_text(encoding='utf-8'))
    edit['clips']=[c for c in edit['clips'] if c['id']!='brain']
    for clip in edit['clips']:
        if clip['id']=='impact':
            clip.update(id='impact-xray-v2',path=str(HERE/'impact-composite.mp4'),duration=3.7)
    (PRODUCTION/'edit-v2.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')

def picture():
    lead=HERE/'live-impact-lead.mp4'
    effect=HERE/'motion/xray-impact.mp4'
    if not effect.is_file(): raise FileNotFoundError(effect)
    layout=('[0:v]fps=30,split=2[bg][fg];'
            '[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,gblur=sigma=34,eq=brightness=-0.20:saturation=0.6[b];'
            '[fg]scale=960:540,crop=720:540:(iw-ow)/2:0[f];'
            '[b][f]overlay=0:350,setsar=1[out]')
    run(['-ss','0.2','-i',FIGHT,'-filter_complex',layout,'-map','[out]','-frames:v','16','-an',
         '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',lead])
    run(['-i',lead,'-i',effect,'-filter_complex',
         '[0:v]setpts=PTS-STARTPTS,setsar=1[a];[1:v]setpts=PTS-STARTPTS,setsar=1[b];[a][b]concat=n=2:v=1:a=0[out]',
         '-map','[out]','-frames:v','111','-an','-c:v','libx264','-preset','fast','-crf','17',
         '-pix_fmt','yuv420p','-movflags','+faststart',HERE/'impact-composite.mp4'])

def audio():
    # Keep all approved edit timing outside the replaced impact sequence.
    # CC0 chalk is layered as short dry crack transients; CC0 whoosh carries flight.
    f=("[0:a]volume=enable='between(t,14.1,17.8)':volume=0[base];"
       '[1:a]atrim=start=0.2:end=0.733333,asetpts=PTS-STARTPTS,aresample=48000,volume=0.45,afade=t=out:st=0.49:d=0.0433,adelay=14100|14100[live];'
       '[2:a]atrim=end=0.45,asetpts=PTS-STARTPTS,asetrate=48000*0.62,aresample=48000,lowpass=f=2600,volume=0.65,afade=t=out:st=0.25:d=0.45,adelay=14633|14633[hit];'
       '[3:a]atrim=end=0.19,asetpts=PTS-STARTPTS,asetrate=48000*0.75,aresample=48000,volume=0.48,adelay=15433|15433[crack1];'
       '[3:a]atrim=end=0.16,asetpts=PTS-STARTPTS,asetrate=48000*1.35,aresample=48000,volume=0.28,adelay=15683|15683[crack2];'
       '[3:a]atrim=end=0.20,asetpts=PTS-STARTPTS,asetrate=48000*0.5,aresample=48000,volume=0.55,adelay=16083|16083[break];'
       '[4:a]atrim=end=1.1,asetpts=PTS-STARTPTS,aresample=48000,volume=0.65,afade=t=out:st=0.6:d=0.5,adelay=15783|15783[flight];'
       '[base][live][hit][crack1][crack2][break][flight]amix=inputs=7:duration=first:normalize=0,alimiter=limit=0.891:level=0,atrim=end=24.6[out]')
    run(['-i',PRODUCTION/'audio/master.wav','-i',FIGHT,'-i',SOUND/'fs-whirlpool-537920.mp3',
         '-i',SOUND/'fs-page-stroke-447925.mp3','-i',SOUND/'fs-whoosh-1-706679.mp3',
         '-filter_complex',f,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',PRODUCTION/'audio/master-v2.wav'])

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--picture',action='store_true')
    ap.add_argument('--audio',action='store_true')
    args=ap.parse_args()
    edit_manifest()
    if args.audio: audio()
    if args.picture: picture()
