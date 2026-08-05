# Episode 1 — Claude Design Handoff

This package contains the render-resolved still artwork for **History – Episode 1**. It is designed for repository readers that cannot resolve Git LFS objects.

## Contents

- `canonical-visual-coverage.v12.json` — the 139 canonical timestamp slots.
- `plates-1080/` — 145 flat, 1920×1080 PNG plates. These are normal Git blobs, not LFS pointers.
- `plates-1080-manifest.json` — direct mapping from an `asset_id` and `coverage_slot_id` to its flat plate path, plus SHA-256 hashes.
- `audio/narration.m4a` — optional local reference only. Upload it directly to the chat if the repository reader cannot ingest M4A files.

## Use in Claude Design

1. Treat `canonical-visual-coverage.v12.json` as the timeline.
2. Resolve a slot to its approved still(s) with `plates-1080-manifest.json` by matching `coverage_slot_id` to the slot's `slot_id`.
3. Use the filename in `plate_path`; no wave-folder traversal or Git LFS download is required.
4. If narration is needed, upload `audio/narration.m4a` directly into the design chat rather than relying on its repository reader.
5. Preserve the plate hashes and mapping manifest when exporting a new design/edit package.

This is a handoff copy of the approved Episode 1 final inputs, not an authorization to publish or alter the original production revision.
