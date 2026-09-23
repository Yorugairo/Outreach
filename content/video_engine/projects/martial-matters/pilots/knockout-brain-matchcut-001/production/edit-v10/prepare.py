"""Move the existing impact effect onto the first post-interview left hook."""
from pathlib import Path
import json
import subprocess

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
DURATION=17.866667

def ff(args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    # Source frames 13..21 lead directly to the existing source-frame-22 scan.
    ff(['-i',PROD/'edit-v6/follow-up.mp4','-vf','trim=end_frame=9,setpts=PTS-STARTPTS','-an',
        '-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'left-hook-lead.mp4'])
    # Remove only the old 16-frame lead; preserve existing scan, fracture, launch and white exit.
    ff(['-i',PROD/'edit-v5/impact-out.mp4','-vf','trim=start_frame=16,setpts=PTS-STARTPTS','-an',
        '-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'first-left-impact.mp4'])
    edit=json.loads((PROD/'edit-v8.json').read_text(encoding='utf-8'))
    clips=edit['clips'][:2]
    clips += [{'id':'left-hook-lead','path':str(HERE/'left-hook-lead.mp4'),'start':7.6,'duration':0.3},
              {'id':'first-left-impact','path':str(HERE/'first-left-impact.mp4'),'start':7.9,'duration':round(95/30,6)}]
    for clip in edit['clips'][-2:]:
        clip['start']=round(clip['start']-5.8,6)
        clips.append(clip)
    edit.update(clips=clips,duration=DURATION)
    (PROD/'edit-v10.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')
    # Foreground cut only; keep the music continuous instead of splicing its beats.
    gain="if(lt(t,6.0),1,if(lt(t,6.166667),1-0.292054*(t-6.0)/0.166667,if(lt(t,7.6),0.707946,if(lt(t,7.8),0.707946+0.292054*(t-7.6)/0.2,1))))"
    graph=('[0:a]atrim=end=7.9,asetpts=PTS-STARTPTS[a];'
           '[0:a]atrim=start=13.7:end=23.666667,asetpts=PTS-STARTPTS[b];'
           f"[a][b]concat=n=2:v=0:a=1,volume='{gain}':eval=frame[front];"
           f'[1:a]atrim=end={DURATION},asetpts=PTS-STARTPTS,afade=t=out:st={DURATION-0.5}:d=0.5[bed];'
           f'[front][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.891:level=0,atrim=end={DURATION}[out]')
    ff(['-i',PROD/'edit-v8/foreground.wav','-i',PROD/'edit-v9/continuous-bed.wav','-filter_complex',graph,
        '-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v10.wav'])
    measured=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(PROD/'audio/master-v10.wav')],text=True))
    assert abs(measured-DURATION)<0.01,(measured,DURATION)
    proof={'quote_end':7.6,'lead_source_frames':[13,21],'xray_at':7.9,'contact_at':8.6,'brain_launch_at':8.7,
           'hendo_at':round(7.9+95/30,6),'duration':DURATION,'removed':'extra plain follow-up, replay hold, repeated anime buildup',
           'bed':'v9 continuous -30 LUFS target, no sidechain; new end fade'}
    (HERE/'timing-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof))

if __name__=='__main__':main()
