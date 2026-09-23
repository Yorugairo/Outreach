# History of BJJ Ep 1 — chapter build treatment: "Maeda Enters a Larger Brazilian Story"

Status: **draft treatment, read-only planning.** Not a build. No asset promoted, no gate set.

The operator, 2026-09-20, on the slice and the bar:

> *"one chapter subvideo of the landscape master. we should lower the evidence floor compared to
> finance, and improve the narrative/story telling aspect. Not EVERYTHING needs to be grounded in
> fact, sometimes a narrator can't let unimportant facts get in the way of an engaging story, but we
> need to maintain accuracy where possible."*

## Recall

- The chapter and its contract: `content/video_engine/projects/history-of-bjj/episode-1.json` (`status: research_ready`,
  3 chapters, 600 s landscape master, `chapter-maeda-and-the-belem-network` = 250 s).
- The narration under treatment: `episode-1-narration-v2.json` (`status: research_gate_revision`) — 7 segments,
  702 words, 7 `claim_refs`, all with `citation_refs` (Cairus, Penglase, Stanlei).
- The lane spec: `docs/content-video-engine/10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md:3` — editorial stands;
  **§4 visual modes and §5 editorial motion ownership are SUPERSEDED by 29 and 39.**
- The evidence bar, already calibrated per lane: `docs/portable/OPERATOR-RULINGS.md` **A5** — "Evidence precision —
  the *bar*, never the *system*… A history episode needs archival provenance and flagged contested interpretation."
- The production layer: **29** (evidence-motion standards), **39** (evidence chart system), **41** (ledger page species).
- The species available: `content/video_engine/scripts/species/` — `vecmap`, `flow`, `compare`, `record`, `thread`,
  `span`, `trace`, `chip`, `figure` (24 in total).
- `docs_find` **0 hits for "history lane rebuild"** — no prior treatment for this lane exists.
- **CORRECTION (2026-09-20, after a deeper search).** An earlier draft of this treatment claimed no build existed.
  That was wrong — the search covered only the main checkout's project dir, and the render lives in a
  **gitignored `.context` evidence root inside a dormant worktree**. The real artifacts are in §0 below.

---

## 0. What actually exists (found 2026-09-20)

A full episode draft was built **2026-07-31 → 08-03** in the dormant worktree
`.claude/worktrees/content-generation-system-52f077`, under the gitignored root
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/`.

| Artifact | Measured |
|---|---|
| `assembly/history-of-bjj-episode-1-block-assets-with-audio.mp4` | 1280×720, **15 fps**, 559.96 s, sha `49209c0f…` |
| `assembly/history-of-bjj-episode-1-draft-with-audio.mp4` | 854×480, 15 fps, 559.96 s |
| `assembly/block-plates-video.mp4` | **56 plates**, sha `e28210bf…` |
| `audio/canonical/history_episode_1_master.mp3` | ElevenLabs, sha `d6143a27…` |
| `animatic/editorial-beat-plan.json` | **138 beats**, 608.0 s, 15 parent scenes |
| `animatic/review-packet.json` | 137 cuts, **`approval_granted: false`** |
| `asset_selection/approved-review.json`, `entitlement.json` | asset approval + rights |
| `asset-promotion/v8…v12` (5 waves) | promotion history |

**This changes the shape of the work.** There *is* a structure to rebuild from — and it is far better than the
15 narration segments this treatment was first written against:

- **136 of 138 beats carry `citation_refs` AND `claim_refs`.** The episode is already fully citation-mapped
  at beat granularity.
- Each beat carries `function`, `duration_s`, `micro_events[]` (with `action`, `at_s`, `recipe`), `motion`,
  `motion_recipe`, `literature_mode`, and `narration_excerpt`.
- Beats per chapter: **kano 46 · maeda 59 · from-network 33**. Beat duration 2.28–5.96 s, mean 4.41 s.

The old `function` vocabulary maps almost one-to-one onto the new engine's species:

| old `function` | count | new species |
|---|---:|---|
| `migration_map_timeline` | 37 | **vecmap** ("a country that lights, an arc that crosses") |
| `archival_portrait` | 29 | plate + **record** |
| `lineage_graph` | 19 | **thread** / **flow** |
| `chapter_cta` | 13 | card / outro |
| `artifact_cold_open` | 12 | plate |
| `concept_mechanics_cutaway` | 11 | **flow** |
| `document_quote_closeup` | 9 | **record** (typewriter + highlighter, B5) |
| `illustrated_reconstruction` | 8 | plate, labelled as reconstruction |

**65 beats were always designed to be evidence documents** — 37 maps, 19 lineage graphs, 9 document quotes.
They were rendered as something weaker because the capability did not exist yet. It does now.

What the draft genuinely lacks is narrower than this treatment first assumed:

1. **Motion.** The manifest is explicit: *"Motion is a deterministic restrained push-in on the approved plates
   until provider clips are available."* That is Ken Burns — the exact defect the operator identified.
2. **Evidence rendering.** The 65 evidence beats exist as plans, not as engine species.
3. **Delivery spec.** 720p at 15 fps; the engine runs 1440p at 24 fps.
4. **Approval.** `approval_granted: false` — it is a draft, never a master.
5. **Voice.** The master is ElevenLabs; ruling **E70** leaves YouTube's voice OPEN ("not ElevenLabs by
   default either"). This is an operator decision, not a rebuild detail.

---

## 1. The diagnosis: the draft's protagonist is the historiography

The chapter is well-researched and citation-clean. It is also **not a story yet**. The narrator's subject is the
practice of history, not the people in it:

| The draft says | The problem |
|---|---|
| "Scholarship documents Japanese jiu-jitsu demonstrations…" | The agent is *scholarship*; the passive hides who acted |
| "The evidence is mixed, and a single winner would create more certainty than the sources allow." | This is a methods seminar, spoken aloud |
| "The responsible claim is narrower than the familiar legend and stronger because of that restraint." | The narrator is grading their own homework |
| "Cairus describes…", "scholarship also identifies…", "Cairus identifies him as…" | The scholars are the protagonists. Maeda, Carlos and Ferro are objects |
| "The historical task is to restore those stages where the evidence allows it." | Closes on the discipline, not the person |

Every one of those moves is *correct epistemics* and *wrong storytelling*. The draft spends its narration
budget performing uncertainty instead of telling the story of a man who crossed two oceans, fought in public
for money, and taught in a city built on rubber — while scholars argue about what exactly he handed over.

Sentence-level, it also breaks the standing voice rules: repeated `not X but Y` constructions
("not a sealed package", "more than a pin on a migration map", "a network is not a single arrow on a family
tree"), agent-hiding passives, and several sentences well past the 22-word ceiling.

## 2. The fix, and why it is the operator's own instruction

**Move the uncertainty off the voice and onto the screen.**

The narration currently carries two jobs: tell what happened, *and* disclose how confident we are. The new
production layer already owns the second job. Under 29 and 39, a docked evidence document carries provenance,
attribution and verbatim numerals — so the narrator no longer has to say "the evidence is mixed." A comparison
dock says it in one beat, with the sources named on it, and the narrator is freed to say what happened.

That is what buys the story room. The evidence floor drops because the disclosure no longer has to be *spoken* —
it has to be *shown*. The discipline is unchanged; the delivery moves.

## 3. The calibrated bar (proposed as a ruling)

Consistent with A5 — the bar is a dial, the system is invariant.

**What drops for the history lane:**

- Evidence *density* — fewer sourced facts per minute than finance
- The verbatim-numeral rule in narration — "about two hundred", not a sourced figure, when the number is scenery
- The audit beat — A4 caps it at one or two per *video*; for history, zero or one
- The falsifiable-tripwire tell — that is a finance instrument, not a documentary one
- Narration of the method — the epistemology belongs in the docks

**What holds, in every lane:**

- Every *stated* fact is true
- A contested claim is **framed as contested**, never asserted — this chapter has four
  (`first-teacher-status-contested`, `carlos-training-details-contested`, `jiujitsu-in-brazil-before-maeda`,
  `multiple-japanese-lineages`)
- A reconstruction is labelled as a reconstruction; it never reads as archival record
- No invented quote, document, date, name or figure
- Uncertainty is voiced where it is material to the claim, and shown where it is not

The line, stated plainly: **you may tell fewer facts, never a false one.** Composite scenes, dramatic
connective tissue and compressed detail are all licensed; a fabricated document is not.

## 4. The rows — segment to beat

The seven segments keep their order, their claims and their citations. What changes is who carries the
uncertainty and what the viewer sees.

| # | segment (scene) | claim | narration becomes | evidence species | the record |
|---|---|---|---|---|---|
| 1 | `brazil-before-maeda` (5) | `jiujitsu-in-brazil-before-maeda` | Open on the 1909 Rio contest as an *event*, not a corrective. The pre-existing scene is the hook: Brazil was already watching. | **record** — the 1909 press account, typewriter + highlighter (B5) | B5; the two citations are the document |
| 2 | `first-teacher-question` (6) | `first-teacher-status-contested` | Stop narrating the dispute. Let the dock hold it. | **compare** — the competing claims side by side, each with its source named | 39; A5 (flag contested interpretation) |
| 3 | `maeda-arrival` (7) | `maeda-satake-arrived-1914` | Make it physical: two men, a circuit, a crossing. Drop "not a sealed package". | **vecmap** — the route arcs land country by country (world-110m paths) | CAPABILITIES:104 |
| 4 | `belem-network` (8) | `maeda-reached-belem-1915` | Belém as a *place*: rubber money, theatres, a crowd that paid to watch. | **registered plate** + **span** (the rubber-economy window) | C7 (screens and boards set a room); B2 |
| 5 | `public-contest-context` (9) | `maeda-prizefighting-context` | The challenge hall versus the class — two rooms, two kinds of teaching. | **record** — a challenge notice / contest terms, verbatim | B5; C5 (diegetic composite) |
| 6 | `carlos-training` (10) | `carlos-training-details-contested` | Say what is known: Carlos was in the network. Qualify the shape once, not four times. | **thread** — the transmission, with the contested span marked | B6 (species variety); 39 |
| 7 | `ferro-intermediary` (11) | `jacyntho-ferro-role` | Land on the person the family tree deleted. This is the chapter's payoff. | **flow** — the teaching network, chips + clothoid arrows, Ferro as a node | CAPABILITIES:102; the chapter's own thesis |

Two structural notes. The chapter's emotional payoff is row 7 — *the man the lineage diagram erased* — and the
current draft buries it in a paragraph about visual grammar ("prevents the visual grammar of lineage from
deleting the intermediaries"). The flow dock does that work silently; the narration should spend the beat on
Ferro. And row 2 is the chapter's biggest saving: an entire segment currently exists to say "the evidence is
mixed," which a comparison dock says in one beat.

## 5. The count

Seven segments, seven claims, four contested. Under the current draft, uncertainty is spoken in **five** of
seven segments. Under this treatment it is spoken in **one** (row 6, where the shape of the handoff is the
subject) and shown in **three** docks. Runtime unchanged at ~250 s.

**Plate target:** the finance rule (C3, runtime ÷ 12 s) gives ~21 distinct world plates. For this lane the
operator is lowering the floor, so a calibrated target of **12–14 plates** is the proposal — the density
dial, applied. The operator rules the number.

## 6. What stays exactly as recorded

The research brief and packet, the episode contract, the three chapters, the 600 s target, the two shorts and
the chapter subvideos as planned outputs, and — **now that the draft has been found** — the whole editorial
layer: the 138-beat plan with its per-beat `claim_refs`/`citation_refs`, the 56 approved plates, the
`asset_selection/approved-review.json` + `entitlement.json` rights record, and the canonical audio master.

**The draft is never touched.** The old build lives in the dormant worktree's `.context` root; this chapter is
constructed into its own directory in the main checkout. The rebuild reuses the *editorial* layer and replaces
the *production* layer — motion, evidence species, resolution and frame rate.

One scope correction: this treatment's §4 rows were written against the 15 narration segments, because that was
the finest layer visible at the time. The real editorial unit is the **beat** — **59 beats** for the Maeda
chapter, not 7 segments. §4 stays valid as the *argument* and the species mapping; the row count is 59 and each
row inherits its `function`, `micro_events` and `motion_recipe` from the beat plan.

## 7. The hard bar before the operator sees a link

- Every docked document carries its source and date on the face of it
- Every contested claim is visibly marked as contested, on screen
- Every reconstruction is labelled as a reconstruction
- No numeral on screen that is not verbatim in its document (B3)
- M25 / M28 clean on every page; no plate under three seconds
- No light without a named target; cues bound to what fires
- Every world change probed at −0.3 / 0 / +0.6 s and **read on frames** before the link
- `recall_verify.py` passes on the production ledger before first compile (P67)

## 8. Open questions — the operator's, not mine

1. **Which chapter?** This treatment is written for `maeda-and-the-belem-network` (250 s, 7 segments, 702 words,
   4 contested claims) because it is the chapter where the story-versus-accuracy tension is highest and the
   payoff is strongest. `kano-system-before-brazil` (210 s, 4 segments) is the cleaner first proof if you would
   rather build the foundation first.
2. **Narration disposition.** Rewrite the prose and preserve the claim/citation map (this treatment's
   assumption), or preserve the prose and only re-layer?
3. **The calibrated bar.** Is §3 the ruling you want written into `OPERATOR-RULINGS.md`, and what is the plate
   number in §5?
4. **Lane voice.** C1 calibrates delivery style per lane. Is this its own history-documentary register, or a
   Martial Matters delivery?
5. **Asset promotion.** Everything in `assets/` is `review_only`. Promotion is the operator's action.
