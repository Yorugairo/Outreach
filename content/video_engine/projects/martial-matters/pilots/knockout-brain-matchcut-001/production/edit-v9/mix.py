"""Lower continuous bed, no speech-triggered pumping; preserve exact v8 video."""
from pathlib import Path
import subprocess
import hashlib
import json

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
OUT=PROD/'assembly-v9/build/render/knockout-brain-matchcut-001-v9.mp4'
VIDEO=PROD/'assembly-v8/build/render/knockout-brain-matchcut-001-v8.mp4'
DURATION=23.666667

def ff(args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    # Modest dynamics control on the music itself, never triggered by speech.
    ff(['-i',PROD/'edit-v8/music-excerpt.wav','-af',
        f'acompressor=threshold=0.1:ratio=2:attack=50:release=500,loudnorm=I=-30:TP=-6:LRA=7,aresample=48000,afade=t=in:st=0:d=0.15,afade=t=out:st={DURATION-0.5}:d=0.5',
        '-ar','48000','-ac','2','-c:a','pcm_s16le',HERE/'continuous-bed.wav'])
    # Ease the interview down by 3dB with ramps either side of its boundaries.
    gain="if(lt(t,6.0),1,if(lt(t,6.166667),1-0.292054*(t-6.0)/0.166667,if(lt(t,7.6),0.707946,if(lt(t,7.8),0.707946+0.292054*(t-7.6)/0.2,1))))"
    graph=(f"[0:a]volume='{gain}':eval=frame[front];"
           f'[front][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.891:level=0,atrim=end={DURATION}[out]')
    ff(['-i',PROD/'edit-v8/foreground.wav','-i',HERE/'continuous-bed.wav','-filter_complex',graph,'-map','[out]',
        '-ar','48000','-ac','2','-c:a','pcm_s16le',PROD/'audio/master-v9.wav'])
    ff(['-i',VIDEO,'-i',PROD/'audio/master-v9.wav','-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT])
    # Encoded video stream hash proves that picture timing and frames did not change.
    def video_hash(path):
        return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
    before=video_hash(VIDEO);after=video_hash(OUT)
    assert before==after,(before,after)
    record={'artifact':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
            'video_hash':after,'video_unchanged':True,'bed_lufs_target':-30,'speech_sidechain':False,
            'interview_gain_db':-3,'duration':DURATION}
    (HERE/'receipt.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))

if __name__=='__main__':main()
