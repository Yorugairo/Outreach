# Probe: Agent Generation Loop — Work Order v1

Paste this whole document into Antigravity (or GPT desktop). It is a complete,
self-contained work order: generate two images, judge them against the rubric,
deliver the approved files to the exact paths below.

This is a **probe**, not a library batch. It exists to answer two questions
before any pipeline is built on them: (1) can the generating agent place
correctly named files at a specified path with a valid manifest, and (2) does
its output hold the `ep1-index-funds-vox-newsprint-v3` style family. Nothing
delivered here will be promoted to any catalogue.

---

## Delivery contract

- **Target folder** (create it):
  `C:\Users\Snipe\.codex\worktrees\p29-remotion-console\Outreach Program\content\video_engine\projects\systems-and-blowups\assets\generated\review\probe-agent-loop-v1\`
- Files go **directly in that folder**, named exactly:
  - `objects/object-abacus-probe-v1.png`  (create the `objects` subfolder)
  - `objects/object-hourglass-probe-v1.png`
- **1024×1024, PNG, fully transparent background** (real alpha channel, not a
  checkerboard drawn in pixels, not white).
- When both files are final, write `probe-agent-loop-v1.manifest.json` in the
  target folder:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "ep1-index-funds-vox-newsprint-v3",
  "source_prompt": "docs/content-video-engine/prompts/PROBE-AGENT-LOOP-V1.md",
  "assets": [
    {
      "asset_id": "object-abacus-probe-v1",
      "path": "objects/object-abacus-probe-v1.png",
      "sha256": "<lowercase hex sha256 of the file bytes>",
      "kind": "prop",
      "semantic": "wooden abacus, paper-cut collage"
    },
    {
      "asset_id": "object-hourglass-probe-v1",
      "path": "objects/object-hourglass-probe-v1.png",
      "sha256": "<lowercase hex sha256 of the file bytes>",
      "kind": "prop",
      "semantic": "hourglass with sand mid-fall, paper-cut collage"
    }
  ]
}
```

- Compute each sha256 from the delivered file's bytes (PowerShell:
  `Get-FileHash -Algorithm SHA256 <file>`; lowercase the hex).
- Last, write `approvals.json` next to the manifest:

```json
{
  "judge": "<agent name and model>",
  "attempts": {"object-abacus-probe-v1": 1, "object-hourglass-probe-v1": 1},
  "approved": ["object-abacus-probe-v1", "object-hourglass-probe-v1"],
  "unresolved": [],
  "notes": "<one line per rejected attempt, if any>"
}
```

`approvals.json` is written **last** — it is the completion signal.

---

## The two subjects

Deliberately absent from the existing library, so probe output can never be
confused with real assets.

1. **object-abacus-probe-v1** — a wooden abacus, side-on, beads in charcoal and
   cobalt on a cream frame. One subject, nothing else.
2. **object-hourglass-probe-v1** — an hourglass mid-pour, frame in charcoal,
   sand in sunflower. One subject, nothing else.

## Style Block (verbatim from the v3 library build — do not paraphrase)

```
Style: hand-cut layered paper collage with woodblock ink contours. Visible paper
fibre and torn deckle edges. Soft directional shading with gentle depth between
paper layers — matte, never glossy, never photographic. Bold clean silhouettes
readable at small size.
Palette strictly: cream #F4E6C7, charcoal #25313C, cobalt #1769C2, teal #178C83,
sunflower #F5B72E, coral #ED6A4A. Adult editorial tone, financially credible,
never childish.
```

## Camera and Lighting Block (verbatim)

```
Use: asset for compositing into an explainer video. Isolated library element, not
a finished illustration.
Camera: eye-level, straight-on, no perspective distortion, no dutch angle.
Framing: full subject with clear margin on all sides, nothing cropped.
Lighting: soft even light from the upper left, gentle shadow falling lower right,
low contrast. Identical light direction on every asset in this library.
```

## Negative Block (verbatim)

```
Negative: no text, no words, no letters, no numerals, no charts with labels, no
currency symbols, no dollar signs, no logos, no watermarks, no signatures, no UI
chrome. No photorealism, no celebrity likeness, no toy or childish proportions,
no extra fingers, no malformed hands, no cropped feet, no floating props, no busy
background clutter, no dark navy full-bleed grounds.
```

---

## Judge rubric — you are the reviewer before delivery

After each generation, judge the image against every criterion. **Maximum two
attempts per subject.** If the second attempt still fails, do not deliver a
third — list the subject under `unresolved` in `approvals.json` with the
failing criterion, and deliver whatever passed.

Reject and regenerate if:

1. Any text, numeral, label or currency symbol appears anywhere. No exceptions.
2. The background is not genuinely transparent (inspect the alpha channel, not
   the preview).
3. More than the one named subject appears, or filler objects were added.
4. Photographic texture, legible micro-detail, or specular/glossy surface.
5. Palette strays outside the six declared colours.
6. Lighting direction is not upper-left.
7. The subject is cropped by any edge.

---

## After delivery

Reply in your own session with: the two file paths as delivered, the attempt
count per subject, and any criterion that forced a regeneration. The engine's
deterministic scan runs on this delivery independently — your approval is the
first gate, not the last.
