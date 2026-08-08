# HyperFrames Unit Lane

*Date: 2026-08-08 · Implements `P13-REMOTION-INSTALL-AND-HYPERFRAMES-LANE.plan.md` · Extends the
renderer-ownership table of `16-EDITORIAL-MOTION-SYSTEM.md` §1 without changing it.*

## 1. Renderer ownership (extended)

| Renderer | Owns |
|---|---|
| **Remotion** (`content/video_engine/editor/`, pinned 4.0.502) | Documentary editorial timeline, layer composition, camera transforms, cuts, captions, citations, canonical narration |
| **HyperFrames** (`content/video_engine/hyperframes/`, pinned 0.7.101) | **Short/caption/motion units**: vertical shorts, title cards, caption units, animatic previews |
| Manim | Exact maps, routes, timelines, relationship diagrams |
| FFmpeg | Media inspection, trimming, encoding, compatibility |

The unit lane obeys the same laws as the documentary lane: contracts are **asset-ID-only**
(no renderer paths), assets bind by sha256 to an approved, rights-reviewed manifest, plates hold
2–6 seconds, and the renderer executes plans — it never invents motion or content.

## 2. Contract and flow

`hyperframes_unit.v1` (`configs/hyperframes_unit.schema.json`) →
`src/services/hyperframes_render.py`:

```
validate (all violations collected)
  → resolve assets (manifest membership + review status + sha256, fail closed)
  → compile deterministic composition HTML (data-* timing from word intervals)
  → hyperframes check (project-pinned CLI, npm-script wrapper contract)
  → hyperframes render -c compositions/unit-<id>.html
  → ffprobe duration vs expected (±2% gate) → summary
```

Operator entry: `python content/video_engine/cli.py render-unit <unit.json> [--dry-run] [--skip-check]`.

## 3. Timing authority per unit kind

| Unit kind | Timing source |
|---|---|
| `vertical_short`, `caption_unit`, `title_card` | **Canonical ElevenLabs word timings only** (hash-bound). None exist yet — paid synthesis remains operator-gated — so these kinds cannot render today by design. |
| `animatic_preview` | Deterministic **estimated** timings (140 wpm) derived from the approved narration source doc; `canonical_hash` binds the source document. Provisional by definition; never publishable. |

## 4. v1 limitations (explicit)

1. **Silent visual builds** — narration audio muxing stays with the compositor/FFmpeg per the
   ownership table; units carry timing, not audio.
2. **Image plates only** (`.jpg/.jpeg/.png/.webp`); motion inside units is composition-level
   (HyperFrames), not generated video.
3. QC (duration drift, output existence, check gate) lives inside the service summary; it is not
   yet merged into `guards/qc_checks.py`.

## 5. Evidence (2026-08-08)

- Editor hardened: typecheck 0 errors; smoke render `editor/out/smoke.mp4` (1.088s, 70,685 B).
- Scaffold: `hyperframes check` — 0 issues across 9 samples, contrast pass.
- First unit: `ep1-teaser-animatic-v1` (vertical, 2 approved episode-1 archive plates, 16
  estimated words, 4 caption groups) → `hyperframes/renders/unit-ep1-teaser-animatic-v1.mp4`,
  actual 6.867s vs expected 6.857s, **drift 0.14%**, check pass, QC pass.
- Tests: `tests/test_hyperframes_render.py` — 11 passed (validation, resolution fail-closed,
  compile determinism, dry-run isolation).

## 6. Port-evaluation spike — status: NOT RUN

The plan's T6 (port `Editorial.tsx` ~15s slice via `/remotion-to-hyperframes`, measure parity +
render time, write keep/migrate/defer verdict) was **deferred, not executed** — the unit lane
proved out without it and the documentary lane needs no migration decision today. Until the
spike runs, the standing verdict is **keep Remotion for the documentary lane**; nothing here
licenses a migration.

## 7. Environment

```
HYPERFRAMES_PROJECT=        # default content/video_engine/hyperframes
HYPERFRAMES_VERSION_PIN=    # default 0.7.101
HYPERFRAMES_TIMEOUT_S=      # default 900
```

`doctor` note: whisper/Kokoro/MusicGen report as missing — all optional local fallbacks this
lane never uses (narration is pipeline-owned; music is compositor-owned). Hard dependencies
(Node ≥22, FFmpeg/FFprobe, Chrome headless) all pass on the verified machine.
