# Knockout Brain Match-Cut v2 assembly

`build_assembly_v2.py` is an isolated adapter around the reviewed v1 assembly
builder. It reads parent-owned `production/edit-v2.json` and
`production/audio/master-v2.wav`, preserves the measured intro word clock, and
writes only below `production/assembly-v2/build/`. The original
`production/assembly/` build and MP4 are not touched.

The v2 edit contract keeps the 24.6s hard-cut timeline but replaces the
standalone 14.8–17.8s brain diagram with one parent-produced
`impact-v2/impact-composite.mp4` clip spanning the merged 14.1–17.8s window:
0.55s live punch lead followed by 3.15s of continuous X-ray freeze, fracture,
and brain-offscreen motion. The engine still embeds each clip as a live
`clip:<path>` world and uses authored `exit: "cut"` rows.

Do not render until the parent has landed `edit-v2.json`, `master-v2.wav`, and
`impact-v2/impact-composite.mp4`:

```powershell
python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/assembly-v2/build_assembly_v2.py `
  --compile --render --workers 2 --output-size 1080x1920 `
  --force "M11: footage-only v2 has no chart/data dock; M16: current gate does not count clip-world frame motion across hard-cut spans; review-only"
```

The distinct final artifact is
`production/assembly-v2/build/render/knockout-brain-matchcut-001-v2.mp4`.
