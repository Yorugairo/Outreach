# Work Order — claim `steel-and-paper-ledger-page-v1`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `woodblock-vox-newsprint-v2`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

- `C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\content\video_engine\projects\systems-and-blowups\review\claims\steel-and-paper-plates-wave-3\objects\world-ledger-page-v1.png`

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to 3 candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

### world-ledger-blank-page-v1  (world_board)

WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. Subject: a blank cream washi page filling the whole frame - the ledger page BEFORE anything is written on it. Woodblock / vox newsprint register, matte, flat even light from the upper left. Cream washi paper #F4E6C7 with visible paper grain and faint fibre, deckle-soft edges, the same paper stock as the reference ledger page. Landscape 16:9, 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the same file as both source/ and objects/. The image contains no text, letters, numbers, logos, watermarks, people, hands, faces, lamps or objects: it is the empty page itself.

### world-ledger-inked-board-v1  (world_board)

WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. Subject: the SAME blank cream washi page as world-ledger-blank-page-v1, pixel-for-pixel the same paper, with one large rounded rectangle filled solid in charcoal ink #25313C - hand-inked, the fill dense and even inside, its edge crisp, like a chalkboard painted onto the page. The inked board occupies exactly one rectangle: its left edge at 6% of the image width, its top edge at 8% of the image height, its width 88% of the image width, its height 84% of the image height, corners rounded with a radius of about 2.4% of the image width. Outside that rectangle the cream page is untouched and identical to the blank page. Woodblock / vox newsprint register, matte, flat even light from the upper left. Cream washi paper #F4E6C7 with visible paper grain and faint fibre, deckle-soft edges, the same paper stock as the reference ledger page. Landscape 16:9, 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the same file as both source/ and objects/. The image contains no text, letters, numbers, logos, watermarks, people, hands, faces, lamps or objects: it is the empty page itself.


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

    C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\review\claims\steel-and-paper-ledger-page-v1

Write `steel-and-paper-ledger-page-v1.manifest.json` in the delivery folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "woodblock-vox-newsprint-v2",
  "source_prompt": "claim:steel-and-paper-ledger-page-v1",
  "assets": [
    {
      "asset_id": "world-ledger-blank-page-v1",
      "path": "objects/world-ledger-blank-page-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "",
      "source": {
        "path": "source/world-ledger-blank-page-v1-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "world-ledger-inked-board-v1",
      "path": "objects/world-ledger-inked-board-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "",
      "source": {
        "path": "source/world-ledger-inked-board-v1-source.png",
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
