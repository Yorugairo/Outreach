"""Versioned edit/audio integration for resumed footage and snap-timed ejection."""
from pathlib import Path
import subprocess
import json
import sys

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
PROJECT=PROD.parent
REPO=next(p for p in HERE.parents if (p/'content/video_engine/scripts/render_episode.py').exists())
SOUND=REPO/'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound'
FIGHT=PROJECT/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'

def ff(args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def audio():
    graph=("[0:a]volume=enable='between(t,14.1,17.8)':volume=0,volume=enable='between(t,8.1,11.6)':volume=0.18[base];"
      '[1:a]atrim=start=0.2:end=0.733333,asetpts=PTS-STARTPTS,aresample=48000,volume=.4,adelay=14100|14100[lead];'
      '[1:a]atrim=start=0.733333:end=1.066667,asetpts=PTS-STARTPTS,atempo=.5,atempo=.666667,aresample=48000,volume=.32,adelay=15133|15133[slow];'
      '[1:a]atrim=start=1.1:end=2.733333,asetpts=PTS-STARTPTS,aresample=48000,volume=.32,adelay=16167|16167[tail];'
      '[2:a]atrim=end=.45,asetpts=PTS-STARTPTS,asetrate=48000*.62,aresample=48000,lowpass=f=2600,volume=.6,afade=t=out:st=.25:d=.45,adelay=15333|15333[hit];'
      '[3:a]atrim=end=.19,asetpts=PTS-STARTPTS,asetrate=48000*.75,aresample=48000,volume=.48,adelay=15333|15333[crack];'
      '[3:a]atrim=end=.20,asetpts=PTS-STARTPTS,asetrate=48000*.5,aresample=48000,volume=.55,adelay=15433|15433[break];'
      '[4:a]atrim=end=1.1,asetpts=PTS-STARTPTS,aresample=48000,volume=.6,afade=t=out:st=.6:d=.5,adelay=15133|15133[flight];'
      '[5:a]aresample=48000,volume=1.8,adelay=8100|8100[verdict];'
      '[base][lead][slow][tail][hit][crack][break][flight][verdict]amix=inputs=9:duration=first:normalize=0,alimiter=limit=.891:level=0,atrim=end=24.6[out]')
    graph=graph.replace('=.','=0.')
    ff(['-i',PROD/'audio/master.wav','-i',FIGHT,'-i',SOUND/'fs-whirlpool-537920.mp3',
        '-i',SOUND/'fs-page-stroke-447925.mp3','-i',SOUND/'fs-whoosh-1-706679.mp3',
        '-i',PROD/'audio/verdict-v4.wav','-filter_complex',graph,'-map','[out]',
        '-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v4.wav'])

def picture():
    ff(['-i',PROD/'impact-v2/live-impact-lead.mp4','-i',HERE/'xray-impact.mp4',
        '-filter_complex','[0:v]setpts=PTS-STARTPTS,setsar=1[a];[1:v]setpts=PTS-STARTPTS,setsar=1[b];[a][b]concat=n=2:v=1:a=0[out]',
        '-map','[out]','-frames:v','111','-an','-c:v','libx264','-preset','fast','-crf','17',
        '-pix_fmt','yuv420p','-movflags','+faststart',HERE/'impact-composite.mp4'])

def manifest():
    edit=json.loads((PROD/'edit-v2.json').read_text(encoding='utf-8'))
    for clip in edit['clips']:
        if clip['id']=='impact-xray-v2':
            clip.update(id='impact-head-snap-v4',path=str(HERE/'impact-composite.mp4'))
    (PROD/'edit-v4.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')

if __name__=='__main__':
    manifest()
    if '--audio' in sys.argv: audio()
    if '--picture' in sys.argv: picture()
