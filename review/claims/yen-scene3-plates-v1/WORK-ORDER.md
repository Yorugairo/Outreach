# Work Order — claim `yen-scene3-plates-v1`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `notebooklm-pencil-paper-v1`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

- `C:\Users\Snipe\Downloads\flow-hook-refs-yen\JAPAN-LAST-FRAME.png`
- `C:\Users\Snipe\Downloads\omni-hook-refs\ref-A-chip-tweezers-END-FRAME.png`

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to 3 candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

### yen-p1-borrow-buy  (world_plate)

A small charcoal-ink machine sits centred on bare cream paper. Into its left side feeds a bundle of banknotes drawn in charcoal linework with teal (#178C83) fields, engraved scrollwork only. Out of its right side rises a neat stack of microchips, each chip a teal square with charcoal pin legs. The machine is the object: a loan turning into stock. Quiet zone: the top third. Coloured pencil and watercolour illustration on cream paper (#F4E6C7), visible pencil hatching and light paper grain, matte, flat even light from the upper left with a gentle shadow lower right, camera straight on at eye level. Colours limited to cream #F4E6C7, charcoal ink #25313C, teal #178C83, coral #ED6A4A and cobalt #1769C2; no other hues, no gradients, no glow. Vertical 9:16, 1080x1920. One side of the frame stays bare cream as a quiet zone. The image contains no text, letters, numbers, logos, watermarks, people, hands or faces; any banknote or document shows only illegible engraved scrollwork.

### yen-p2-easy  (world_plate)

The same stack of teal microchips, now grown tall and orderly, standing on cream paper. Beside its base, small in comparison, a single coral (#ED6A4A) coin on a short charcoal-ink chain rests on the paper — the loan, tiny next to what it bought. The chip stack casts a soft shadow lower right. Quiet zone: the top third. Coloured pencil and watercolour illustration on cream paper (#F4E6C7), visible pencil hatching and light paper grain, matte, flat even light from the upper left with a gentle shadow lower right, camera straight on at eye level. Colours limited to cream #F4E6C7, charcoal ink #25313C, teal #178C83, coral #ED6A4A and cobalt #1769C2; no other hues, no gradients, no glow. Vertical 9:16, 1080x1920. One side of the frame stays bare cream as a quiet zone. The image contains no text, letters, numbers, logos, watermarks, people, hands or faces; any banknote or document shows only illegible engraved scrollwork.

### yen-p3-yen-rises-heavier  (world_plate)

A balance scale drawn in charcoal ink stands on cream paper. Its right pan is dragged all the way down by one large, swollen coral (#ED6A4A) coin on a chain — the coin is physically heavy and oversized. Its left pan, holding the stack of teal microchips, is lifted high. The scale is the object: the debt got heavier. Quiet zone: the top third. Coloured pencil and watercolour illustration on cream paper (#F4E6C7), visible pencil hatching and light paper grain, matte, flat even light from the upper left with a gentle shadow lower right, camera straight on at eye level. Colours limited to cream #F4E6C7, charcoal ink #25313C, teal #178C83, coral #ED6A4A and cobalt #1769C2; no other hues, no gradients, no glow. Vertical 9:16, 1080x1920. One side of the frame stays bare cream as a quiet zone. The image contains no text, letters, numbers, logos, watermarks, people, hands or faces; any banknote or document shows only illegible engraved scrollwork.

### yen-p4-forced-sell  (world_plate)

The tall stack of teal microchips tipping over and scattering toward the right edge of the frame, individual chips tumbling with charcoal motion hatching, a few leaving the frame. A single charcoal-ink arrow points down-right beside them. The object is a stack being sold off in a hurry. Quiet zone: the top-left third. Coloured pencil and watercolour illustration on cream paper (#F4E6C7), visible pencil hatching and light paper grain, matte, flat even light from the upper left with a gentle shadow lower right, camera straight on at eye level. Colours limited to cream #F4E6C7, charcoal ink #25313C, teal #178C83, coral #ED6A4A and cobalt #1769C2; no other hues, no gradients, no glow. Vertical 9:16, 1080x1920. One side of the frame stays bare cream as a quiet zone. The image contains no text, letters, numbers, logos, watermarks, people, hands or faces; any banknote or document shows only illegible engraved scrollwork.


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

    C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\youtube-video-review-e67e8f\review\claims\yen-scene3-plates-v1

Write `yen-scene3-plates-v1.manifest.json` in the delivery folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "notebooklm-pencil-paper-v1",
  "source_prompt": "claim:yen-scene3-plates-v1",
  "assets": [
    {
      "asset_id": "yen-p1-borrow-buy",
      "path": "objects/yen-p1-borrow-buy.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_plate",
      "semantic": "",
      "source": {
        "path": "source/yen-p1-borrow-buy-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "yen-p2-easy",
      "path": "objects/yen-p2-easy.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_plate",
      "semantic": "",
      "source": {
        "path": "source/yen-p2-easy-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "yen-p3-yen-rises-heavier",
      "path": "objects/yen-p3-yen-rises-heavier.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_plate",
      "semantic": "",
      "source": {
        "path": "source/yen-p3-yen-rises-heavier-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "yen-p4-forced-sell",
      "path": "objects/yen-p4-forced-sell.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_plate",
      "semantic": "",
      "source": {
        "path": "source/yen-p4-forced-sell-source.png",
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
