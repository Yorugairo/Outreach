# Probe: Agent Generation Loop — Work Order v2

Supersedes v1. What changed and why: v1 demanded native alpha at generation
time, which the image surface cannot produce — both subjects failed on a
criterion the generator can never meet. v1 did prove the mechanics: manifest
and approvals landed at exact paths, the two-attempt cap held, and the
self-judge was honest (its hourglass halo call was confirmed by deterministic
measurement: 12.6% partial-alpha rim, dark slate). v2 restructures the loop so
each stage is judged on what it can control:

**generate (opaque, best-of) → extract (matting) → self-judge the cutout →
deliver both source and cutout.** The raw render is the irreplaceable
artifact — extraction is cheap and repeatable; a bad cutout with a good source
is recoverable downstream without regenerating.

Target folder (create it):
`C:\Users\Snipe\.codex\worktrees\p29-remotion-console\Outreach Program\content\video_engine\projects\systems-and-blowups\assets\generated\review\probe-agent-loop-v2\`

---

## Stage A — Generate (2 subjects, best-of, opaque allowed)

Subjects, style, camera/lighting, and negative blocks are **unchanged from v1**
(`PROBE-AGENT-LOOP-V1.md`) with two amendments:

- **Background: a single flat solid ground is expected** — pale neutral, no
  gradient, no vignette, no dark backdrop. Do not attempt transparency at
  generation time.
- **Margin is a hard rule:** the full subject with clear ground on all four
  sides. Edge contact killed both abacus attempts in v1 — if the subject
  touches any edge, regenerate before bothering with extraction.

Generate up to 3 candidates per subject and keep the best. Save the chosen
originals as:

- `source/object-abacus-probe-v2-source.png`
- `source/object-hourglass-probe-v2-source.png`

## Stage B — Extract

Matte each chosen source to a true-alpha cutout (rembg or equivalent — your
tools, your call), then:

- trim to the subject's bounding box,
- pad onto a square transparent canvas, subject centred, ~5% margin,
- save as `objects/object-abacus-probe-v2.png` and
  `objects/object-hourglass-probe-v2.png`.

## Stage C — Self-judge the cutout (max 2 extraction attempts per subject)

Judge the **cutout**, not the source:

1. Alpha is genuine (inspect the channel; full 0–255 range, subject opaque).
2. No visible halo: zoom the subject's edge over both a dark and a light
   ground — no rim of backdrop colour either way. A soft anti-aliased edge in
   the subject's own colours is fine; a rim in the *background's* colour is
   the failure.
3. Nothing of the subject was eaten by the matte (thin parts, interior holes
   like the hourglass waist and abacus rods survive).
4. All v1 content criteria still hold on the source: one subject, palette,
   upper-left light, no text or numerals, matte paper surface.

If extraction fails twice on a good source, **deliver the source anyway** and
list the cutout under `unresolved` — a delivered source is recoverable; a
withheld one is not.

## Stage D — Deliver

`probe-agent-loop-v2.manifest.json` in the target folder, same shape as v1 but
listing **both** files per subject:

```json
{
  "schema_version": "review_manifest.v1",
  "status": "review_only",
  "render_eligible": false,
  "style_family": "ep1-index-funds-vox-newsprint-v3",
  "source_prompt": "docs/content-video-engine/prompts/PROBE-AGENT-LOOP-V2.md",
  "assets": [
    {"asset_id": "object-abacus-probe-v2", "path": "objects/object-abacus-probe-v2.png",
     "sha256": "<hex>", "kind": "prop", "semantic": "wooden abacus, paper-cut collage",
     "source": {"path": "source/object-abacus-probe-v2-source.png", "sha256": "<hex>"}},
    {"asset_id": "object-hourglass-probe-v2", "path": "objects/object-hourglass-probe-v2.png",
     "sha256": "<hex>", "kind": "prop", "semantic": "hourglass with sand mid-fall, paper-cut collage",
     "source": {"path": "source/object-hourglass-probe-v2-source.png", "sha256": "<hex>"}}
  ]
}
```

`approvals.json` written **last**, same shape as v1, with per-stage attempt
counts (`generation_attempts`, `extraction_attempts`).

## After you

The engine's deterministic scan measures every cutout's alpha rim
(partial-alpha fraction and edge mean colour) independently — calibration from
v1: 1.6% partial rim passed, 12.6% with a dark rim failed. A second judge
(Gemini) then reviews style and semantics against the same rubric. Assembly
consumes only what passes both.
