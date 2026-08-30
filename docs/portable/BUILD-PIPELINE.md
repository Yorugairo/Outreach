# BUILD PIPELINE — portable contract

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
| 6 | **SHOT TABLE — AUTHORED** | narration + plate `semantic` fields + evidence `context` | plate, Ken Burns, docks and badge times per beat |
| 7 | Motion | the authored table | motion plan |
| 8 | Render | timeline + base64 assets | self-contained player |

## Stage 4 → 5: the take is ground truth

Word timings decide everything downstream. **Never resample captions onto
beat boundaries** — that collapses word-timed lines onto beats and the
captions drift off the narration.

A long episode records as **two chained parts** (the provider caps a single
request). Part two is conditioned on part one's request id so prosody
carries. To merge:

1. Offset = part one's **last word end** + a **1.2s settle**.
2. Discard the provider's trailing silence — any silence over 1.2s belongs
   to the editor's timeline, not the voice.
3. Join with **one re-encode pass** and a short crossfade. Never a raw
   concat of independently generated segments.
4. **Pause discipline (provider best practice):** the payload is REFLOWED —
   paragraph breaks only at section seams (~8–10 per part; every blank line
   is a pause and an intonation reset). Target **≈3 break tags per
   generation** (the provider's own working figure; excessive tags cause
   speed-ups and artifacts); never stack a tag against a paragraph seam.
   Em-dashes carry the micro-pauses. Longer silences are the editor's.

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

## The plate cadence (the default pattern)

One shape, repeated. It is easy to produce, easy to check, and it is what the
reference build looked like:

> **Two evidence pieces per plate, two badges each, a breath between them,
> then wipe.** If the plate cannot field two pieces that genuinely earn their
> place, it carries **one big piece** instead.

- **12-20s plate -> two pieces.** That is the hold the pair is sized for.
  Piece one settles, badges at +1.3s / +2.6s, **breath 1.1s**, piece two
  settles, **savour 2.2s**, wipe.
- **Cannot field two -> one solo card, wide.** Not two weak ones. A stat tile
  dragged in to make a count is worse than a single document with room.
- **Under ~8s -> one piece or none.** A pair cannot settle, badge and breathe
  inside a short hold; forcing it produces the strobing the breath exists to
  prevent.
- **Some plates carry nothing.** The world plate is doing the work and the
  narration is carrying itself. Not every beat needs proof on the glass.
- **Two badges per card is the target**, and a badge numeral must appear
  verbatim in the document behind it. A card with no badges leaves its whole
  information layer blank.

**Evidence that spans scenes persists.** It is authored once per scene it
covers, and the player coalesces those into one span: the card holds, the
world wipes underneath it. A card whose life ends at a scene boundary is part
of the outgoing page and the **wipe carries it off** - it is never faded on
its own schedule while the world slides, which reads as clipping.

## The density CHECK (operator rule) — run it against the authored table

- **One plate per 12 seconds of runtime, minimum.**
- **20 seconds is the absolute ceiling**, and only when **two strong
  evidence pieces of different species** cover that plate.
- Allocate `ceil(stretch_length / 12)` **per bare stretch**. The aggregate
  understates demand — each stretch needs at least one plate and partials
  round up.
- **Plates tile continuously.** A plate is the world layer; it persists
  under evidence and drifts while the evidence holds locked. It does not
  stop where evidence begins.

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
| dock entrance | 0.75s expo-out `cubic-bezier(.16,1,.3,1)`, translateY 32px, scale **0.88 → 1.00** |
| dock exit | 0.72s expo-out |
| wash fade | 0.75s |
| stat pill | 0.65s expo-out, translateY 12px |
| scene wipe | 0.62s quart-in-out |
| world parallax | scale 1.00 → 1.04 during the shot |

**Never scale from zero.** Scale-from-zero with bounce reads cartoon; the
document snaps into focus, it does not float in from space. **Settles are
slow, moves are fast.**

Cadence within a beat: world plate alone 1.7s → card settles → badges at
+1.3s / +2.6s → **settle 1.1s** → second card → **savour 2.2s** → wipe.

## Stage 8: render contract

The player takes a timeline document and an asset map:

```
{{TIMELINE}}  a scene_evidence_timeline.v1 document
{{URIS}}      { asset_id: "data:image/png;base64,…", "__audio__": "data:audio/mpeg;base64,…" }
```

**Assets are base64-embedded, not referenced by path.** A path-referenced
player renders black the moment it is opened anywhere but its own directory.

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
                     exit:  "wipe_right" | "cut",
                     span:  [start_s, end_s],
                     docks: [ { slide, slot, enter, exit, badge_at } ] } ]
```

A **scene owns its world plate and that plate's Ken Burns move.** Docks carry
a **semantic slot**: evidence roams by slot; the caption anchor never moves.
In `caption_pages`, `k` marks a keyword that takes the accent colour.

## Captions — a hard gate

> **A caption that swaps as a static block is a defect.**

- **One fixed lower-third anchor.** Evidence roams; the caption does not.
- Transparent glyphs plus text shadow. **No pill, no panel.**
- **Kinetic:** 2–4 word groups punch in ~0.34s apart, ease `power3.out`,
  scale 1.14 → 1.0, y 12 → 0. Keywords in the accent colour. Group timings
  come from the word timings, never from beat boundaries.
- **Quiet mode:** while a document holds the stage — smaller, static, single
  fade, keywords still coloured, **no punch-in**. Kinetic runs only when the
  caption is the **sole text layer on stage**; every evidence species carries
  text, so quiet engages for any docked evidence.

Word-by-word model: group tokens into pages by a time window (cap at 4 words
or ~1.2s, whichever binds first); inside a page highlight the active token
where `token.start <= now < token.end`.

## Palette (validated, dark surface `#16181c`)

crimson `#e5484d` · teal `#1fa892` · amber `#c98500` · cobalt `#4a7fd6`
Ink `#f2f2ef` / `#b9bcc4` / `#8b8f98` · de-emphasis `#6b6f78` ·
grid `#24262b` · baseline `#33363d`. Caption keyword accent: amber.

**Two tiers.** The values above are the GRAPHIC tier - chart lines, chips,
fills, where 3:1 contrast passes. Text on a dark pill needs 4.5:1 and deep
cobalt fails it badly (2.4:1). Badge numerals and tags take the TEXT tier:
sunflower `#F5B72E` · coral `#FF8A70` · teal `#3BC9B0` · cobalt `#8FB3F0`
(5.7-7.4:1 on the charcoal pill). Never put a graphic-tier accent on text
over a dark ground.

## Verify before reporting

1. Every asset resolves **and opens as a valid image**.
2. **Zero uncovered frames** — no second without a plate.
3. No unresolved `{{placeholders}}` in the output.
4. Worst bare-plate hold against the 12s target and 20s ceiling.
5. Audio duration matches the timeline runtime.
6. **Open it and look.** A build that passes every check and renders black
   has passed nothing.
