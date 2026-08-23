# Interactive Remotion Production Editor

Local, loopback-only timeline and canvas editor for evidence-aware Remotion
episodes. The browser edits a typed draft; the bridge validates immutable,
hash-bound revisions and recompiles them without changing narration, transcript,
source media, evidence approval, or prior revisions.

## Run locally

```powershell
npm ci
npm run typecheck
npm run test
npm run build
```

Start the Python `production-console` bridge on `127.0.0.1:4317`. The built
console is served by that bridge; Vite development mode also remains loopback
only and proxies `/api` and opaque `/media/<asset-id>` requests.

## Editing model

- Timeline: seek or scrub the ruler, zoom, drag/trim editable blocks, and use
  scene buttons to focus the episode. Hold `Alt` while releasing a drag to
  bypass snapping.
- Canvas: click or shift-click an item, then drag, resize, or rotate it. The
  inspector exposes crop/focal point, opacity, layer, text, caption layout,
  narration trim/volume, and approved keyframe controls.
- Palette: insert approved evidence, overlay text, annotations, the approved
  teacher stamp, or one of the eleven reviewed Remotion Bits.
- History: `Ctrl/Cmd+Z`, `Ctrl/Cmd+Shift+Z` or `Ctrl/Cmd+Y`; history is capped at
  100 committed commands. Pointer gestures commit once on release.
- Selection: `Escape` clears selection. Arrow keys nudge one pixel; hold `Shift` for ten. `Ctrl/Cmd+D`
  duplicates and `Delete` removes an editable item. Toolbar actions align or
  distribute multi-selection.
- Playback: `Space` toggles play/pause. Frame updates move the playhead
  imperatively; application state is updated on seek and pause.

## Evidence-rail grammar

PowerPoint and NotebookLM-derived visuals are evidence objects, never the hero
composition. Keep the woodblock world plate full-frame and use this sequence:

`world plate → hand opens one evidence slot → source appears → leader line connects it to the world → evidence retracts → world continues`

The clutter budget is one world plate, one active evidence crop, one photographed
marker hand only during reveal, one short leader/annotation, and one small source
marker. Prefer hash-bound semantic crops over miniature full slides. On
`memory-skepticism-v2`, the teal, navy, and orange bottom cards form a sequential
evidence rail; conflicting rail overlays are removed and the immutable caption is
moved to the upper-left. On `hero-fab-constraint-v1`, use one off-center field note
anchored to a manufacturing station and retract it before the next fact.

## Drafts and immutable revisions

Uncommitted drafts are stored locally by project ID and base snapshot hash. A
draft with a stale base hash is quarantined and can be exported before clearing.
Saving creates an `editorial_timeline_revision.v1`; the server validates and
replays every operation, then writes a new runtime directory containing the
revision, replayed timeline, scene/cue ranges, and the exact
`ProductionTimeline` render props used by the Player.

Revisions fail closed for stale hashes, unknown assets/components, unsafe
paths, protected transcript or approval changes, invalid ranges, narration cuts
through spoken words, unsupported props, or malformed keyframes.

## Remotion Bits intake

The runtime pins `remotion-bits@0.2.0`. The browser never downloads or executes
third-party code. Eleven reviewed adapters are enabled; an enable request for
the remaining catalog downloads a local review artifact. New source requires
license, dependency, deterministic-render, prop-allowlist, adapter, and preview
review before its catalog status can become `enabled`.

Provenance and integrity are recorded in
`.claude/PRPs/evidence/P30/remotion-bits-provenance.md`.
