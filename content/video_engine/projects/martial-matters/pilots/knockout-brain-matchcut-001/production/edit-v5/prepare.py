"""Verdict-first opener and a brief flash bridge; preserve the v4 action."""
from pathlib import Path
import importlib.util
import json
import subprocess

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
PROJECT=PROD.parent
REPO=next(p for p in HERE.parents if (p/'content/video_engine/scripts/render_episode.py').exists())
SOUND=REPO/'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound'
FIGHT=PROJECT/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
spec=importlib.util.spec_from_file_location('media_base',PROD/'prepare_media.py')
media=importlib.util.module_from_spec(spec); spec.loader.exec_module(media)

def ff(args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def picture():
    # 56 held/pre-punch frames + 30 anime frames + 19 live frames = 3.5s.
    # Existing anime flash is at local 0.333s, hence absolute 2.200s.
    layout=media.layout()
    ff(['-i',FIGHT,'-filter_complex',layout+';[v]trim=end_frame=6,tpad=stop_mode=clone:stop_duration=2[out]',
        '-map','[out]','-frames:v','56','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'hook-lead.mp4'])
    ff(['-ss','0.2','-i',FIGHT,'-filter_complex',layout+';[v]null[out]',
        '-map','[out]','-frames:v','19','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'hook-hit.mp4'])
    ff(['-i',HERE/'hook-lead.mp4','-i',PROD/'edit-media/anime.mp4','-i',HERE/'hook-hit.mp4',
        '-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=30,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[out]',
        '-map','[out]','-frames:v','105','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',HERE/'hook.mp4'])
    ff(['-i',PROD/'impact-v4/impact-composite.mp4','-vf','fade=t=out:st=3.533333:d=0.166667:color=white',
        '-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'impact-out.mp4'])
    ff(['-i',PROD/'edit-media/hendo.mp4','-vf','fade=t=in:st=0:d=0.166667:color=white',
        '-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'hendo-in.mp4'])

def audio():
    graph=("[0:a]volume=enable='between(t,0,3.5)+between(t,8.1,11.6)':volume=0[base];"
        '[1:a]aresample=48000,volume=1.8[hook];'
        '[2:a]atrim=start=8.1:end=11.6,asetpts=PTS-STARTPTS,adelay=8100|8100[restore];'
        '[3:a]atrim=start=0.2:end=0.833333,asetpts=PTS-STARTPTS,aresample=48000,volume=0.40,adelay=2867|2867[punch];'
        '[4:a]atrim=end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.45,adelay=1900|1900[power];'
        '[4:a]atrim=start=0.15:end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.34,afade=t=out:st=0.3:d=0.35,adelay=17500|17500[transition];'
        '[5:a]atrim=end=0.25,asetpts=PTS-STARTPTS,aresample=48000,lowpass=f=1800,volume=0.24,afade=t=out:st=0.05:d=0.2,adelay=17800|17800[land];'
        '[base][hook][restore][punch][power][transition][land]amix=inputs=7:duration=first:normalize=0,alimiter=limit=0.891:level=0,atrim=end=24.6[out]')
    ff(['-i',PROD/'audio/master-v4.wav','-i',PROD/'audio/verdict-v4.wav','-i',PROD/'audio/master.wav',
        '-i',FIGHT,'-i',SOUND/'fs-whoosh-1-706679.mp3','-i',SOUND/'fs-whirlpool-537920.mp3',
        '-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v5.wav'])

def manifest():
    edit=json.loads((PROD/'edit-v4.json').read_text(encoding='utf-8'))
    paths={'hook':HERE/'hook.mp4','impact-head-snap-v4':HERE/'impact-out.mp4','hendo':HERE/'hendo-in.mp4'}
    for clip in edit['clips']:
        if clip['id'] in paths: clip['path']=str(paths[clip['id']])
    edit['captions']=[{'at':0,'until':1.197,'text':'NO CHARGES FILED.'},
        {'at':1.197,'until':2.199,'text':'THEN SHARAF DELIVERED A'},
        {'at':2.199,'until':3.5,'text':'ONE-PUNCH VERDICT.'}]
    (PROD/'edit-v5.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')

if __name__=='__main__':
    HERE.mkdir(exist_ok=True)
    picture(); audio(); manifest()
