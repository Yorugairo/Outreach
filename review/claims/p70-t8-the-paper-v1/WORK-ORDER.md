# Work Order — claim `p70-t8-the-paper-v1`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `props-catalogue-woodblock-v1`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

- `C:\Users\Snipe\AppData\Local\Temp\claude\C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16\45114c3b-258a-4ca8-9aaf-b674a804cc7e\scratchpad\p70-t8\tree\content\video_engine\assets\props\cutouts\prop-memory-steel-ibeam-v1.png`
- `C:\Users\Snipe\AppData\Local\Temp\claude\C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16\45114c3b-258a-4ca8-9aaf-b674a804cc7e\scratchpad\p70-t8\tree\content\video_engine\assets\props\cutouts\prop-federal-reserve-building-v1.png`

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to 3 candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

### prop-paper-bond-stack-v1a  (prop)

Subject: THE PAPER - a tall, slightly uneven stack of about twenty-five engraved bond certificates, each a cream
sheet with a scrollwork border, stacked flat and squared but not perfectly (a few sheets overhang a little, one corner
lifts), heavy and dense - the stack is visibly a LOAD, about as wide as it is tall (width : height about 1 : 1). The
top sheet faces up and is the most detailed. It must read at a glance as a pile of financial paper, not a book, a box
or a ream of blank printer paper.

FRAMING: exactly ONE object, centred, a three-quarter view from slightly above like the reference I-beam, the whole
stack in frame with clear margin on all four sides (edge contact is a regeneration), on a single flat solid PALE ground
(no gradient, no vignette, no table, no floor line, no hands, no other object). It is cut out as a prop: bare, no card,
no frame around it.

TEXT (E99 s113 - text on a prop is allowed only when intentional and verified):
- The TOP certificate carries one engraved title, exactly BOND - four capitals, B-O-N-D - in a Victorian engraved serif,
  dark charcoal, centred on the top sheet's upper half, legible when the whole prop is shown 300 px wide.
- No other words anywhere. Every other line is TEXTURE, NOT WRITING: fine engraved scrollwork borders, guilloche rosettes,
  wavy ruled lines that form no letters. No numerals, no dates, no amounts, no currency signs, no company, place or
  person names, no seal lettering, no pseudo-letters. If a line cannot stay illegible, leave it blank.
- No logos, watermarks, flags or political symbols; no real-person likeness.

STYLE (verbatim; match the two reference cutouts - the props catalogue this prop joins): a single object drawn as
a detailed engraved woodblock / etching illustration with a light hand-coloured finish - fine charcoal #25313C contour and
hatching lines carrying the form, aged cream paper #F4E6C7 for the certificates, a little warm sepia in the shadows. The
same line weight, finish and three-quarter view as the reference I-beam. Matte, never glossy, never photographic, never
a flat vector icon. Adult, financially credible.
LIGHT: soft light from the upper left, shade on the lower right faces (the stage light the engine hatches its shadows by);
no cast shadow on the ground (the engine draws the prop's own resting shadow).

### prop-paper-bond-stack-v1b  (prop)

Subject: THE PAPER - a tall, slightly uneven stack of about twenty-five engraved bond certificates, each a cream
sheet with a scrollwork border, stacked flat and squared but not perfectly (a few sheets overhang a little, one corner
lifts), heavy and dense - the stack is visibly a LOAD, about as wide as it is tall (width : height about 1 : 1). The
top sheet faces up and is the most detailed. It must read at a glance as a pile of financial paper, not a book, a box
or a ream of blank printer paper.

FRAMING: exactly ONE object, centred, a three-quarter view from slightly above like the reference I-beam, the whole
stack in frame with clear margin on all four sides (edge contact is a regeneration), on a single flat solid PALE ground
(no gradient, no vignette, no table, no floor line, no hands, no other object). It is cut out as a prop: bare, no card,
no frame around it.

TEXT: NONE. No letters, words, numerals, dates, amounts or currency signs anywhere - every line on every sheet is
engraved TEXTURE (scrollwork borders, guilloche rosettes, wavy ruled lines that form no letters). If a line cannot stay
illegible, leave it blank. No logos, watermarks, flags or political symbols.

STYLE (verbatim; match the two reference cutouts - the props catalogue this prop joins): a single object drawn as
a detailed engraved woodblock / etching illustration with a light hand-coloured finish - fine charcoal #25313C contour and
hatching lines carrying the form, aged cream paper #F4E6C7 for the certificates, a little warm sepia in the shadows. The
same line weight, finish and three-quarter view as the reference I-beam. Matte, never glossy, never photographic, never
a flat vector icon. Adult, financially credible.
LIGHT: soft light from the upper left, shade on the lower right faces (the stage light the engine hatches its shadows by);
no cast shadow on the ground (the engine draws the prop's own resting shadow).


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

    C:\Users\Snipe\AppData\Local\Temp\claude\C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16\45114c3b-258a-4ca8-9aaf-b674a804cc7e\scratchpad\p70-t8\claim-root\review\claims\p70-t8-the-paper-v1

Write `p70-t8-the-paper-v1.manifest.json` in the delivery folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "props-catalogue-woodblock-v1",
  "source_prompt": "claim:p70-t8-the-paper-v1",
  "assets": [
    {
      "asset_id": "prop-paper-bond-stack-v1a",
      "path": "objects/prop-paper-bond-stack-v1a.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "prop",
      "semantic": "the paper: a heavy stack of engraved bond certificates, BOND on the top sheet",
      "source": {
        "path": "source/prop-paper-bond-stack-v1a-source.png",
        "sha256": "<lowercase hex sha256>"
      }
    },
    {
      "asset_id": "prop-paper-bond-stack-v1b",
      "path": "objects/prop-paper-bond-stack-v1b.png",
      "sha256": "<lowercase hex sha256 of the delivered file bytes>",
      "kind": "prop",
      "semantic": "the paper: a heavy stack of engraved bond certificates, no text",
      "source": {
        "path": "source/prop-paper-bond-stack-v1b-source.png",
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
