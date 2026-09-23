# Private-package command references

These are the existing commands for a future private package. They are reference-only; no authoring, voice, alignment, or render command in this file was run for this baseline.

From the repository root in PowerShell:

```powershell
$PRIVATE_PROJECT = "C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\normal-for-which-bridge\package-2026-09-15"
$PRIVATE_BUILD = "$PRIVATE_PROJECT\build-private-2026-09-15"
$ENGINE = "content\video_engine\scripts"
```

Scratch voice lane (both engines, then local Whisper alignment):

```powershell
python "$ENGINE\scratch_take.py" --engine both --script "$PRIVATE_PROJECT\SCRIPT-SHORT-VO.txt" --out "$PRIVATE_PROJECT\vo-short\scratch"
python "$ENGINE\align_take_whisper.py" "$PRIVATE_PROJECT\SCRIPT-SHORT-VO.txt" "$PRIVATE_PROJECT\vo-short\scratch\scratch-chirp.mp3" "$PRIVATE_PROJECT\vo-short\audio\scene_1.words.json"
```

Recorded voice and retime commands, if the operator selects that lane:

```powershell
python "$ENGINE\record_short_take.py" "$PRIVATE_PROJECT\SCRIPT-SHORT-VO.txt" --out "$PRIVATE_PROJECT\vo-short\audio" --go
python "$ENGINE\retime_take.py" "$PRIVATE_PROJECT\vo-short\audio\scene_1.mp3" --gaps --out "$PRIVATE_PROJECT\vo-short\audio\scene_1-retimed"
```

Authoring command after the build script itself has been copied into the private package (the source-door script is unsafe because it writes the original project SHOT-TABLE and sound plan regardless of BRIDGE_BUILD_DIR):

```powershell
$env:BRIDGE_BUILD_DIR = "build-private-2026-09-15"
$env:SELF_WATCH = "0"
python "$PRIVATE_PROJECT\build_short.py"
```

Private render command:

```powershell
python "$ENGINE\serve_player.py" "$PRIVATE_BUILD" --port 87XX
$env:RENDER_ASPECT = "9:16"
$env:RENDER_BUILD = $PRIVATE_BUILD
$env:RENDER_URL = "http://127.0.0.1:87XX/player.html"
$env:RENDER_NAME = "normal-for-which-bridge-2026-09-15"
python "$ENGINE\render_episode.py" --test
python "$ENGINE\render_episode.py"
```

The baseline used only the existing local probe, motion, floor, and self-watch commands captured in RUN-SUMMARY.tsv; it rendered nothing.
