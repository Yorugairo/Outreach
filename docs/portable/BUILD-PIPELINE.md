# BUILD PIPELINE — portable contract

Audited against the record 2026-09-13 (P54, docs/operator-ledger/PORTABLE-AUDIT.md).

Model-agnostic. Paste this into any assistant — Gemini, GPT, a fresh Claude —
and it can build an episode without tribal knowledge. No Claude-specific
tooling is referenced.

Companion to `DOCTRINE-CORE.md` (world view, voice, standards),
`VOICE-PACK.md` (voice by exemplar) and `OPERATOR-RULINGS.md` (standing
corrections, which override everything).

---

## The one rule that prevents the common failure

**Enumerate before you search.** List the directory and read the index
*before* grepping. Searching returns confirmations of what you already
suspect; it cannot surface a component you don't know exists. Seven
established components — including the renderer — were once rebuilt from
scratch because folders were never listed.

**Before building any tool or generating any asset, check whether one
already exists.**

## Stages

| # | Stage | Input | Output |
|---|---|---|---|
| 1 | Write | injection block + phase guides + prior ledger | script + ledger |
| 2 | Strength loop | draft | fixpoint draft + rewrite log |
| 3 | Lint / audit | script text | gate findings |
| 4 | Record | script text | audio + word timings (`*.words.json`) |
| 5 | Word timeline | word timings | merged timeline (mechanical) |
| 6 | **SHOT TABLE — AUTHORED** | narration + plate `semantic` fields + evidence `context` | world (a ledger page by default, or a plate naming its use - E61), docks and badge times per beat |
| 7 | Motion | the authored table | motion plan |
| 8 | Render | timeline + asset map | split player: `player.html` shell + `assets.json`, served (see Stage 8) |

## Stage 4 → 5: the take is ground truth

Word timings decide everything downstream. **Never resample captions onto
beat boundaries** — that collapses word-timed lines onto beats and the
captions drift off the narration.

An ElevenLabs long-form master records as **two chained parts** (the provider
caps a single request) - this section is that recording path only. YouTube's
voice is OPEN and not ElevenLabs by default; a one-shot renders both takes, free
or near-free (`scratch_take.py --engine both`) (E70, 2026-09-12). Part two is
conditioned on part one's request id so prosody carries. To merge:

1. Offset = part one's **last word end** + a **1.2s settle**.
2. Discard the provider's trailing silence — any silence over 1.2s belongs
   to the editor's timeline, not the voice.
3. Join with **one re-encode pass** and a short crossfade. Never a raw
   concat of independently generated segments.
4. **Pause discipline:** the payload is REFLOWED — paragraph breaks only at
   section seams (~8–10 per part; every blank line is a pause and an
   intonation reset). **No break tag ever enters the payload**: the recorder
   sets `ELEVENLABS_NO_BREAK_TAGS=1`, pause marks strip to plain text, and
   the key beats are edit pauses cut in by the editor, where nothing can
   speak them - the ~3-tag practice is superseded by zero (37 §21,
   2026-08-30). Em-dashes carry the micro-pauses. Longer silences are the
   editor's.

A short's single take is not chained. `retime_take.py` caps its silence GAPS,
not the take (intra-sentence over 0.40s to 0.30s, inter-sentence over 0.65s
to 0.50s - 37 §14), then applies any tempo change.

## The plate library

One index of every generated plate: `sources/PLATE-LIBRARY.json` — id,
**semantic**, style register, approval state as the manifest records it, and
path. **Search it by meaning before generating anything.** Status lives in
the manifest, never in the directory name. **Channels are identity walls,
not tags**: every plate carries a `channel` and every consumer filters by
it — a martial-arts plate never resolves into a finance episode, however
well its semantic matches. Search with `--channel <name>`.

## Stage 6 is AUTHORED — there is no allocator

Someone reads the narration beat by beat and chooses the plate that depicts
it and the evidence that proves it. Every asset carries a saved `semantic`
or `context` description written for exactly this. **Read those, never
filenames.**

**The density rules below are a CHECKLIST on authored work, not a
generator.** They tell you the authoring is wrong; they cannot tell you what
to author. An allocator filling slots by count answers "how many fit," not
"which one belongs," and cannot be tuned into correctness.

Shape of the artifact — one row per window:

```
(beat_start, beat_end, plate_id, ken_burns(scale,x,y),
 [ (evidence_id, slot, enter, exit, [badge_times...]) ])
```

## The world and the dock cadence (long form)

**The chart is the world.** A long form is authored on the ledger page by
default; a plate appears for ONE of three uses and names it on its row - a
**landing surface** (evidence docked on it), a **bridge** (a narration plate
between ideas) or a **reset** (it covers the world so the next page mounts
clean); a plate with no named use WARNs (E61, 2026-09-11;
`lint_species_choice.py`). A short follows E44/E45, not this cadence (E46 §1).

When a world carries docks, one shape works - **one way to live in a frame,
not the way** (E69 §2: a species, a page beat, a chart state change or stage
captions count too):

> **Two evidence pieces, two badges each, a breath between them.** If the
> world cannot field two pieces that genuinely earn their place, it carries
> **one big piece** instead.

- **12-20s hold -> two pieces.** Piece one settles, badges at +1.3s / +2.6s,
  **breath 1.1s**, piece two settles, **savour 2.2s** - a dock hold, never a
  bare plate with a slow drift (doc 29 §9.25 #3).
- **Cannot field two -> one solo card, wide.** Not two weak ones. A stat tile
  dragged in to make a count is worse than a single document with room.
- **Under ~8s -> one piece or none.** A pair cannot settle, badge and breathe
  inside a short hold; forcing it produces the strobing the breath exists to
  prevent.
- **A world with no dock is never still.** The captions take the stage and
  ARE the motion; no stretch runs past 12s without a visual event, 8s is the
  working target (E21, doc 29 §9.25).
- **Two badges per card is the target**, and a badge numeral must appear
  verbatim in the document behind it. A card with no badges leaves its whole
  information layer blank.

**How the world changes.** The wipe is retired as the default (E47 §3,
amended 2026-09-12): when the WORLD actually changes - a different plate,
clip or chart page arriving without a signature - the default is the **dip**
through black; the same world (a dock added, a page returning) cuts; a page
arriving by a signature (the mount, the spiral, the morph) cuts, because the
signature carries the change. `wipe` / `wipe_right` stay as effects reached by
name. An authored exit wins.

**A chart never survives a plate change** (E25, doc 29 §9.30, gate M12): a
chart dock that straddles a scene boundary FAILs; if the narrative returns,
the chart RE-ENTERS spotlit on the new datum. Two clocks, never merged: a
chart DOCK held over 10s (6s in the opening minute) FAILs (M12). A ledger
PAGE's deployed life is 6-8s from its last data mark on average, 12s at most
(E50; M21 WARNs past 12s), then it un-draws or becomes the next thing. A
non-chart card may hold across a boundary while its claim spans the scenes
(E12, doc 29 §9.15 item 2); its exit is proof-governed (E25, §9.30 rule 4).

## The density CHECK (operator rule) — run it against the authored table

- **Runtime / 12s** stays the plate-density target where a stretch is built
  from plates (doc 29 §9.13) - but **do not manufacture worlds to pass a
  hold rule** (E69 §4); a long form's worlds are ledger pages by
  default (E61).
- **Hold length is not a defect; a dead frame is** (E69, 2026-09-12; doc 29
  §9.13 amended in place). Past 20s the gate (M05) reads the longest gap
  between visual events INSIDE the hold against the long form's working
  target (8s, M02) or a short's pulse (an event every 1.2-2.5s, M16). The
  two-dock condition is withdrawn. A still world held past 20s with nothing
  on it still FAILs.
- **Diagnose which layer is thin** before ordering work on a bare stretch -
  the cure may be a species, a page beat or stage captions, not another
  plate (doc 29 §9.13; E69 §2).
- **The world tiles continuously.** No second without a world (a ledger page
  or a plate); it persists under evidence and holds at its named idle under a
  locked camera, not a push (E49, E59).

## Evidence — what to reach for when authoring

Dock each object to **the sentence whose claim it proves**. No anchor in the
narration means the dock is wrong — do not place it anyway.

**Six species, and variety is the density mechanism:** chart · table ·
record document (typewriter on paper, one highlighter stroke on the exact
phrase spoken) · instrument reading (our own measurement, with method,
period and tripwire on screen) · stat tile · registered deck plate.

A viewer moving between *kinds* of proof stays engaged on one plate far
longer than one watching a fifth chart. When a stretch runs long, reach for
a **different species** before reaching for another plate.

Registered deck material must be **figure-verified against the episode's
dossier before docking** — a registered plate that contradicts the narration
hands the viewer the error in typeset form.

## Stage 7: motion

| Element | Value |
|---|---|
| dock entrance | the engine's analytic spring (doc 42 §42.2, `kinetics/spring.mjs`): the card springs in at reading size on its word, then shrinks and slides (min-jerk) to its parked place - never a plain dissolve or a cut (E45, 2026-09-06). On a ledger page it is about half the stage width and never reads or parks over the data's ink; it is placed in E65's order: a band outside the plot, the plot's empty room, over the x-axis band, the emptiest corner at the floor size (E45, E63, E65; M25, M27) |
| dock exit | 0.72s expo-out |
| wash fade | 0.75s |
| stat pill | 0.65s expo-out, translateY 12px |
| world change | `dip` through black, 14 frames / 0.47s (a `[DERIVED]` starting reference); a signature arrival (mount, spiral) cuts; `wipe` is an effect by name only (E47) |
| world life | a NAMED idle per held element (breathing scale 1-2 %, a slow directional drift or a luminance pulse), a pure function of `t`; the camera LOCKED by default, moving only for a reason the frame can name (E49, E59). Ken Burns is plate life on a still that must hold, not a stillness fix (E46 §2) |

**Never scale from zero.** Scale-from-zero with bounce reads cartoon; the
document snaps into focus, it does not float in from space. **Settles are
slow, moves are fast.**

Cadence within a beat: card settles on its word → badges at +1.3s /
+2.6s → **settle 1.1s** → second card → **savour 2.2s** → the world's exit
(a dip only where the world actually changes, E47 §3).

## Stage 8: render contract

The player takes a timeline document and an asset map:

```
{{TIMELINE}}  a scene_evidence_timeline.v1 document
{{URIS}}      { asset_id: "data:image/png;base64,…", "__audio__": "data:audio/mpeg;base64,…" }
```

**The build splits the player** (P51 T1; `docs/content-video-engine/PIPELINE.md`
stage 8): `player.html` (a 46 KB shell), `assets.json` (the data URIs,
fetched), a copy of `scene-evidence-engine.mjs` and `player.json` (its sha).
**Serve the build dir** (`.mjs` as text/javascript); a `file://` open cannot
fetch. `render_baseline.instantiate` still composes the single file for the
goldens and the tests.

**`__audio__` is one joined file** for the whole episode.

### `scene_evidence_timeline.v1`

```
schema_version   "scene_evidence_timeline.v1"
episode_id, project_id
narration        { canonical_hash, words_path }
captions         [ { at, until, text } ]                    # block fallback
caption_pages    [ { s, e, t: [ { w, s, e, k } ] } ]        # kinetic layer
evidence         { <id>: { title, source, document:{path,sha256}, badges } }
scenes           [ { scene_id,
                     world: { asset_id, sha256, ken_burns:{scale,x,y} },
                     exit:  "cut" | "dip" | "blurzoom" | "dissolve" |
                            "wipe" | "wipe_right" | "suck" | "melt",
                            # SCENE_EXITS, build_scene_timeline_f.py
                     span:  [start_s, end_s],
                     docks: [ { slide, slot, enter, exit, badge_at } ] } ]
```

A **scene owns its world** - a ledger page (`world.kind = "ledger"`, doc 29
§9.26) or a plate - under a camera LOCKED by default (E59); `ken_burns` is
plate life on a still that must hold, not a stillness fix (E46 §2, E49 §2).
A scene's `exit` names the transition INTO the scene it sits on (E47;
`SCENE_EXITS`, `build_scene_timeline_f.py`), so a suck or a melt on a scene
takes the page BEFORE it, and that outgoing page is the one stamped
`exit=cut` (R26-60). A ledger page arrives by its roll-out, `mount`, `spiral`
(a return), `snap`, `throw`, `drop` (E50 amendment) or `axes` (the hook; chart
to chart - a page that follows a page, whatever the transition, E73 corrected
2026-09-13) - `axes` / `built` elsewhere is an authored need for speed (E45,
E47, E73). Docks carry a
**semantic slot**: evidence roams by slot; the caption moves to the band a
card leaves free (E62).
In `caption_pages`, `k` marks a keyword that takes the accent colour.

## Captions — a hard gate

> **A caption that swaps as a static block is a defect.**

- **STAGE mode when no dock is up** (E21; doc 29 §9.25, shipped P34 T5):
  centred in the frame (on a ledger page, in its quiet zone), 64px at 1080,
  weight 800; each word enters at its own spoken time, scale 1.16 → 1.0 with
  an alternating ±2.5° tilt settling in ~6 frames; keywords in the accent,
  the spoken word full white. Stage captions count as a visual event; gate
  M08 FAILs a still stretch over 12s that carries no stage page.
- **Under a card the caption keeps its size and MOVES** (E62, 2026-09-11) -
  to the band the page leaves free of the card. It drops to the quiet anchor
  only when no band holds two lines clear of the card and the data; that
  anchor's floor is 48px / 800 on a short. The punch is the size; a card is a
  reason to move, not to shrink. M25 refuses a caption in a card's box.
- Transparent glyphs plus text shadow. **No pill, no panel.** (A short's
  PHRASE style is its own - CAPABILITIES "PHRASE captions (shorts)".)
- Timings come from the word timings, never from beat boundaries.

Word-by-word model: group tokens into pages of **4-6 words** (`MAX_WORDS = 6`,
`CHAR_BUDGET` 34, a break on a gap over 0.60s - `build_caption_pages.py`,
operator 2026-09-01; gate M06 WARNs off that cadence); inside a page the
active token is the one where `token.start <= now < token.end`.

## Palette

**The chart field's inks are electric and high-contrast** (E67, 2026-09-12),
measured against the charcoal field (`#25313C`): teal `#34F5C5` · Claude
orange `#FF8A4C` (in the `crimson` token slot) · cobalt `#4FC3FF` · amber
fourth; the sign colours lift to `#3DDC84` up / `#FF4D4D` down. The live line
blooms in its own hue; muted history keeps the series hue at 0.45. **Grey is
never a default** - an undeclared series cycles teal, orange, cobalt, amber.
The chart is the thumbnail: a landing frame reads at 320px wide. The table of
record is `samples/scene-evidence-engine.mjs`. The 2026-08-30 dark-surface
tokens (crimson `#e5484d`, teal `#1fa892`, cobalt `#4a7fd6` on `#16181c`) are
superseded for chart inks; E67 does not restate the ink-grey, grid, baseline
or caption-accent tokens - read them from the engine, not from here.

**Two tiers.** The inks above are the GRAPHIC tier - chart lines, chips,
fills, where 3:1 contrast passes. Text on a dark pill needs 4.5:1; the retired
deep cobalt `#4a7fd6` failed it (2.4:1). Badge numerals and tags take the TEXT
tier: sunflower `#F5B72E` · coral `#FF8A70` · teal `#3BC9B0` · cobalt `#8FB3F0`
(5.7-7.4:1 on the charcoal pill - measured before E67, not re-measured). Never put a graphic-tier accent on text
over a dark ground.

## Verify before reporting

1. Every asset resolves **and opens as a valid image**.
2. **Zero uncovered frames** — no second without a plate.
3. No unresolved `{{placeholders}}` in the output.
4. Stillness: no stretch over 12s without a visual event (8s target), and
   every hold past 20s LIVES - its longest inner gap read by the gate (E21,
   E69).
5. Audio duration matches the timeline runtime.
6. **Open it and look.** A build that passes every check and renders black
   has passed nothing. Gate-clean is necessary and not sufficient: read the
   frames, and fix or write up every defect you can see, before a cut is
   offered (E71, 2026-09-12).


## The recorded-take chain (2026-08-30 — first full run)

Order: whisper gate → defended join → timeline → **kill dead space**
(`compress_dead_space.py --write`) → edit pauses (`insert_edit_pauses.py`
refuses an uncompressed timeline) → retime →
**topic-exit audit** → captions → scene build → choreography gates →
filmstrips. Tools for every stage live in `content/video_engine/scripts/`
(see CAPABILITIES.md). Three lessons the run burned in:

1. **A retime is half a migration.** Pinning docks to anchors moves
   enters correctly but carries OLD durations; and where the script
   reordered beats, whole plate stretches compress. Always follow with
   the enumerated topic-exit audit (E12) and expect close-region
   re-authoring when the script's structure moved.
2. **Anchors are enter-moments.** After re-staging, re-sync each dock's
   anchor to the sentence it now enters on — a stale anchor poisons the
   NEXT retime (one bad pin squeezed six close plates into 9 seconds).
3. **Gates only see what they model.** The clash class (same-slot
   overlap, >2 concurrent) was invisible until modeled; it caught a real
   overlap the same minute it was added. When the operator's eye finds a
   defect class, the fix ships WITH its gate.

**Audience units:** on-card figures in USD at a sourced spot rate (E14).
