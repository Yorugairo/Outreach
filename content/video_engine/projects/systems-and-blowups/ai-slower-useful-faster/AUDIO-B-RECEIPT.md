# Audio B preparation receipt — pending blind-viewer clearance

Status: PREPARED ONLY. No synthesis, alignment, tempo edit, network call, or
audio overwrite was run in this task. The parent must confirm the blind-viewer
pass before running the commands below.

## Reflowed payload

- Source: `SCRIPT-B-VO.txt` (latest B script; gate hash `c30f08af1ee69f5ceb4240d49e422ce233b528650103746597316f690647ea68`).
- Payload: `scratch-b/SCRIPT-B-REFLOWED.txt`.
- Beat tags stripped; punctuation preserved; one movement paragraph.
- Normalized spoken SHA-256 (source and payload): `c30f08af1ee69f5ceb4240d49e422ce233b528650103746597316f690647ea68`.
- Verification: equal normalized payloads, one paragraph, zero tags. The gate's
  current script token count remains the authority for authoring; this receipt
  does not rewrite the display script.

## Commands — do not run until parent clearance

Run from the repository root. Separate output directories keep the raw voice
renders independent and reversible.

```powershell
python content/video_engine/scripts/scratch_take.py --engine chirp --script content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/SCRIPT-B-REFLOWED.txt --out content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-chirp-r1p00 --rate 1.0
python content/video_engine/scripts/scratch_take.py --engine kokoro --script content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/SCRIPT-B-REFLOWED.txt --out content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-kokoro-r1p00 --rate 1.0

python content/video_engine/scripts/align_take.py content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-chirp-r1p00/scratch-chirp.mp3 --out content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-chirp-r1p00/scratch-chirp.words.json --script content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/SCRIPT-B-REFLOWED.txt --model small.en --engine chirp

python content/video_engine/scripts/retime_take.py content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-chirp-r1p00/scratch-chirp.mp3 --gaps --tempo 1.10 --out scratch-chirp-gaps-r1p10
python content/video_engine/scripts/retime_take.py content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/scratch-b/raw-kokoro-r1p00/scratch-kokoro.mp3 --gaps --tempo 1.10 --out scratch-kokoro-gaps-r1p10
```

`scratch_take.py` writes Kokoro's own words sidecar; only the Chirp take needs
the local `align_take.py --script` forced alignment. `retime_take.py --out`
uses a new stem in the input directory, preserving each raw MP3 and sidecar.
The 1.10 candidate is reversible and must be selected against the printed raw
WPM; 1.08 or 1.12 may be substituted to land the measured 180–195 WPM target.

## Requirements / gates

- Chirp: `GEMINI_TTS_API_KEY` in `docs/local.env`; this is the only networked
  call and remains pending clearance.
- Kokoro: installed local `kokoro`, `numpy`, and `soundfile`.
- Forced alignment: local `faster-whisper` (`small.en`); no paid/cloud STT.
- Both voices: `ffmpeg`/`ffprobe`.
- After any candidate is made: inspect duration, final-word coverage, and ear-
  review before any downstream build. No YouTube voice approval is implied;
  E70 leaves YouTube voice OPEN.
