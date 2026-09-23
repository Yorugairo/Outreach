"""Original local cartoon reaction voices; never alters source fight audio."""
import json
import os
import subprocess
from pathlib import Path

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(parents=True, exist_ok=True)
pipe = KPipeline(lang_code='a')
records = []
for name, voice, pitch in [('interviewer-a', 'am_michael', 1.38), ('interviewer-b', 'am_michael', 1.7)]:
    chunks = list(pipe('Oh my God!', voice=voice, speed=0.85))
    samples = np.concatenate([r.audio.numpy() for r in chunks])
    raw = ROOT / f'{name}-raw.wav'
    sf.write(raw, samples, 24000)
    target = ROOT / f'{name}.wav'
    # Original fictional voice sound design, not a real-person impersonation.
    filt = f'silenceremove=start_periods=1:start_threshold=-45dB,asetrate={24000*pitch},aresample=48000,atempo={1/pitch},loudnorm=I=-19:TP=-3:LRA=5,apad,atrim=duration=2.2'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',filt,'-ar','48000',str(target)], check=True)
    records.append({'file':target.name,'voice':voice,'text':'Oh my God!','pitch_factor':pitch,'source_duration':len(samples)/24000,'duration':2.2})
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'interviewer-a.wav'),'-i',str(ROOT/'interviewer-b.wav'),'-filter_complex','[0:a]pan=stereo|c0=0.8*c0|c1=0.4*c0[a];[1:a]adelay=100,pan=stereo|c0=0.4*c0|c1=0.8*c0[b];[a][b]amix=inputs=2:normalize=0,alimiter=limit=0.7:level=0,atrim=duration=2.3[out]','-map','[out]','-ar','48000',str(ROOT/'reaction-duo.wav')], check=True)
(ROOT/'reaction-receipt.json').write_text(json.dumps({'engine':'local Kokoro-82M','status':'private listening proof','actors':'two pitched treatments of one original synthetic voice; no cloning','limitation':'comic pitched speech, not a verified acted scream','stems':records,'mix_duration':2.3},indent=2))
print('Saved reaction-duo.wav and voice stems')
