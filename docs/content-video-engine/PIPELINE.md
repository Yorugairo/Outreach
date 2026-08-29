# PIPELINE — what exists, what consumes what

**Read this before building anything in this folder.** It exists because
seven established components were bypassed and rebuilt from scratch in a
single session — not because they were hard to find, but because nothing
pointed at them and searching only ever returns what you already suspect.

The rule that follows from that: **enumerate before you grep.** `ls` the
directory, read the index, *then* search. Grep confirms a hypothesis; it
cannot surface a component you don't know exists.

---

## The stages, in order

| # | Stage | Owned by | Consumes | Emits |
|---|---|---|---|---|
| 1 | **Write** | `patterns/SCRIPT-PATTERN-KIT.md` + `patterns/phase-guides/P1–P6.md` | `patterns/INJECTION.md` (lane params), the previous phase's ledger | script sections + ledger |
| 2 | **Strength loop** | `patterns/STRENGTH-LOOP.md` | the draft | a fixpoint draft + rewrite log |
| 3 | **Lint** | `scripts/lint_script_pattern.py` | script text | pass/fail, mechanical tier |
| 4 | **Audit** | `scripts/audit_script_doctrine.py` (+ `scripts/kit_spec.py`) | script text, the kit's tables, any take on disk | timed-gate findings |
| 5 | **Record** | `scripts/record_chained_take.py` | script text | `vo-*/audio/*.mp3` + `*.words.json` |
| 6 | **Word timeline** | `scripts/build_timeline_f.py` | the take | merged word timeline (mechanical, safe to automate) |
| 7 | **SHOT TABLE — AUTHORED** | **a human or model reading the narration** | word timeline · plate `semantic` fields · evidence `context` fields | the window table: plate + Ken Burns + docks + badge times, per beat |
| 7b | Motion | `scripts/build_render_f.py` | the authored table | motion plan |
| 8 | **Render** | **`samples/scene-evidence-player.template.html`** | a `scene_evidence_timeline.v1` + base64 asset map | a self-contained preview |

## Stage 7 is AUTHORED. There is no allocator.

**This is the step that was replaced with a loop and broke the build.**

Every prior episode was built from a hand-written window table — see
`projects/*/steel-and-paper/build_scene_evidence_cut.py`:

```python
WINDOWS = [
    (0, 0.0, 10.0, "world-spike-desk-v1", (0.05, 14, -8), []),
    (0, 10.0, 40.0, "world-two-rooms-divergence-v1", (0.06, -18, 6),
     [("svg-divergence", 0, 13.5, 25.0, [16.0, 19.0])]),
    ...
```

The spike opens the video because **someone wrote that line** after reading
the narration. Every entry is a semantic decision: which plate depicts this
beat, which evidence proves this claim, when the badges land.

**The density rules are a CHECKLIST on authored work, not a generator.**
One plate per 12s, 20s ceiling, 1–2 evidence per plate — these tell you your
authoring is *wrong*. They cannot tell you what to author. An allocator that
fills slots by count can never produce the right answer at any quality of
tuning, because it is answering "how many fit," not "which one belongs."

**Author from the saved semantics — they exist for this.**

- Every plate manifest carries a `semantic` field. All 74 of them.
  `world-spike-desk-v1` → *"antique iron railway spike on dark desk, the
  ring token, macro"*. That IS the shot list.
- Every deck asset carries `context.what_it_is` and a `visual_role`.
- `sources/decks/asset-selection-index.md` describes every slide.

Reading filenames instead of manifests is what put the hype machine over
the opening line about an iron spike.

## The render contract — READ THIS BEFORE WRITING A PLAYER

**There is already a player. Do not write another one.**
`samples/scene-evidence-player.template.html` is the renderer. It takes two
substitutions and nothing else:

- `{{TIMELINE}}` — a `scene_evidence_timeline.v1` document
- `{{URIS}}` — `{asset_id: "data:image/png;base64,..."}` **plus** the key
  `__audio__` holding ONE audio data URI for the whole episode

**Assets are base64-embedded, not referenced by path.** A player using
relative paths renders black the moment it is opened anywhere but its own
directory. That is not a bug to debug; it is the reason the template embeds.

**`__audio__` is one file.** A chained two-part take must be joined first —
doc 37 §8.2: trim part one to its last word plus the 1.2s settle, then one
re-encode pass with a short crossfade.

### `scene_evidence_timeline.v1`

Worked example: `samples/current-bubble-five-minute-v4.timeline.json`.

```
schema_version  "scene_evidence_timeline.v1"
episode_id, project_id
narration   { canonical_hash, words_path }
captions    [ { at, until, text } ]
evidence    { <asset_id>: { title, document:{path,sha256}, source, badges } }
scenes      [ { scene_id,
                world: { asset_id, sha256, ken_burns:{scale,x,y} },
                exit:  "wipe_right" | ...,
                span:  [start_s, end_s],
                docks: [ { slide, slot, enter, exit, badge_at } ] } ]
```

Note what the schema encodes that a flat cue list does not: **scenes own a
world plate with its own Ken Burns move**, docks carry a **semantic slot**
(evidence roams by slot; the caption anchor never moves), and evidence
carries **badges** and a **source line**.

## Captions — doc 29 Part 5, not your own design

- One **fixed** lower-third anchor. Evidence roams; the caption does not.
- Transparent glyphs + text shadow. **No pill, no panel.**
- **Kinetic:** 2–4 word groups punch in ~0.34s apart, `power3.out`,
  scale 1.14 → 1.0, y 12 → 0, keywords in the accent colour. Group timings
  come from `words.json`, never from beat boundaries.
- **Quiet (§4.2):** while a document holds the stage — smaller, static,
  single fade, keywords still coloured, no punch-in. Kinetic runs only when
  the caption is the **sole text layer on stage**.
- §9.1: *"a caption that swaps as a static block is a defect."*

Word-by-word model: `remotion-video-creation/rules/display-captions.md` —
`createTikTokStyleCaptions` pages, active token by `fromMs <= now < toMs`.

## Asset libraries — check before you generate

| Library | Where | Count |
|---|---|---|
| Episode plates | `projects/*/review/claims/*plates-wave-*/objects/` | per wave, newest wins |
| Built evidence | `projects/*/<episode>/evidence/objects/` | chart · table · record · instrument · tile |
| Deck slides + crops | `content/video_engine/sources/decks/` **(main checkout)** | 86 slides, 9 semantic crops |
| Teacher-stamped visuals | `sources/decks/teacher-stamped-production-visuals/` | 86, keyed by `image_id` → `extracted_path` |

Indexes to read first: `sources/decks/asset-selection-index.md`,
`deck-asset-manifest.json`, `teacher-stamped-production-visuals-manifest.v1.json`.

**The deck libraries live in the MAIN CHECKOUT, not the worktree.** Worktree
isolation governs writes. Reads go anywhere.

## Handoff

`docs/portable/BUILD-PIPELINE.md` is the model-agnostic version of this
document — paste-able into Gemini or GPT with no Claude-specific tooling.
Keep the two in sync. Anything a fresh model needs that lives only in a
Claude skill file is a handoff failure waiting to happen.

Skills: `script-writer` owns stages 1-4, `episode-build` owns 5-8.

## Doctrine — derivation, not operation

Run the kit. Read a numbered doc to learn *why* a rule exists or to change
it. `README.md` indexes them; `patterns/FULL-VIDEO-MAP.md` is the spine.
Constants have **one owner**: the kit's tables, parsed by `kit_spec.py`. Never
restate a value in a second place — the sentence-length figure once lived in
ten and all ten drifted.
