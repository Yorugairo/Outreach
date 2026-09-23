# Work Order — claim `mp-ai-useful-faster-trump-poster-v1`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `woodblock-vox-newsprint-v2`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

- none supplied — follow the prompt text alone

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to 3 candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

### trump-uncle-sam-poster-v1  (world_board)

WORLD-BOARD OVERRIDE FOR THIS SLOT ONLY: create one flat opaque landscape editorial thumbnail poster at exactly 1920x1080 (16:9). This is a graphic poster exception, not a parallax plate: keep the complete RGB image as the deliverable, skip alpha matting, and use the same image as source and object.

SUBJECT: a recognizable editorial caricature of Donald Trump depicted as Uncle Sam, wearing an Uncle Sam top hat and jacket, facing the viewer and pointing one clear index finger directly at the viewer. Keep the face, pointing hand, and headline dominant and large in the frame, with strong margins and phone-legible shapes. The pointing gesture should make the viewer feel recruited into supervising an AI assistant.

TYPOGRAPHY: the exact large on-screen headline is “AI STILL NEEDS YOU!” Keep every word, letter, and punctuation mark exactly as written, high-contrast, clean, and legible. Type is a major visual subject and does not repeat the project title. No quotation marks or attribution around the headline.

STYLE: A light application of woodblock print meets vox newspaper with rich anime colors. Clearly an editorial illustration, not a photograph. Use a restrained brand palette: warm cream #F4E6C7 ground, charcoal #25313C ink, controlled red #ED6A4A and blue #1769C2 accents. Flat ink contours, newsprint texture, crisp color blocks, matte finish. Compose face, pointing hand, and headline as the primary three masses; no tiny flowchart or decorative card pile.

CONTENT BOUNDARIES: no official seal, no campaign branding, no logos, no watermark, no quote attribution, and no fabricated screenshot. Do not present the phrase as Trump's words. Keep the poster clearly editorial and illustrative.


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

    C:\Users\Snipe\Downloads\Outreach Program\review\claims\mp-ai-useful-faster-trump-poster-v1

Write `mp-ai-useful-faster-trump-poster-v1.manifest.json` in the delivery folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "woodblock-vox-newsprint-v2",
  "source_prompt": "claim:mp-ai-useful-faster-trump-poster-v1",
  "assets": [
    {
      "asset_id": "trump-uncle-sam-poster-v1",
      "path": "objects/trump-uncle-sam-poster-v1.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "world_board",
      "semantic": "editorial recruitment poster, flat landscape thumbnail",
      "source": {
        "path": "source/trump-uncle-sam-poster-v1-source.png",
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
