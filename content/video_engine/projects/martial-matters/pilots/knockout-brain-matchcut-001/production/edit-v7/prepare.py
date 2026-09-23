"""Let the opening combination and ground impact finish before the interview."""
from pathlib import Path
import json
import subprocess

HERE=Path(__file__).resolve().parent
PROD=HERE.parent

def ff(args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    edit=json.loads((PROD/'edit-v6.json').read_text(encoding='utf-8'))
    cut=106/30
    extension=92/30
    quote_duration=43/30
    ff(['-i',PROD/'edit-v6/hook.mp4','-i',PROD/'edit-v6/follow-up.mp4',
        '-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[out]',
        '-map','[out]','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',HERE/'hook-complete.mp4'])
    edit['clips'][0]['path']=str(HERE/'hook-complete.mp4')
    edit['clips'][0]['duration']=round(cut+extension,6)
    ff(['-ss','2','-i',PROD/'edit-v6/news.mp4','-frames:v','43','-an','-c:v','libx264',
        '-crf','17','-pix_fmt','yuv420p',HERE/'quote.mp4'])
    edit['clips'][1].update(path=str(HERE/'quote.mp4'),start=round(cut+extension,6),duration=round(quote_duration,6))
    shift=extension+quote_duration-4.5
    for clip in edit['clips'][2:]:clip['start']=round(clip['start']+shift,6)
    edit['duration']=round(edit['duration']+shift,6)
    (PROD/'edit-v7.json').write_text(json.dumps(edit,indent=2),encoding='utf-8')
    fight=PROD.parent/'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
    graph=(f'[0:a]atrim=end={cut},asetpts=PTS-STARTPTS[a];'
           '[1:a]atrim=start=0.433333333333:end=3.5,asetpts=PTS-STARTPTS,aresample=48000,volume=0.85[b];'
           f'[0:a]atrim=start={cut+2}:end={cut+2+quote_duration},asetpts=PTS-STARTPTS,afade=t=out:st=1.413333:d=0.02[c];'
           f'[0:a]atrim=start={cut+4.5},asetpts=PTS-STARTPTS[d];'
           '[a][b][c][d]concat=n=4:v=0:a=1,alimiter=limit=0.891:level=0[out]')
    ff(['-i',PROD/'audio/master-v6.wav','-i',fight,'-filter_complex',graph,'-map','[out]',
        '-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v7.wav'])
    print(json.dumps({'interview_at':cut+extension,'quote_duration':quote_duration,'quote_source':[5.84,5.84+quote_duration],
                      'duration':edit['duration'],'source_continuation':[13/30,3.5]}))

if __name__=='__main__':main()
