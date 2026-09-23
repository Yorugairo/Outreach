"""Contact-bound interview interruption; preserve the existing replay tail."""
from pathlib import Path
import importlib.util
import json
import subprocess
import argparse

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
PROJECT=PROD.parent
REPO=next(p for p in HERE.parents if (p/'content/video_engine/scripts/render_episode.py').exists())
WHOOSH=REPO/'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound/fs-whoosh-1-706679.mp3'
FIGHT=PROJECT/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
SHORT=PROJECT/'assets/raw/source-short/supplied-short-high.mkv'
spec=importlib.util.spec_from_file_location('media',PROD/'prepare_media.py')
media=importlib.util.module_from_spec(spec); spec.loader.exec_module(media)

def ff(args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def encode(args,path):
    ff([*args,'-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',path])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--right-end',type=float,required=True)
    parser.add_argument('--news-end',type=float,required=True)
    args=parser.parse_args()
    # The source pre-punch pose occupies the first 0.2s. Slow its movement
    # through 'filed', then hold from 1.2s; anime flash stays at 2.2s.
    layout=media.layout().replace('[0:v]fps=30','[0:v]trim=end=0.3,setpts=6*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc')
    encode(['-i',FIGHT,'-filter_complex',layout+';[v]trim=end_frame=36,tpad=stop_mode=clone:stop_duration=1[out]',
            '-map','[out]','-frames:v','56'],HERE/'lead.mp4')
    # Stretch just this short first impact to let the complete verdict finish.
    hit_frames=20
    hit_duration=hit_frames/30
    speed=(args.right_end-0.2)/hit_duration
    layout=media.layout().replace('[0:v]fps=30',f'[0:v]trim=start=0.2:end={args.right_end},setpts=(PTS-STARTPTS)/{speed},fps=30')
    encode(['-i',FIGHT,'-filter_complex',layout+';[v]tpad=stop_mode=clone:stop_duration=0.1[out]',
            '-map','[out]','-frames:v',str(hit_frames)],HERE/'right.mp4')
    hook_duration=(56+30+hit_frames)/30
    encode(['-i',HERE/'lead.mp4','-i',PROD/'edit-media/anime.mp4','-i',HERE/'right.mp4',
            '-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=30,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[out]',
            '-map','[out]','-frames:v',str(56+30+hit_frames)],HERE/'hook.mp4')
    media.OUT=HERE
    news_duration=round((args.news_end-3.84)*30)/30
    media.clip('news',SHORT,3.84,news_duration,portrait=True,extra=
        'drawbox=x=0:y=65:w=720:h=190:color=black@0.90:t=fill,'+
        media.text('SEAN SHARAF - PRESS CONFERENCE',90,26,'0xffdb4d')+','+
        media.text('2019 SEXUAL-ASSAULT ALLEGATION',142,27)+','+
        media.text('NO CHARGES FILED',189,32,'0xffdb4d')+','+
        'drawbox=x=0:y=1110:w=720:h=80:color=black@0.85:t=fill,'+
        media.text('Hennepin County Attorney / Dec. 2019',1133,23))
    return_duration=round((3.5-args.right_end)*30)/30
    media.clip('follow-up',FIGHT,args.right_end,return_duration)
    edit=json.loads((PROD/'edit-v5.json').read_text(encoding='utf-8'))
    rows=[('hook',HERE/'hook.mp4',hook_duration),('news',HERE/'news.mp4',news_duration),('follow-up',HERE/'follow-up.mp4',return_duration)]
    rows += [(c['id'],Path(c['path']),c['duration']) for c in edit['clips'][3:]]
    at=0; clips=[]
    for name,path,duration in rows:
        clips.append({'id':name,'path':str(path),'start':round(at,6),'duration':round(duration,6)})
        at+=duration
    edit['clips']=clips; edit['duration']=round(at,6)
    (PROD/'edit-v6.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')
    return_at=hook_duration+news_duration
    tail_at=return_at+return_duration
    # Copy the reviewed tail with all its synchronized source audio and cues.
    graph=(f'[0:a]atrim=start=11.6:end=24.6,asetpts=PTS-STARTPTS,adelay={round(tail_at*1000)}|{round(tail_at*1000)}[tail];'
        '[1:a]aresample=48000,volume=1.8[vo];'
        '[4:a]atrim=end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.45,adelay=1900|1900[power];'
        f'[2:a]atrim=start=3.84:end={3.84+news_duration},asetpts=PTS-STARTPTS,aresample=48000,volume=1.0,adelay={round(hook_duration*1000)}|{round(hook_duration*1000)}[news];'
        f'[3:a]atrim=start={args.right_end}:end=3.5,asetpts=PTS-STARTPTS,aresample=48000,volume=0.85,adelay={round(return_at*1000)}|{round(return_at*1000)}[follow];'
        f'[3:a]atrim=start=0.2:end={args.right_end},asetpts=PTS-STARTPTS,aresample=48000,atempo={speed**0.5},atempo={speed**0.5},apad,atrim=end={hit_duration},volume=0.4,adelay=2867|2867[hit];'
        f'[tail][vo][news][follow][hit][power]amix=inputs=6:duration=longest:normalize=0,alimiter=limit=0.891:level=0,apad,atrim=end={at}[out]')
    ff(['-i',PROD/'audio/master-v5.wav','-i',PROD/'audio/verdict-v4.wav','-i',SHORT,'-i',FIGHT,'-i',WHOOSH,
        '-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v6.wav'])
    proof={'freeze_at':1.2,'filed_end':1.197,'anime_flash_at':2.2,'right_source_end':args.right_end,'news_source':[3.84,3.84+news_duration],
           'news_at':hook_duration,'follow_up_at':return_at,'tail_at':tail_at,'duration':at}
    (HERE/'timing-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof))

if __name__=='__main__':main()
