# Episode 1 — Claude Design Handoff

This package contains the render-resolved still artwork and one compact narration file for **History – Episode 1**.

## Contents

- `art-kit/canonical-visual-coverage.v12.json` — the 139 canonical timestamp slots.
- `art-kit/asset-map.json` — the approved render asset map. Its relative `path` values resolve from `art-kit/` exactly as copied here.
- `art-kit/generated_visuals/action_assets/` — 145 referenced PNG plates (426.3 MB total). A small number of canonical slots use more than one render asset.
- `audio/narration.m4a` — the 559.97-second narration extracted from the approved 4K master, AAC stereo at 128 kbps (8.5 MB).

## Use in Claude Design

1. Treat `canonical-visual-coverage.v12.json` as the timeline.
2. Resolve a slot to its approved still(s) with `asset-map.json` by matching `metadata.coverage_slot_id` to the slot's `slot_id`.
3. Use `audio/narration.m4a` as the single narration/audio bed; do not use the 4K MP4 as an audio source.
4. Preserve the asset hashes and source mapping in `asset-map.json` when exporting a new design/edit package.

This is a handoff copy of the approved Episode 1 final inputs, not an authorization to publish or alter the original production revision.
