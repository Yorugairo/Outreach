param(
    [string]$OutputPath = (Join-Path $PSScriptRoot 'master.wav')
)

$ErrorActionPreference = 'Stop'

$repoRoot = (git -C $PSScriptRoot rev-parse --show-toplevel).Trim()
$audioDir = $PSScriptRoot
$suppliedShort = Join-Path $repoRoot 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/supplied-short-high.mkv'
$sharafSteveson = Join-Path $repoRoot 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/ufc-sharaf-steveson-high.mkv'
$hendoBisping = Join-Path $repoRoot 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/henderson-bisping/ufc-49967-henderson-bisping-official.mp4'
$swirl = Join-Path $repoRoot 'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound/fs-swirl-in-478722.mp3'
$whirlpool = Join-Path $repoRoot 'content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound/fs-whirlpool-537920.mp3'

foreach ($path in @(
        (Join-Path $audioDir 'intro.wav'),
        (Join-Path $audioDir 'bridge.wav'),
        (Join-Path $audioDir 'outro.wav'),
        $suppliedShort,
        $sharafSteveson,
        $hendoBisping,
        $swirl,
        $whirlpool
    )) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing audio input: $path"
    }
}

$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$filter = @'
[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=2.0,atrim=start=0:end=3.5,asetpts=PTS-STARTPTS[vo_intro];
[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.95,atrim=start=0:end=1.4,asetpts=PTS-STARTPTS,adelay=11600|11600[vo_bridge];
[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.9,atrim=start=0:end=1.1,asetpts=PTS-STARTPTS,adelay=17800|17800[vo_outro];
[3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=3.84:end=8.44,asetpts=PTS-STARTPTS,volume=0.48,adelay=3500|3500[news];
[4:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=0:end=3.5,asetpts=PTS-STARTPTS,volume=0.45,adelay=8100|8100[ko];
[4:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=0.2:end=0.9,asetpts=PTS-STARTPTS,volume=0.45,adelay=14100|14100[official_contact];
[5:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=31.7:end=32.8,asetpts=PTS-STARTPTS,volume=0.27,adelay=17800|17800[hendo_duck];
[5:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=32.8:end=35.9,asetpts=PTS-STARTPTS,volume=0.55,adelay=18900|18900[hendo_main];
[5:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=46.9:end=49.5,asetpts=PTS-STARTPTS,volume=0.55,adelay=22000|22000[hendo_replay];
[6:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=0:end=1.2,asetpts=PTS-STARTPTS,volume=0.7,afade=t=in:st=0:d=0.03,afade=t=out:st=0.9:d=0.3,adelay=12900|12900[anime_cue];
[7:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=0:end=1.0,asetpts=PTS-STARTPTS,volume=0.65,afade=t=in:st=0:d=0.01,afade=t=out:st=0.72:d=0.28,adelay=14400|14400[brain_hit];
[7:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=0:end=1.0,asetpts=PTS-STARTPTS,lowpass=f=900,volume=0.22,aecho=0.8:0.7:650:0.35,apad=pad_dur=3,atrim=end=3.0,afade=t=out:st=1.7:d=1.3,adelay=14800|14800[brain_resonance];
anullsrc=r=48000:cl=stereo:d=24.6[bed];
[bed][vo_intro][news][ko][official_contact][vo_bridge][anime_cue][brain_hit][brain_resonance][hendo_duck][hendo_main][vo_outro][hendo_replay]amix=inputs=13:duration=first:dropout_transition=0:normalize=0,atrim=end=24.6,alimiter=limit=0.891:level=1:attack=5:release=50,aresample=48000[out]
'@

$ffArgs = @(
    '-hide_banner',
    '-loglevel', 'warning',
    '-y',
    '-i', (Join-Path $audioDir 'intro.wav'),
    '-i', (Join-Path $audioDir 'bridge.wav'),
    '-i', (Join-Path $audioDir 'outro.wav'),
    '-i', $suppliedShort,
    '-i', $sharafSteveson,
    '-i', $hendoBisping,
    '-i', $swirl,
    '-i', $whirlpool,
    '-filter_complex', $filter,
    '-map', '[out]',
    '-c:a', 'pcm_s16le',
    '-ar', '48000',
    '-ac', '2',
    $OutputPath
)

& $ffmpeg @ffArgs
if ($LASTEXITCODE -ne 0) {
    throw "ffmpeg failed with exit code $LASTEXITCODE"
}

Write-Host "Built $OutputPath"
