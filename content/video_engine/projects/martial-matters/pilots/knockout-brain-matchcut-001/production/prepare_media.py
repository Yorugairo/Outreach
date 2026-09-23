"""Prepare editorial source windows and a modular anime effect for engine assembly."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
OUT = ROOT / 'edit-media'
OUT.mkdir(exist_ok=True)
FIGHT = PROJECT / 'assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
SHORT = PROJECT / 'assets/raw/source-short/supplied-short-high.mkv'
HENDO = PROJECT / 'assets/raw/henderson-bisping/ufc-49967-henderson-bisping-official.mp4'
FONT = "C\\:/Windows/Fonts/arialbd.ttf"

def run(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *map(str,args)], check=True)

def text(value, y, size=38, color='white'):
    return f"drawtext=fontfile='{FONT}':text='{value}':fontsize={size}:fontcolor={color}:x=(w-text_w)/2:y={y}:shadowcolor=black:shadowx=2:shadowy=3"

def layout(portrait=False):
    if portrait:
        return '[0:v]fps=30,scale=720:1280,setsar=1[v]'
    # Keep both fighters and the contact point. Portrait background extends the arena.
    return ('[0:v]fps=30,split=2[bg][fg];'
            '[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,gblur=sigma=34,eq=brightness=-0.20:saturation=0.6[b];'
            '[fg]scale=960:540,crop=720:540:(iw-ow)/2:0[f];'
            '[b][f]overlay=0:350,setsar=1[v]')

def clip(name, source, start, duration, title='', subtitle='', portrait=False, extra=''):
    filters=layout(portrait)
    overlays=[]
    if title: overlays.append(text(title,165,43,'0xffdb4d'))
    if subtitle: overlays.append(text(subtitle,225,28))
    if extra: overlays.append(extra)
    if overlays: filters += ';[v]'+','.join(overlays)+'[out]'
    else: filters += ';[v]null[out]'
    path=OUT/f'{name}.mp4'
    run(['-ss',start,'-i',source,'-t',duration,'-filter_complex',filters,'-map','[out]','-an',
         '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','30','-movflags','+faststart',path])
    return path

def anime():
    # Transform matched source pose through a six-frame light bloom; all motion deterministic.
    duration=1.2
    filt=('[0:v]scale=1920:1080,fps=30,format=yuv420p[a];'
          '[1:v]scale=1920:1080,fps=30,format=yuv420p[b];'
          '[a][b]xfade=transition=fade:duration=0.2:offset=0.24,'
          "eq=brightness='0.20*exp(-pow((t-0.36)/0.085,2))':eval=frame,"
          "zoompan=z='1+0.055*on/36':x='iw/2-iw/zoom/2+3*sin(on*2)':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=30,"
          'split=2[bg][fg];'
          '[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,gblur=sigma=34,eq=brightness=-0.25[bkg];'
          '[fg]scale=960:540,crop=720:540:120:0[hero];'
          '[bkg][hero]overlay=0:350,'+text('ONE PUNCH MODE',170,45,'0xffdb4d')+','+
          text('ANIME REPLAY',236,24)+
          ",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.5:t=fill:enable='between(t,0.333,0.367)'[out]")
    run(['-loop','1','-i',ROOT/'anime/pre-punch.png','-loop','1','-i',ROOT/'anime/saitama-transform.png',
         '-filter_complex',filt,'-map','[out]','-t',duration,'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',OUT/'anime.mp4'])

def main():
    clip('hook',FIGHT,5.0,3.5,'10 SECONDS.','SHARAF vs STEVESON')
    # Original source captions are retained as a quote, attribution precedes the accusation.
    clip('news',SHORT,3.84,4.6,portrait=True,extra=
         'drawbox=x=0:y=65:w=720:h=190:color=black@0.90:t=fill,'+
         text('SEAN SHARAF - PRESS CONFERENCE',90,26,'0xffdb4d')+','+
         text('2019 SEXUAL-ASSAULT ALLEGATION',142,27)+','+
         text('NO CHARGES FILED',189,32,'0xffdb4d')+','+
         'drawbox=x=0:y=1110:w=720:h=80:color=black@0.85:t=fill,'+
         text('Hennepin County Attorney / Dec. 2019',1133,23))
    clip('knockout',FIGHT,0,3.5,'THEN THE BELL.','SEAN SHARAF vs GABLE STEVESON')
    clip('replay',FIGHT,0,0.2,'WATCH THAT AGAIN.','')
    run(['-i',OUT/'replay.mp4','-vf','tpad=stop_mode=clone:stop_duration=1.1','-t','1.3','-an',
         '-c:v','libx264','-crf','18',OUT/'replay-hold.mp4'])
    anime()
    clip('impact',FIGHT,0.2,0.7,'ONE PUNCH.','',extra="eq=contrast=1.09:saturation=0.9")
    clip('hendo',HENDO,31.7,4.2,'LOOK FAMILIAR?','HENDERSON vs BISPING / UFC 100')
    clip('hendo-replay',HENDO,46.9,2.6,'THE H-BOMB.','HENDERSON vs BISPING / REPLAY')
    rows=[('hook',3.5),('news',4.6),('knockout',3.5),('replay-hold',1.3),('anime',1.2),('impact',0.7),
          ('brain',3.0),('hendo',4.2),('hendo-replay',2.6)]
    at=0
    manifest=[]
    for name,duration in rows:
        path=ROOT/'blender/brain-recoil.mp4' if name=='brain' else OUT/f'{name}.mp4'
        manifest.append({'id':name,'path':str(path),'start':round(at,3),'duration':duration})
        at+=duration
    captions=[{'at':1.288,'until':1.975,'text':'SEAN SHARAF'},
              {'at':1.975,'until':3.3,'text':'SHUTS THE LIGHTS OUT.'}]
    (ROOT/'edit.json').write_text(json.dumps({'duration':round(at,3),'clips':manifest,'captions':captions},indent=2),encoding='utf-8')
    print(json.dumps({'duration':at,'manifest':str(ROOT/'edit.json')}))

if __name__=='__main__': main()
