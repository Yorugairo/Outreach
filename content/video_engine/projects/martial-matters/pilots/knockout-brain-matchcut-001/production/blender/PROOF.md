# Knockout brain match-cut — Blender insert

Status: **review-only diagnostic**; `review_state=review_only`; `render_eligible=false`; no publication approval claimed.

## Acceptance

Three seconds at 720x1280 / 30 fps. The camera makes a restrained push while a translucent head/skull silhouette rotates left first; the coral brain visibly lags, overshoots, and performs a second smaller recoil. The insert is non-graphic: no gore, ejection, or medical claim.

Representative frames: `frames/frame-0001.png`, `frames/frame-0024.png`, `frames/frame-0038.png`, `frames/frame-0050.png`, `frames/frame-0090.png`. Structured motion facts are in `state.json`; forward/reverse sample hashes are in `determinism.json`.

## Reproduction

```text
C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python knockout_brain_matchcut.py -- --samples
C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python knockout_brain_matchcut.py -- --render
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration -of json brain-recoil.mp4
```

Build mode: `render`. Reverse-seek sample equality: **True**.

## Custody

The scene is code-authored and source-free. It remains quarantined for operator frame review; the presence of a render is not an approval or a publication claim.

## Movie probe receipt

```json
{
  "path": "brain-recoil.mp4",
  "exists": true,
  "bytes": 970682,
  "ffmpeg_command": "C:\\Users\\Snipe\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.2-full_build\\bin\\ffmpeg.EXE -y -framerate 30 -start_number 1 -i C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\martial-matters\\pilots\\knockout-brain-matchcut-001\\production\\blender\\movie-frames\\frame-%04d.png -frames:v 90 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\martial-matters\\pilots\\knockout-brain-matchcut-001\\production\\blender\\brain-recoil.mp4",
  "ffmpeg_exit": 0,
  "ffmpeg_stderr_tail": "7661), yuv420p(tv, unknown/bt709/iec61966-2-1, progressive), 720x1280 [SAR 1:1 DAR 9:16], q=2-31, 30 fps, 15360 tbn\n    Metadata:\n      encoder         : Lavc62.28.102 libx264\n    Side data:\n      EXIF metadata: (54 bytes)\n      CPB properties: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: N/A\n[mp4 @ 00000215385a5f40] Starting second pass: moving the moov atom to the beginning of the file\n[out#0/mp4 @ 00000215385c2940] video:946KiB audio:0KiB subtitle:0KiB other streams:0KiB global headers:0KiB muxing overhead: 0.200570%\nframe=   90 fps=0.0 q=-1.0 Lsize=     948KiB time=00:00:02.93 bitrate=2647.3kbits/s speed=9.29x elapsed=0:00:00.31    \n[libx264 @ 000002153864c200] frame I:1     Avg QP:15.91  size: 65113\n[libx264 @ 000002153864c200] frame P:25    Avg QP:17.58  size: 22023\n[libx264 @ 000002153864c200] frame B:64    Avg QP:18.97  size:  5506\n[libx264 @ 000002153864c200] consecutive B-frames:  3.3%  4.4%  3.3% 88.9%\n[libx264 @ 000002153864c200] mb I  I16..4: 15.7% 52.4% 31.9%\n[libx264 @ 000002153864c200] mb P  I16..4:  0.3%  1.9%  0.5%  P16..4: 32.3% 14.8% 14.5%  0.0%  0.0%    skip:35.9%\n[libx264 @ 000002153864c200] mb B  I16..4:  0.0%  0.0%  0.0%  B16..8: 51.2%  5.7%  1.1%  direct: 0.9%  skip:41.1%  L0:43.5% L1:48.4% BI: 8.0%\n[libx264 @ 000002153864c200] 8x8 transform intra:59.4% inter:82.3%\n[libx264 @ 000002153864c200] coded y,uvDC,uvAC intra: 71.8% 49.4% 35.7% inter: 16.3% 7.3% 2.4%\n[libx264 @ 000002153864c200] i16 v,h,dc,p: 51% 21% 18% 10%\n[libx264 @ 000002153864c200] i8 v,h,dc,ddl,ddr,vr,hd,vl,hu: 16% 13% 45%  5%  4%  4%  4%  3%  5%\n[libx264 @ 000002153864c200] i4 v,h,dc,ddl,ddr,vr,hd,vl,hu: 28% 17% 18%  7%  6%  5%  8%  5%  6%\n[libx264 @ 000002153864c200] i8c dc,h,v,p: 62% 18% 16%  4%\n[libx264 @ 000002153864c200] Weighted P-Frames: Y:0.0% UV:0.0%\n[libx264 @ 000002153864c200] ref P L0: 57.8%  8.9% 22.0% 11.3%\n[libx264 @ 000002153864c200] ref B L0: 78.2% 17.2%  4.6%\n[libx264 @ 000002153864c200] ref B L1: 90.2%  9.8%\n[libx264 @ 000002153864c200] kb/s:2581.46\n",
  "ffprobe_command": "C:\\Users\\Snipe\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.2-full_build\\bin\\ffprobe.EXE -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration -of json C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\martial-matters\\pilots\\knockout-brain-matchcut-001\\production\\blender\\brain-recoil.mp4",
  "ffprobe_exit": 0,
  "ffprobe": {
    "programs": [],
    "stream_groups": [],
    "streams": [
      {
        "codec_name": "h264",
        "width": 720,
        "height": 1280,
        "r_frame_rate": "30/1",
        "nb_frames": "90"
      }
    ],
    "format": {
      "duration": "3.000000"
    }
  }
}
```
