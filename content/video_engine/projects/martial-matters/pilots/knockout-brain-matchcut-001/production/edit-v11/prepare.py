"""Existing effect in the opening powered-up exchange; no slowed crowd audio."""
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
spec=importlib.util.spec_from_file_location('media',PROD/'prepare_media.py')
media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)
def ff(args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    media.OUT=HERE
    media.clip('ground-tail',FIGHT,82/30,23/30)
    ff(['-i',PROD/'edit-v6/lead.mp4','-i',PROD/'edit-media/anime.mp4','-i',PROD/'impact-v4/impact-composite.mp4','-i',HERE/'ground-tail.mp4',
        '-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=30,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[3:v]setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0[out]',
        '-map','[out]','-frames:v','220','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'powered-impact-opening.mp4'])
    ff(['-i',PROD/'edit-v6/follow-up.mp4','-vf','fade=t=out:st=2.9:d=0.166667:color=white',
        '-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'plain-follow-up.mp4'])
    edit=json.loads((PROD/'edit-v8.json').read_text(encoding='utf-8'))
    rows=[('hook',HERE/'powered-impact-opening.mp4',220/30),('news',PROD/'edit-v7/quote.mp4',43/30),
          ('follow-up',HERE/'plain-follow-up.mp4',92/30)]
    rows += [(c['id'],Path(c['path']),c['duration']) for c in edit['clips'][-2:]]
    clips=[];at=0
    for name,path,duration in rows:
        clips.append({'id':name,'path':str(path),'start':round(at,6),'duration':round(duration,6)})
        at+=duration
    edit.update(clips=clips,duration=round(at,6))
    (PROD/'edit-v11.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')
    # Narration anchors time zero. Every fight-audio excerpt stays native rate.
    graph=('[0:a]aresample=48000,volume=1.8[vo];'
        '[1:a]atrim=start=0.2:end=0.733333,asetpts=PTS-STARTPTS,aresample=48000,volume=0.4,adelay=2867|2867[lead];'
        '[1:a]atrim=start=0.733333:end=1.1,asetpts=PTS-STARTPTS,aresample=48000,volume=0.32,adelay=4033|4033[contact];'
        '[1:a]atrim=start=1.1:end=3.5,asetpts=PTS-STARTPTS,aresample=48000,volume=0.65,adelay=4933|4933[ground];'
        '[2:a]atrim=start=6.166667:end=7.6,asetpts=PTS-STARTPTS,volume=0.707946,adelay=7333|7333[quote];'
        '[2:a]atrim=start=7.6:end=10.666667,asetpts=PTS-STARTPTS,adelay=8767|8767[follow];'
        '[2:a]atrim=start=16.866667:end=23.666667,asetpts=PTS-STARTPTS,adelay=11833|11833[hendo];'
        '[3:a]atrim=end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.45,adelay=1900|1900[power];'
        '[3:a]atrim=end=1.1,asetpts=PTS-STARTPTS,aresample=48000,volume=0.6,afade=t=out:st=0.6:d=0.5,adelay=3900|3900[flight];'
        '[3:a]atrim=start=0.15:end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.34,afade=t=out:st=0.3:d=0.35,adelay=11533|11533[transition];'
        '[4:a]atrim=end=0.45,asetpts=PTS-STARTPTS,aresample=48000,volume=0.5,afade=t=out:st=0.2:d=0.25,adelay=4100|4100[hit];'
        '[5:a]atrim=end=0.2,asetpts=PTS-STARTPTS,aresample=48000,volume=0.5,adelay=4100|4100[crack];'
        '[5:a]atrim=end=0.2,asetpts=PTS-STARTPTS,aresample=48000,volume=0.55,adelay=4200|4200[launch];'
        f'[6:a]atrim=end={at},asetpts=PTS-STARTPTS,afade=t=out:st={at-0.5}:d=0.5[bed];'
        f'[vo][lead][contact][ground][quote][follow][hendo][power][flight][transition][hit][crack][launch][bed]amix=inputs=14:duration=longest:normalize=0,apad,alimiter=limit=0.891:level=0,atrim=end={at}[out]')
    ff(['-i',PROD/'audio/verdict-v4.wav','-i',FIGHT,'-i',PROD/'edit-v8/foreground.wav',
        '-i',SOUND/'fs-whoosh-1-706679.mp3','-i',SOUND/'fs-whirlpool-537920.mp3','-i',SOUND/'fs-page-stroke-447925.mp3',
        '-i',PROD/'edit-v9/continuous-bed.wav','-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v11.wav'])
    proof={'power_flash':2.2,'effect_lead_at':86/30,'xray_at':3.4,'contact_at':4.1,'brain_launch_at':4.2,
           'ground_tail_source':[82/30,3.5],'quote_at':220/30,'plain_follow_up_at':263/30,'hendo_at':355/30,'duration':at,
           'no_time_stretched_fight_audio':True,'bed':'continuous v9 bed without sidechain'}
    (HERE/'timing-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof))
if __name__=='__main__':main()
