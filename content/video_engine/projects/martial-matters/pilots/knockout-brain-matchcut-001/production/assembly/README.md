# Knockout Brain Match-Cut assembly

`build_assembly.py` is the only assembly entrypoint. It consumes the
parent-owned `production/edit.json`, `production/audio/master.wav`, and the
canonical intro word clock in `production/audio/intro.words.json`, then
uses the existing scene-evidence compiler/player to produce a split review
build and MP4. The build never edits the raw custody assets or `edit.json`.

The manifest contract is:

```json
{
  "duration": 24.6,
  "clips": [
    {"id": "hook", "path": "production/edit-media/hook.mp4", "start": 0, "duration": 3.5}
  ],
  "captions": [
    {"at": 0, "until": 1.2, "text": "A caption page"}
  ]
}
```

Paths may be absolute (the current parent manifest) or relative to
`production/`. Every clip must be present, contiguous, and end exactly at the
declared duration. The wrapper re-encodes each source to a seekable silent
H.264 clip in `build/clips/`, writes an explicit `exit: "cut"` shot table, and
lets `scene-evidence-engine.mjs` seek the live video at every rendered frame.
Caption pages keep their manifest hold windows, while each spoken word uses
the matching `start_s`/`end_s` pair from `intro.words.json`; this avoids
inventing evenly spaced timings.

Build/compile once the master audio and Blender clip exist:

```powershell
python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/assembly/build_assembly.py `
  --compile
```

Render a private 1080x1920 review MP4:

```powershell
python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/assembly/build_assembly.py `
  --compile --render --workers 1 --output-size 1080x1920 `
  --force "footage-driven portrait review cut; motion gate is not tuned for this lane"
```

Outputs are under `production/assembly/build/`: `player.html`, the compiled
timeline, the split asset map/engine, `render/knockout-brain-matchcut-001-1080x1920.mp4`,
and `ASSEMBLY-RECEIPT.json`.
