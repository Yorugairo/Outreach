---
id: P55-THE-EFFECTS-CATALOGUE
title: The effects catalogue - every effect the engine performs, named, aliased, callable and proven, generated from the registries the compiler already asserts, with a drift gate and the first two inline effects promoted to modules
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-13
updated: 2026-09-13
---

# The effects catalogue

## Summary

The operator, 2026-09-13: *"what I want is for these effects to be easily referenced, for example, how would a different
agent know what to call the evidence wall, what it does, etc? is it a component or does it live as logic only?"* and
*"the inventory & effect catalogue. i would've told you thath we already have done this somewhere. The whole point of
upgrading the editor from the prior state was to begin building actual components and catalogues that other,
less-informed, and less-capable agents could use reliably"*. Not only for shorts: *"we should be able to do that too"*.

The triggering finding (parent, measured 2026-09-13): the evidence wall approved on Steel and Paper
(`SHOT-TABLE-F.py:136`, asset `ev-holds-stack-v1`, 701.73-727.63 s) is the VERDICT STACK - `drawStack` inline in
`docs/content-video-engine/samples/scene-evidence-engine.mjs` (:3720, its dock payload at :3232-3272, called at :10027);
the three-question TEST card is `if (C.checklist)` inside `drawChart` (:3587-3625). Neither is a module under
`content/video_engine/scripts/species/`. Neither has a golden frame.

All paths below are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`, head `5aa0f8f`). The
sweet-villani worktree this draft was written in is 432 commits behind and has none of these files.

### Recall (run before drafting, 2026-09-13)

- Recall: `sigmap_context.py query "species registry" --top 5` ranks `build_animation_registry.py` (`formula_md`,
  `render_md`) and `sync_kinetics.py` (`registrations_of`, `space_of`, `module_files`, `check`, `write`).
- Recall: docs_find 0 hits for "evidence wall", "test card", "effects inventory", "dock option", "species registry",
  "exit grammar", "enter grammar", "caption mode", "gallery", "press pile", "served proof".
- Recall: docs_find "verdict stack" = 3 hits: `29-EVIDENCE-MOTION-STANDARDS.md:1364` "9.24 The VERDICT STACK species
  (operator, s68, 2026-08-30)"; `CAPABILITIES.md:169` "VERDICT STACK species - N proofs fly in from depth over the world
  plate, word-matched"; the CAPABILITIES manifest line.
- Recall: docs_find "component library" = 1 hit: `GRILL-ANIMATOR-ITERATION-2026-09-11.md:52` "5. The horizon:
  AnimatorOS - we need like an 'AnimatorOS' where we start a component library + editor".
- Recall: docs_find "SPECIES_WHEN" = 4 hits: `SPECIES-BY-SENTENCE.md:1`, `:119` "4. The compiler's `when` on every kind
  (generated: `--when --md`; the test compares)", topic `species-when`.
- Recall: docs_find "module rule" = `CAPABILITIES.md:86` "SPECIES AS MODULES - the mechanism, WIRED (P50 T2 (A); the
  operator's module rule: each a module file inlined by the existing kinetics sync, never written into the template body)".
- Recall: docs_find "stack hand-off" = `CAPABILITIES.md:88` "The PRESS CARD dock and the STACK hand-off, WIRED".
- Recall: docs_find "SPECIES_PAINTERS" = `BACKLOG.md:447` "R26-41 One painter registry for PAGE species too".
- Recall: docs_find "golden frame" = `docs/runbooks/RENDER-REGRESSION.md:9` "PASS 4 golden frames identical".
- Recall: docs_find "STAGE mode" = gate M08 `gate_motion_density.py:1049` "doc 29 s9.25 caption STAGE mode".
- Recall: docs_find "blurzoom" = ANIMATION-REGISTRY dials only (`BLURZOOM_IN 1.10`, `BLURZOOM_S 0.27`,
  `BLURZOOM_SCALE 1.35` at engine :2447) - the dials are indexed, the EFFECT is not.
- Recall: docs_find "slide" = topic hits incl. `OPERATOR-RULINGS.md:2623` (E87: "Named `slide` ... Not built: BACKLOG R26-75").
- Recall: docs_find "typewriter" = `CAPABILITIES.md:19` "Record-document species - typewriter + per-word highlighter".
- Recall: BACKLOG `R26-81` "The three-question TEST card on a short (lifted, never used) - the engine already draws it
  (`scene-evidence-engine.mjs:3587-3625` `if (C.checklist)`) ... no frame of it is on disk".

### What already exists - the operator's "we already have done this somewhere", mapped exactly

| piece | what it covers | what it does NOT cover |
| --- | --- | --- |
| `SPECIES_WHEN` / `CHART_TO_WHEN` (`build_scene_timeline_f.py:291`, `:327`) with `assert set(SPECIES_WHEN) == set(SPECIES_KINDS) and set(CHART_TO_WHEN) == set(CHART_TO_KINDS), "every kind carries a when (P50 T1)"` (:352) | a one-line WHEN for every stage/page species kind (~31) and the five `chart_to` verbs; the only compiler-asserted "every token documented" rule in the repo | dock kinds (`image`/`video`/`cutout`/`press`), dock payloads (`record`, `chart`, `stack`), the 17 `DOCK_OPTS`, chart-dock forms (`checklist`, `shares`, `bars`, `log`), the 9 ledger `VARIANTS` (`ledger_page.py:64`), 8 `SCENE_EXITS`, 9 `LEDGER_ENTERS`, `LEDGER_EXITS`, `CAMERA_MOVES`/`CAMERA_EASES`/`CAMERA_ATTENTION`, 6 `IDLE_KINDS`, `ARRIVALS`/`MASSES`/`MORPH_SHAPES`, 9 `PLATE_OPTS`, `PLATE_USES`, caption modes (`stage`, `quiet`, page `caption: "anchor"`, `caption_style: "phrase"`) and `CAPTION_ARRIVALS`, `OVERFLOW_MODES`. No aliases, no authoring example, no code path, no proof, no status. |
| `lint_species_choice.py --when [--md] [--write-doc \| --check-doc]` + `SPECIES-BY-SENTENCE.md` s4 (generated between `SPECIES_WHEN` markers) + `test_lint_species_choice.py::test_every_kind_and_verb_carries_a_when` | the generated-doc pattern from compiler data, with a stale check; the ten sentence acts -> species | the same axes as the row above; the map is keyed by ACT, not by name - an agent holding a name ("evidence wall") cannot land on it |
| `docs/content-video-engine/CAPABILITIES.md` (305 lines, "Check this file before building anything", rows: what, where, state, proof, **Use when**) | prose rows for most built effects incl. the verdict stack (:169), press stack (:88), module rule (:86), exits (:63), idles (:64, :72), camera (:77-78), captions (:22-24, :40, :59) | hand-written, not validated: the verdict-stack row cites `samples/scene-evidence-player.template.html` (stackbox / drawStack) - P51 T1 moved the runtime to `scene-evidence-engine.mjs`, so the cited path is stale today; no aliases; no machine-readable form; not one card per effect |
| `docs/ANIMATION-REGISTRY.{jsonl,md}` by `build_animation_registry.py` (283 code, 175 dial, 352 formula records; status implemented/tracked/retired/orphaned) | every `export` of `kinetics/*.mjs`, the engine dial objects (`MARK`/`SP`/`LP`/...), every formula line in docs 29, 42-53, with a status and tests | effects: it indexes `BLURZOOM_S` but not "the blur-zoom exit"; its code read is `kinetics/*.mjs` (its own header), so `species/*.mjs` painters are outside its code records |
| `docs/GATES-REGISTRY.{jsonl,md}` by `build_gates_registry.py` | the generated-from-source registry pattern with `--write`/`--check`, doc cites resolved through `DOCS-INDEX.jsonl`, tests by id | gates only |
| `build_docs_layers.py` (`LAYERS` :52, 8 layers, write then check) + `docs_find.py` (`LAYERS` :119: manifest, index, topics, cites, gates, animation, craft) | the one retrieval every entry file routes agents to, with per-layer searched fields | no effects layer; no alias field on any layer except topics |
| The module rule: `species/*.mjs` (15 modules: agenda, breakthrough*, chip, countarray, flow, melt, newsreel, press, ring, span, thread, tiers, tippill, treemap, vecmap; *breakthrough lives in `kinetics/` region order), `sync_kinetics.py` (one name space over `kinetics/` + `species/`, `/* SPACE: page\|stage */`, `--check`), `SPECIES_PAINTERS` (engine :7010) and `PAGE_PAINTERS` (:606), `test_kinetics_sync.py`, `tests/kinetics/*.test.mjs` (29 files) | the COMPONENT form: header doc with WHEN and THE LAW, a frozen dials object, a painter registered as the last statement, a node test, a region | everything painted inline: `drawStack` (:3720), `drawChart` (:3769) incl. checklist/shares/bars, `drawRecord` (:3952), `paintPressCard`/`paintPress` (:2686, :2722), ledger builders `paintLedgerRace/Decline/Combo/Share` (:5004-5311), page perform `paintCross/Spread/Figure/Bracket/Perform` (:5800-5895), `paintMorph` (:5976), `paintLedger` enters (:6659-6685: morph, built, axes, snap, camera, drop, throw, mount), scene-loop transitions (:9829-9878: spiral, melt, snap, camera, throw, mount; dip/blurzoom/wipe/suck), the built-in `paintSpecies` kinds (:8924: punch, callout, spotlight, trace, ticker, ...), captions (:10218-10320) |
| Golden frames: `tests/test_golden_frames.py` `SURFACES`, `tests/golden/build_golden_sources.py`, `tests/golden/{sources,frames}` (32 sources, 44 frames incl. `species-proof@proof-{agenda,count,ring}` from `render_baseline.py:57-65`) | byte-identical proof for 32 surfaces; `species-proof` is already a one-clock multi-species proof player - the gallery precedent | no `verdict-stack`, no `test-card` / checklist, no record/typewriter, no exits other than melt, no page enters, no camera surface |
| P51 T0 authoring kit `content/video_engine/scripts/authoring/` (`words`, `docks`, `table`, `audio`; "one door for both formats") | the mechanism an episode pours facts into: `docks.dock_still/dock_clip/chart_card/record_words/...` | no name -> effect resolution; an agent must already know the tuple shape and the option key |
| P51 T7 thin editor `content/video_engine/editor/editor.html` (species panel :117, :450-456; dials section says "not editable yet") | lists a row's species by id and writes the sidecar | shows the kind token only - no card, no one-liner, no proof |
| P30 `configs/editor_component_catalog.schema.json` (`editor_component_catalog.v1`, closed, <= 128 components, kinds caption/text/annotation/teacher_stamp/world_plate/evidence_plate/shape/chart/remotion_bit) + `production_editor.py` | a component catalogue for the Remotion Production Console runtime | a DIFFERENT runtime (P51 Not Building: "The Remotion Production Console: a different runtime"); none of the scene-evidence engine's effects |
| `console/routes/catalog.py` + `templates/catalog.html` | the ASSET catalogue (`asset_catalog.load_catalog`, render_eligible / review_only) | effects - it is plates and cutouts, not motion |
| P51 "Not Building": "AnimatorOS (the component library + canvas + built-in agents ...): the horizon"; grill s5 "Not planned until P51 stands" | records that a component LIBRARY was asked for and deferred | any catalogue or library slice - this plan is the first |

**The gap, in one line:** the compiler knows every token it accepts; two of ~20 token families carry a documented WHEN;
nothing maps a human name to a token, a token to its code, or either to a proof; and the effects the operator approved
most visibly (the verdict stack, the test card) are the ones with no module, no golden and no card.

**A naming hazard the catalogue must resolve:** `stack` is three different effects today - the `stack` DOCK OPTION
(the press pile hand-off, `DOCK_OPTS`, doc 29 s9.27), the `stack` DOCK PAYLOAD (the verdict stack, doc 29 s9.24,
`ev.stack.items`), and the `stack` OVERFLOW MODE (a breakthrough bar stepping, `ledger_page.py:243`, E60). A name search
cannot tell them apart; card ids must be axis-qualified.

## Intent And Acceptance

Intent: a less-capable agent holding only a name (the operator's word, a past record's word, or the token) runs one
command and gets the effect's card: what it is, which sentence it serves, the authoring line that compiles, where it
lives, what governs it, its status and the frame that proves it - and the build fails the day the compiler and the
catalogue disagree.

Acceptance (all observable):

1. `python content/video_engine/scripts/docs_find.py "evidence wall"` prints the verdict stack's card as its first hit;
   `"test card"` prints the checklist card first; `"stack"` prints three distinct axis-qualified cards.
2. `docs/EFFECTS-CATALOG.jsonl` + `.md` are generated by `build_effects_catalog.py --write`, are one of the layers
   `build_docs_layers.py` writes and checks, and are never hand-edited.
3. The drift gate fails (with the token named) when: the compiler accepts a token on any inventoried axis with no card
   and no parent card listing it as an option; a card names a token the compiler does not accept (unless
   `status: planned` with a BACKLOG row); a card's code path or symbol is absent; a card's proof frame is absent; a card's
   authoring example is refused by the compiler's own validator for that axis; two cards share an alias.
4. `species/verdict.mjs` and `species/checklist.mjs` exist under the module rule; `sync_kinetics.py --check` passes; the
   golden surfaces `verdict-stack` and `test-card` are byte-identical before and after extraction; the Steel and Paper
   build-f player has been served and played at the stack (701.7-727.6 s) and the test card (492.3 s, 778.6 s) with frames
   read by the parent.
5. `python content/video_engine/scripts/effects_card.py "evidence wall"` prints the card with its example; the thin
   editor's species panel shows each species' card title, one-liner and proof link.
6. One routing line (no pack) in the entry files and `docs/agent-context/SKILL_ROUTER.md` points at the catalogue.

## Scope

- T1: a read-only inventory across every axis the compiler and engine accept (machine-readable + gap list + promotion rank).
- T2: the card schema and the name ledger (parent decision; operator gate on the operator-coined names).
- T3: the cards (data), the generator, the docs layer, the docs_find layer with aliases.
- T4: the drift gate (validator + tests), examples checked by the compiler's own per-axis validators.
- T5: reconcile the hand-written docs that already carry these facts (CAPABILITIES stale path, SPECIES-BY-SENTENCE s5).
- T6-T7: goldens first, then promote the verdict stack and the checklist to modules - sequenced behind the engine lanes.
- T8: the agent-facing surface (kit resolver + CLI + editor panel text).
- T9: a generated gallery page from the golden frames, if HG2 keeps it.
- T10: routing lines. T11: the ranked promotion queue as BACKLOG rows.

## Not Building

- AnimatorOS (canvas, built-in agents, asset pulls) - still the horizon (P51 Not Building; grill s5).
- A parallel prose doc of effects: the catalogue is generated; CAPABILITIES keeps its dated history rows and gains card
  ids, it is not duplicated.
- Moving any WHEN text out of `SPECIES_WHEN` / `CHART_TO_WHEN`: cards READ those dicts; the compiler stays the owner.
- Mass extraction of every inline painter: only the verdict stack and the checklist in this plan; the rest are ranked
  BACKLOG rows (T11), each its own slice later.
- Rendered clips per effect (renders cost and review builds are frozen copies): the gallery links a served proof player
  at a time, not an mp4.
- The slide transition (R26-75), the melt rework (R26-76), embed fit (R26-74 / E95), the caption blend (R26-77), race path
  and collision (R26-78/79), the agenda beautified (R26-80), the test card on a short (R26-81): cards record them
  (`planned` or their current status); this plan builds none of them.
- The P30 `editor_component_catalog.v1` (Remotion console runtime) and the asset `catalog.py`: untouched.
- Dial editing in the editor (editor.html: "the sidecar has no dials key").
- Packs in AGENTS.md: routing lines only.

## Human Gates

- **HG1 - the name ledger (operator, before T3 seeds the cards).** The canonical title and aliases for effects the
  operator named in conversation or review: "evidence wall" -> the verdict stack (`dock_payload:stack`); "test card" /
  "three-question test card" -> the checklist (`chart_dock:checklist`); and the three `stack` titles (the press pile, the
  verdict stack, the stepped overflow). The parent proposes from T1's alias column; the operator approves or renames. A
  name is the operator's vocabulary, not an agent's.
  **HG1 ANSWERED 2026-09-13 (the operator):** *"Agents will largely be the ones choosing effects, and your reccomendations
  so far make sense so i trust you to make reasonable decision for the stack names also, approved."* The names, fixed by
  the parent under that delegation: `dock_payload:stack` = **The verdict stack** (aliases: "evidence wall", the
  operator's "pull back in all of our evidence cards"); `chart_dock:checklist` = **The test card** (aliases: "checklist",
  "three-question test card", "test list"); `dock_option:stack` = **The press pile** (aliases: "press stack",
  "stack hand-off"); `overflow:stack` = **The stepped overflow** (aliases: "overflow stack"). Titles for every other
  card: the doctrine's own heading wording (doc 29 / CAPABILITIES / OPERATOR-RULINGS), the parent's call - agents are the
  main readers, so a title is chosen to be unambiguous across axes, and every older name survives as an alias.
- **HG2 - the gallery earns its keep (operator, after T9's first served page).** One read of the generated page on the
  review server; keep, trim, or retire T9. Nothing else in the plan depends on it.

Parent decisions (not operator gates; recorded here so they are not re-litigated): the card schema and file layout (T2,
proposed below); whether a dock painter gets a third registry or a direct call (T7, proposed: direct call first); the
engine-lane order (Execution Path).

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Lane write sets, Hand-off policy, PRP Format).
- `content/video_engine/scripts/build_scene_timeline_f.py`: the axis tuples :55-102, `DOCK_OPTS` :89, `SPECIES_KINDS`
  :187-342, `PAGE_SPECIES` :260, `CHART_TO_KINDS` :262, `SPECIES_WHEN` :291, `CHART_TO_WHEN` :327, the assert :352,
  `CAMERA_*` :360-386, `validate_camera` :457, `validate_species` :1222, `parse_ledger_id` :1281, `parse_exit` :1380,
  the dock-option normaliser (:2280-2335, raises `dock: stack must be True`), `assign_press_stack` :3423, the dock entry
  with `stack`/`record`/`chart` payloads :3975-4000. (Line numbers drift under the melt lane; cards anchor on symbols.)
- `content/video_engine/scripts/ledger_page.py` `VARIANTS` :64, `OVERFLOW_MODES` :243, `UNCHARTABLE` :85.
- `docs/content-video-engine/samples/scene-evidence-engine.mjs`: the dock payload :3232-3272, `drawStack` :3720,
  `drawChart` checklist :3587-3625, `drawRecord` :3952, `PAGE_PAINTERS` :606, `SPECIES_PAINTERS` :7010, `paintSpecies`
  :8924, the scene loop's enters/exits :9829-9878, captions :10218-10320.
- `content/video_engine/scripts/sync_kinetics.py` (header: the module rule and THE SPACE), `species/chip.mjs` (header pattern).
- `content/video_engine/scripts/build_gates_registry.py` (generated-from-source pattern), `build_animation_registry.py`
  (header), `build_docs_layers.py` `LAYERS`, `docs_find.py` `LAYERS`.
- `content/video_engine/scripts/lint_species_choice.py` (`--when`, `--write-doc`, `--check-doc`) and its test.
- `tests/test_golden_frames.py`, `tests/golden/build_golden_sources.py`, `scripts/render_baseline.py` (`species-proof` :57-65).
- `docs/content-video-engine/CAPABILITIES.md` :86, :88, :169; `SPECIES-BY-SENTENCE.md` s4, s5; doc 29 s9.24, s9.27, s9.28.
- `docs/portable/OPERATOR-RULINGS.md` E47, E48, E49, E56, E60, E87, E88, E93, E95.
- `docs/content-video-engine/BACKLOG.md` R26-74..R26-81; `.claude/PRPs/plans/P51-THE-ANIMATORS-LOOP.plan.md` T0, T7, Not Building.

## Execution Path

1. **Read first.** T1 (explorer) inventories; nothing is written to the product until the parent has the table.
2. **Decide.** T2: the parent fixes the schema below against T1's rows; HG1 fixes the operator-coined names.
3. **Build the catalogue off the contended files.** T3 then T4 (implementation_luna) write only NEW files plus
   `build_docs_layers.py` / `docs_find.py` (neither is in the melt lane's dirty set). They IMPORT the compiler read-only.
   T5 (parent, Claude doc lane) and T8 (luna) run after T3 on disjoint files.
4. **Engine work waits its turn.** On 2026-09-13 main carries the melt lane uncommitted in `build_scene_timeline_f.py`,
   `species/melt.mjs`, `render_baseline.py`, `tests/golden/build_golden_sources.py`, `tests/test_golden_frames.py` and
   golden sources; R26-74 (embed fit, "after the melt lane frees the compiler") follows it. T6 and T7 touch exactly those
   files, so they take the engine slot AFTER R26-76 and R26-74 commit, and BEFORE R26-81 and R26-80 - both of which build
   on the checklist (R26-81 lifts it onto a short; E93/R26-80 make it the agenda's model), so they should consume the
   module, not the inline branch. R26-75 (slide), R26-77 (caption blend) and R26-78/79 (race) touch other engine regions;
   the parent serialises engine writers one at a time regardless (one file, one writer), and rebases the card rows of
   whatever lands first.
5. **Surface.** T9 after T6's goldens exist; T10 after T3 and T8; T11 after T7.

### The card schema (T2 proposal - the parent confirms or amends)

One card per EFFECT. A token that is a parameter of an effect (a mass, an ease, a camera attention, a melt ending) is
listed in its parent card's `options`, not given its own card - the drift gate accepts a token that is a card name OR a
listed option. Cards live as data, one JSON file per axis (fewer merge collisions: a lane adding an exit edits one
file): `content/video_engine/effects/cards/<axis>.json`, validated by `content/video_engine/configs/effect_card.schema.json`.

```
id            "<axis>:<token>"  e.g. "dock_payload:stack", "dock_option:stack", "overflow:stack", "exit:blurzoom"
axis          species | page_species | chart_to | page_builder | dock_kind | dock_payload | chart_dock | dock_option |
              exit | page_enter | page_exit | camera | idle | arrival | plate_option | caption | overflow | kinetics
token         the authoring key exactly as the compiler accepts it
title         the canonical human name ("The verdict stack")                 [HG1 for operator-coined]
aliases       every name people and records use ("evidence wall", "nine-proof wall")  - unique across the catalogue
does          one sentence, what the viewer sees
when          PULLED from SPECIES_WHEN / CHART_TO_WHEN for those axes (never copied); authored for the others
serves        the acts from SPECIES-BY-SENTENCE s1 (QUOTES, RANKS, ...) - optional
author        {"example": "<a literal shot-row fragment>", "check": "<validator id: species|exit|enter|dock|camera|plate|chart>"}
phases        a COMPOSITE effect's arc in order, read from the painter code: [{name, does, trigger, dials}]; empty for a
              single-phase effect; `does` summarises the WHOLE arc (T2 amendment, operator correction 2026-09-13 below)
blends        the references it fuses, each tied to the phase it became: [{source, became, record, tie: recorded|inferred}]
options       the parameter tokens this effect takes, each with a one-line meaning
dials         {"module": "<path>", "object": "<FROZEN_NAME>"} - values pulled at build, never written on the card
lives         {"form": "module | inline | compiler-only | declared-unbuilt", "path": "...", "symbol": "..."}
doctrine      ["29 s9.24", "E60", ...] - resolved to path:line through DOCS-INDEX at build, like GATES-REGISTRY cites
status        live | wired | draft | declared | planned | retired  (+ "backlog": ["R26-75"])
implicit      true when the effect has no token (decision 3); lives.also / lives.note (decision 4)
proof         {"golden": "<surface or frame>", "test": "<test id>", "first_use": {"project", "build", "t"}}
callable      {"today": true|false, "why": "<one line when false>"}
```

The generator joins the card files to the compiler's tuples (the key-set truth), the `*_WHEN` dicts, the module dials
and DOCS-INDEX, and writes `docs/EFFECTS-CATALOG.jsonl` (the searched layer: `id`, `title`, `aliases`, `does`, `token`)
and `.md` (grouped by axis, with a header recipe like the animation registry's). The compiler never imports the cards.

**T2 amendment - composite effects keep every phase (operator correction, 2026-09-13).** The draft's verdict-stack line
was CAPABILITIES' one-liner ("N proofs fly in from depth"). The operator: *"it soudns like your verdict stack is very
limited, are you ignoring the other effects we blended in? we didn't just fly them in - we flew them in, 1 at a time,
dancing with choreography, spread assigned them around the page, then burst them out"* and *"thats why i pointed out to
you that what we did was based off ~3 different remotion-bits effects"*. The record agrees: `drawStack` is ENTER (one at a
time from depth on each verbatim beat) -> FOCUS (large near centre while its phrase is spoken, drifting) -> RECEDE (to one
of nine asymmetric rail spots when the next beat lands; the page re-composes as a mosaic) -> IDLE (railed cards float)
-> BURST (radial along each card's own bearing on the pivot line, spinning, 60 ms stagger); the operator's references of
2026-08-31 (`docs/operator-ledger/LEDGER.jsonl` `ddc90e1656f9`) were remotion-bits `transform3d-showcase`,
`fracture-reassemble`, `mosaic-reframe` and the `hyperframes-opening-v1` pilot (doc 29 s9.24b, commits 270b131, 680debd,
d0eeaba; the portable extraction `docs/portable/MOTION-GRAMMAR.md`). So every card carries `phases` and `blends`, the
drift gate FAILs a card whose painter has more than one phase in its T1 row but an empty `phases`, and `effects_card.py`
prints the phases. Memory: `composite-effects-keep-every-phase`.

**T2 parent decisions (2026-09-13, from T1 group C's rows and gaps; recorded so they are not re-litigated).**

1. **Status.** `live` = used in a table the operator approved or shipped (today: `japan-tariff-trick/SHOT-TABLE-SHORT.py`, APPROVED at `japan-tariff-trick/REVIEW-CLAUDE.md:5`; Steel and Paper `SHOT-TABLE-F.py`, shipped) or a compiler default every build runs (`exit:cut`, `page_exit:cut`, `camera_attention:locked`); `live` ALSO covers a cut whose render carries an operator approval record (AMENDED 2026-09-13 on the evidence: `tokyo-tea-break/build-short.v2/render/APPROVALS.json`, `approved_by: operator`, 2026-09-06 - the published Tokyo short; effects first used there are live, the later Tokyo remake builds are the test bed); `wired` = compiles and paints, used only in a test bed (Tokyo) or an unready build (the bridge short); `draft` = its lane is uncommitted (the melt, R26-76); `planned` = a BACKLOG row, not built (`exit:slide`, R26-75); `declared` = named in doctrine, no painter.
2. **Collisions.** The same token on two axes is two cards (`page_enter:throw`, `melt_ending:throw` - an option of `exit:melt` - and the dock arrival `throw`); every title names its axis in words ("The throw page enter", not "Throw"); an alias is unique across the catalogue, so a name that means several things ("push", "peel", "mount", "vortex", "hold", "snap") is an alias of NONE and is resolved by `effects_card.py` printing every card whose token or title contains it.
3. **Implicit effects.** An effect with no token (the default page VORTEX retract; the chart-to-chart stamps `enter=axes` / `enter=built` / `exit=cut` from `stamp_transition_pages`) gets a card with `implicit: true`, a slug token (`page_exit:retract`, `page_enter:stamped`), and an `author.example` that is the row producing it.
4. **Anchors.** `lives.symbol` is ONE identifier the drift gate greps in `lives.path` (dotted allowed); further identifiers go in `lives.also`, prose in `lives.note`. T1 rows' free-text symbols ("render / THE DIP block + dipIn/dipOut") are split by T3.
5. **Shape.** `phases[].dials` is a name -> literal-string object (as T1 wrote it); `blends[]` T1 rows `{name, source}` map to `{source: name + source, became: <the phase>, record, tie}` - T3 fills `became` from the phases, `tie: inferred` when no record names it.
6. **Stale doctrine found by T1 (T5's list; compiler comments queue behind the melt lane as a BACKLOG row).** `CAPABILITIES.md` rows at :35 (`melt:splash` grammar, refused since E88), :50, :69, :77 (cite the template; the runtime is `scene-evidence-engine.mjs`), :57 (THE DANCE cross-fade, retired R26-50, `lpDance` exists nowhere), :169 (the verdict stack's template path and its one-liner); doc 29 :2128 and :2137 (the same DANCE and `lpDance`), :986 (the pre-E47 mechanical default); `build_scene_timeline_f.py` :55 (`enter = spiral | mount=<seconds>` - 9 enters), :77 (`melt:splash`), `scene_exit`'s docstring ("dip when the scene carries docks" - the code keys on `world_changed`); `steel-and-paper/SHOT-TABLE-F.py:10` (pre-E47 docstring, a shipped table: annotate, never rewrite). From group A: `CAPABILITIES.md` :64 (`IDLE_CLASS`/`idleOf`/`idleCssFor`), :67 (`capFrac`/`buildPerform`/`paintBracket`/`paintPerform`), :111 (`morphProp`/`buildMorph`/`paintMorph`) cite the template for symbols that live only in the engine; :72 "Idle `live`: nothing truly still, WIRED" is false today (R26-93); `SPECIES-BY-SENTENCE.md:169` lists the art-embed plate and the continuity three as unbuilt while CAPABILITIES :31/:99 and their goldens say WIRED; `SHOT-TABLE-F.py:16` lists ten species kinds (35 today) - annotate.
7. **Two goldens pytest never checks.** `ledger-extend.png` and `ledger-keyed.png` are in `build_golden_sources.py` SURFACES but not in `tests/test_golden_frames.py` SURFACES, so `chart_to:rescale` / `chart_to:extend` cite a proof nothing verifies. T6 adds both to the pytest SURFACES (its file, its slot) and confirms they still match; until then those cards carry `proof.golden` with `proof.test: null` and the drift gate treats an unchecked golden as no golden.
8. **The regression T1 found - R26-93.** `idle=live` is accepted by the compiler and painted by nothing since 235832a deleted the inline branch 72b7516 had added outside the module (the approved Japan short's six `;idle=live` pages would hold still on a rebuild). Fixed ahead of T6 as the engine's next writer after E95, with the missing gate: every compiler `IDLE_KINDS` token must exist in `kinetics/idle.mjs`. The card `idle:live` stays `live` with `backlog: ["R26-93"]` until the fix lands. The same class - a compiler tuple token with no painter - is exactly what the T4 drift gate's "lives.symbol found" check must catch for every axis (group A also found `beat_freeze`, `radial` and `push` compile with no painter; `progress` is never returned by `pick_builder`; no engine branch reads the `object` variant).

## Patterns To Mirror

- `build_gates_registry.py` / `build_animation_registry.py`: stdlib only, deterministic, LF, `--write` / `--check`, the
  recipe as the generated file's header, cites resolved through `docs/DOCS-INDEX.jsonl`.
- `lint_species_choice.py --check-doc` and the assert at `build_scene_timeline_f.py:352`: "every token documented" as a
  test, not a convention.
- `build_docs_layers.py` `LAYERS` entry + `docs_find.py` `Layer(name, path, fields)` entry.
- The module rule (`sync_kinetics.py` header; `species/chip.mjs`): header doc with WHEN and THE LAW, a frozen dials
  object, `/* SPACE: ... */` when it paints in a registry, a node test under `tests/kinetics/`, region order = dependency.
- `tests/test_golden_frames.py` `SURFACES` + `build_golden_sources.py` + `render_baseline.py --update`: a golden is
  committed from the CURRENT code before a refactor, and the refactor keeps it byte-identical (P50 T2 (A): "every built-in
  kind's branch is untouched (the goldens byte-identical)").
- `render_baseline.py` `species-proof@proof-*` (several species on one clock, frames at named instants): the gallery.
- Memory anchors, never line numbers, on cards (`path | symbol`).

## Task Slices

### T1: The inventory - every effect across every axis (read-only)
- Status: complete
- Owner: explorer
- Depends on: none
- Write set: `docs/research/runs/p55-effects-inventory/inventory.jsonl`, `docs/research/runs/p55-effects-inventory/gaps.md` (gitignored disk-as-bus, the return contract; if the harness refuses the write the parent saves the returned pack there)
- Acceptance: one JSONL row per token the compiler accepts on every axis listed in the Summary table (`SPECIES_KINDS`, `PAGE_SPECIES`, `CHART_TO_KINDS`, ledger `VARIANTS`, `DOCK_KIND_*`, dock payloads `record`/`chart`/`stack`, chart-dock forms `checklist`/`shares`/`bars`/`log`, `DOCK_OPTS`, `SCENE_EXITS`, `TIMED_EXITS`, `MELT_ENDINGS`, `LEDGER_ENTERS`, `LEDGER_EXITS`, `CAMERA_MOVES`/`EASES`/`ATTENTION`, `IDLE_KINDS`, `ARRIVALS`, `MASSES`, `MORPH_SHAPES`, `PLATE_OPTS`, `PLATE_USES`, caption modes and `CAPTION_ARRIVALS`, `OVERFLOW_MODES`, the 14 kinetics modules) plus the planned `slide` (R26-75); each row: axis, token, proposed title, aliases found in records (quote the record path), does, where it lives (module path + region, or engine symbol, or compiler-only, or declared-unbuilt - e.g. `beat_freeze`, `radial` per SPECIES-BY-SENTENCE s5), authoring key + a minimal row copied from a shipped shot table, doctrine/rulings, status, proof (golden surface or test or first use with project/build/t), callable-today with why; `gaps.md` lists tokens with no WHEN, no proof, stale doc paths (CAPABILITIES :169 is one), name collisions (`stack` x3), and a promotion rank of inline painters by use count x approval x size. Every count and path copied from disk, "not found in <places>" for negatives.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import json,sys; rows=[json.loads(l) for l in open('docs/research/runs/p55-effects-inventory/inventory.jsonl',encoding='utf-8')]; print(len(rows), sorted({r['axis'] for r in rows}))"` (from the main checkout; the parent then greps three random paths)
- Evidence: three read-only explorers (groups A species/builders/idles/kinetics, B docks/plates/captions, C exits/enters/camera) wrote `docs/research/runs/p55-effects-inventory/inventory-{A,B,C}.jsonl` = 84 + 56 + 34 = 174 rows and `gaps-{A,B,C}.md` (deviation: three files instead of one, parallel by axis group). Validate runs: A `84 ['arrival', 'chart_to', 'idle', 'kinetics', 'mass', 'morph_shape', 'overflow', 'page_builder', 'page_species', 'species']`; B `56 ['caption', 'caption_arrival', 'chart_dock', 'dock_kind', 'dock_option', 'dock_payload', 'embed', 'plate_option', 'plate_use']`; C `34 ['camera_attention', 'camera_ease', 'camera_move', 'exit', 'melt_ending', 'page_enter', 'page_exit', 'timed_exit']`. Parent spot-check: every `lives.path` exists (A 0 problems, B 1 free-text symbol, C 2 dotted symbols - decision 4); rows read in full for `exit:dip`, `page_enter:spiral`, `melt_ending:splash:plate`, `species:trace`, `idle:live`, `overflow:stack`, `dock_payload:stack` (5 phases, 4 blends), `chart_dock:checklist` (5 phases), `dock_option:stack`. Mid-slice operator correction: composite effects keep every phase (the T2 amendment) - all three explorers re-read their painters and added `phases`/`blends`. Defects found: R26-93 (`idle=live` paints nothing, traced by the parent to 235832a), `cutout` dock option KeyError (group B gap 1, reproduced by the parent). Promotion rank (for T11): group A `trace` 476 > `spotlight` 320 > `callout` 306 > `figure` 204; group B the checklist branch 488 > `drawRecord` 140 > `drawStack` 91 (the plan's guess that the record heads the queue does not hold); group C `page_enter:spiral` 195 > `exit:dip` 180 (mount/cut scores inflated by the shared `paintLedger`).

### T2: The schema and the name ledger
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/configs/effect_card.schema.json`; this plan's schema section (amended in place)
- Acceptance: the schema above confirmed or amended against T1's rows; every T1 token assigned to a card or to a parent card's `options`; HG1 answered for the operator-coined names and recorded verbatim here.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import json; json.load(open('content/video_engine/configs/effect_card.schema.json',encoding='utf-8')); print('schema ok')"`
- Evidence: `content/video_engine/configs/effect_card.schema.json` (`effect_cards.v1`, Draft 2020-12, `check_schema` passes; card fields id, axis, token, title, aliases, does, when, when_source, serves, author, phases, blends, options, dials, lives {form, path, symbol, also, note}, doctrine, status, backlog, proof, callable, implicit); HG1 answered by the operator (delegated, recorded verbatim under Human Gates); the T2 amendment (phases + blends, the operator's correction); T2 parent decisions 1-8 (status, collisions, implicit effects, anchors, shape, stale doctrine, unchecked goldens, R26-93). Group B adds to decision 6: `CAPABILITIES.md` :19, :60, :170, :189 also cite the template (CSS-only now); `SPECIES-BY-SENTENCE.md:90` says `;use=` is unwritten (it ships); doc 29 s9.24 (:1375) and BACKLOG R26-82 give the stack's enter depth as translateZ -940 while `drawStack` uses -700 (T7 lifts the CODE's value; the doc is corrected in T5).

### T3: The cards, the generator, the docs layer
- Status: complete
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/effects/cards/*.json`, `content/video_engine/scripts/build_effects_catalog.py`, `docs/EFFECTS-CATALOG.jsonl`, `docs/EFFECTS-CATALOG.md`, `content/video_engine/scripts/build_docs_layers.py` (one `Layer` entry), `content/video_engine/scripts/docs_find.py` (one `Layer("effects", "docs/EFFECTS-CATALOG.jsonl", ("id", "title", "aliases", "does", "token"))` entry, first in order), `content/video_engine/tests/test_build_effects_catalog.py`
- Acceptance: cards seeded from T1 with HG1's names; `--write` deterministic (two runs, identical bytes); `--check` exits 1 when stale; `when` pulled from the compiler dicts, dials from the module objects, cites resolved through DOCS-INDEX; `build_docs_layers.py --check` reports every layer in sync (9 layers); `docs_find.py "evidence wall"` first hit = `dock_payload:stack`, `"test card"` = `chart_dock:checklist`, `"stack"` = three cards; the compiler file is not modified.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_build_effects_catalog.py -q && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/docs_find.py "evidence wall"`
- Evidence: (2026-09-13) `content/video_engine/effects/cards/` 18 axis files, 125 cards schema-valid (species 23, page_species 12, chart_to 5, page_builder 11, overflow 2, idle 6, arrival 3, kinetics 14, dock_kind 4, dock_payload 3, chart_dock 5, dock_option 7, plate_option 6, caption 3, exit 8, page_enter 10, page_exit 2, camera 1); 49 parameter tokens folded as options; implicit cards `page_exit:retract`, `page_enter:stamped`; `camera:keys` added (six rows named it as a parent); 52 dials objects read; 261/274 doctrine cites resolved (13 null: compiler comments and unindexed memory files); `AMBIGUOUS_NAMES` holds 9 names dropped as aliases + decision 2's six. `build_effects_catalog.py` (`--write`/`--check`), `docs/EFFECTS-CATALOG.{jsonl,md}`, `build_docs_layers.py` gains the effects-catalog layer (`every layer in sync (9 layers)`), `docs_find.py` gains the effects layer first; `test_build_effects_catalog.py` + the layer pins in `test_docs_find.py` / `test_build_docs_layers.py`: 57 passed. docs_find: "evidence wall" -> `dock_payload:stack` first, "test card" -> `chart_dock:checklist` first, "stack" -> the three stack cards. Parent review: the effects layer takes 3 of docs_find's 20-hit budget, so a fourth card saying "stack" would push one out - `effects_card.py` (T8) is the reliable resolver, docs_find the discovery. Judgement calls reviewed: `camera_move` rows merged into the `species:punch|focus_zoom|pull_back` cards (camera moves are species kinds) - kept; "the STACK hand-off" alias moved off `species:push` - kept; Tokyo-first-use cards downgraded to wired - REVERSED by the parent (decision 1 amended: the v2 cut's render is operator-approved). Parent corrections after landing (`scratchpad/p55/card_updates.py`, `card_fix2.py`): the verdict stack and the test card -> their T7 modules + T6 goldens + node tests; `idle:live` -> restored module, callable (R26-93); `dock_option:cutout` -> callable (R26-94); `dock_option:embed` `fit:cover` -> the E95 default for a bare still or clip; `exit:melt` -> look pass 3 accepted, still draft (uncommitted).

### T4: The drift gate
- Status: complete
- Owner: implementation_luna
- Depends on: T3
- Write set: `content/video_engine/scripts/effects_catalog_check.py`, `content/video_engine/tests/test_effects_catalog_drift.py`
- Acceptance: the test fails, naming the token or card, for each of: a compiler token with no card and no parent option (proved by monkeypatching a tuple with a fake exit); a card token the compiler does not accept and not `planned` with a BACKLOG row; a `lives.path` absent or `lives.symbol` not found in that file; a `proof.golden` absent under `tests/golden/frames` or `SURFACES`; an `author.example` refused by the axis validator (`validate_species`, `parse_exit`, `parse_ledger_id`, the dock-option normaliser, `validate_camera`, ledger `VARIANTS`/`UNCHARTABLE` for chart forms) - each broken on purpose in a tmp copy; a duplicate alias. It passes on the committed catalogue. The check is imported by `build_effects_catalog.py --check`, so `build_docs_layers.py` carries it.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_build_effects_catalog.py content/video_engine/tests/test_lint_species_choice.py -q`
- Evidence: (2026-09-13) `content/video_engine/scripts/effects_catalog_check.py` (459 lines; `check_coverage` over one `SOURCES` axis->compiler-tuple table, `check_phantoms`, `check_anchors`, `check_proof` against the CURRENT pytest SURFACES + FLAG_FRAMES + PROOF_FRAMES, `check_examples` through the compiler's own validators with a printed SKIPPED_EXAMPLE list (never a silent pass), `check_aliases`, `check_phases` against the inventory rows (skipped with a note when the gitignored inventory is absent), `check_when`); `content/video_engine/tests/test_effects_catalog_drift.py` (323 lines) breaks each on purpose: a fake exit `zzz_fake` in SCENE_EXITS, a wired phantom vs a planned card with a backlog row, a renamed symbol, a missing `also` and path, `golden: zzz-missing`, a golden on disk but outside SURFACES, a missing test function, an exit example `melt:splash`, a species example `validate_species` refuses, an unparseable example listed as skipped, a duplicate alias "Evidence  Wall", an alias equal to a title, a composite card that lost its phases, a species card copying its WHEN, a kind with no WHEN entry; `build_effects_catalog.py` `main` calls the gate on every non-`--write` run (`test_build_effects_catalog_check_exits_1_on_drift`) and `test_the_committed_catalogue_passes_every_check`. Real drift T4 fixed in cards (only `author.example`, from each card's own `example_source`): `exit:cut`, `exit:dip`, `exit:melt`, `exit:suck` (full 6-element rows), `dock_option:read`, `plate_option:then`, `species:ticker`, `overflow:burst`, `overflow:stack`. Acceptance pytest 57 passed; the gate 0 failures, 16 examples skipped (13 sent back to be rewritten as copyable literals - a builder expression or a fragment is exactly what a less-capable agent would copy and fail on). Layers: `every layer in sync (9 layers)` on its third pass (the index went stale between passes while the parent edited the plan - finding 1's exclude closes the catalogue half of that).

### T5: The hand-written docs point at the cards
- Status: complete
- Owner: parent
- Depends on: T3
- Write set: `docs/content-video-engine/CAPABILITIES.md` (the rows naming an effect gain its card id; the verdict-stack row's stale template path corrected), `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (s5 cites card ids; s4 untouched - it stays generated)
- Acceptance: `rg "scene-evidence-player.template.html \(stackbox" docs/content-video-engine/CAPABILITIES.md` returns nothing; every card id cited in the two docs exists in `docs/EFFECTS-CATALOG.jsonl`; `lint_species_choice.py --when --check-doc` still exits 0.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/lint_species_choice.py --when --check-doc && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py`
- Evidence: (2026-09-13, `scratchpad/p55/t5_docs.py`, parent) `CAPABILITIES.md` 16 edits: 13 rows citing the retired `scene-evidence-player.template.html` now cite `samples/scene-evidence-engine.mjs` with card ids; the verdict-stack row rewritten to the five phases + the operator's references and disambiguated from `dock_option:stack` / `overflow:stack`; THE DANCE marked retired (R26-50); `idle:live`'s regression and restoration (R26-93); the melt grammar `melt[:throw|:splash:chart|:splash:plate][:<s>][:<x>,<y>]` verified by calling `parse_exit`. `SPECIES-BY-SENTENCE.md` 3 edits: row 15's `;use=` ships (card `plate_option:use`), s5's art-embed plate and continuity three moved to "built since", beat-freeze/radial/push marked compile-with-no-painter. Deviation: doc 29 s9.24's enter depth -940 -> -700 (the code). 20 card ids cited, every one asserted present in the catalogue.

### T6: Goldens first - the verdict stack and the test card as they draw today
- Status: complete
- Deviations (parent, 2026-09-13): (1) T6 does NOT write `effects/cards/dock_payload.json` / `chart_dock.json` - T3 is writing the card files concurrently, so the parent fills both `proof.golden` fields after T3 and T6 land (one file, one writer); (2) T6 also adds decision 7's `ledger-extend` and `ledger-keyed` to the pytest `SURFACES`; (3) the burst is a named instant `verdict-stack@proof-burst`; (4) T6 builds from the engine's CURRENT inline code on the uncommitted tree (the writer-serialised queue, see Evidence And Handoff).
- Owner: implementation_luna
- Depends on: T3
- Write set: `content/video_engine/tests/golden/build_golden_sources.py`, `content/video_engine/tests/golden/sources/verdict-stack.*`, `content/video_engine/tests/golden/sources/test-card.*`, `content/video_engine/tests/golden/frames/verdict-stack*.png`, `content/video_engine/tests/golden/frames/test-card*.png`, `content/video_engine/tests/test_golden_frames.py` (`SURFACES` entries), `content/video_engine/scripts/render_baseline.py` (named instants only, if a surface needs more than one), `content/video_engine/effects/cards/dock_payload.json` and `chart_dock.json` (`proof.golden` filled)
- Acceptance: two new surfaces rendered from the CURRENT inline code - the verdict stack mid-pile (items landed, one lit) and at the burst, the test card with question cells typed and one answer highlighted - committed as goldens; the whole golden suite passes; the harness's break test still fails on a one-value change; the drift gate now passes the two `proof.golden` fields.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: (2026-09-13) surfaces `verdict-stack` (t 12.5: five cards on 3/5/7/9/11/13 s, `clear_at` 20.0), `verdict-stack@proof-burst` (t 20.25, `render_baseline.py` PROOF_FRAMES) and `test-card` (t 11.4: dock at 2.0, rows at 1/4/7 s) built from synthetic stdlib PNG members through the compiler's entry points; `ledger-extend` and `ledger-keyed` added to the pytest SURFACES and pass against their existing goldens (decision 7 closed). `build_golden_sources.py` gained `write_surface(name)` (`build_golden_sources.py verdict-stack test-card` writes only those). Before/after sha256: all 102 pre-existing frame + source files byte-identical, +3 frames +4 sources. Determinism: each instant rendered twice, identical (`9981063ad3c5bf15`, `34bdd8056c33ea15`, `4bc3f4e9d7e0025b`). Break test on tmp copies (`clear_at` 20.0 -> 20.05, row 3 delay 7.0 -> 7.5): `MUTATED: 2 failures` / `COMMITTED: 0 failures`. `pytest test_golden_frames.py`: 52 passed in 109.08s. The parent READ all three frames: the mid-pile shows cards 1-4 tilted on the top rail spots and card 5 LARGE near centre; the burst shows cards 1-3 flung outward and fading (4 barely moved, 5 and 6 still on their side spots - the 60 ms stagger), the test card shows all three questions typed, the where-to-look cells in and the answer cells highlighted. Nit found, not fixed: the `ledger-keyed` FRAME_T line carries `ledger-extend`'s comment glued on.

### T7: Promote the verdict stack and the checklist to modules
- Status: complete (the two cards' `lives` / `proof.golden` updated by the parent after T3)
- Owner: implementation_luna
- Depends on: T6
- Write set: `content/video_engine/scripts/species/verdict.mjs`, `content/video_engine/scripts/species/checklist.mjs`, `content/video_engine/tests/kinetics/verdict.test.mjs`, `content/video_engine/tests/kinetics/checklist.test.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the two inline bodies replaced by their regions and a call), `content/video_engine/tests/test_kinetics_sync.py` (region expectations only if a test enumerates regions), `content/video_engine/effects/cards/dock_payload.json`, `content/video_engine/effects/cards/chart_dock.json` (`lives.form: module`)
- Acceptance: each module carries the header pattern (WHEN from doc 29 s9.24 / the checklist v2 comment, THE LAW, a frozen dials object lifting today's literals - fly-in depth translateZ -700 (the code; doc 29 s9.24's -940 is stale, T2 evidence), the 60 ms burst stagger, the 58 px row pitch, the default column colours - with no value changed); the module's region and name are distinct from the `stack` dock option; module names do not collide in the shared name space; no new registry - the engine's dock slot calls the inlined painter by name (a `DOCK_PAINTERS` registry is a later decision once a third dock painter exists; recorded, not built); `sync_kinetics.py --check` passes; both goldens byte-identical; node tests cover the pure math (landing clock, burst bearing, column auto-fit); the parent serves the Steel and Paper build-f player, PLAYS it at 701.7-727.6 s and at 492.3 s and 778.6 s, and reads frames at those instants against the goldens.
- Validate: `node --test content/video_engine/tests/kinetics/verdict.test.mjs content/video_engine/tests/kinetics/checklist.test.mjs && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/sync_kinetics.py --check && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: (2026-09-13) `content/video_engine/scripts/species/verdict.mjs` (157 lines; exports `VERDICT`, `verdictGeometry`, `verdictNextAt`, `verdictPose`, `verdictBurst`, `paintVerdict`; imports nothing; `ENTER_Z` -700 lifted from the code) and `species/checklist.mjs` (202 lines; exports `CHECKLIST`, `buildChecklist`, `paintChecklist` and the fit/row/sweep math; imports `INK`, `kmHex` from `kinetics/ink.mjs`, region after ink); both register NO painter - the engine calls them by name (no `DOCK_PAINTERS` registry, recorded not built); headers carry WHEN, THE LAW, the five phases with the blend each came from (fracture-reassemble marked inferred) and the stale-doc note. Scope beyond the slice text: the stack's setup in the dock fill (SPOTS, tilts, active pose) and the checklist's column fit + row paint inside `drawChart` moved too; `test_kinetics_sync.py` `SPECIES` gained the two names. Engine call sites: `verdictGeometry` (the dock fill), `buildChecklist` (the chart build), `drawStack` -> `paintVerdict`, `paintChecklist` (drawChart). Validation: node `verdict.test.mjs` + `checklist.test.mjs` 17/17 (the enter clock, the focus->rail blend, the burst bearing and stagger, the recap switch); `sync_kinetics: in sync (31 module(s): 14 kinetics, 17 species)`; pytest kinetics sync + golden frames 71 passed; sha256 of all 47 golden frames identical before and after (`verdict-stack` 9981063a, `@proof-burst` 34bdd805, `test-card` 4bc3f4e9). SERVED PROOF (the parent): a private split player of Steel and Paper build-f on the extracted engine (`scratchpad/p55/buildf-proof/`, never the frozen build-f; launch `p55-buildf-proof` :8753, no-store), audio clock 806.47 s = the timeline, 0 console errors; PLAYED with the player's own button from 701.5 s and read at 705.5 (the first proof LARGE near centre over the factory plate), 712.7 (earlier cards receded to the top rail, a new active card), 722.8 (seven cards in the mosaic around the active "We checked. It's bigger.") and 726 (the last card in focus as the wipe begins), then scrubbed to the burst at 727.25 (cards flung outward and fading) and 727.5 (almost gone on "I'll go further than Bravos"); the test card read at 497.5 s (typed rows, highlighted answers over the plate) and 781.5 s (the recap). Lesson recorded: `vo.play()` from a script advances the audio clock but not the render loop - play through the player's button or the scrub.

### T8: The agent-facing surface
- Status: complete
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/scripts/authoring/effects.py`, `content/video_engine/scripts/effects_card.py`, `content/video_engine/tests/test_authoring_effects.py`, `content/video_engine/editor/editor.html` (species panel text only)
- Acceptance: `authoring.effects.card("evidence wall")` returns the verdict-stack card; an unknown name raises with the three nearest titles; `effects_card.py "<name>"` prints title, does, when, the example, lives, status and proof path in under 40 lines; `authoring/__init__.py` stays untouched except `effects` added to its imports and `__all__` (parent-owned integration point - the parent makes that one-line edit); the editor's species panel shows `title - does` and a proof link beside each species id, reading `docs/EFFECTS-CATALOG.jsonl` from the served build; the kit names no episode (its rule).
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_authoring_effects.py -q && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/effects_card.py "evidence wall"`
- Evidence: (2026-09-13) `content/video_engine/scripts/authoring/effects.py` (`load` reads only `docs/EFFECTS-CATALOG.jsonl`; `find` tiers: exact id, exact token on any axis, title/alias equality with a leading the/a/an ignored and hyphens/whitespace normalised, then substring of title/alias/does; `card` raises `LookupError` listing the candidates or the three nearest), `content/video_engine/scripts/effects_card.py` (`"evidence wall"` exit 0 in 26 lines: title + id, status + backlog, does, when, the example + its validator, the 5 numbered phases, 5 blends, lives `module species/verdict.mjs :: paintVerdict`, proof golden `verdict-stack` + node test + first use Steel and Paper build-f 701.73 s, callable; `"stack"` exit 2 listing `dock_option:stack`, `dock_payload:stack`, `overflow:stack`), `tests/test_authoring_effects.py` 19 passed (failed first on `ImportError`; every card prints in <= 40 lines; the kit names no episode, grepped against all 16 project dirs). `editor/editor.html` +49 lines: `loadCatalog` (not awaited; a failed fetch leaves a quiet note), `speciesCard`, `catalogEntry` (`title - does` + the golden link or "no proof yet", textContent only). Found by T8: the review server serves only the build directory, so `/docs/...` 404s and the panel shows only its note - the parent dispatched two read-only GET routes in `content/video_engine/scripts/serve_player.py` mirroring its `GET /editor.html`: `/docs/EFFECTS-CATALOG.jsonl` (ndjson) and `/content/video_engine/tests/golden/frames/<name>` (only `[A-Za-z0-9._@-]+\.png` whose resolved parent IS the frames dir; percent-decoded before the check; anything else 404; every other path still serves from the build). `tests/test_editor.py` +4 tests (the catalogue bytes + type, a real golden's bytes, `..%2F..%2Fdocs%2F...`, `../serve_player.py`, a `.txt` and a slashed name all 404 - failed before on `('/content/video_engine/tests/golden/frames/..%2F..%2Fdocs%2FEFFECTS-CATALOG.jsonl', 200)` because the handler fell through to the build directory; today's paths unchanged) and, in the existing real-browser test on s04, a wait for `The bracket page species` in `#species` (timed out before, passes after) - the parent accepts that browser assertion as the panel's browser verification (deviation: no separate manual look). A pre-existing red in the same file (`test_a_post_writes_the_sidecar...`: the fixture copied `build-short-t7`'s own 2026-09-11 `overrides.json` into every test) was fixed in the FIXTURE (skip `OVERRIDES_NAME` when copying), never the build - its sidecar is untouched (88 bytes, mtime 2026-09-11 14:36:37). `test_editor.py`: 10 passed.

### T9: The gallery (kept only if HG2 says so)
- Status: built - awaiting HG2 (the operator's one read of the served page)
- Owner: implementation_luna
- Depends on: T6
- Write set: `content/video_engine/scripts/build_effects_gallery.py`, `content/video_engine/tests/test_build_effects_gallery.py`, generated output under a gitignored review dir (`content/video_engine/effects/gallery/`, added to `.gitignore` by the parent)
- Acceptance: one static page, one tile per card grouped by axis: title, aliases, does, the example, status, the golden frame when one exists and an explicit "no proof yet" tile when not (the gap stays visible), and for module-backed effects a link to the served proof player at the named instant; served no-store on the review server; generated from `EFFECTS-CATALOG.jsonl` only (no second source); HG2 read.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_build_effects_gallery.py -q`
- Evidence: (2026-09-13) `content/video_engine/scripts/build_effects_gallery.py` + `tests/test_build_effects_gallery.py` (8 passed: deterministic bytes, each id once, the no-proof marker, the verdict stack's 5 phases, no network strings outside quoted examples/blend text, the counts line, the proof-frame strip, the callable-false warning). Output `content/video_engine/effects/gallery/index.html` + 34 copied golden PNGs; `.gitignore:185` added by the parent (`git check-ignore` confirms). Counts: `125 cards | live 39 | wired 77 | draft 1 | declared 7 | planned 1 | with golden 45 | with test 110 | no proof 12`. Served no-store on launch `p55-effects-gallery` :8758. Deviation: the plan's per-effect link to a served proof player at a named instant is not built - no per-effect proof player exists (the golden frame + its `@proof-*` strip stand in); HG2 decides whether it is wanted.

### T10: Routing
- Status: complete
- Owner: parent
- Depends on: T8
- Write set: `CLAUDE.md` (one fast-route line), `GEMINI.md` (the same line), `docs/AGENTS-VIDEO-ENGINE.md` (one line), `docs/agent-context/SKILL_ROUTER.md` (one row)
- Acceptance: each file gains exactly one line: "Name an effect, find what it does and how to call it -> `python content/video_engine/scripts/effects_card.py "<name>"` (the catalogue: `docs/EFFECTS-CATALOG.md`, generated)"; AGENTS.md unchanged; `build_docs_layers.py` in sync.
- Validate: `git diff --stat -- CLAUDE.md GEMINI.md docs/AGENTS-VIDEO-ENGINE.md docs/agent-context/SKILL_ROUTER.md AGENTS.md && C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py`
- Evidence: (2026-09-13, `scratchpad/p55/t10_routing.py`, parent) one line each in `CLAUDE.md` (fast routes, before the operator-history route), `GEMINI.md` (item 9, retrieval order), `docs/AGENTS-VIDEO-ENGINE.md` (the retrieval list), `docs/agent-context/SKILL_ROUTER.md` (a row after the operator-history row) naming `python content/video_engine/scripts/effects_card.py "<name>"` and the generated `docs/EFFECTS-CATALOG.md`; `AGENTS.md` unchanged; the kit's integration point `authoring/__init__.py` exports `effects` (import + `__all__`). `git diff --stat`: 5 files, 6 insertions, 2 deletions. The script asserted `effects_card.py "evidence wall"` resolves to `dock_payload:stack` before writing. Docs layers regenerated after.

### T11: The promotion queue
- Status: complete
- Owner: parent
- Depends on: T7
- Write set: `docs/content-video-engine/BACKLOG.md` (one row per ranked inline painter)
- Acceptance: T1's promotion rank written as BACKLOG rows, each naming its card id, its engine symbol, the golden it needs first, and the engine lane it must queue behind; the likely head of the queue (to be confirmed by T1's measure) is `drawRecord` (the typewriter), the scene-loop transitions (dip, blur-zoom, wipe, suck - beside R26-75's slide), and the page enters (spiral, snap, throw, drop, mount, axes).
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py`
- Evidence: (2026-09-13, `scratchpad/p55/t11_queue_rows.py`) BACKLOG R26-95 `species:trace` (476), R26-96 `species:spotlight` (320), R26-97 `species:callout` (306, golden exists), R26-98 `page_species:figure` (204), R26-99 `dock_payload:record` (140 - the plan's guess that the record heads the queue did not hold; the checklist, 488, was promoted by T7), R26-100 `exit:dip` (180, with the scene-loop transitions beside R26-75's slide), R26-101 `page_enter:spiral` (195, with the vortex retract); each names its engine symbol, the golden needed first and the lane it queues behind; every card id asserted present in the catalogue.

## Verification

- Catalogue: `python content/video_engine/scripts/build_docs_layers.py` -> every layer in sync (9 layers).
- Drift: `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_build_effects_catalog.py content/video_engine/tests/test_lint_species_choice.py -q`.
- Retrieval: `python content/video_engine/scripts/docs_find.py "evidence wall"`, `"test card"`, `"stack"`, `"blur-zoom"`, `"slide"` - first hits are cards (slide: `planned`, R26-75).
- Components: `python content/video_engine/scripts/sync_kinetics.py --check`; `node --test content/video_engine/tests/kinetics/`; `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q`.
- Served proof: the Steel and Paper build-f player played at the stack and test-card instants, frames read by the parent (not a render).
- Plan: `python scripts/prp_validate.py .claude/PRPs/plans/P55-THE-EFFECTS-CATALOGUE.plan.md`.

### Review of the landed slices (2026-09-13, `reviewer`, read-only; report `scratchpad/p55/review-landed.md`)

Clean: T6 (the golden builders, SURFACES, PROOF_FRAMES, `art_embed` through `embed_fit`); T7 (every literal matches the inline code at HEAD; DOM writes, zIndex, removal, recap, one-time fit and the K-M band all kept; 9:16 geometry unchanged); the compiler fixes (`embed_fit` order, the cutout refusals and kind, `live` = breath + drift with its gate); the docs' 22 cited card ids and doc 29's -700. Findings and their dispositions:

1. HIGH - the docs layers could not converge: `docs/DOCS-INDEX.config.json` excluded every generated layer except the effects catalogue, and the index is built before it, so any card text change failed the stack's own re-check. FIXED by the parent: `docs/EFFECTS-CATALOG.jsonl` and `.md` added to the index's `exclude`.
2. MED - `dock_kind:cutout` still said not callable (R26-94 fixed the option). FIXED (`scratchpad/p55/card_fix3.py`, after re-proving `dock_opts({'cutout': True})`): callable, `backlog: [R26-94]`.
3. MED - `CAPABILITIES.md` still attributed ~25 rows' JS symbols to the template shell (T5 fixed only decision 6's list); rows 169/189 named inline code T7 moved into modules. FIXED (junior_developer, parent-reviewed; `scratchpad/p55/cap_engine_fix.py`): 29 rows re-attributed (18, 20, 22, 49, 52, 53, 60-63, 68, 73, 78-81, 86, 88, 96, 97, 105-110, 114, 169, 189) - every moved symbol counted >= 1 in the engine or its module and 0 in the template before writing; mixed cells (22, 63, 80, 81, 169) credit the engine for JS and the template shell for CSS; rows 169/189 -> `scripts/species/verdict.mjs` / `scripts/species/checklist.mjs`; left on the template by design: 41 (`text-rendering: geometricPrecision`), 167 (`:root`), history/claim rows 51, 65, 100, 250-255, 262-285 and 116's status claim; the parent corrected row 81's selector to the shell's real `html[data-aspect="9:16"] .dock.record`. Re-scan: 14 symbols attributed to the template, all present there after the row-81 fix.
4. MED - statuses against decision 1. FIXED (`card_fix3.py`, each verified first): the approved Tokyo v2 timeline carries `page_enter:spiral` at s04 44.88 s and s06 75.73 s and `exit:suck` at s03 38.96 s - both `live` with that first use; `idle:breath` (the engine's `IDLE_CLASS` default) and `arrival:spring` (`arriveOf`'s default) `live` as defaults every build runs.
5. MED - a cite with no heading match fell back to line 1 and counted as resolved (23). FIXED (junior_developer, parent-reviewed): no match keeps a null line and is uncounted; a BACKLOG row id / ruling id resolves by its own text (`| **R26-30`, `## E88`; R26-70 no longer matches R26-7 - `BACKLOG R26-7` had pointed at the R26-70 row, now line 432). Real tree: `in sync (125 cards, 49 options, 241/274 cites resolved)` (was 261 - the honest count): 3 of the 23 now resolve to their real rows, 20 are unresolved vague cites (`CAPABILITIES`, `SPECIES-BY-SENTENCE row 13`, `s5`, `SHORT-FORM-SHAPE s1`, `MOTION-GRAMMAR`, ...) - a card-text refinement for a later pass, never a line-1 pretence.
6. MED - a missing dials module/object passed silently; `compiler_when` ignored `--repo`. FIXED: `--write`/`--check` exit 1 with `INVALID - <card id>: dials module/object ...`; `--repo` loads that checkout's compiler under a unique module name, out of the import cache; T4's gate call kept. 4 new tests failed before (e.g. `Failed: DID NOT RAISE CatalogError`); generator + drift suites 34 passed.
7. LOW - stale card text. FIXED (`card_fix3.py`): `dock_payload:stack`'s callable note no longer claims "no golden" (it names what a row needs and R26-82's 9:16 gap); `idle:live`'s `does` is real text. The fragment `author.example`s: T4 completed nine from their sources; the remaining 13 non-literal examples were REWRITTEN as copyable literals (junior_developer, parent-reviewed): `chart_to:extend` (test_chart_transitions.py:363), `dock_kind:press` / `dock_option:stack` (test_press_dock.py:39/:128, META's values written out), `dock_option:embed` (test_art_embed_media.py:91), `page_species:span` / `page_species:cross` / `species:flow` / `species:agenda` / `species:count_array` / `species:stamp` / `species:arc` (build_golden_sources.py :539, :472, :514, :1030, :1026, :589, :586 with `VECMAP_GULF` expanded), `species:chip` (test_targeted_species.py:176), `species:newsreel` (test_caption_band.py:209) - no shipped shot table carries any of the 13; `lives.note` says what a real row adds (press meta path, surface, etc.); the old `page_species:span` example had come from a squiggle TARGET in SHOT-TABLE-F's docstring, not the span species. The gate now skips only 3 (`caption:phrase` - no compiler validator; `exit:slide` - planned R26-75; `species:spotlight` - `dur: 'hold'` resolves in the build loop): `0 failure(s), 3 example(s) skipped`; drift + generator + kit tests 53 passed.
8. LOW - `docs_find` dropped its `next: sed -n` hint when an effects hit (no line) came first, and T3 loosened the test. FIXED (junior_developer, parent-reviewed): `next_window` names the first hit with a line in any layer; effects-only -> `python content/video_engine/scripts/effects_card.py "<id>"`; the loosened `--limit` assertion made strict again + two new tests (failed before: `'1 hit(s) in effects' != '1 hit(s) in effects; next: python ... effects_card.py "dock_payload:widget"'`); `test_docs_find.py` 14 passed; `docs_find "evidence wall" --limit 6` -> the card first and `next: sed -n 468,508p docs/content-video-engine/BACKLOG.md`. Side effect accepted: a `--layer cites` search now also gets a window.
9. LOW - "every layer in sync (9 layers)" did not reproduce on the tree the reviewer read (another lane's untracked docs plus #1). Re-proved at the final verification after every fix lands.

## Evidence And Handoff

- **Post-completion finding (2026-09-13, the studio readiness review's full-suite baseline):** P55's verification ran the catalogue, kinetics, golden and editor suites, not the whole `content/video_engine/tests` tree, and three by-design changes left test pins red. Found by `python -m pytest content/video_engine/tests --continue-on-collection-errors` (66 failed, 2,734 passed) and FIXED the same evening: (1) `test_authoring_kit::test_the_kit_is_the_five_modules_the_plan_names` - the pin now includes T8's `effects.py`; (2) `test_portrait_parity::test_no_landscape_literal_in_player_code` - T7 lifted `REF_W: 1920` / `REF_H: 1080` out of a `STAGE_W` expression; proven used only as `stageW * V.BURST_NORM_X / V.REF_W` (a fraction of the stage) and allowlisted with that reason; (3) `test_page_boxes::test_the_fixture_names_every_builder...` - `content/video_engine/assets/page-boxes.v1.json` re-measured with `measure_page_boxes.py --write`: every box identical to the backup, only `player_sha256` (caac8c3c -> 8d715a7a) and the date moved. Re-run: 81 passed. Lesson: a slice that adds a module, moves a literal or changes the engine runs the WHOLE test tree before its completion claim, not its own suites.

- Final verification (2026-09-13, `scratchpad/p55/verify_all.py`, every output saved under `scratchpad/p55/verify/`, nothing piped): layers `build_docs_layers: every layer in sync (9 layers)`; catalogue `build_effects_catalog: in sync (125 cards, 49 options, 241/274 cites resolved)`; drift gate `effects_catalog_check: 0 failure(s), 3 example(s) skipped`; catalogue + kit + gallery + docs_find + layer pytest `111 passed in 107.77s (0:01:47)`; `lint_species_choice --when --check-doc` `SPECIES-BY-SENTENCE.md: SPECIES_WHEN block in sync`; kinetics `sync_kinetics: in sync (31 module(s): 14 kinetics, 17 species)`; node `ℹ pass 348` (31 files named explicitly - Node 24 treats a bare directory as a module path); engine/golden/idle/cutout/embed/transitions/motion/press pytest `269 passed in 191.52s (0:03:11)`; docs_find effects-first for "evidence wall" (`dock_payload:stack`), "test card" (`chart_dock:checklist`), "stack" (the three stack cards), blurzoom and slide (planned); `effects_card.py "evidence wall"` exit 0, `"stack"` exit 2 listing three ids; plan validator PASS. HG2 (the gallery) remains the operator's read; it gates nothing else.

- APPROVED 2026-09-13: the operator invoked `/prp-implement P55` (goal set); status running; copied to main.
- Draft 2026-09-13 by architect_sol from the main checkout at `5aa0f8f` (read-only); written in the sweet-villani worktree
  because the harness blocks writes to the main checkout's `.claude`; the parent copies it to main on approval.
- Deviation: the brief's `npm run prp:validate` has no `package.json` script in either checkout; the plan was validated
  with `scripts/prp_validate.py` (the runbook's PRP Format command).
- Deviation (2026-09-13, parent): the engine queue is serialised by WRITER, not by commit. The plan ordered T6-T7 "AFTER R26-76 and R26-74 commit"; the commit batch (BACKLOG R26-83) needs the operator's word, so the lanes hand the engine files over one writer at a time on the uncommitted tree: the melt lane finished (look pass 3 accepted by frame read), E95's still-fill default took the compiler next, then R26-93 (the `live` idle restored), then T6 (goldens) and T7 (modules). The golden hash comparison before and after each writer is the isolation, as it is for a commit.
- Contention recorded at draft time: main's uncommitted melt lane (`build_scene_timeline_f.py`, `species/melt.mjs`,
  `render_baseline.py`, `tests/golden/build_golden_sources.py`, `tests/test_golden_frames.py`, golden sources, docs layers).
  T1-T5 and T8 write none of those; T6-T7 queue behind it.
- Slice evidence (inventory counts, generator runs, drift-gate failures proved, golden hashes, served-player frame paths)
  is recorded under each slice's Evidence line as it lands.
