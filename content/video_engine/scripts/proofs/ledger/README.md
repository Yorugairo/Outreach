# Ledger-page proof tools (secured from the 2026-09-03 session scratchpad)

Run every script from the repo root with the root as the first argument.

| Script | What it makes | Inputs it needs |
|---|---|---|
| `build_ledger_proof.py .` | `steel-and-paper/build-f/ledger-species-proof.html` - the synthetic three-scene player for the LEDGER PAGE species (host plate, deckle field, punch, focus, targeted species). Served by the `episode-player` launch config on :8731. | `deckle-edge.json`, `host-boards.json` (beside it), the claim deliveries below |
| `derive_host_boards.py .` | `host-board-*-blank.png` beside the delivered host plates + `host-boards.json` (board bbox, inner rect, hand clearance, quiet zone) | `review/claims/steel-and-paper-host-board-v1/objects/*.png`, `review/claims/steel-and-paper-ledger-page-v1/objects/world-ledger-blank-page-cream-v1.png` |
| `gen_ledger_page.py <hyperframes dir>` | the three hyperframes candidates `compositions/ledger-page-v1-{A,B,C}.html` (the first stitch, for the record) | the registry components in `compositions/components/` |
| `build_review_page.py` | the hosted review-pass page (`review-pass.html`) | `review-images.json` beside it (regenerate: base64 of the filmstrips under `build-f/render/`) |
| `open_host_board_claim.py .` | opens the host-on-board claim and renders its work order | the host references named inside |

Claim deliveries (review quarantine, on disk, not in git):
- `review/claims/steel-and-paper-ledger-page-v1/objects/` - `world-ledger-blank-page-v1.png`, `world-ledger-inked-board-v1.png` (retired), `world-ledger-inked-deckle-v1.png`, `world-ledger-blank-page-cream-v1.png`, `world-ledger-inked-deckle-cream-v1.png` (the cream-ground pair the species uses)
- `review/claims/steel-and-paper-host-board-v1/objects/` - `host-board-{present,point,turned}-v1.png` and their derived `-blank.png`
