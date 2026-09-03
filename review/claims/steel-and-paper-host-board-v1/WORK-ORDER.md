# Work Order — claim `steel-and-paper-host-board-v1`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `woodblock-vox-newsprint-v2`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

- `C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\content\video_engine\projects\systems-and-blowups\review\claims\finance-host-evidence-exp-2\objects\host-presents-board-v1.png`
- `C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\content\video_engine\projects\systems-and-blowups\assets\generated\cutouts\actor-host-present-open-v1.png`
- `C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\content\video_engine\projects\systems-and-blowups\assets\generated\cutouts\actor-host-point-right-v1.png`
- `C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\review\claims\steel-and-paper-ledger-page-v1\objects\world-ledger-inked-deckle-cream-v1.png`

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to 3 candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

### host-board-present-v1  (world_board)

WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. THE HOST (identity anchor, exact): an adult Black man with sculpted loc twists and a trimmed goatee, BLACK rectangular glasses (critical: frames are BLACK, never blue/cobalt), deep-indigo suit, copper tie, small gold lapel pin. Same face structure, hair, glasses, and wardrobe in every image - condition on the supplied reference images. Confident, composed, warm; never caricatured. THE BOARD (exact, condition on the reference plate world-ledger-inked-deckle-cream-v1): a sheet of cream washi paper with a deckled edge lying on a plain cream ground fills the frame; the paper is filled solid charcoal ink #25313C right up to its deckle edge, like a chalkboard painted onto the page, EXCEPT the host's zone. The board interior is EMPTY - no chart, no text, no marks: the chart is composited later into the surface he points at. Subject: the host stands in the RIGHT third of the frame, in front of the cream page's right margin, three-quarter to camera, presenting the board with an open hand toward its centre; the board fills the left two thirds of the paper; the host's body never overlaps the board interior - only his presenting hand reaches into it. Quiet zone for the chart: the board's left two thirds. Woodblock / vox newsprint register: carved ink contours, flat editorial colour, matte, even light from the upper left. Colours limited to cream #F4E6C7, charcoal #25313C, indigo suit, copper tie, small gold pin; no other hues, no gradients, no glow. Landscape 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the same file as both source/ and objects/. The image contains no text, letters, numbers, logos or watermarks anywhere.

### host-board-point-v1  (world_board)

WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. THE HOST (identity anchor, exact): an adult Black man with sculpted loc twists and a trimmed goatee, BLACK rectangular glasses (critical: frames are BLACK, never blue/cobalt), deep-indigo suit, copper tie, small gold lapel pin. Same face structure, hair, glasses, and wardrobe in every image - condition on the supplied reference images. Confident, composed, warm; never caricatured. THE BOARD (exact, condition on the reference plate world-ledger-inked-deckle-cream-v1): a sheet of cream washi paper with a deckled edge lying on a plain cream ground fills the frame; the paper is filled solid charcoal ink #25313C right up to its deckle edge, like a chalkboard painted onto the page, EXCEPT the host's zone. The board interior is EMPTY - no chart, no text, no marks: the chart is composited later into the surface he points at. Subject: the host stands in the RIGHT third of the frame, turned to the board, pointing with one finger at the board's UPPER area (a datum will be composited exactly where he points); his eyes follow his finger; the board fills the left two thirds of the paper; only his pointing hand reaches into the board interior. Woodblock / vox newsprint register: carved ink contours, flat editorial colour, matte, even light from the upper left. Colours limited to cream #F4E6C7, charcoal #25313C, indigo suit, copper tie, small gold pin; no other hues, no gradients, no glow. Landscape 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the same file as both source/ and objects/. The image contains no text, letters, numbers, logos or watermarks anywhere.

### host-board-turned-v1  (world_board)

WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. THE HOST (identity anchor, exact): an adult Black man with sculpted loc twists and a trimmed goatee, BLACK rectangular glasses (critical: frames are BLACK, never blue/cobalt), deep-indigo suit, copper tie, small gold lapel pin. Same face structure, hair, glasses, and wardrobe in every image - condition on the supplied reference images. Confident, composed, warm; never caricatured. THE BOARD (exact, condition on the reference plate world-ledger-inked-deckle-cream-v1): a sheet of cream washi paper with a deckled edge lying on a plain cream ground fills the frame; the paper is filled solid charcoal ink #25313C right up to its deckle edge, like a chalkboard painted onto the page, EXCEPT the host's zone. The board interior is EMPTY - no chart, no text, no marks: the chart is composited later into the surface he points at. Subject: the host stands at the LEFT edge of the frame, seen from behind at three-quarter, turned to the board on his right, one hand at his chin as if reading it; the board fills the right two thirds of the paper; he does not overlap the board interior. Quiet zone for the chart: the board's right two thirds. Woodblock / vox newsprint register: carved ink contours, flat editorial colour, matte, even light from the upper left. Colours limited to cream #F4E6C7, charcoal #25313C, indigo suit, copper tie, small gold pin; no other hues, no gradients, no glow. Landscape 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the same file as both source/ and objects/. The image contains no text, letters, numbers, logos or watermarks anywhere.


## Stage B — Extract

Matte each chosen source to a true-alpha cutout (rembg or equivalent), trim to
the subject's bounding box, pad onto a square transparent canvas with ~5%
margin, then **resize the padded canvas to exactly 1024x1024 (LANCZOS)**
unless the slot states another size — downscaling also cleans hard matte
edges. Save as `objects/<asset_id>.png`. World-board slots that declare an
override keep their stated landscape size and skip matting.

## Stage C — Self-judge the cutout (max 2 extraction attempts per slot)

1. Alpha is genuine — inspect the channel; full 0-255 range, subject opaque.
2. No halo: zoom the edge over a dark and a light ground — a rim in the
   *background's* colour is the failure; the subject's own soft edge is fine.
3. Nothing of the subject was eaten by the matte (thin parts, interior holes).
4. The source honours its prompt: one subject, stated palette and lighting,
   no text or numerals anywhere.

If extraction fails 2 times on a good source, **deliver
the source anyway** and list the cutout under `unresolved` — a delivered
source is recoverable; a withheld one is not.

## Prompt adaptation — permission with a boundary

When an attempt fails your own judgment, you may **strengthen** the prompt
before retrying: add emphasis, spatial constraints, density language, or
clarifying description that pushes the result toward what the slot asks for.
You may never weaken or drop the NEGATIVE block, never alter the STYLE or
LIGHT blocks, and never change the subject itself. Record every adapted
prompt verbatim in `approvals.json` under
`"prompt_adaptations": {"<asset_id>": ["<adapted prompt>"]}` — the
adaptations that worked become next batch's starting prompts.

## Stage D — Deliver

Delivery folder (create subfolders as needed):

    C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\review\claims\steel-and-paper-host-board-v1

Write `steel-and-paper-host-board-v1.manifest.json` in the delivery folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "woodblock-vox-newsprint-v2",
  "source_prompt": "claim:steel-and-paper-host-board-v1",
  "assets": [
    {
      "asset_id": "host-board-present-v1",
      "path": "objects/host-board-present-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "",
      "source": {
        "path": "source/host-board-present-v1-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "host-board-point-v1",
      "path": "objects/host-board-point-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "",
      "source": {
        "path": "source/host-board-point-v1-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "host-board-turned-v1",
      "path": "objects/host-board-turned-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "",
      "source": {
        "path": "source/host-board-turned-v1-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    }
  ]
}
```

Compute every sha256 from the delivered file's bytes (PowerShell:
`Get-FileHash -Algorithm SHA256 <file>`; lowercase the hex).

Write `approvals.json` **last** — it is the completion signal:

```json
{
  "judge": "<agent name and model>",
  "generation_attempts": {"<asset_id>": 1},
  "extraction_attempts": {"<asset_id>": 1},
  "approved": ["<asset_id>", "..."],
  "unresolved": [],
  "notes": "<one line per rejected attempt, if any>"
}
```

The engine's deterministic scan verifies every hash and measures every alpha
rim independently — your approval is the first gate, not the last.
