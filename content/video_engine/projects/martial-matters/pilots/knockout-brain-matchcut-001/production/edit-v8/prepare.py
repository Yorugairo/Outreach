"""Normal-speed post-freeze opening and user-provided ducked music bed."""
from pathlib import Path
import importlib.util
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
PROJECT=PROD.parent
REPO=next(p for p in HERE.parents if (p/'content/video_engine/scripts/render_episode.py').exists())
FIGHT=PROJECT/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
MUSIC=Path('C:/Users/Snipe/Downloads/Inspired by nang.wav')
WHOOSH=REPO/'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound/fs-whoosh-1-706679.mp3'
spec=importlib.util.spec_from_file_location('media',PROD/'prepare_media.py')
media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)

def ff(args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    media.OUT=HERE
    media.clip('normal-action',FIGHT,0.2,3.3)
    # 56 opening frames + 30 anime frames + 99 original-speed action frames.
    ff(['-i',PROD/'edit-v6/lead.mp4','-i',PROD/'edit-media/anime.mp4','-i',HERE/'normal-action.mp4',
        '-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=30,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[out]',
        '-map','[out]','-frames:v','185','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'hook.mp4'])
    edit=json.loads((PROD/'edit-v7.json').read_text(encoding='utf-8'))
    hook_duration=185/30
    shift=hook_duration-edit['clips'][0]['duration']
    edit['clips'][0].update(path=str(HERE/'hook.mp4'),duration=round(hook_duration,6))
    for clip in edit['clips'][1:]:clip['start']=round(clip['start']+shift,6)
    edit['duration']=round(edit['duration']+shift,6)
    (PROD/'edit-v8.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')
    duration=edit['duration']
    # Rebuild the opener from untouched speech and native-rate fight audio.
    graph=(f'[0:a]atrim=start=6.6,asetpts=PTS-STARTPTS,adelay={round(hook_duration*1000)}|{round(hook_duration*1000)}[tail];'
        '[1:a]aresample=48000,volume=1.8[vo];'
        '[2:a]atrim=start=0.2:end=3.5,asetpts=PTS-STARTPTS,aresample=48000,'
        "volume='if(lt(t,0.633333),0.4,0.85)':eval=frame,adelay=2867|2867[action];"
        '[3:a]atrim=end=0.8,asetpts=PTS-STARTPTS,aresample=48000,volume=0.45,adelay=1900|1900[power];'
        f'[vo][action][power][tail]amix=inputs=4:duration=longest:normalize=0,apad,atrim=end={duration}[out]')
    ff(['-i',PROD/'audio/master-v7.wav','-i',PROD/'audio/verdict-v4.wav','-i',FIGHT,'-i',WHOOSH,
        '-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',HERE/'foreground.wav'])
    # Store the actual music excerpt so rebuilding doesn't depend on Downloads.
    ff(['-i',MUSIC,'-t',duration,'-ar','48000','-ac','2','-c:a','pcm_s16le',HERE/'music-excerpt.wav'])
    mix=(f'[1:a]loudnorm=I=-27:TP=-3:LRA=11,aresample=48000,afade=t=in:st=0:d=0.15,afade=t=out:st={duration-0.5}:d=0.5[music];'
         '[0:a]asplit=2[front][side];'
         '[music][side]sidechaincompress=threshold=0.025:ratio=4:attack=10:release=250[ducked];'
         f'[front][ducked]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.891:level=0,atrim=end={duration}[out]')
    ff(['-i',HERE/'foreground.wav','-i',HERE/'music-excerpt.wav','-filter_complex',mix,'-map','[out]',
        '-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v8.wav'])
    measured=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(PROD/'audio/master-v8.wav')],text=True))
    assert abs(measured-duration)<0.01, (measured,duration)
    proof={'action_start':86/30,'action_source':[0.2,3.5],'action_speed':1.0,'audio_atempo':False,
           'interview_at':hook_duration,'duration':duration,'music_source':str(MUSIC),
           'music_sha256':hashlib.sha256(MUSIC.read_bytes()).hexdigest(),'music_window':[0,duration],
           'music_target_lufs':-27,'ducking':'foreground sidechain 4:1, 10ms attack, 250ms release'}
    (HERE/'timing-audio-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof))

if __name__=='__main__':main()
