# Source-recovery commands

Recorded 2026-09-20 in the repository checkout. Retrieval was public and
unauthenticated: no account, cookies, paywall bypass, DRM circumvention, or
provider credentials were used. Paths below are relative to this directory.

## Supplied Short

```powershell
python .agents/skills/watch/scripts/setup.py --json
python .agents/skills/watch/scripts/watch.py 'https://youtube.com/shorts/ID0sgoVzFNQ?si=MU3r0VLMpfC8VGyC' --detail balanced --max-frames 40 --resolution 1024 --no-whisper --out-dir 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/watch-pass'
yt-dlp --no-playlist --list-formats 'https://youtube.com/shorts/ID0sgoVzFNQ?si=MU3r0VLMpfC8VGyC'
yt-dlp -N 8 --no-playlist -f '616+251' --merge-output-format mkv --keep-video --write-info-json --write-subs --write-auto-subs --sub-langs 'en.*' --sub-format vtt --convert-subs vtt --no-part -o 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/supplied-short-high.%(ext)s' 'https://youtube.com/shorts/ID0sgoVzFNQ?si=MU3r0VLMpfC8VGyC'
```

`watch.py` downloaded its working copy and frames, then exited while printing
because the Windows cp1252 stdout could not encode the Short title's emoji.
The downloaded files and extracted frames remain in `watch-pass/`; this is a
tool-output limitation, not a source-download success claim for the report.

## Official UFC underlying-bout highlight

The page exposes a public DVE metadata endpoint. The first POST returns an
ephemeral playback URL; the second GET returns the unmodified provider JSON,
which is retained as `ufc-sharaf-steveson-provider.json`. The signed playback
URL is intentionally held in that raw response and not copied into this
command log.

```powershell
$root=(Resolve-Path 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short').Path
$provider=Join-Path $root 'ufc-sharaf-steveson-provider.json'
$tokenUrl=(Invoke-WebRequest -Uri 'https://www.ufc.com/dve.php?vid=1020834' -Method Post -UseBasicParsing -Headers @{'Accept'='text/plain';'Referer'='https://www.ufc.com/video/160276'}).Content.Trim()
$jsonresp=Invoke-WebRequest -Uri $tokenUrl -UseBasicParsing -Headers @{'Accept'='application/json';'Referer'='https://www.ufc.com/video/160276'}
[IO.File]::WriteAllText($provider,$jsonresp.Content,(New-Object Text.UTF8Encoding($false)))
$obj=$jsonresp.Content | ConvertFrom-Json
$hls=$obj.hls.url
yt-dlp -N 8 --no-playlist --merge-output-format mkv --write-info-json --no-part -o ($root+'\ufc-sharaf-steveson-high.%(ext)s') $hls
```

The public page HTML was retained with:

```powershell
Invoke-WebRequest -Uri 'https://www.ufc.com/video/160276' -UseBasicParsing -OutFile 'ufc-video-160276.html'
```

## Probes, contact sheets, and hashes

```powershell
ffprobe -v quiet -print_format json -show_format -show_streams -show_programs -show_chapters -- <media-path>
ffmpeg -hide_banner -loglevel error -y -i supplied-short-high.mkv -vf "fps=2,scale=270:-2,tile=5x10:padding=4:margin=4" -q:v 3 contact_sheets/supplied-short-full-2fps.jpg
ffmpeg -hide_banner -loglevel error -y -ss 13 -to 18.5 -i supplied-short-high.mkv -vf "fps=10,scale=360:-2,tile=10x6:padding=4:margin=4" -q:v 3 contact_sheets/supplied-short-ko-window-13-18p5s.jpg
ffmpeg -hide_banner -loglevel error -y -ss 14.8 -to 17.0 -i supplied-short-high.mkv -vf "fps=20,scale=320:-2,tile=10x5:padding=4:margin=4" -q:v 3 contact_sheets/supplied-short-ko-fine-14p8-17s.jpg
ffmpeg -hide_banner -loglevel error -y -i ufc-sharaf-steveson-high.mkv -vf "fps=2,scale=320:-2,tile=5x10:padding=4:margin=4" -q:v 3 contact_sheets/ufc-sharaf-steveson-full-2fps.jpg
ffmpeg -hide_banner -loglevel error -y -ss 0 -to 5 -i ufc-sharaf-steveson-high.mkv -vf "fps=10,scale=480:-2,tile=10x5:padding=4:margin=4" -q:v 3 contact_sheets/ufc-sharaf-steveson-ko-window-0-5s.jpg
ffmpeg -hide_banner -loglevel error -y -ss 0.4 -to 3.2 -i ufc-sharaf-steveson-high.mkv -vf "fps=20,scale=384:-2,tile=10x6:padding=4:margin=4" -q:v 3 contact_sheets/ufc-sharaf-steveson-ko-fine-0p4-3p2s.jpg
Get-FileHash -Algorithm SHA256 <path>
```
