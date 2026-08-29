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
| 6 | **Timeline** | `scripts/build_timeline_f.py` | word timings, plate inventory | merged word timeline, plate plan |
| 7 | **Motion** | `scripts/build_render_f.py` | timeline, plate plan, evidence dock | motion plan |
| 8 | **Render** | **`samples/scene-evidence-player.template.html`** | a `scene_evidence_timeline.v1` + base64 asset map | a self-contained preview |

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
