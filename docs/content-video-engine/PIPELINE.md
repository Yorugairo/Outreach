# PIPELINE — what exists, what consumes what

> **Before building anything, read `CAPABILITIES.md`** — the index of
> every built renderer, engine, gate and prototype. Three capabilities were
> rebuilt from scratch in one session because nothing indexed them.

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
| 3–4 | **Script gates (runner)** | `scripts/run_script_gates.py` — runs `lint_script_pattern.py` → `audit_script_doctrine.py` (+ `kit_spec.py`) → `gate_opening_structure.py` → `enumerate_strength_screens.py`, in order, each through its own `main()` | script text, `--pivot "<line>"`, `--ring <t>`, `--counterparty <n>`, any take on disk (`--timeline build-f/timeline.json`) | `<script>-GATES.md` beside the script: the CHECK-RESPONSIBILITIES §5 TOOLS block, each tool's stdout verbatim, `script_hash` of the spoken text, `VERDICT: PASS|FAIL`; `<script>-SCREENS.md`; exit 1 on any FAIL |
| 4b | **The viewer** (P36) — the blind read | `scripts/viewer_windows.py` → `scripts/viewer_run.py` → `scripts/viewer_score.py` | the script (+ the take's timings, the title and the FINAL thumbnail) | `<script>-VIEWER.md`: beat recall and information gain from a reader that knows no doctrine; the runner shows it as a VIEWER block that **binds** since P36 HG1 (2026-09-03): an unperceived declared beat FAILs, confusion WARNs, gain is INFO-only |
| 5 | **Record** | `scripts/record_chained_take.py` | script text **+ a current, passing `<script>-GATES.md`** — the recorders refuse to spend when the report is missing, stale (hash ≠ the script) or carries a FAIL; `--force "<reason>"` records anyway and writes the reason into the take manifest | `vo-*/audio/*.mp3` + `*.words.json` |
| 6 | **Word timeline** | `scripts/build_timeline_f.py` | the take | merged word timeline (mechanical, safe to automate) |
| 7 | **SHOT TABLE — AUTHORED** | **a human or model reading the narration** | word timeline · plate `semantic` fields · evidence `context` fields | the window table: plate + Ken Burns + docks + badge times, per beat; a plate id `ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>]]` places a LEDGER PAGE world (doc 29 §9.26 / §9.28) that `build_scene_timeline_f.py` compiles from `evidence/objects/<series-id>.series.json` into `world.kind = "ledger"` + `world.page` (no plate PNG); an optional 7th row element `species` is a list of TARGETED SPECIES (doc 29 §9.27, P35 T7: `{"kind": punch|callout|focus_zoom|spotlight|squiggle|pull_back|plate_life|beat_freeze|radial|push, "at", "dur", "target": {"kind": datum|point|region|span, ...}}`) - the targeting law is `validate_species`: a pointing species with no declared target, two camera moves on one row, or a camera move over Ken Burns (§9.28 C3) is a hard build error naming the row; the list is emitted verbatim as `scene["species"]`; the timeline lists every species present in `species` (the ledger world + the targeted kinds) |
| 7b | Motion | `scripts/build_render_f.py` | the authored table | motion plan |
| 7c | **Motion-density gate** (E21 / doc 29 §9.25) | `scripts/gate_motion_density.py` | the compiled timeline — its own `scenes[].docks` (enter / exit / badge_at) are the dock clock; `evidence-dock.json` is read only when the timeline carries no docks (P35 T0: the file drifted to an older clock) — and `motion-plan.json` cues | exit 1 on any stretch > 12s without a visual event, evidence gaps > 45s, plate holds > 20s, a thin opening minute; the list of stretches that need stage captions. A LEDGER PAGE's build beats (scene start +0 / 0.6 / 3.4 / 4.2 / 7.2s: roll-out, field, outline, build start, build complete) count as visual events and its start as an evidence entry; the hold after the build is still (§9.28 C5 / D1 / D2). Stats say `dock_source` and `ledger_pages` | Captions: the build stamps `cap_mode` per page and declares `caption_modes`; M08 FAILs a still stretch > 12s with no stage page (P34 T5). Targeted species (P35 T7) fire as events per the §9.27 "Gate treatment" column (`SPECIES_EVENTS`: punch / callout / radial / push at `at`; focus_zoom / spotlight / pull_back / beat_freeze at `at` and `at+dur`; plate_life stepping at 10 fps across its duration so it fills a bare plate; squiggle none of its own - a stage caption event only). M09 FAILs a scene that stacks two camera moves (punch | focus_zoom | pull_back) or one over Ken Burns scale > 0 - the builder rule mirrored so a hand-edited timeline is caught (§9.28 C3). Opening-minute rows (E24 / E25, §9.29–9.30): M10 FAILs any still stretch > 6s that begins in the first 60s; M11 FAILs unless the first chart (chart/data dock or ledger page) enters 0:08–0:20 with a spotlight / callout / punch / focus_zoom within 1.5s (sound cue within 1.5s or WARN); M12 FAILs a chart dock that spans a scene boundary or holds > 10s (> 6s in the opening minute) - the chart is the proof, not the homework; re-enter it spotlit. The page beats are now +0 / 0.7 / 1.5 / 3.9 / 4.7 / 5.2 / 8.2s (roll-out, savor, field, line, punch, build start, build end + focus - §9.26, E22 addendum 6). The script-side rows G45 (packaging echo, `--title`/`--thumb`), J12 (`--thumb-file`) and the G09 0:45 WARN live in stage 4's opening gate and pass through the runner.
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

## Plate motion — parallax, ambient, sequential generation (2026-09)

Applies to an APPROVED plate; it never regenerates locked art. Full rows and the
ComfyUI node inventory are in `CAPABILITIES.md` under "Generative video".

- **A still plate to a camera move** — `create_comfy_parallax_video({imagePath,
  outputPath})` on the `video-engine` MCP (Depth Anything v2 + Depthflow). ComfyUI
  must be up on `127.0.0.1:8188`.
- **A sequential plate chain**, plate N seeding plate N+1 — `create_flow_batch({scenes,
  outputDir})` on the same server. Needs Chrome running with CDP on `9222`.
- **Queue, preflight and bridge diagnostics** live on the separate `flow-queue` server
  (`flow_enqueue_batch`, `flow_preflight_batch`, `flow_bridge_status`, ...).

Any plate carrying a Graphic Silhouette actor needs SAM 2 + LaMa first, or the camera
smears the actor's edge: SAM 2 cuts the subject to alpha, LaMa fills the ground behind
it, and the move then plays two clean layers. The same mask pins the actor when
LTX-Video animates the ground, which is what stops a generative model morphing the
silhouette.

**None of this satisfies the motion gates.** Ambient loops are texture, never authored
events — haze behind a chart the narration has left makes stillness prettier, not
comprehensible (E21, E25). A parallax move counts as plate life only when it is bound
to a narration anchor, the same rule as narration-keyed chart draw.

## The plate library — ONE index, search it before generating

`content/video_engine/sources/PLATE-LIBRARY.json` — every generated plate
across every source, with its **semantic** (what it depicts), its style
register, its approval state **as the manifest records it**, and its real
path.

```bash
python content/video_engine/scripts/build_plate_library.py            # rebuild
python content/video_engine/scripts/build_plate_library.py "memory"   # search
```

Search it by MEANING, not filename. That is the field you author against.

**Status comes from the manifest, never the path** (E10). The library exists
because the pilot's 195 approved plates sat in a directory named
`quarantine/` and were skipped, the stamped visuals resolve by `image_id`
rather than filename, and a shot table was authored from `objects/*.png`
while the `semantic` describing each plate sat unread beside it.

**A claim may declare its own `register`** in `approvals.json` — a borrowed
lane (ruling C9) keeps its own style label rather than inheriting the
folder's.

## Asset libraries — the sources the index reads

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
