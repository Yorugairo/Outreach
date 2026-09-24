---
id: P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY
title: The stamp lands (R26-247 + the chip's stamped landing), the page pin and the bands close (R26-241/230/222/231), the compare on bars (R26-190), the s90 page (B's type scale, badges as the key), and the body of Steel and Paper H (P68 T6)
status: running
operation: feature
risk: standard
owner: parent
branch: claude/fable-p68
contract: tdd-v1
created: 2026-09-22
updated: 2026-09-22 (APPROVED by the operator's `/prp-implement P69` and "resolve all non-human blockers and i'll review human gates at the end": HG1-HG4 and the debt-issuance tier are batched to the end; the build proceeds past them on the proposed defaults, each reversible. Revision 2 by architect_sol - folds in REVIEW-P69 B1-B3 and items 4-19, and the operator's three decisions of 2026-09-22; not approved; staged in the sweet-villani worktree because the harness refuses a cross-worktree write - the parent moves it to fable-p68 at the same path)
---

# P69 - The stamp lands, the page pin and bands close, the s90 page, and the body of H

## Summary

The operator's `/prp-plan 2-4`, taken from the parent's order after the baseline, plus the operator's
decisions of 2026-09-22.

- **(2)** R26-247: a stamp is not yet a landing to the motion gate, the cues or the camera. With it, the
  chip `form: "stamp"` lands by the real stamp arrival, rendered both ways so the operator can pick.
- **(3)** R26-230, R26-222 and R26-231: built by Astra and still marked open; this plan verifies and
  closes them. It adds two items:
  - **R26-241, reopened.** Every engine commit reddens `test_page_boxes`, so it is fixed at the root
    before any engine slice.
  - **R26-190.** The figure on a bars page paints nothing, and three H beats need it.
- **(4)** P68 T6: the body of Steel and Paper H, one beat per slice (E99 s82 (a)), with the six
  direct-match props stamped.
- **(new)** E99 s90, which the Fable lane took back from Astra (register `ff08213`): B's phone type
  scale for the full-stage 16:9 page, badges as the key, and the three layout fixes. It is built behind
  an option, and becomes the default only on the operator's read of frames. The body is read on the s90
  page.

**The operator's decisions (2026-09-22), each encoded as a dependency:**

1. **The stamp's contact instant is read later, together with the chip landing (P69-HG1).** Everything
   builds on the proposed default, `STAMP_LAND.tc` = 0.1542 s (the scale settling). P69-HG1 is the one
   place where it can be overturned (T13).
2. **The body builds on today's page type, 33 px captions and the scratch Kokoro take. It does not wait
   for P68 HG3.** T0 amends P68 T6's `Depends on: T5, HG3` accordingly (`P68-...plan.md:402`).
3. **E99 s90 is the Fable lane's** (`ff08213`). It is built here (T8-T11), and the body adopts it before
   its read (T33).

**Repository truth (re-measured for this revision):**

- fable-p68 is at `ff08213` (= main = origin/main). The dirty files are this lane's untracked plan plus
  the two effects files this plan does not own.
- The register (`docs/WORKTREE-REGISTER.md`):
  - `:38` now reads "E99 s90 claim RELEASED to the Fable lane";
  - `:46` claims P69 and E99 s90. The claim was committed before this plan's approval; T0 records the
    approval against it.
- **Item (3) is built in code on main, from Astra's `75fc99f`.** That commit's message reads "wip ...
  Preservation only, not production approval". The pieces:
  - R26-230: `ledger_page._full_stage_bands` (`:1363-1378`), emitted by `page_boxes` (`:1890-1891`);
  - R26-231: `page_build_envelope_s` / `page_build_span_error` (`build_scene_timeline_f.py:4597-4640`)
    and `validate_page_build_spans` (`:4644`, called at `:7686-7692`);
  - R26-222: the engine's y-only rescale hand-over (`scene-evidence-engine.mjs:12201`).

  Their tests pass (`46 passed in 20.78s` in this worktree). T7 closes the rows on those tests and its
  own run, not on the commit.
- **R26-241 was closed in error** by `4130942`. Commit `4b3058f` fixed only the CRLF half:
  `measure_page_boxes.template_sha()` (`:394-398`) still hashes the whole template plus engine, and
  `test_page_boxes.py:65` asserts `FIXTURE["player_sha256"] == M.template_sha()`. So any engine byte
  reddens it. In addition, `build()` writes `measured: date.today()` (`:452`), and `--check` compares
  the whole text (`:490-494`), so a check run on any later day drifts.
- **The stamp's readers today** (all probed red by the review):
  - the gate reads throw/land only, at `:1032` (`_attention_moves`), `:1150` (`camera_state_at`),
    `:2991-2993` (`_landings`, where a stamp falls to `+0.0`) and `:3150` (`_arrivals` feeding
    `_arrival_events`, which goes into M01-M03/M07 at `:1308`);
  - the gate carries **two throw contacts**: 0.46 at `:2992` (pinned by
    `test_gate_motion_density.py:1411-1413`) and `STOP_FLIGHT_S` = 0.45 at `:1034/:1152/:3151`. The
    audio side carries a third: `landing_contact` steps a throw to 11/24 s (`authoring/audio.py:136-137`);
  - `camAttentionState` (`kinetics/camera.mjs:118-121`) filters throw|land, and the engine's `? 0`
    branch (`:13383`) is dead.
- **The mass default disagrees.** The engine paints a stamp at `d.mass || "ink"` (`:16969`). `fired()`
  labels it `e.option or "paper"` (`authoring/audio.py:299`), and the H door writes its slot as
  `opts.get("mass", "paper")` (`build_episode_h.py:604`).
- **R26-247's R1 is already built.** `stamp_dock_place` clips a plate stamp's bounds to `plate_room`
  (`build_scene_timeline_f.py:5871-5875`, from `4756d9d`), and it is tested
  (`test_the_stamp_arrival.py:598-610`). R26-247's residual is therefore R4 only.
- **R26-190 is open** (`BACKLOG.md:621`). `buildPerform` (`scene-evidence-engine.mjs:11364`, and the
  `if (!pts.length) return null` at `:11449`) drops every figure on a bars page, so `paintCompare`
  (`:11319`) has nothing to morph. The treatment needs it at three beats:
  - row 17: the 94 bar "with the figure";
  - row 18: the 20 bar halves (`chart_to compare`);
  - row 21: the wafer ratio, 1 vs 3 (`chart_to compare`).

  All three are `shares` objects drawn as bars.
- **The s90 starting point.**
  - `readability: "landscape-phone"` is a SERIES-file field (`ledger_page.py:251`). It is refused off
    the dense-line builder (`:257-258`) and on board/chart_box pages (`:262-263`).
  - The engine reads it per page (`scene-evidence-engine.mjs:7907-7910`, `:9192`, `:9254-9259`,
    `:9549`).
  - A long name is refused rather than homed (`_readability_fit_error`, `ledger_page.py:1563`).
- **The body's inputs.**
  - Every body plate resolves via `find_asset`.
  - The props, the host stills, the take, `sound/` and the outro are present.
  - **No series file:** `ev-debt-issuance-v2` (row 16, a bars page) exists as a PNG only. So does
    `ev-three-manias` (row 12), which the treatment calls an HTML record.
  - The dossier's issuance figures (`EVIDENCE-DOSSIER.md:130`, `:137`, `:227`: "~$121B", MS ">$100B")
    are secondary.
  - `NVIDIA_CHIP` (`build_episode_h.py:423`) is an SVG chip, not form stamp.
  - The reference mp4 is in the MAIN checkout only.

## Intent And Acceptance

1. **The page-box pin is honest (R26-241).** An engine byte that moves no box leaves
   `test_page_boxes` green. A moved box turns it red. `--check` passes on a fixture measured on another
   day. Every engine slice still carries the fixture and re-measures it.
2. **A stamp is a landing everywhere downstream (R26-247).**
   - The contact is `STAMP_CONTACT_S` = `STAMP_LAND.tc`, read from the module and applied to STAMPS
     ONLY. Throw and land keep each reader's own existing value; byte-identical throw/land output is a
     hard acceptance.
   - Three consumers read it: the gate (M01-M03/M07, M20, E51, M29), the cues (with the stamp's mass
     defaulting to `ink`, as the engine paints it), and the camera. The camera and the gate's camera
     mirror land in one slice, so main never carries a gate/player mismatch.
   - L2: the stamp takes the room first (s88), and the row's other docks are placed around it. This is
     read on the frame.
   - R4 stays as R26-247's residual.
3. **A figure lands on a bars page and the compare morphs it (R26-190).**
4. **The chip's stamped landing is an option**, rendered both ways and picked at P69-HG1. That gate also
   rules the contact instant.
5. **R26-230, R26-222 and R26-231 are closed on their tests.** The rows cite the tests and T7's run.
   R26-230's caption-size half stays with P68 HG3 (A).
6. **E99 s90 is built behind an option:**
   - the phone type scale on every builder the body uses, as a per-row option;
   - long names get a home;
   - the subtitle never meets the y label;
   - x-tick labels clear the axis line by at least main's measured 18 px;
   - badges become the key on the even-pill ladder.

   The operator reads frames at P69-HG3, and the default flips only on that ruling.
7. **The body of H is built, one treatment row (= one beat, P68 T4: "one table row per beat") per
   slice.**
   - The first prop goes to the operator on its own card (P69-HG2) before props 2-6.
   - The body adopts the s90 page (T33).
   - The whole cut is gated, frozen and critiqued once, then read beside the reference at P69-HG4. The
     render stays with P68 T7.

## Scope

- **Lane A** (fable-p68, one slice in flight at a time):
  - T0-T7: R26-241, the stamp consumers, L2, R26-190, and the item (3) closure;
  - T14-T34: the body preflight, the 18 row slices, the s90 integration, and the whole-cut close.
- **Lane B** (a new Fable worktree `claude/p69-s90`, created off main after T6 merges, with its own
  register row): T8-T10 (s90) and T12 (the chip option). Lane B holds the engine lock for its whole life.
- **Parent-only slices**, run in lane A at a merged slice boundary: T11 (P69-HG3), T13 (P69-HG1), and
  the P69-HG2 card inside T23.
- **Files:**
  - `measure_page_boxes.py`, `test_page_boxes.py`, `assets/page-boxes.v1.json`;
  - `gate_motion_density.py`, `authoring/audio.py`, `kinetics/camera.mjs`, the engine,
    `species/chip.mjs`, `build_scene_timeline_f.py`, `ledger_page.py`;
  - the tests each slice names;
  - the H door and its build;
  - one proof door;
  - the records.

## Not Building

- R26-247 R4 (a stamped card with no `card_aspect`). H stamps no card.
- A default flip of the s90 profile or of the chip's landing without the operator's ruling.
- The render, the upload and the unlisting of the 2026-08-30 original (P68 T7 / HG4).
- Any compile into `build-f/`, and any restore of the main checkout's `build-f/` (`REFERENCE-F.md`).
- Any script change made to pass a gate (E99 s89; the next letter).
- A 16:9 caption-size change (P68 HG3 (A)). The body uses today's 33 px strip, by Decision 2.
- The 2.5D/3D model engines (Astra's current work).

## Human Gates

Each gate's row goes into `docs/content-video-engine/review-queue.v1.json` in the change that frames it,
and `REVIEW-QUEUE.md` is regenerated. Rulings are written as `E99 s??` and numbered at merge.

- **P69-HG1: the chip's landing, and the stamp's contact instant** (Decision 1).
  - The chip: one proof beat built twice from one source (T13), `springPop` versus the stamp.
  - The contact: the `prop-stamp` scrub at enter +0.00 / +0.10 / +0.154 / +0.17 s, with the cue placed
    at `STAMP_CONTACT_S`.
  - What to judge: which landing reads right for a chip, and does the cue hit on the frame where the
    mark reads as landing?
  - What it blocks: the chip's default, and a possible one-constant change of `STAMP_CONTACT_S`. The
    body builds on 0.1542 s and re-times automatically if the constant moves.
- **P69-HG2: the first prop, on its own card** (`REBUILD-TREATMENT-H.md:138`: "No prop has ever landed
  in a shipped cut, so the first one comes to the operator on a card").
  - What is shown: row 15's Fed stamp, frozen and served, with its enter/contact/rest frames and the
    cue.
  - What it blocks: the row slices that stamp props 2-6 (T24, T26, T29, T30).
- **P69-HG3: the s90 page, before and after** (T11). The frames are the H bed page, one bars page and
  the representatives, each with the option off and on, and the three layout fixes measured. What it
  blocks: the default flip only. The body opts in per row either way (T33).
- **P69-HG4: the body read on frames beside the reference** (T34).
  - What is shown: H's tiles at the instants that matter, beside build-f's frames at the same instants,
    extracted from the sha-verified `steel-and-paper-full-1440p.mp4`; the critic, run once; the gates.
  - What it blocks: P68 T7 / HG4.
- **Not a gate for this plan: P68 HG3's open answers** (A, the voice, the plate balance). By Decision 2
  they re-time the body later; they do not block it.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`: `:46-72`, `:84-91` and `:93-105`.
  - The Codex model names at `:50` (Luna 6/max, Sol 6/xhigh) govern CODEX dispatch only.
  - On the Claude side, the roles are `implementation_luna`, `junior_developer`, `reviewer`, `explorer`
    and `release_steward` on Opus 5, and `speedster` on Sonnet 5.
- `docs/WORKTREE-REGISTER.md`: `:1-36`, `:38`, `:46`.
- `docs/content-video-engine/BACKLOG.md`: `:457` (R26-51), `:621` (R26-190), `:629` (R26-198), `:635`
  (R26-204), `:653` (R26-222), `:661` (R26-230), `:662` (R26-231), `:672` (R26-241), `:678` (R26-247).
- `.claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md`: `:119-139`, `:331-360` (T4, "one table row per
  beat"), `:387-416`, `:418-436`.
- `docs/portable/OPERATOR-RULINGS.md`:
  - s82: `:3282`, `:3284`, `:3286` (a) one lane, one scope, one file; (b) the bed; (c) the critic once;
    (e) life seen on two tiles 2 s apart;
  - `:3288`, `:3292`;
  - s83 `:3294`; s84 `:3296` (Ken Burns alone; the badge-ladder even pills); s87 `:3301-3305`; s88
    `:3307`; s89 `:3309`; s90 `:3311`; s91 `:3313`;
  - E47 `:1419`, E50 `:1520`, E51 `:1671`, E61 `:1991`, E62 `:2018`, E65 `:2111`, E74 `:2393`.
- `steel-and-paper/REBUILD-TREATMENT-H.md` (`:61-84`, `:103-138`, `:139-150`, the flow count, the foot)
  and `REFERENCE-F.md`.
- Code, at the lines cited in the Summary, plus:
  - `stopaction.mjs:286-395`;
  - `species/chip.mjs:27`, `:65-85`, `:113-160`;
  - `build_scene_timeline_f.py:106`, `:112` (`PLATE_OPTS`), `:197`, `:1573-1600`, `:5669-5920`,
    `:6919-6923`, `:7505-7519`;
  - `ledger_page.py:81`, `:244-270`, `:1195-1253`, `:1533-1600`;
  - `measure_page_boxes.py:380-500`;
  - `test_page_boxes.py:60-75`;
  - `build_episode_h.py:1-54`, `:70-131`, `:420-426`, `:577-610`.

## Execution Path

**Recall.** The rule: every mechanism noun is searched before it is proposed.

- Recall: docs_find "stamp arrival" -> `docs/content-video-engine/CAPABILITIES.md:79` "The STAMP arrival (arrive: stamp) and the BARE PROP payload (prop: True) — BUILT - remotion-ui RU-2's badge-stamp PORTED from its source on disk"; `content/video_engine/scripts/kinetics/stopaction.mjs:286` "export const STAMP_ARRIVAL = Object.freeze({"
- Recall: docs_find "landing cue" -> `CAPABILITIES.md:78` "Stop-action mechanics: throw and land with weight, WIRED"; `:54` "THE CUT'S SOUND AND THE RETURNING CHARACTER ARE GATED"
- Recall: docs_find "attention landings" -> `CAPABILITIES.md:88` "The camera arrival: the eye goes to the landed card, WIRED, opt-in"
- Recall: docs_find "push anchor" -> `CAPABILITIES.md:69` "Dock placement on a page, WIRED". No hit names the stamp as a push anchor; the record is E99 s87, `OPERATOR-RULINGS.md:3301`: "E51 (a landed stamp is a legal push anchor)".
- Recall: docs_find "chip stamp" -> `CAPABILITIES.md:100` "The icon CHIP - a named thing as one of a set, crossed out on a later word — WIRED"
- Recall: docs_find "prop stamp" -> effects `recipe:prop-stamped-onto-its-page` "status: candidate - count 0 (unfired)"
- Recall: docs_find "full stage bands" -> `CAPABILITIES.md:23` "THE CAPTION LAYER AT 16:9, AND THE PAGE THAT IS THE PLATE (R26-205 / E99 s82), WIRED"
- Recall: docs_find "re-stage" -> `49-GENERATIVE-VIDEO-AND-THE-VERTICAL-STAGE.md:13` "49.1 The vertical safe box"; `:52` "Centre-cropping 16:9 → 9:16 destroys 68.36 % of horizontal area"
- Recall: docs_find "page build span" -> `CAPABILITIES.md:32` "M28 - text on text among a page's OWN labels". There is no row for R26-231; T7 adds one.
- Recall: docs_find 0 hits for "rescale hand-over". T7 adds a row.
- Recall: docs_find "page boxes fixture" -> `BACKLOG.md:457` "R26-51 The measured page-boxes fixture is stale against the template — `tests/test_page_boxes.py` asserts the fixture's `player_sha256` equals the template's sha"
- Recall: docs_find "compare melt" -> `CAPABILITIES.md:38` "THE MELT EXIT, REWORKED TO E88: THE CHART MELTS, THE BOARD STAYS". The bars failure is R26-190 (`BACKLOG.md:621`).
- Recall: docs_find "landscape-phone" -> `CAPABILITIES.md:342` "Fed production additions — 2026-09-19 (working tree, not release approval) — Landscape phone-readable dense lines: source `readability: "landscape-phone"`"
- Recall: docs_find "badge ladder" -> effects `recipe:badge-ladder` "status: proven - count 41 (a grammar)"; the member line "the rail lands on an EVEN pill count (2 or 4) where the series allows"
- Recall: docs_find "badges as the key" -> `CAPABILITIES.md:75` "A MULTI-LINE PAGE BUILDS LINE BY LINE (R26-226 / E99 s82)". s90 has no capability row yet.
- Recall: docs_find 0 hits for "x-tick" in the engine docs. The only hit is `docs/portable/CHART-DISCIPLINE.md:113` "Standing analyst-grade rules". The clearance is s90's own number.
- Recall: docs_find "outro clip" -> effects `recipe:outro-clip-life` "The close: the outro clip is the world, its declared life carries the motion"
- Recall (SigMap):
  - `camAttentionState` -> `kinetics/camera.mjs`;
  - `row_arrivals` -> `lab_build.py`, `authoring/table.py`;
  - `stamp_dock_place` -> `authoring/docks.py`, `lab_build.py`, `gate_motion_density.py`;
  - `chipPose` -> `species/chip.mjs`;
  - `full_stage_bands` -> `tests/test_fed_full_stage_bands.py`, `measure_page_boxes.py`,
    `ledger_page.py`.

**Checkouts and order.** Nothing that shares a checkout runs at the same time: one slice in flight per
worktree, always.

- **Lane A (fable-p68)**, strictly serial:
  - T0 -> T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7;
  - then T14 -> T15 ... T32 (one row each);
  - then T33 -> T34.
  - T7 runs after T2-T4 merge, because the H-bed rebuild imports `authoring.audio` and
    `gate_motion_density` (`build_episode_h.py:70-71`).
- **Lane B (`claude/p69-s90`)**, created off main after T6 merges: T8 -> T9 -> T10 -> T12.
  - It runs in PARALLEL with lane A's body slices. The body slices write only the door and `build-h/`
    and hold no engine lock. Lane B holds the engine lock and is the only writer of `ledger_page.py`,
    `measure_page_boxes.py`, the fixture and the engine during that window.
  - Lane A merges main only at a slice boundary, never mid-slice. That is how each s90 or chip merge
    reaches the body build.
- **Parent gates in lane A**, each at a merged boundary with no body slice in flight: T11 (after T10
  merges), T13 (after T12 merges), and HG2 inside T23.
- **T33 needs T10 merged and T32 done.** It does not need the P69-HG3 ruling: the body opts in per row.

**Why the contact covers the stamp only (B3).** The throw already has three values across the readers
(0.46, 0.45, 11/24), each pinned by its own tests. Unifying them is not this plan's job. So
`STAMP_CONTACT_S` is added beside each reader's existing throw/land expression, and an
`arrive == "stamp"` branch is the only new path.

**The pin (B2, R26-241).** T1 fixes the root: freshness is decided by the measured boxes, not the
player's bytes. After T1, every engine slice (T4, T6, T8, T9, T10, T12, and the default flip if ruled)
still:

- carries `content/video_engine/assets/page-boxes.v1.json` in its write set;
- runs `python content/video_engine/scripts/measure_page_boxes.py --write`, then `test_page_boxes.py`;
- commits the fixture in the same commit as the engine change.

**Who re-measures once per merge:** the slice that changed the engine, in its own commit. If both sides
of a merge moved the engine, the lane doing the merge re-measures once, in the merge commit, under the
checklist's step 4.

**Coordination with Astra.** Astra no longer holds s90 and has no engine lock (`:38`). Its current work
is the 2.5D/3D model engines. Every P69 engine slice merges to main the same day, and Astra runs
`git merge main` before its next engine commit. If Astra takes an engine lock, the register names the
holder and P69's engine slices wait.

**Working rules (every slice).**

- The register row names the slice and the engine lock before the first write.
- Same-day merge through the checklist (`PRP_EXECUTION.md:84-91`, plus `test_page_boxes.py` and
  `measure_page_boxes.py --check`).
- New behaviour goes behind an option or an opt-in arrival. No default changes without a ruling.
- `reviewer` reads every diff before a merge.
- Numbers are written as `s??` / `R26-???` and assigned at merge.
- Gated steps run unpiped.

**Environment prerequisites.**

- **Lane A has:** the take, `evidence/objects`, `host/`, `sound/`, the props, the icons, every body
  plate, the outro, `build-h/`, and frozen copies d-g.
- **Lane A needs:**
  - build-f's reference frames: `ffmpeg` extracts them read-only from
    `C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/render/steel-and-paper-full-1440p.mp4`,
    after its sha256 matches `REFERENCE-F.md`, into `build-h/reference/` only;
  - `ev-debt-issuance-v2.series.json` (T14).
- **Lane B needs, copied in read-only as fable-p68 was:** the compiled timelines that the fixture
  records under `projects` (so `--write` can re-measure them); the H bed's gitignored inputs (for T11's
  frames); and the icon and prop cutouts (for T12's goldens).
- **Tools:** node, Playwright Chromium, ffmpeg.
- **Validator:** `python scripts/prp_validate.py`. npm is unavailable in fable-p68.

## Patterns To Mirror

- **A kinetics clock mirrored in Python**, with a `[DERIVED]` cite and a test pinned to the module:
  `gate_motion_density.py:144-145`, `:487`; `authoring/audio.py:120-128`.
- **Source module, then sync, then check:** `sync_kinetics.py --write` / `--check`,
  `test_kinetics_sync.py`. For a species importing stopaction, see `species/melt.mjs:74`.
- **An opt-in that writes nothing new otherwise:** `stopCss` (`stopaction.mjs:398-402`),
  `stamp_full_stage` (`build_scene_timeline_f.py:3325-3339`).
- **Refuse by name, never fit blind:** `test_the_stamp_arrival.py:583-590`.
- **A golden is added in the commit that builds the capability:** `prop-stamp`
  (`test_golden_frames.py:80`).
- **A row-level plate option:** `PLATE_OPTS` (`build_scene_timeline_f.py:112`), e.g. `domain=`, `build=`.
- **The H door:** named constants with their cites (R26-197), `_assert_read_only`, cues bound before the
  report is stamped (R26-198).


**Numbers assigned at the lane-A merge (2026-09-22):** rulings E99 s92 (a prop is bare of paper, not of weight - T6b), s93 (a PLAUSIBLE page draws), s94 (read the monitor on the script's own basis), s95 (five years on the operator's word); backlog R26-249 (every page's build vs its span), R26-250 (a rule label over the bars), R26-251 (the measurer's font-rebuild race), R26-252 (the lab's stamp clock), R26-253 (the empty room covers the basis label), R26-254 (the ingester), R26-255 (a bars figure re-placed by the line rule under chart states), R26-256 (an emphasized bar's pill). Where this plan still reads `s??` / `R26-??`, this table is the key.

## Ruling coverage (added 2026-09-23 after the membership stack was found unslotted)

Every operator ruling that asks for something to be BUILT names its carrier here in the SAME commit that writes the ruling; a ruling with no row below is a principle only. The parent re-runs the coverage audit (every E99 ruling since the plan opened, against this table, the slices and the backlog) before each lane merge.

| ruling | ask | carrier |
|---|---|---|
| s87 / s88 | the stamp, its size, its ring | T2-T5 (done) |
| s90 / s97 | the longform profile, the phone type scale, badges as the key, the default flip | T8, T9, T10, T11 |
| s92 / s96 | the prop's shadow; the 196 px bar | T6b, T6c (done) |
| s93 | plausible pages; new recipes | T14 (done), T35 |
| s94 | row 22 on the script's basis; a drawn figure names its basis | T30 |
| s95 | the fives cite s95 | T27, T31 |
| s98 | blur under a dock | T40 (+ T8b's receded panels) |
| s99 | a light that travels / blinks is motion; the freeze beat | T36, T42, T49, T75 (the ring that travels), T77 (a blinking glow) |
| s100 / s109 (5) | area forms; E53 as defaults | T50, T44 (the iceberg), T51 (the fill gauge), T64 (the stacked bar of values) |
| s101 | the membership stack | T45 |
| s102 | a second / inverted axis | T43b, T64 (the combo's line on its own labelled scale) |
| s103 | H-3 keeps its certificate (no re-roll) | `host/HOST-NOTES-H.md` |
| s104 (+ amendments) | panels, four panels, composable focus; row 21 on them; a panel arrives by resize | T8b (done), T8c, T29, T52 (companion bars as a panel), T54 (the inset echo), T60 (two verdict panels) |
| s105 (+ amendment) | a recast / a story-moving transform resets M03 | T26c, T26c2 (done in lane B) |
| s106 | props placed and moved freely; the fit advises | T26d (done), T59 (the balance's loads), T69 (the rig's prop) |
| s107 | prop <-> page / chart morphs | T26e (done; follow-ups R26-292, R26-293) |
| s108 | chrome as objects; the camera free | T26f (done), T61 (the chapter pill as chrome), T80 (the pedestal and the lens) |
| s109 (1)-(4) | schematics; rings on every vertex; pies incl. 3D exploded + the push | T46, T47, T48, T62 (candles and the motif as schematics), T63 (the tilt is the camera's), T75 (the phase-shift slide on a schematic) |
| s109 | the broken cross-era axis | answered by s111 - T66 |
| s110 (1) | a stack of values is valid under s109's tests; its home case is the stacked-bar-plus-line COMBO, each scale labelled per s102 | T64 (+ T50's honesty check) |
| s110 (2) | a ring may circle a picture, a card or a prop the sentence points at, its number beside it (E56 narrowed, not lifted) | T65 |
| s111 | the broken cross-era axis when the claim is the LEVEL (one y unit, both eras labelled, the break drawn); the rebased overlay stays for a SHAPE claim | T66 |

**Harvest coverage** (added 2026-09-23; the operator: "yes, add all of the bravos slices"): every MISSING/PARTIAL harvest item is carried by T36-T50 / T51-T80 (or by T8-T10, T8b, T26a, T43b, T45 where they already name it) or listed as skipped below. Carriers by harvest id (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`):
- TYPE: T1 T44; T3 T45; T7 T46; T8 T62; T9 T47; T10 T48 (the honest donut; the decor use is skipped); T14 T43b; T21 T43; T23 T41; T24 T58; T26 T60; T27 T59; T29 T50 + T64; T30 T48; T31 T57; T32 T55; T33 T63; T34 T51; T35 T66 (s111); T38 T56; T39 T52; T40 T54; T46 T62.
- ACTION: A9 T39; A10 T38; A11 T36; A12 T37; A13 T36 (the comet head); A14 T42 (tiles) + T62 (a datum); A16 T44; A17 T41; A19 T67; A21 T76; A23 T40; A26 T57; A27 T43; A33 T80; A34 T61; A35 T69; A36 T42; A37 T63 (after its frame check); A40 T59; A41 T76; A42 T38; A43 T38; A44 T61; A45 T73; A46 T73; A48 T72 (on T26a); A49 T37; A50 T74; A51 T74; A52 T75; A53 T75 (measured; T46 carries the schematic's lag); A54 T75; A55 T46; A56 T68; A57 T80; A59 T42 (SELL) + T60 (BUY); A60 T56; A61 T53.
- EFFECT: F2 T77; F3 T42; F12 T53; F14 T77; F15 T43b; F17 T8; F18 T76; F19 T77.
- RECIPE: R1 T44; R2 T79; R3 T40; R4 T67; R5 T68; R6 T46; R8 T43; R13 T53; R14 T60; R16 T69; R17 T63; R18 T44; R19 T70; R20 T44; R21 T71; R22 T44; R24 T44; R25 T44 (composing T56's equation row); R26 T68; R27 T71; R28 T72; R29 T73; R30 T72; R31 T74; R32 T71; R34 T70; R35 T70; R36 T54.
- STYLE: S2 T8 + T10; S3 T41; S5 T79; S6 T79; S9 T78; S10 T78; S11 T78.
- Rulings beyond the harvest: s110 (1) T64; s110 (2) T65; s111 T66.

**Skipped, with reasons:**
- T44 promo dashboard / strategy equity curve / returns table: conversion content, not a sentence act - the harvest (`:83`) marks it "**Not proposed**: this is conversion content"; the guide (`BRAVOS-USE-WHEN.md:1125-1126`): "(not ours) a product pitch" / "we have no product".
- T45 end-card collage: the harvest (`:84`) "Decor only, not proposed"; the guide (`:1132`) "it would be read as evidence".
- T10's decorative use (a donut with no figures): fails s100 (b) (harvest `:49`); the honest donut is T48.
- F6 circuit-trace ground: decor (harvest `:171`); the guide (`:688`) "don't: on a data page".
- F13 satellites with cone beams: decor over a count array, one Gemini 09-10 sighting (the guide `:547-548`: "decor over a count array" / "don't: as evidence").
- F16 vignette + noise ground: Gemini-only and disputed by the spec's measured flat ground (C12, OPEN on weak evidence); E22 owns the ground register (the guide `:1137-1138`).
- Not MISSING/PARTIAL, noted for completeness: A64 (continuous push) and A65 (tracking pan) are HAVE as `camera:keys` and REFUSED by E59 and M14 (C11).

## Task Slices

The TDD fields: `tdd-v1` has no definition on disk, so this plan defines its own. **Regression** is the
command that must go red first. **Expected RED** is what it prints before the change; the review
re-verified the stamp, chip and T9 reds on `ff08213`. **Red / Green / Refactor evidence** hold the
verbatim tails and are left pending.

**Every body row slice (T15-T32) shares these rules:**

- **Owner:** implementation_luna. **Lane:** A. **Engine lock:** none.
- **Write set:** `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`,
  `.../SHOT-TABLE-H.md` and `.../build-h/**`.
- **Common acceptance:**
  - the row is built on today's page and captions (Decision 2), words-anchored;
  - each dip names the transform it refused (s74), and a dip happens only at a world change (E47);
  - life is visible on two tiles 2 s apart (s82 (e)), and the idle-token count is written;
  - E50's clock holds on every chart;
  - every FAIL is fixed or named;
  - the parent reads the row's tiles beside build-f's frames at the same instants.
- **Common Validate:** the door, then
  `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`,
  unpiped.
- **Common Expected RED:** before the slice, `SHOT-TABLE-H.md` has no row covering the slice's window.

### T0: The approval, the claim and the three decisions recorded
- Status: done
- Owner: parent
- Depends on: approval
- Write set: `docs/WORKTREE-REGISTER.md` (this lane's row: P69 approved, the slice, no engine lock yet; lane B's row when it is created), `.claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md` (T6: `Depends on: T5, HG3` becomes T5 plus the operator's 2026-09-22 decision (2); T6 is routed to P69 T14-T34), `docs/content-video-engine/BACKLOG.md` (R26-241 reopened, with the note that `4130942` closed it on the CRLF half only), this plan
- Acceptance: the register row says the claim at `ff08213` predates approval and is now approved; P68 T6's dependency reads as the operator's decision; the R26-241 row reads `open`; Decisions 1-3 are written into this plan's Summary
- Validate: `python -m pytest content/video_engine/tests/test_worktree_register.py -q` and `python scripts/prp_validate.py .claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`
- Evidence: 2026-09-22 parent - register row, P68 T6 dependency, R26-241 reopened, status running; test_worktree_register + prp_validate green

### T1: The page-box pin measures boxes, not bytes (R26-241, at the root)
- Status: done
- Owner: implementation_luna
- Depends on: T0
- Write set: `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/tests/test_page_boxes.py`, `content/video_engine/assets/page-boxes.v1.json`, `docs/content-video-engine/BACKLOG.md` (the R26-241 row, closed by the parent on this slice's evidence)
- Acceptance: (1) `--check` compares the document with `measured` and `player_sha256` excluded; both stay in the file as provenance. (2) `test_page_boxes`'s sha equality becomes a provenance-shape check (a 64-hex string), and freshness becomes a browser test that re-measures and diffs the boxes (`needs_browser`). (3) An engine byte that moves no box leaves both green; a moved box fails, naming the builder, the aspect and the box. (4) `ledger_page._full_stage_fixture_is_fresh` is left alone (`ledger_page.py` is lane B's), and its one test (`test_fed_full_stage_fixture.py:327`) stays green
- Regression: `python -m pytest content/video_engine/tests/test_page_boxes.py -q -k "pin or check"`
- Expected RED: (a) the new case monkeypatches `M.template_sha` to another digest and fails with "the fixture was measured from a different player"; (b) the new case runs `--check` against a copy whose `measured` is yesterday, and gets `DRIFT` and exit 1
- Validate: `python -m pytest content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_fed_full_stage_fixture.py -q` then `python content/video_engine/scripts/measure_page_boxes.py --check`
- Red evidence: `4 failed, 1 passed, 44 deselected` - "the fixture was measured from a different player" and "DRIFT ... assert 1 == 0" (the two expected reds)
- Green evidence: in place, fable-p68: `test_page_boxes.py` + `test_fed_full_stage_fixture.py` -> `64 passed in 34.18s`; `measure_page_boxes.py --check` -> `PASS 5 builders x 15 geometr(ies) measured identical` (exit 0)
- Refactor evidence: a first combined run under load failed the freshness test on a font-rebuild race in the shared `render_baseline.prepare_page` (fixed 250 ms settle) - re-run idle green; filed as backlog R26-?? (the measurer can read a page before its font rebuild lands), outside T1's write set
- Evidence: built by implementation_luna as a patch (the harness fences this session's agents out of fable-p68 Edit), applied by the parent with `git apply`; the fixture needed no `--write`; R26-241 closed in BACKLOG

### T2: The motion gate counts a stamp's contact (R26-247, the gate; STAMP ONLY)
- Status: done
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_stamp_is_a_landing.py` (new)
- Acceptance: (1) `STAMP_CONTACT_S` is mirrored with `[DERIVED: stopaction.mjs STAMP_LAND.tc]` and pinned by a test that computes `tc` from the module's `STAMP_ARRIVAL.LAND` (the closed form at `stopaction.mjs:307-312`) to within 1e-4. (2) An `arrive == "stamp"` branch is added to `_landings` (`:2991-2993`), `_arrivals` / `_arrival_events` (`:3144-3157`) and `_cadence_gate`. The throw/land expressions in every reader are untouched: 0.46 at `:2992`, `STOP_FLIGHT_S` / `STOP_LAND_S` elsewhere. (3) A stamp dock yields an M01-M03/M07 event, an M20 row, an E51 anchor and an M29 dock landing, all at `enter + STAMP_CONTACT_S`. (4) The camera mirror (`_attention_moves`, `camera_state_at`) is NOT touched here; it moves with the player in T4. (5) **Hard:** every throw/land output is byte-identical, including `test_gate_motion_density.py:1411-1413` (the 9.00 s landing)
- Regression: `python -m pytest content/video_engine/tests/test_stamp_is_a_landing.py -q`
- Expected RED: for a stamp dock, `_arrival_events` returns `[]`, `_landings` gives `(enter + 0.0, 'dock ... stamp')`, and `_cadence_gate` returns `None`
- Validate: `python -m pytest content/video_engine/tests/test_stamp_is_a_landing.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_gate_motion_density_surface_clock.py -q`
- Red evidence: `9 failed, 2 passed in 0.78s` (the two passing are the throw/land pins); probed on the old code: `_arrival_events []`, `_landings [(9.2158, 'dock fed stamp')]` (enter + 0.0), `_cadence_gate None`
- Green evidence: parent re-run in place: `152 passed, 4 skipped in 1.25s` (the skips: the Tokyo short build not on disk)
- Refactor evidence: a before/after snapshot of `_landings`/`_arrivals`/`_arrival_events`/`_cadence_gate`/`_dock_landings`/`_untied_pushes`/`_attention_moves` and every gate message over all 39 on-disk timelines with a throw/land/stamp dock: 37 identical, 2 changed - exactly the two stamp goldens (`prop-stamp`, `prop-stamp-ink`)
- Evidence: `STAMP_CONTACT_S = 0.1542` (module 0.154206). OPEN FOR P69-HG1: the engine's own comments (`stopaction.mjs:279-281`, ~`:380`) and `test_the_stamp_arrival.py:42` call a stamp's contact its t = 0 (the ring is thrown from it); the plan builds on the scale crossing, per the operator's decision 1 - HG1 rules. `probe.py:837` reads `G._landings`, so its stamp instants move by 0.1542 s too

### T3: A stamped landing is sounded at its contact, at the engine's mass (R26-247, the cues)
- Status: done
- Owner: junior_developer
- Depends on: T2 (same checkout; the same contact)
- Write set: `content/video_engine/scripts/authoring/audio.py`, `content/video_engine/tests/test_authoring_kit.py`
- Acceptance: (1) `stamp_contact_s()` reads `STAMP_ARRIVAL.LAND` from `STOP_MODULE` and computes `tc`. (2) `landing_contact(t, "stamp", dials)` = `t + STAMP_CONTACT_S`; the throw and land branches are unchanged. (3) `row_arrivals` yields stamp docks by default. (4) `fired()` gives a stamp its contact, and its mass as `e.option or "ink"`: the engine's own default (`:16969`), for stamps only; throw/land keep `"paper"`. (5) An `arrival_mass(opts)` helper returns that default, for the door to call in T14. (6) The binder matches `landing N (stamp, ink)`. (7) The Evidence line states that `lab_build.py:1014` and `tokyo-tea-break/build_short.py:507` carry no stamp rows, so their outputs do not move
- Regression: `python -m pytest content/video_engine/tests/test_authoring_kit.py -q -k "stamp or landing or row_arrivals"`
- Expected RED: `A.landing_contact(2.0, "stamp", dials)` = `2.32`; `list(A.row_arrivals(<stamped row>)) == []`; `fired()` labels an unmassed stamp `paper`
- Validate: `python -m pytest content/video_engine/tests/test_authoring_kit.py -q`
- Red evidence: `6 failed, 7 passed, 77 deselected` - `assert 2.3200000000000003 == (2.0 + 0.1542)`, `assert [] == ['prop-x']`, no `stamp_spring` / `arrival_mass`; probed: an unmassed stamp labelled `paper`
- Green evidence: parent re-run in place: `test_authoring_kit.py` -> `90 passed in 0.53s`
- Refactor evidence: `stamp_contact_s()` rounds to the gate's 4 dp, so the cue and `G.STAMP_CONTACT_S` read one instant (0.1542)
- Evidence: grep - no stamp rows in `lab_build.py`, `tokyo-tea-break/build_short.py` or `steel-and-paper/build_episode_h.py` (a third `row_arrivals` caller, `:601`), so none of their outputs move. Filed backlog R26-?? (`lab_build` has no stamp in `ARRIVAL_MASS` `:210` / `ARRIVAL_LANDS_S` `:168`)

### T4: The camera may push on a landed stamp - the player and the gate's mirror together (R26-247, the camera; E51)
- Status: done
- Owner: implementation_luna
- Depends on: T3
- Write set: `content/video_engine/scripts/kinetics/camera.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (only the synced `camera` region and the `contactOf` at `:13383`), `content/video_engine/scripts/gate_motion_density.py` (`_attention_moves` `:1026-1036` and `camera_state_at` `:1143-1156`: a stamp branch only), `content/video_engine/tests/kinetics/camera.test.mjs`, `content/video_engine/tests/test_camera.py`, `content/video_engine/tests/test_stamp_is_a_landing.py`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: (1) `camAttentionState` accepts a stamp. (2) `contactOf` gives a stamp `STAMP_LAND.tc`; the `? 0` branch is live. (3) The gate's mirror agrees at the same instant, and main never carries one without the other (a single commit). (4) A browser test (the P49 T4 pattern, `test_camera.py:210`) shows identity before the stamp's contact and a 1.06 pull after it. (5) Throw/land camera behaviour is byte-identical. (6) The goldens are byte-identical. (7) The fixture is re-measured, and `test_page_boxes` is green
- Regression: `node --test content/video_engine/tests/kinetics/camera.test.mjs`
- Expected RED: `camAttentionState` returns `null` for a stamp dock (the review probed this); the browser case reads zoom `1` at contact + 0.5 s; the gate's `_attention_moves` returns `[]`
- Validate: `node --test content/video_engine/tests/kinetics/camera.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_camera.py content/video_engine/tests/test_stamp_is_a_landing.py content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: node `pass 11, fail 1` (`camAttentionState` null for a stamp); pytest `4 failed, 12 passed` - `assert [] == [(9.37, 9.87, 'fed')]`, mid-ramp zoom 1.0 not 1.03, the browser case `('half-way in from the contact', 1)`
- Green evidence: parent in place - node camera tests 12/12; `sync_kinetics --check` in sync (43 modules); `test_stamp_is_a_landing` + `test_kinetics_sync` + `test_gate_motion_density` 162 passed, 4 skipped; `test_camera` + `test_page_boxes` + `test_golden_frames` 235 passed in 441.83s (goldens byte-identical)
- Refactor evidence: HEAD vs new gate, `_attention_moves` + `camera_state_at` at 0.1 s over 39 on-disk timelines with a throw/land/stamp dock: 39 identical; a node-vs-gate cross-check at 9 instants agrees within 1e-4; `--check` before `--write`: no box moved (only `player_sha256` rewritten)
- Evidence: the player and the gate mirror land in ONE commit. The replaced engine comment cited E99 s87 ("its contact IS its enter, which is why the ring is thrown from that frame"): the camera now pulls from 0.1542 while the ring still fires from the enter - P69-HG1 rules the instant (operator decision 1); reverting is one constant per consumer

### T5: The stamp takes the room first; the row's other docks are placed around it (R26-247 L2; E99 s88)
- Status: done
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (the row loop at `:7505-7519` and the `reserve` passed to `stamp_dock_place` / `dock_place`), `content/video_engine/tests/test_the_stamp_arrival.py`
- Acceptance: (1) A row's stamps are fitted FIRST, in row order, each against the earlier stamps' fitted boxes (mark plus ring peak), so "the room chosen is the one that gives the biggest mark" (s88 (3)). (2) The row's other docks are then placed with every stamp's fitted box in their `reserve`. E65's placer still always finds a place (by scale), and never lands over a mark or its ring. (3) A card plus a stamp, and two stamps, on the golden page compile with 0 px overlap, or are refused by name with the row number. (4) Single-dock rows and the `prop-stamp` goldens are unchanged. (5) Frame: the new browser case renders the stamp-plus-card row and writes its PNG to the test's tmp dir (the path is printed), and the parent reads that frame (judge the frame, not the diff). (6) R26-247's residual line names R4 only; R1 is built (`:5871-5875`, `4756d9d`)
- Regression: `python -m pytest content/video_engine/tests/test_the_stamp_arrival.py -q -k "other_dock or two_stamps or takes_the_room_first"`
- Expected RED: the new cases measure a positive overlap, or a smaller mark than the stamp fitted alone (today the stamp is fitted blind to the row's other docks - review item re-verified)
- Validate: `python -m pytest content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: `7 failed, 30 deselected` - card over the turned mark `(41605.2 px^2, ring 159.5 px into the card)`; two stamps fitted to one spot `clash (54604.3, 159.5)`; frame overlap 45291.7 px^2
- Green evidence: parent re-run in place: `test_the_stamp_arrival.py` + `test_golden_frames.py` -> `198 passed in 385.30s`; the agent's 11 neighbouring placer files `424 passed, 3 skipped`
- Refactor evidence: stamp alone 206.5 x 189.5 = stamp beside a card (same mark, same centre, ring 1.1037x); the card gives ground (382 x 239 -> 194 x 133, over the 80 px floor); a second stamp 131.1 x 120.1 near the 120 px floor; 0.0 px^2 / 0 px ring overlap every way. Stamp boxes pass as a sibling `clear_of` (not `reserve`, which `free_bands` reads only as a foot cut-off)
- Evidence: FRAME READ by the parent (`scratchpad/p69t5-stamp-plus-card.png` beside the red): the Fed mark clear at full size, the card in open ground, neither over the other. Seen and filed, pre-existing: the E65 `empty` room covers the y basis label (backlog R26-??). R26-247 residual: R4 only

### T6: A figure lands on a bars page and the compare morphs it (R26-190)
- Status: done
- Owner: implementation_luna
- Depends on: T5
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildPerform` `:11364-11450` and the figure anchor it feeds; `paintCompare` `:11319` only if its read of the figure must change), `content/video_engine/scripts/species/compare.mjs` (only if the compare's source must change; synced), `content/video_engine/tests/test_compare_on_bars.py` (new), `content/video_engine/assets/page-boxes.v1.json`, `content/video_engine/tests/golden/**` (only if a golden carries a figure on a bars page that never painted - it re-pins in this commit, with the parent's frame read)
- Acceptance: (1) On a `story`/`bars` page, a figure anchors to its bar's top (the emphasized bar's own rect), as a line figure anchors to its point. (2) `chart_to compare` (form melt, then splash) morphs it. (3) The three H beats are compiled as fixtures and paint: row 17's 94 figure, row 18's 20 -> 10 halving, and row 21's 1 vs 3. (4) Line pages are byte-identical. (5) The fixture is re-measured, and `test_page_boxes` is green
- Regression: `python -m pytest content/video_engine/tests/test_compare_on_bars.py -q`
- Expected RED: the served player reports `nFig: 0` on a bars page with a `figure` species, and the compare paints nothing at its instant (the `if (!pts.length) return null` at `:11449`)
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_compare_on_bars.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q`
- Frame acceptance: the parent reads the halving at its start, middle and landing
- Red evidence: `5 failed, 3 passed` - `nFig: 0 - the bars page dropped its figure (R26-190)` x3; `u=0.15: the compare paints nothing at its instant` x2
- Green evidence: parent re-run: `sync_kinetics` in sync (43); `measure_page_boxes --check` PASS (no box moved); `test_compare_on_bars` + `test_page_boxes` + `test_golden_frames` + `test_kinetics_sync` -> `249 passed in 418.54s`; `node --test content/video_engine/tests/kinetics/*.test.mjs` -> 651 pass, 0 fail
- Refactor evidence: three rounds on the parent's frame reads - (1) the bar's own value label YIELDS to its figure, which sits centred at the bar top (no "94% 94%" / "20% 20% 10%"); every written line inside SAFE_BOX; value labels clear comparator rules (`lpValsClearRules`); (2) a number never sits on the far side of a rule its value does not pass - `lpBarLabelPlace` puts the 94 INSIDE its bar under the 100 rule (E28); (3) the operator: "that bar can't be that wide ... it reads like a giant block" - `LPBAR.CAP_N = 2` caps a bar at a two-bar page's width, fewer bars centred (a 3-4 bar cap re-pins the `tags-to-bars` golden: the operator's pick at the end-of-run card, beside T10b)
- Evidence: frames read by the parent (`scratchpad/p69t6-{halving-*,94-land,1v3-land}.png`); goldens byte-identical, line pages byte-identical. Filed: the hline label over a bar (R26-??). Open outside the write set: `species/figure.mjs` re-places a bars figure with the line rule on a page with a SECOND chart; an emphasized bar's pill is not yielded

### T6b: A bare prop carries a resting shadow - depth and weight (the operator, 2026-09-22)
- Status: done
- Owner: implementation_luna
- Depends on: T6 merged; runs in LANE B (`claude/p69-s90`, the engine lane) FIRST, before T8 - so lane A's body rows never render on an engine mid-edit
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the dock painter's prop branch and the `.dock-contact` settle), `content/video_engine/scripts/kinetics/stopaction.mjs` (a `PROP_SHADOW` dial block only, synced), `content/video_engine/tests/kinetics/stopaction-stamp.test.mjs`, `content/video_engine/tests/test_prop_shadow.py` (new), `content/video_engine/tests/golden/**` (the `prop-stamp*` goldens re-pinned with the parent's frame read), `content/video_engine/effects/cards/dock_kind.json` (the `dock_kind:prop` card's `does` loses "no ... shadow"), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the operator: "the props should have shadow added to them to give them some depth/weight" (a ruling, `E99 s??` at merge; it amends the bare-prop card's "no paper, border, shadow or rail" - a prop stays bare of PAPER, never of weight). (1) A `dock_kind:prop` cutout carries a RESTING drop shadow that follows its painted alpha (a CSS `drop-shadow` on the cutout, not a box under the element), cast from the engine's ONE stage light - the same direction as the extruded bar's cast shadow and the melt's highlight (find it; never a second light) - soft, short and dark enough to seat the prop on the page, on the charcoal page and on a light ground alike. (2) The stamp's CONTACT shadow hands over to the resting shadow at settle instead of vanishing (`sx.phase !== "settled"` today zeroes it), so the weight is continuous. (3) A card (paper) keeps its own shadow exactly as today - byte-identical card goldens. (4) The prop's box for placement and the stamp fit include the shadow's extent, so nothing lands on it. (5) The `prop-stamp` / `prop-stamp-ink` goldens re-pin in THIS commit, with the parent's frame read; every other golden byte-identical AMENDED 2026-09-22 on the operator's read of v1 (a soft drop-shadow): "The shadow doesn't look great, I think we need like cross hatch markings as shadow for texture" - the resting shadow is a CROSS-HATCHED silhouette (two families of fine engraved lines, the primary along the stage light, masked by the prop's own alpha, offset toward the light's fall, the pattern fixed to the page), visible on the charcoal page and on a light ground; the stage light is DROP's `-125` (R26-257)
- Regression: `python -m pytest content/video_engine/tests/test_prop_shadow.py -q`
- Expected RED: the served player shows no `drop-shadow` on a settled prop cutout, and the contact shadow's opacity reads 0 after settle
- Validate: `node --test content/video_engine/tests/kinetics/stopaction-stamp.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_prop_shadow.py content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Frame acceptance: the parent reads the settled Fed on the charcoal page and on a light ground, before and after; the operator reads it at P69-HG2 (the first stamped prop)
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: lane B, 2026-09-22/23 - v1 soft drop-shadow REJECTED by the operator; v2 cross-hatch `1d7fbf5` (primary 4.5 px / crossing 7 px, 29.3 / 112.4 levels line-vs-gap); the operator: "the cross hatching needs to be much tighter/finer" -> `041e2ff` (primary 2.25 / 0.7 px, crossing 3.75 / 0.5 px, TAPER_PX 3; +11.6 levels on charcoal, +40.4 on light, against the bare ground; reach 15.35 px inside the stamp fit's 16.8). Goldens re-pinned: prop-stamp 03c396dd.. -> f974a8c0.., prop-stamp-ink beb325d9.. -> 3698dbca.., prop-stamp@proof-exit d3646b8c.. -> 3e4d26c5..; every other golden byte-identical. Parent in place: node 654/654, pytest 259 passed. Open: thrown props' placement (R26-258), the hatch fixed while the prop's own camera moves it (R26-271)

### T6d: A prop keeps its alpha through the compiler; end tags boxed at their drawn size (found on T23's frames, 2026-09-23)
- Status: done (lane B ff0ad89 + fixes4 1931431; on main 19144bb)
- Owner: implementation_luna (LANE B, after the key-rail fixes)
- Depends on: T6b, T10c, the key-rail fixes; lane B
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`data_uri` / `dock_uri`), `content/video_engine/scripts/ledger_page.py` (`_landscape_full_boxes`, `page_boxes`), `content/video_engine/assets/page-boxes.v1.json`, `content/video_engine/tests/test_prop_alpha.py` (new), `content/video_engine/tests/test_page_boxes.py`
- Acceptance: (1) a dock asset with an alpha channel (a `dock_kind:prop` cutout, any PNG with transparency) compiles to a data URI that KEEPS the alpha (PNG or WebP-with-alpha, at the card width), so the Fed's sky is the page and the T6b hatch follows the silhouette, not the square; a photo without alpha stays JPEG (bytes unchanged); every golden that embeds no alpha asset byte-identical, and `build_golden_sources._prop_stamp`'s direct embed and the compiler's path give the same pixels. (2) On a MEASURED page the end tags are boxed at their drawn rects (one box per tag), not the estimate's solid column (x 1329-1880, y 250-808 on v4), so a stamp can take the empty right margin level with the rules; an estimated page keeps the column. (3) The row's door is never edited here.
- Regression: `python -m pytest content/video_engine/tests/test_prop_alpha.py content/video_engine/tests/test_page_boxes.py -q`
- Expected RED: the compiled asset map names `data:image/jpeg` for `prop-federal-reserve-building-v1.png`, and `page_boxes` on a measured two-series page returns one tag column
- Validate: `node --check` the engine, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_golden_frames.py`
- Frame acceptance: the parent reads the Fed stamped on T23's page: no black square, the hatch on the silhouette, parked in the right margin
- Evidence: lane B ff0ad89, 2026-09-23 - a picture with real alpha embeds as PNG (the Fed compiles to data:image/png; opaque pictures keep their JPEG bytes); the fixture records each end tag's drawn rect (`tag_boxes`) and ONLY the stamp's ring fit reads them (the camera kept the estimate: the drawn union would refuse row 1's zoom - R26-281). Parent in place: 293 passed, no golden moved. Scope note (review 4 MN2): EVERY transparent dock asset now embeds with its alpha, not only props - any door rebuilt after the merge changes those pictures from squares to cutouts. Follow-ups in fixes4: colour-key transparency (MN1), a byte cap with WebP-alpha over it (MN2), tag_boxes limited to line end tags with a data fingerprint (MN3). T23 needs, AFTER the merge, `measure_page_boxes.py --write --project build-h` from the merged tree, then FED_STAMPED = True

### T6c: A bar is narrow - the cap at a five-bar page's width (E99 s96)
- Status: done
- Owner: implementation_luna
- Depends on: T6b (the same engine file; lane B's sequence)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`LPBAR.CAP_N` and the bars builder's capped layout only), `content/video_engine/tests/test_compare_on_bars.py`, `content/video_engine/tests/golden/**` (every golden whose page has fewer than five bars re-pins - `tags-to-bars` first - with the parent's frame read), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the operator: "The two bar width is also still way too much" (E99 s96). (1) The cap is Bravos's MEASURED hero-bar width (`docs/research/bravos-style/BRAVOS-LONGFORM-CHART-SPEC.md`): 196 px on a 1920 stage (10% of the frame), its gap at the measured 0.44 bar/spacing ratio - replacing `LPBAR.CAP_N` with a width dial in stage px, [DERIVED] from the spec; fewer bars keep that width, centred, even gaps. The operator's rounded shoulders (T10b) win over Bravos's square corners. (2) The value label, the figure, the category label and `lpBarLabelPlace` follow the narrower bar; a category label wider than its bar wraps to two lines rather than colliding with its neighbour. (3) Pages with five or more bars byte-identical. (4) Every re-pinned golden is listed with before/after sha and its frame read by the parent; line pages byte-identical
- Regression: `python -m pytest content/video_engine/tests/test_compare_on_bars.py -q -k cap`
- Expected RED: with `CAP_N = 2` a one-bar page's bar measures ~405 px on the 1920 stage, over the 196 px cap
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --check` then `--write`, then `python -m pytest content/video_engine/tests/test_compare_on_bars.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Frame acceptance: the parent reads the 94, the halving, the 1 vs 3 and every re-pinned golden before commit
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: lane B `9ffbf60`, 2026-09-23 - `LPBAR = { W_PX: 196, PITCH_RATIO: 0.44 }` [DERIVED from the measured spec] replaces CAP_N; `lpStagePx` measures one chart unit in stage px (browser-checked 1.3340 vs 1.3340); a bar renders at 196.00 px, fewer bars centred, rounded shoulders kept, a wider name wraps. Only `tags-to-bars` re-pinned (1f5b4d9a.. -> 8e827822..); the 16 other golden bars pages already narrower. Parent read the 94 / halving / 1 vs 3 frames. Parent in place: node 654/654, pytest 234 passed. Pre-merge review: MERGE AFTER FIXES (F1 a wrapped name through a rescale, F2/F4 tests) - fixes staged after T8

### T7: R26-230, R26-222 and R26-231 closed on their tests; the one owed test added
- Status: done
- Owner: junior_developer (the test); parent (the rows)
- Depends on: T2, T3, T4 merged (the H-bed rebuild imports the gate and the cues)
- Write set: `content/video_engine/tests/test_restage_through_the_compiler.py` (new), `docs/content-video-engine/BACKLOG.md` (rows R26-230, R26-222, R26-231; R26-247's residual at T5's merge), `docs/content-video-engine/CAPABILITIES.md` (one line each)
- Acceptance: (1) The new test compiles one ledger row through `build_scene_timeline_f` at 16:9 and at 9:16 (the `ASPECT` pin, `test_the_stamp_arrival.py:572-580`). The portrait plot sits inside `SAFE_BOX["9:16"]`, the landscape plot inside `full_stage_bands.evidence_safe`, and the data payload is identical. (2) The H bed, rebuilt into a private dir, compiles under `validate_page_build_spans`. (3) `probe.py <dir> --gate`, then the gate, shows M28 with no label paired with its identical copy. (4) Each row reads DONE, citing its tests (`test_fed_full_stage_bands.py`, `test_fed_page_build_span.py`, `test_fed_axis_handoff.py`, the new test) and this slice's run, with `75fc99f` named as the origin ("wip preservation"), not the approval. The `reviewer`'s read of those three diffs is the review of record. (5) R26-230's caption-size half stays with P68 HG3 (A) (6) ADDED from the review: R26-231 closes stating its scope - only pages with an authored build are checked (`build_scene_timeline_f.py:4501`); a follow-up row asks for every page (replaying 44 timelines, 0 of 160 page rows would be refused); R26-222 closes citing the player fix (`scene-evidence-engine.mjs:12203-12261`) and the probe's invisible-label skip (`probe.py:125-133`), and its stale `:2316-2368` becomes `rescale_state` `:2949`
- Regression: `python -m pytest content/video_engine/tests/test_restage_through_the_compiler.py -q`
- Expected RED: none - this characterizes code already on main; a failure is the finding and keeps the row open
- Validate: `python -m pytest content/video_engine/tests/test_fed_full_stage_bands.py content/video_engine/tests/test_fed_page_build_span.py content/video_engine/tests/test_fed_axis_handoff.py content/video_engine/tests/test_restage_through_the_compiler.py content/video_engine/tests/test_full_stage_page_is_measured.py content/video_engine/tests/test_page_is_the_plate.py -q`
- Red evidence: n/a (characterization)
- Green evidence: `test_restage_through_the_compiler.py` 6 passed; the six-file Validate `102 passed in 32.46s`; the H bed rebuilt into a private dir (`STEEL_H_BUILD_DIR`) compiles under `validate_page_build_spans` (door exit 0, cues 3 of 3 bound); `M28 PASS ... 789 label pair(s) checked`
- Refactor evidence: n/a
- Evidence: rows R26-230/222/231 CLOSED in BACKLOG on the reviewer's read (`REVIEW-P69-T7-ASTRA-ROWS.md`) and this run, `75fc99f` named as origin; R26-231's scope follow-up filed. Found and fixed by the parent: the door's `## Recall` block cited `audio.py:429` and `CAPABILITIES.md:93`, stale after T3 - the P67 receipt refused the compile; now `:471` / `:94`. The door rewrites the tracked `SHOT-TABLE-H.md` on every run (restored after the private build). Planning run 2026-09-22 (fable-p68, `4130942`): the three Astra files -> `46 passed in 20.78s`; the review re-ran them at `ff08213` -> `46 passed in 20.52s`

**RE-SCOPED 2026-09-22 by E99 s97** (the operator: "go much more tighter in [Bravos's] direction ... the chart style in long format is sharper, more electric, and more professional"): T8-T10 build a `longform` page profile to the MEASURED spec `BRAVOS-LONGFORM-CHART-SPEC.md` (a measurement pass over Bravos's frames on disk, landing before T8 starts) - s90's phone type, badges as the key and the three layout fixes are folded into it; T6c's cap takes the spec's measured bar width; T10b's rounded shoulders and hatch are reconciled with the spec (the operator's words win over the reference where they differ). Every override of our own signature is listed for P69-HG3.

### T8: s90 (a) - the phone type scale on every builder the body uses, as a row option (lane B)
- Status: done (lane B 58c5f86 + def63cf; on main 19144bb); HG3 open
- Owner: implementation_luna
- Depends on: T6 merged; lane B created with its register row
- Write set: `content/video_engine/scripts/ledger_page.py` (`READABILITY_PROFILES`, `_validate_readability` `:244-270`, the profile's geometry), `content/video_engine/scripts/build_scene_timeline_f.py` (a `readability` entry in `PLATE_OPTS` `:112` and its stamp onto the page), `content/video_engine/scripts/measure_page_boxes.py` (representatives with the profile), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the profile's reads at `:7907-7910`, `:9192`, `:9254-9259`, `:9549`, extended to the other builders), `content/video_engine/tests/test_fed_chart_readability.py`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: (1) `;readability=landscape-phone` on a ledger row opts that page in without editing the evidence object. The series-file field stays, and the row option wins. (2) The profile is legal on dense-line and on the builders the body's pages use (bars / `shares`, `story`, the checklist/record pages if they are ledger pages - T14's inventory names them). On any other builder it is refused by name. (3) B's roughly 12.5 px phone type is measured on each (s90: "over main's roughly 6.5 px"). (4) Absent the option, every page is byte-identical. (5) The fixture is re-measured; the goldens are byte-identical ADDED 2026-09-23 on the parent's frame read of the first `longform` render (the phone floor applied everywhere: ~61 px ticks, a 60 px source, a sub colliding with the y-label, end tags off the stage): s90 (bigger phone type) and s97 (Bravos's measured 15-18 px ticks) CONFLICT - the operator picks at P69-HG3. The profile carries a TYPE_SCALE dial with three presets (`;readability=longform:bravos|middle|phone`, plain = `middle`); the body builds on `middle` (title ~44, ticks ~26, end tags ~30, source ~20 px at 1920) until the ruling; no collision at any preset; the divergence and railway pages compile under it UPDATED 2026-09-23 (the operator): "the phone version is definitely too bulky" - the `phone` preset is out; `middle` against `bravos` is decided on a real phone at actual scale at the review (P69-HG3)
- Regression: `python -m pytest content/video_engine/tests/test_fed_chart_readability.py -q -k "row_option or bars"`
- Expected RED: `;readability=` is an unknown plate option (refused by the `PLATE_OPTS` check); a bars page with the profile is refused with "only supported by the dense-line builder" (`ledger_page.py:257-258`)
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: lane B `58c5f86` (2026-09-23) - `;readability=longform[:bravos|middle|phone]` on dense-line and bars: #14181E ground, #222830 panel in a 1.5 px border, no gridlines (a zero line only across zero), Inter loaded as its own family (R26-259 within the profile), a pink sans title, sub and source in one safe column, the chart placed below with M28's air, end tags shortened full -> badge -> value (long names kept for T10's key). TYPE_SCALE presets bravos (the spec) / middle (title 44 / ticks 26 / tags 30 / source 20 px at 1920, the working default) / phone (the s90 floor). The first render (the floor everywhere: ~61 px ticks, collisions) was sent back on the parent's frame read. Parent in place: node 654, pytest 323 passed; without the option every golden byte-identical. The review fixes `2e51c16` (F1 wrapped name through a rescale, F2 the hatch's cold seek / failed decode, F4 the cap at every aspect, F5 handed-page punch): pytest 361 passed. Second review (REVIEW-P69-LANE-B-MERGE-2): MERGE AFTER FIXES - N1 the phone source into the caption strip, N2 a `;then=` state's tags unfitted, N3 the Python box estimate 73 px off - fixing before the merge. Overrides of our own signature (option only) listed for P69-HG3: E22 ground/deckle/Kalam/no-outline, the one accent, E53.4 gridlines, "both axes always"; s90's floor met only at `phone`

### T8b: The ledger page draws PANELS - two charts side by side on one page (E99 s104)
- Status: done (lane B 7369f12; r8 refused on the parent's frame read - the quad small, the grown panel ~45% of the stage; r9 accepted); the two-panel single <-> row resize moved to T8c
- Owner: implementation_luna
- Depends on: lane B's current sequence (T10b, T10c, the key-rail fixes); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (a `panels` builder: validation, layout, `page_boxes` per panel), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the page painter: N plots in one page, each with its own axes, title line, end tags / key, and species addressed by panel), `content/video_engine/scripts/build_scene_timeline_f.py` (a species' `panel` index in its target; validation), `content/video_engine/scripts/measure_page_boxes.py` (a panels representative), `content/video_engine/tests/test_ledger_panels.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the operator: "no reason it shouldn't be able to, we already handle 2 evidence docks on world plates, it rhymes to have 2 data panels/charts on ledger plates when needed" (E99 s104). (1) A `panels` object (the format `ev-tnx-two-eras-v3` already carries, and the card's `chart_dock:panels` draws) compiles as a ledger PAGE: two (up to four) plots laid side by side (landscape) or stacked (portrait), each with its panel sub, its axes and its end tags. (2) E79: panels of one measure share ONE scale by default; `independent: true` gives each its own, and the compiler's scale WARN (`ledger_page.scale_warnings`) applies. (3) Species (`build_to`, `figure`, `ring`, `spread`, callouts, the key rail) take a `panel` index and land in that panel's plot; a panel builds on its own clock (one after the other by default). (4) The page composes with `;readability=longform` (each panel in the framed-panel style; one key rail for the page) and with docks/stamps (every panel's boxes in `page_boxes`, so a stamp takes the biggest room across the page). (5) Recast/undraw work per panel. (6) Every existing page and golden byte-identical; one new golden: `ev-tnx-two-eras-v3` as a two-panel page, read by the parent beside the card render. (7) T23 (row 15) may take the panels page or keep v4's overlay - the parent decides on the frame (8) ADDED 2026-09-23, the operator: "we can already resize easily, and morph in various ways, so making that fit with charts should be pretty easy" - a panel ARRIVES by the engine's existing transforms, never by a cut: a standing single-chart page RESIZES into its panel slot (the resize/rescale machinery - `chart_to` rescale/extend, the card-becomes-the-chart resize) while the second panel builds in beside it, and the reverse (a panel leaves, the survivor grows back to the full plot); a morph between the panels (the existing morph/recast verbs) works panel to panel. Find those transforms with `docs_find` first and REUSE them - T8b adds the panel layout and the panel address, not a new motion system (9) ADDED 2026-09-23 (s104 amended, for row 21's four charts): up to FOUR panels on a page; and FOCUS - a panel or a `then=` state can RECEDE (scale back, dim, soften behind the focused one; reuse the composite stack's `recede to the mosaic` and T40's `blur` under a dock - docs_find "recede" / "blur") and be BROUGHT BACK on its word, animated by the existing resize/morph transforms; a receded chart is still on the page (no cut, no dip); the four-chart row never needs a fifth state, so STATE_MAX stays 3 for `then=` while panels carry the rest (10) ADDED 2026-09-23: FOCUS may also be a RACK - the receded panel softens by the existing blur (CAPABILITIES :47/:71) as depth-of-field, the focused one stays sharp (the GITS blueprint's rack focus, research only), in place of or with the scale-back (11) ADDED 2026-09-23 (s104 amended again): FOCUS IS A COMPOSABLE STATE, not a mode list. The page carries a list of FOCUS STATES keyed to words, each naming (a) a LAYOUT - `row` | `stack` | `quad` | `free` (a box per panel, stage fractions) - and (b) per panel a ROLE - `active` (sharp, full ink, its species live), `receded` (scale-back factor, dim, blur radius - each a dial with a default), or `hidden`; one, two or more panels may be active. A change of focus state on a word is ONE transition: every panel's box, dim and blur interpolate on the transition's clock (reuse the resize/morph transforms and the existing blur), so `quad` -> panel 2 grows to cover the page while 1/3/4 blur and recede behind it -> back to `quad` -> panel 4 grows ... composes from the same parts, as does two active side by side with two receded above. Seek-safe; the key rail, species and camera (T26f's chrome) address a panel by index in any state; a receded panel's species hold. Byte-identical for a page with no focus states. Frames: the four-chart row 21 page run through quad -> grow -> quad -> grow, and a two-active state
- Regression: `python -m pytest content/video_engine/tests/test_ledger_panels.py -q`
- Expected RED: a `panels` object compiles to a dense-line page with 0 series (`ev-tnx-two-eras-v3`, P69 T23)
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_ledger_panels.py content/video_engine/tests/test_longform_profile.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the two-panel page beside the card's panels render and v4's overlay
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T8c: A panel's box changes SHAPE and the chart re-lays out - the single <-> row resize (E99 s104 amended, T8b's open item)
- Status: done (lane B; the parent read the resize-in, leave and quad-grow sheets)
- Owner: implementation_luna
- Depends on: T8b; lane B
- Write set: `content/video_engine/scripts/ledger_page.py`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/scripts/build_scene_timeline_f.py` (only if needed), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/tests/test_ledger_panels.py`, `content/video_engine/tests/golden/**`, `content/video_engine/assets/page-boxes.v1.json`, `content/video_engine/effects/cards/page_species.json`
- Acceptance: T8b fixed each panel's viewBox aspect, so a quad grows properly but a two-panel page's single chart stands at its slot size and the resize-in became a fade. (1) A standing single chart on a panels page fills the whole plot region; (2) when the second panel arrives the first SHRINKS into its row slot while the second builds in beside it, and the reverse (the survivor GROWS back to the full region) - one clock, never a cut; (3) the plot re-projects its data to the box's current size every frame, text unstretched (ticks, labels, end tags keep their size and their gridlines, E28), data-anchored species follow; (4) the quad/free grow stays as good as T8b's r9; (5) seek-safe; byte-identical elsewhere; one golden at the resize midpoint
- Regression: `python -m pytest content/video_engine/tests/test_ledger_panels.py -q`
- Expected RED: a single standing panel's plot spans only its slot; mid-resize the plot width does not interpolate
- Validate: T8b's Validate list + `test_authoring_*`, `test_build_effects_catalog.py`
- Frame acceptance: the parent reads the resize-in, the leave and the quad-grow sheets
- Evidence: pending

### T9: s90 (b) - the three layout fixes the side-by-side found (lane B)
- Status: done (lane B 0df626a; review fixes 5ddc035)
- Owner: implementation_luna
- Depends on: T8
- Write set: `content/video_engine/scripts/ledger_page.py` (`_readability_fit_error` `:1563`, `_profile_tag_units` `:1536`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the profile's end-tag, sub, y-label and x-tick placement), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/tests/test_fed_chart_readability.py`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: under the option, each measured on the served player - (1) a long name gets a home - the badge key's line (T10) or a wrapped end tag inside the stage - never a refusal; (2) the subtitle's box and the y-axis label's box never intersect (0 px); (3) the x-tick labels clear the axis line by at least 18 px (main's measured value; B measured 0). Absent the option, byte-identical (4) ADDED 2026-09-22 from the T7 review (`scratchpad/REVIEW-P69-T7-ASTRA-ROWS.md`, MEDIUM): under the profile the plot top measures y 178 in the player, 19 px INTO the full-stage top band (`ledger_page.py:1363-1379`); the profiled page keeps E99 s82's bands - a test pins the plot inside `full_stage_bands.evidence_safe` with the option on
- Regression: `python -m pytest content/video_engine/tests/test_fed_chart_readability.py -q -k "long_name or sub_ylabel or xtick_clearance"`
- Expected RED: a long-name dense-line page with the profile is refused ("cannot fit its enlarged inline end tags", `ledger_page.py:1574`); the measured x-tick clearance under the profile is 0 px; the sub/y-label intersection is non-zero on the representative that the side-by-side read
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T10: s90 (c) - badges as the key, on the even-pill ladder (lane B)
- Status: done (lane B 0df626a; key per state 5ddc035); HG3 open
- Owner: implementation_luna
- Depends on: T9
- Write set: `content/video_engine/scripts/ledger_page.py` (the key's geometry and its box in `page_boxes`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the line-end badge and the key rail), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/tests/test_fed_chart_readability.py`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: under the option - (1) At a line end, a short value/label badge (s90). (2) A key rail maps each series colour to its full name on the `badge-ladder` recipe's own clock (the first at +2.05 s, then 1.30 s apart; `recipe:badge-ladder`), landing on an EVEN pill count where the series allow (E99 s84: "prefer to land on even pills (2 or 4)"). (3) The key's box is in `page_boxes`, so docks and stamps avoid it. (4) M28 is clean. (5) Absent the option, byte-identical
- Regression: `python -m pytest content/video_engine/tests/test_fed_chart_readability.py -q -k "badge_key"`
- Expected RED: the profiled page writes the full series name inline and has no key box in `page_boxes`
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T10b: A bar with rounded shoulders and a soft shadow - an option, read off/on (the operator, 2026-09-22)
- Status: done (lane B 91de567)
- Owner: implementation_luna
- Depends on: T6b (the SAME one stage light and shadow dials as the prop's resting shadow); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the bars builder's bar rect only), `content/video_engine/scripts/ledger_page.py` (the option's validation), `content/video_engine/scripts/build_scene_timeline_f.py` (the row option in `PLATE_OPTS`), `content/video_engine/tests/test_bar_style.py` (new), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the operator, 2026-09-22, on the T6 frames: "that bar can't be that wide ... it reads like a giant block" (the width cap, T6) and "I think it should also have some sort of rounded edges, maybe shadows". (1) A row option (`;bar_style=soft`) gives every bar ROUNDED SHOULDERS (the top corners - the baseline stays square, so a bar still stands on zero; a negative bar rounds its bottom) and a SOFT SHADOW cast from the one stage light (T6b's dials; short, low-alpha - weight, not a 3D prism, which stays `;form=extruded_bar`). (2) The value label, the figure and every rule keep their clearances against the new rect. (3) Absent the option every page is byte-identical (goldens untouched). (4) The body's bars rows take the option (T33 adopts it with the s90 page). (5) The default flips only on the operator's read at the end (a card beside P69-HG3: bars off/on on the 94, the halving and the 1 vs 3) AMENDED 2026-09-22: the bar's shadow is the SAME cross-hatch as the prop's (T6b v2), cast from the stage light (DROP `-125`), so props, cards and bars share one light and one texture
- Regression: `python -m pytest content/video_engine/tests/test_bar_style.py -q`
- Expected RED: `;bar_style=` is an unknown plate option; a bar rect has the builder's default corner radius and no shadow filter
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_bar_style.py content/video_engine/tests/test_compare_on_bars.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Frame acceptance: the parent reads the three H bars pages off/on before the card is queued
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: lane B 91de567, 2026-09-23 - `;bar_style=soft`: LPBAR_SOFT.SHOULDER_PX 14 on the corners away from zero, a square foot on zero, T6b's propHatchLines cut to each bar's thrown silhouette; the parent read halving / 94 / 1v3 soft vs off. Validation: node --check, sync in sync, boxes PASS, 47 passed. HG3 tunes the shoulder by eye

### T10c: A chart card is drawn for its own size - the whole card, bigger type, thicker lines (the operator, 2026-09-22)
- Status: done (lane B b42d6dc + 11ed037)
- Owner: implementation_luna
- Depends on: T8 (the readability profiles it extends); lane B
- Write set: `content/video_engine/scripts/chart_card.py` (and its caller `dock_card` wherever it lives), `content/video_engine/scripts/ledger_page.py` (a `card` readability profile), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the profile's reads), `content/video_engine/tests/test_chart_card_readable.py` (new), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the operator, on row 7's thrown Bravos card: "Those charts still seem tough to read to me" and "Evidence cards that are using charts need to use the whole card and use bigger fonts and thicker lines". Today `chart_card.py` renders the FULL ledger page at the dock width (CAPABILITIES.md:74), so every label shrinks with the card. (1) A chart card is rendered FOR ITS DISPLAYED SIZE: the page is laid out at the card's own on-stage pixel box (not a full stage scaled down), under a `card` readability profile - the plot fills the card edge to edge (no page margins, no caption bands, no source-foot beyond one short line), the type measured at >= the s90 phone floor at the card's displayed size (state the px), lines and marks at least 2x the page's stroke, end tags reduced to short badges (s90's badge key) and minor ticks dropped. (2) The card still carries its title and its one number. (3) A card that is THROWN to become the page (s71 throw-then-zoom) hands over to the full page, not the card render. (4) Absent the profile, every page and card is byte-identical; the body's chart cards take it (T33). (5) Frame: the Bravos pairing card at row 7's size before/after, read by the parent
- Regression: `python -m pytest content/video_engine/tests/test_chart_card_readable.py -q`
- Expected RED: the rendered card's smallest label measures under the phone floor at its displayed size and its line stroke equals the page's
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_chart_card_readable.py content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Frame acceptance: the parent reads the card before/after at its on-stage size; the operator reads it with P69-HG3
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: lane B b42d6dc + 11ed037, 2026-09-23 - the `card` profile: every word at the s90 phone floor at the card's displayed size (59.08 px; was 7.93), lines 10.67 px (page 5.34), a `.card.json` sidecar so a push lays the full page on the card. The parent's read found two indistinguishable "+21%" tags -> 11ed037 names a line when two tags would read the same ("s&p", "mega-cap") and the time axis always states its span (both ends, or one range label "Oct '25 - Jul '26" - the parent's fix). Review 4 MJ1: the names were drawn at 0.5 of the floor and the test read no tspans -> fixes4 (names at the floor or stop and report)

### T11: P69-HG3 - the s90 page card (option off/on); the default flips only on the ruling
- Status: pending
- Owner: parent
- Depends on: T10 merged; lane A at a slice boundary
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-s90-off/**`, `.../build-h-s90-on/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: (1) The H bed page and one bars page, built with the option off and on, frozen and served. (2) The three layout numbers and the type sizes written on the card. (3) The row names what the default flip changes (every 16:9 full-stage page) and what it blocks (only the flip). If the ruling approves the flip, it is a follow-up slice appended to this plan (lane B, engine lock, fixture, goldens re-pinned once with the sha table)
- Validate: `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T12: The chip's stamped landing, an option rendered both ways (lane B)
- Status: pending
- Owner: implementation_luna
- Depends on: T10 (lane B's engine sequence)
- Write set: `content/video_engine/scripts/species/chip.mjs` (`paintChipStamp` and the stamp branch of `chipPose` only; the `landscape-phone` branch untouched), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `chip` region, via `sync_kinetics.py --write` only), `content/video_engine/scripts/build_scene_timeline_f.py` (`_validate_chip` `:1573`, the chip ring fit), `content/video_engine/tests/kinetics/chip.test.mjs`, `content/video_engine/tests/test_chip_stamp.py`, `content/video_engine/tests/golden/build_golden_sources.py`, `content/video_engine/tests/test_golden_frames.py` (two names added), `content/video_engine/tests/golden/sources/chip-stamp-*`, `content/video_engine/tests/golden/frames/chip-stamp-*`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: (1) `arrive: "stamp"` is legal only on a `form: "stamp"` chip. (2) With it, the pose is `stampXf`'s (area-space scale from 2.1, the free rotation resting off-square, the ink and fade, the ring on its split curves, the owed exit within `dur`). (3) Without it, `chipPose` is byte-identical to `springPop`. (4) The ring peak is fitted by `stamp_fit` against `ring_obstacles` and written on the species, or refused by name. (5) Two new goldens, `chip-stamp-pop` and `chip-stamp-arrival`, from one source differing only in `arrive`. (6) The other goldens are byte-identical; the fixture is re-measured
- Regression: `node --test content/video_engine/tests/kinetics/chip.test.mjs`
- Expected RED: `chipPose` is identical with and without `arrive: "stamp"`, and `_validate_chip` ignores `arrive` (both probed red by the review)
- Validate: `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_chip_stamp.py content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Frame acceptance: the parent reads `chip-stamp-pop.png` beside `chip-stamp-arrival.png`
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T13: P69-HG1 - the chip landing and the contact instant, from the chip's own proof door
- Status: pending
- Owner: parent
- Depends on: T12 merged; lane A at a slice boundary, with no body slice in flight
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_chip_landing.py` (new: the proof door - it imports the H door's read-only constants and builds ONE beat of its own, row 7's "and it isn't Nvidia" on the studio desk, with `NVIDIA_CHIP` recast as a `form: "stamp"` chip on an icons-catalogue glyph, the only difference between the two builds being `arrive`), `.../build-h-chipstamp-pop/**`, `.../build-h-chipstamp-stamp/**`, `.../build-h-contact/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: (1) The two chip builds are frozen and served on their own ports (never :8731, never rebuilt while linked), with the four-instant strip. (2) The contact strip shows the `prop-stamp` scrub at +0.00 / +0.10 / +0.154 / +0.17 s with its bound cue. (3) The queue row `p69-hg1-chip-landing-and-contact` asks both questions. (4) If the ruling moves the contact, one follow-up edit per consumer (T2, T3, T4's constant) re-times everything; the body re-times on its next build
- Validate: `python content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_chip_landing.py` then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T14: The body's preflight - inventory, the departures named, the stamp slot's mass
- Status: done
- Owner: parent (with `explorer` for the inventory)
- Depends on: T0 (Decision 2 recorded), T2-T7 merged
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (docstring, constants, and the cue slot's mass via `A.arrival_mass`), `.../evidence/objects/ev-debt-issuance-v2.series.json` (only if authored), `.../build-h/BUILD-NOTES-H.md`
- Acceptance: (1) An inventory for rows 7-24 resolves every page object, card, plate (`find_asset`), prop, host still, cue file and outro part. (2) The `ev-debt-issuance-v2` page is authored from the dossier only at the tier its source earns: the dossier is secondary ("~$121B", MS ">$100B"), so the series is PLAUSIBLE unless a primary source is on disk. The 2026E range is drawn as a range, never a midpoint (E53, E77). Otherwise the row falls back to the PNG card, named as a departure. (3) `ev-three-manias` (a PNG only) is named as a card departure for row 12. (4) The door's constants cite what supersedes the treatment's wording: s84 (Ken Burns alone), s83, s91, E47, E50. (5) The stamp slot reads `landing N (stamp, ink)` unless the row names a mass. (6) `_assert_read_only` covers `REFERENCE-F.md` and `build-f/`. (7) The baseline for "the bed is unchanged" is taken after T7, by comparing `build-h/steel-and-paper-h.timeline.json` and `SHOT-TABLE-H.md` (not `player.html`, which embeds the engine)
- Validate: `python content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, then the timeline and table compared byte-for-byte against the post-T7 baseline
- Evidence: 2026-09-22 - the door carries `BODY_ASSETS` (rows 7-24, 0 missing paths), `BODY_DEPARTURES` (15, each with its fallback), `TREATMENT_SUPERSEDED` (E99 s84 `:3296`, s83 `:3294`, s91 `:3313`, E47 `:1419`/`:1444`, E50 `:1520`/`:1533`), `DEBT_PAGE` + `DEBT_SPREAD` + the "$130–150B"/"2026E" figure, `TWO_CLOCKS_PAGE`; the cue slot reads `A.arrival_mass` (`(stamp, ink)`); `READ_ONLY` covers `REFERENCE-F.md` and `build-f`; the stale `HOST_CARD_REFUSED` note fixed (R26-221 `plate_dock_place`). Bed unchanged: timeline sha `25203c15...` and table sha `a4e8d798...` identical before and after (private dir). PLAUSIBLE pages draw, each with its named fallback, pending the operator's end-of-run answer. The departures file is folded into `BUILD-NOTES-H.md` section 9

### T15: Row 7 (0:54-1:09) - host window 1: the studio, the Bravos card thrown, the NVIDIA chip crossed, the flow
- Status: done
- Owner: implementation_luna
- Depends on: T14
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `UNIT_CUT_PHRASE` moves past row 7; the host plate on Ken Burns alone; `NVIDIA_CHIP` stays the SVG chip (no form stamp - P69-HG1 decides future chips)
- Validate: the shared Validate
- Expected RED: the shared Expected RED (the table ends at row 2, `42.04-52.85`)
- Evidence: T15b (2026-09-23, the operator: "Those charts still seem tough to read to me" - E99 s71): row 7 REBUILT - the Bravos card is thrown on its name and the camera PUSHES it to the stage where the page takes its place (throw-then-push; the snap was refused for a forward-play offset, R26-260); the chart is read at full page size, the NVIDIA chip lands and is crossed on the page, the flow draws beside it; the studio opens earlier (the slate row is now 42.04-49.45, a bed change named for HG4) so M44 holds. SUPERSEDED earlier T15 read, 2026-09-22 - table row 3 `52.92-63.77` on `world-h1-studio-v1` (Ken Burns alone, s84): the Bravos card thrown on its name (55.62), put down on "and it isn't Nvidia" (58.26), 5.95 s (E50); the NVIDIA SVG chip lands on its word (58.60) and is crossed (59.80); the capital -> value flow draws on the left monitor (59.86, its dashed frame drawn on by the nib - flow.mjs `box`, s42.1). 1 dip at a world change (slate -> studio) naming the transforms it refused; life 3 of 3 rows; door exit 0, cues 5 of 5 bound; no frozen run > 0.5 s; gate `2 FAIL / 2 WARN / 21 PASS` - M11 (row 1, the bed, pre-existing) and M03 (the BED's 0:09-0:54 gap: nothing new ENTERS between the certificate and row 7 - named for P69-HG4; row 7 cannot clear it without a card before its own name). The dip cue moved to the row's entry (`r[0] - 0.35`). The parent read the tiles beside build-f's at the same sentences: row 7 carries a host, a thrown card, a crossed chip and a drawn flow where build-f holds a bare pen plate. Noted for HG4: the small caption strip over the desk (55.6-61.6) and the full caption crossing the host's collar at 63.4 (no caption-placement option on a picture plate)

### T16: Row 8 (1:04-1:09) - the dip back to the page (dip 1)
- Status: done
- Owner: implementation_luna
- Depends on: T15
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the dip names its refused transform ("a recast cannot take a photograph plate to a chart")
- Validate: the shared Validate
- Evidence: 2026-09-23 - rows 8-9 are one page (table row 5, 63.80-89.27): NO dip - row 7 now ends on a page, so the boundary is page to page and E47 refuses a dip; their chart melts to a ball and is thrown off on "But capital that fast" (`melt:throw:1`, E88) and the railway index draws on the same board; transforms refused by name (dip, recast, rescale, morph, melt:splash:chart, melt:morph). Life 66.40/68.40 s luma diff 2.99 (4.0%)

### T17: Row 9 (1:09-1:30) - the railway index and the GDP recast
- Status: done
- Owner: implementation_luna
- Depends on: T16
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `RAIL_DROP` "-64%" (the object's arithmetic); the page rings its own GDP data (no invented 7 %/8 % ticks)
- Validate: the shared Validate
- Evidence: 2026-09-23 - the railway climbs to the 1845 peak on "pounds", crashes on "crashed", `-64%` written red above the trough under the 1,000 line (E28); recast to the GDP share on "the internet", the title rewritten 0.1 s after (a same-word retitle is dropped by the compiler), the ring on the page's own Q2-2000 peak (unlabelled - the reference line writes 11.54%), the last twenty years drawn on "AI spending just crossed". The unsourced "GBP 250m raised / $1T+ today" note CUT (no source on disk; the door had mis-cited the dossier). Gate at the end of row 9: `2 FAIL / 2 WARN / 22 PASS` - M03 (the bed) and M11 (row 1), both named for HG4; frozen frames none over 0.5 s; seams 0 faults; cues 7 of 7; life 5 of 5. The parent's frame read: the plots use ~60% of the page width (the rest reserved for end tags) - restaged by the longform profile (T33); the recast's middle is unreadable (R26-261); the GDP page has no years (R26-262). FLAGGED for HG4: the page's end label 11.51% lands on the voice's "eight" (two different measures - a next-letter script note), the railway title says "fell 64%" ~14 s before the voice

### T18: Row 10 (1:30-1:44) - the sell ticket thrown over the recast
- Status: done
- Owner: implementation_luna
- Depends on: T17
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the ticket is `arrive: throw, mass: paper`; the page recasts under it (E64)
- Validate: the shared Validate
- Evidence: 2026-09-23 - the sell ticket thrown on "obvious move" over the GDP page, the page recasting under it to the divergence ("Chipmakers doubling. Customers flat."), lines drawn one at a time. REWORKED on the parent's frame read (the ticket read as a blank pad with a tiny badge): SELL is stamped across the ticket's centre in coral (~140 px read, ~95 px parked) - the largest thing on the card; the badge's probe FAILs gone. Named: the divergence fills only the bottom ~40% of its plot (R26-266); SELL cannot land as its own stamp on its word (R26-267); the recast's half-title flash (R26-261)

### T19: Row 11 (1:44-2:10) - one slot, three records (Karp, Uber, the COO line)
- Status: done
- Owner: implementation_luna
- Depends on: T18
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; each record takes the outgoing card's slot (s80); no world change
- Validate: the shared Validate
- Evidence: 2026-09-23 - on "like a claims adjuster" the divergence MELTS and splashes onto `world-internal-memo-v1` (lamp, desk, memo; refused by name: recede - no door, R26-265; the dip; the thread; recast/remake; park), so Karp, Uber and the COO share one slot on a clean ground (the parent's frame read: empty axes behind the records read as a broken chart). The desk's mug steam is the plate's life (the gate does not credit typing, R26-269). Uber's chart card read at 0.90 of the stage with three badges from its own card

### T20: Row 12 (2:10-2:30) - the trough already doing its job
- Status: done
- Owner: implementation_luna
- Depends on: T19
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `ev-three-manias` as T14 named it (a card record, not a page); the peak-to-trough move carried by the card's own marker or a callout, named in the build notes
- Validate: the shared Validate
- Evidence: 2026-09-23 - the COO card holds through "Remember that line", then the three-manias TABLE lands in the slot at ~0.76 of the stage, composed from its own pixel bands so cells read ~22 px (never a table read small, E99 s71), its four badges springing in turn (priced / fell 64% / twenty years / still open); leaves on "Which flips the question". The "capital committed" row cut (row 9 keeps its ~7-8% off screen). Named for HG4: the badge strip under the table is small; the caption on the bright desk is low-contrast (R26-268)

### T21: Row 13 (2:30-2:45) - reset 1, the dip to 1849 (dip 2)
- Status: done
- Owner: implementation_luna
- Depends on: T20
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `use=reset` with Ken Burns alone; the anaphora in caption STAGE mode
- Validate: the shared Validate
- Evidence: 2026-09-23 - dip 2 (a real world change, desk -> viaduct, E47; refused: thread, edge arrival, occluder, melt, recast) before "And in 1849"; Ken Burns alone plus the locomotive's steam; the anaphora in caption stage mode. Rows 10-13 gate: `2 FAIL / 2 WARN / 22 PASS` - both FAILs the bed's (M03, M11); frozen frames none over 0.5 s; seams 6 boundaries 0 faults; stage gaps 1.0 s (the two licensed dips); cues 13 of 13; life 7 of 7 rows. LANE A PAUSES HERE for the longform profile (rows 14-24 are chart-heavy and build on it)

### T22: Row 14 (2:45-3:20) - the yardstick: dip 3, camera 2, the breakthrough bars
- Status: done
- Owner: implementation_luna
- Depends on: T21
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; camera 2 on the 28 datum, tied to its landing (E51); the bars page states its scale
- Validate: the shared Validate
- Evidence: 2026-09-23 - table row 8 `162.60-196.25` on `ev-capital-formation-v1` under `;readability=longform` (middle): dip 3 at a real world change (viaduct -> page; refused by name: snap / throw-then-zoom / throw-then-push, object-becomes-chart, spiral, mount, melt, recast / rescale / morph); the tech line climbs to the dot-com peak on "peak", the object's own "23%" written there, lands on "twenty-eight" with its end tag; camera 2 pushes 1.06 on that landing (E51) aimed at the 28's rest; the line undraws and the page recasts to `ev-rail-vs-yardstick-bars-v1` (s93 draws), the railways' bar bursting to 50 on a 0-60 rewrite. Gate `2 FAIL / 2 WARN / 23 PASS` (the bed's M03, row 1's M11); cues 15 of 15; life 8 of 8; no frozen run; seams 7, 0 faults. The parent's frame read: the line page's panel takes ~half the page (the long end tag reserves the right margin) - the T10 key rail (lane B `0df626a`) shortens the tags and frees it once merged; the recast's middle garbled (R26-261); the camera's datum drifts on a moved frame (engine, the agent's report); "50" without its "¢" on the burst (engine)

### T23: Row 15 (3:20-4:06) - the trigger and the concession; PROP 1 the Fed, and P69-HG2
- Status: done (row 15 on `ev-tnx-two-eras-v4`; PROP 1 the Fed STAMPED - BUILD-NOTES-H 14b; the 1.2x chrome-fit push - 17b, lane A 020a68f); HG2/HG4 open
- Owner: implementation_luna (the row); parent (the HG2 card)
- Depends on: T22
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`, `.../build-h-frozen-prop1/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: the shared body rules; prop 1 `prop-federal-reserve-building-v1` as `prop: True, arrive: "stamp"` on "The Fed at six and a half" - the compiler's `stamp:` line, its cue (`landing N (stamp, ink)` or the named mass), its gate event, its exit with the page (R26-219); the concession on the same page (no bare plate 2:45-6:04); the parent freezes the row and writes P69-HG2 with enter/contact/rest frames
- Validate: the shared Validate, then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: BLOCKED 2026-09-23 - `ev-tnx-two-eras-v3` keeps its data as two PANELS and a ledger page draws no panels (0 series; only the card chart does), and the Fed stamp is refused on it ("46 px on its long side, under the 120 px mark floor"). Unblock in flight: `ev-tnx-two-eras-v4` authored as ordinary series (the parent's call - keeps the page and the stamp); the draft is staged at `scratchpad/p69t23/door-t23-draft.py`. The Fed 6.5% / Bravos 5.5% as RULES on the yield page are E53 s5's form, not a unit mix UPDATE 2026-09-23 - the row BUILT on v4 (195.82-242.85, 16/16 cues bound, seams 8/0 faults, frozen-frame clean, spoken visuals 0 uncovered; motion gate 3 FAIL: M03 47 s wait while the Fed is withheld, M11 row 1's, M31 a 0.2 s probe blind spot at the melt's first frames) with `FED_STAMPED = False`. The parent's frame read found the title claiming a Bank of England 6% the page never draws -> retitled on "Fed" to "The Fed at 6.5% in 2000: the internet trade rolled over" (the page's own rule); the BoE stays spoken. PROP 1 is withheld by three blockers the row cannot fix: (1) the compiler flattens a prop cutout to JPEG (`dock_uri` -> `data_uri` `convert("RGB")`), so the Fed paints as a BLACK SQUARE - a card by another name; (2) the end tags are reserved as one solid column (`ledger_page._landscape_full_boxes`), so the empty right margin is unreachable; (3) v4 is not in `page-boxes.v1.json`. (1)+(2) are T6d (lane B); (3) is `measure_page_boxes.py --write --project build-h` after lane B merges; then `FED_STAMPED = True`, the re-run, and HG2's card

### T24: Row 16 (4:06-5:25) - who is paying; PROP 2 beside the leases record
- Status: done (lane A ac38175)
- Owner: implementation_luna
- Depends on: T23, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the debt issuance beat as T14 settled it; `ev-ig-credit-weighting-v1` and `ev-capex-consensus-v1` recasts (E58); prop 2 `prop-hyperscale-datacenter-v1` stamped first with the `ev-doc-leases` record placed around it (T5), 0 px overlap, the parent's frame read
- Validate: the shared Validate
- Evidence: lane A ac38175, 2026-09-23 - row 16 (242.38-321.12): the debt line (T14's beat, 2026E a spread), E58's two recasts (IG index, capex consensus) as plain hand-overs, then the melt splashes onto the records' desk: `dock-h-leases-record` and PROP 2 stamped in the desk's room, 0 px overlap, contact 309.00, `landing 11 (stamp, ink)`. The stamp left the page because the three-state page refused it (70 px < 120 px floor) and the fit reads the FIRST state (R26-279). Gates: 19/19 cues; seams 10/0; M03 named (62 s - the gate never counts a recast, R26-280); M21 WARN capex 14.8 s. Owed: R26-282 (units, the capex sub)

### T25: Row 17 (5:25-6:04) - the arithmetic: the 94 bar with its figure
- Status: done (row 17, the 94 bar - BUILD-NOTES-H 16/16a); HG4 open
- Owner: implementation_luna
- Depends on: T24
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the 94 figure paints on the bars page (T6); the PIMCO record in the slot
- Validate: the shared Validate
- Evidence: pending

### T26a: A bar changes its own value - the halving compare moves the bar, not only its number (R26-273; blocks T26)
- Status: done (lane B af869b7; on main 19144bb)
- Owner: implementation_luna (LANE B, after fixes4)
- Depends on: T6, fixes4; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `chart_to compare` bar branch), `content/video_engine/scripts/build_scene_timeline_f.py` (only if the compiler must carry the comparator value), `content/video_engine/tests/test_bar_value_morph.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: E28 - the geometry says what the number says. Today `chart_to compare` melts a bar's figure into the comparator ("20%" -> "10%") while the bar stays at 20% (the T10b halving frame: "10%" printed over a 20% bar). (1) On a compare to a value, the bar's height morphs to the comparator's value on the compare's own clock, its value label riding its top, the soft foot/hatch (T10b) and the extruded form following; (2) a compare with no value change is byte-identical; (3) the old value may stay as a ghost outline at its old height only if the row names it (`ghost=yes`), never by default; (4) one golden: the halving at rest after the morph. T26 builds on it
- Regression: `python -m pytest content/video_engine/tests/test_bar_value_morph.py -q`
- Expected RED: after the compare, the bar's rect height still maps to 20% while its label reads "10%"
- Validate: `node --check` the engine, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_golden_frames.py`, `test_bar_style.py`
- Frame acceptance: the parent reads the halving before / mid / after on the 1v1 halving page, soft and off
- Evidence: lane B af869b7, 2026-09-23 - `lpBarMorphs`: the bar's height morphs to the comparator on the compare's clock, its value riding its top, the soft foot/hatch and the extruded form following; a no-value-change compare byte-identical (11/11 renders); golden `bar-value-morph` (pinned in test_bar_value_morph). The parent read the halving after: the bar at 10%, "10%" on its top, "20%" dimmed beside it. Open for T26: a ring/camera aimed at the bar's datum after the morph still reads the old top; a comparator across zero is unmoved

### T26b: A camera push on a full-stage page keeps the title and the axes in frame (found on T23/T6d's Fed frame; blocks T23's re-stamp and T26's camera 3)
- Status: done (lane B af869b7; on main 19144bb)
- Owner: implementation_luna (LANE B, with T26a)
- Depends on: T6d, fixes4; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the camera's reach on a ledger page), `content/video_engine/scripts/build_scene_timeline_f.py` (the camera key's reach check), `content/video_engine/tests/test_camera_keeps_the_page.py` (new)
- Acceptance: with the Fed stamped on the two-eras page the camera's pull on the landing (218.66) took the title's left edge, the y ticks and the source line off the frame (`scratchpad/p69t6d/frames/t6d-fed-on-v4-held.png`). (1) A camera key on a full-stage ledger page is refused by name (or clamped, the row's choice written) when its framing would cut the page's title, y-tick column, source line or a measured end tag (`tag_boxes`), read from the page's measured boxes; (2) row 1's zoom 1.06 at (624, 541) - which the drawn "+613%" tag makes reachable only to 1.034 - is reported by the check (lane A re-aims it in T33); (3) every existing camera key that clears keeps its frames byte-identical
- Regression: `python -m pytest content/video_engine/tests/test_camera_keeps_the_page.py -q`
- Expected RED: the compiler accepts the stamp-landing pull that crops the title
- Validate: as T26a, plus `test_the_stamp_arrival.py`
- Evidence: lane B af869b7, 2026-09-23 - `camera_reach`: a full-stage page's camera key is refused by name when its framing (the page's breath included) cuts the title, y ticks, source or a measured tag; `"reach": "clamp"` writes `landing_zoom` (the Fed: 1.03; title and sub >= 12 px from the edge, y ticks >= 69 px - the parent read before vs clamped). Row 1's zoom 1.06 is REPORTED (WARN, reachable 1.02) for T33. Parent in place: 933 passed

### T26c: The pacing gate counts a recast as an arrival (E99 s105; closes R26-280)
- Status: done (lane B afd8b3d)
- Owner: implementation_luna (LANE B)
- Depends on: T26b (on main 88574ca); lane B
- Write set: `content/video_engine/scripts/gate_motion_density.py` (M03's arrival list), `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: the operator, 2026-09-23: "yes, recast counts." (1) M03's longest-wait clock resets on a `chart_to` recast that changes the chart on screen (its landing instant, from the timeline's own `chart_to` time + its clock), as it does on a page or dock arrival; (2) a retitle alone, a relight or an idle does not reset it; (3) every build whose timeline carries no recast gets a byte-identical gate report; (4) H's row 16 (242.38-303.54, two recasts) no longer reads a 62 s wait NOTE 2026-09-23 (coverage audit): s105 names "M03 (and its player mirror)" - M03 is computed only in the gate; the player draws no M03, so no second write is owed
- Regression: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Expected RED: a timeline with a page, then two recasts 20 s apart, then nothing for 40 s reports M03's wait from the page's landing
- Validate: the regression, then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` unpiped (read-only on the build)
- Evidence: pending

### T26c2: M03 counts a rescale, extend or morph that moves the story (E99 s105 amended)
- Status: done (lane B 5bd16ee)
- Owner: junior_developer (LANE B)
- Depends on: T26c (lane B afd8b3d)
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: the operator: "true motion doesnt just move the visual it moves the story/narrative/thought process along". (1) A `chart_to` rescale / extend / morph counts as an M03 arrival when BOTH (a) it is anchored to a spoken word (the timeline's own word/cue anchor for the event - find how the compiler records it) and (b) it brings a new thing on screen within its landing window: an extend's new data past the old domain, or a label/badge/callout/figure/ring species landing on the same word or within the transform's duration; (2) a silent re-fit (no word anchor, or nothing new named) does not count; (3) recast behaviour (T26c) unchanged; a timeline with none of these byte-identical; (4) report H's M03 before/after and which transforms counted, each with its word
- Regression: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Expected RED: a rescale on a word landing with a badge does not reset M03
- Evidence: pending

### T26d: A prop goes where the author puts it, and moves after it lands; the fit is a default and advises (E99 s106; closes R26-279)
- Status: done (lane B 5c6871c)
- Owner: implementation_luna (LANE B)
- Depends on: T26c; lane B
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`stamp_dock_place`, the dock placement, the prop's timeline keys), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the dock painter's prop transform over time), `content/video_engine/scripts/authoring/docks.py`, `content/video_engine/tests/test_prop_free_placement.py` (new), `content/video_engine/tests/test_the_stamp_arrival.py`, goldens only if a new one is added
- Acceptance: the operator, 2026-09-23 (s106): "we should be able to manipulate props freely". (1) A prop dock (`prop: True`, any arrival incl. `arrive: stamp`) takes an AUTHORED place - `{"place": {"x", "y", "w"}}` in stage fractions (centre and width; height from the cutout's alpha aspect) and `"rot"` degrees - and the compiler honours it exactly; the stamp's ring and 2.1x approach are drawn around THAT place; (2) a prop takes MOVES after it lands - a list of `{"at": <word or s>, "x", "y", "w", "rot", "dur", "ease"}` keys, painted by the engine on the prop's own clock (a seek lands the same frame as forward play; the T6b hatch rides the prop's transform - closes R26-271's case); (3) with no authored place the compiler's fit is the default, and it reads the boxes of the chart state ON SCREEN at the landing instant (a `then=`/`chart_to` page's state), never the row's first state (R26-279); (4) the fit's and the authored place's findings - over a series or its data mask, over a label, a mark under the floor, cut by the frame, over a caption - are WARNs printed in the door's report with the numbers, never refusals; a place that is off the stage entirely stays a refusal (it cannot be seen); (5) every existing stamp and dock with no authored place compiles byte-identical (the H door, the goldens)
- Regression: `python -m pytest content/video_engine/tests/test_prop_free_placement.py -q`
- Expected RED: an authored `place` on a stamped prop is refused ("read/park refused") or ignored; a stamp landing after a recast is fitted to the first state's boxes; an overlap with data refuses
- Validate: `node --check` the engine, `node --test` kinetics, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_the_stamp_arrival.py`, `test_prop_shadow.py`, `test_prop_alpha.py`, `test_golden_frames.py`, `test_camera_keeps_the_page.py`
- Frame acceptance: the data centre stamped on row 16's capex state at an authored place in the right margin, then moved on a word; the parent reads the strip
- Evidence: pending

### T26e: Props, pages and charts morph into each other, both ways, mid-page (E99 s107)
- Status: done (lane B, P69 T26e; review fixes: the mark held with its tag, the collapse over the next world, M14/M03/M17/M36)
- Owner: implementation_luna (LANE B, after T26d)
- Depends on: T26d (a prop that stands after a morph is placed and moved by s106's grammar); lane B
- Write set: `content/video_engine/scripts/kinetics/arap.mjs` (+ sync), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the morph enter, a morph exit, a mid-page morph verb, the textured mesh), `content/video_engine/scripts/build_scene_timeline_f.py` (the grammar and its checks), `content/video_engine/tests/test_prop_morph.py` (new), `content/video_engine/tests/golden/**` (one golden each way)
- Acceptance: the operator, 2026-09-23 (s107): "we should also be able to morph/transform to/from props to pages and charts." Find and REUSE first (`docs_find "morph"`: CAPABILITIES :109 Method A, :122 morph_to, :123 remake, :125 the object becomes the chart, `MORPH_SHAPES`, `morphInvariants`, the strip mesh). (1) PROP -> PAGE/CHART: `;morph=prop:<id>` on a page enter, and a mid-page `chart_to {to: "morph", from: "prop:<id>"}` on a word - the prop's alpha silhouette (traced from the cutout, simplified, x-monotone strip when the target is an area; the page panel when the target is the page) morphs by ARAP into the target, the prop's pixels texture-mapped on the mesh and handing to the chart's own ink by the landing; (2) PAGE/CHART -> PROP: an `exit: morph:prop:<id>` and a mid-page `chart_to {to: "prop", prop: <id>, place?}` - the page panel or a named mark (a bar, the area under a series) morphs into the prop's silhouette, which then STANDS as a prop dock (T26d's `place` / moves; its T6b hatch); (3) seek-safe (cold seek = forward play), the mesh never inverts (det J > 0 at every t, the existing test pattern), the match-cut invariants printed as a WARN with numbers when they fail, never a refusal (s106); (4) everything that names none of this compiles byte-identical; (5) two goldens (prop->bar, page->prop) read by the parent before pinning (6) ADDED 2026-09-23 from the main-branch survey: `arap.mjs:67` `fanMesh` assumes a star-shaped outline; a traced prop silhouette may not be - triangulate the silhouette (constrained, e.g. ear-clipping or Delaunay on the simplified contour) or refuse the fan by name and fall back to the strip; design reference only: `docs/research/runs/2d-3d-rigging-webgl-optimizations-2026-09/findings_advanced_mathematical_foundations.md` section 1.3 (ARAP local/global) and 2.4 (bounded biharmonic weights) - research, not evidence
- Regression: `python -m pytest content/video_engine/tests/test_prop_morph.py -q`
- Expected RED: `;morph=prop:prop-hyperscale-datacenter-v1` is refused as an unknown morph shape; `chart_to {to: "prop"}` is an unknown verb
- Validate: `node --check` the engine, `node --test` kinetics (incl. the arap tests), `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_golden_frames.py`, `test_prop_free_placement.py`, `test_the_stamp_arrival.py`
- Frame acceptance: the data centre becoming the $690 capex bar, and the capex page collapsing back into the data centre, before / mid / after; the parent reads both
- Evidence: pending

### T26f: The page's chrome is objects - the title rescales and moves, and rides the camera (E99 s108)
- Status: done (lane B 1100c0b)
- Owner: implementation_luna (LANE B)
- Depends on: T26b (the reach check), T26d (the object move grammar - reuse it); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the page's chrome layer, the camera transform), `content/video_engine/scripts/build_scene_timeline_f.py` (the chrome keys and T26b's reach), `content/video_engine/scripts/gate_motion_density.py` (the camera mirror, only if the chrome's frame changes what it reads), `content/video_engine/scripts/ledger_page.py` (the chrome boxes the reach reads), `content/video_engine/tests/test_page_chrome_moves.py` (new), `content/video_engine/tests/test_camera_keeps_the_page.py`
- Acceptance: the operator, 2026-09-23 (s108): "Why can't the title re-scale? ... we should have free dynamic movement between camera and objects." Find and REUSE first (docs_find "retitle", "camera", "rescale", the page's title/sub/source painters, T26d's move keys). (1) Each chrome element (title, sub, source, y ticks, axis names, the key rail) is its own object with a transform: a row may move/rescale it on a word with T26d's key grammar (`{"chrome": {"title": [{"at", "x", "y", "scale", "dur", "ease"}]}}` or the nearest existing grammar) - e.g. the title shrinks to a top-left tag; (2) a camera key may name `chrome: "screen"` (the chrome rides the camera - drawn in screen space at its own size) or `chrome: "fit"` (the chrome counter-scales/re-lays into the pushed frame) - either way nothing the viewer must read leaves the frame; (3) with either, T26b's reach limits the push only by the claim's data (the datum/series/mark the sentence points at stays in frame), chrome findings WARN; a real 1.2x push on the two-eras page and on row 18's index page is reachable; (4) seek-safe; the gate's camera mirror agrees; (5) every existing page and camera key byte-identical until a row names it
- Regression: `python -m pytest content/video_engine/tests/test_page_chrome_moves.py -q`
- Expected RED: a 1.2x push on the two-eras page is refused by T26b ("the y tick column's left edge leaves the stage"); `chrome` keys are unknown
- Validate: `node --check`, `node --test` kinetics, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_camera_keeps_the_page.py`, `test_camera*.py`, `test_golden_frames.py`, `test_gate_motion_density.py`
- Frame acceptance: the two-eras page pushed 1.2x onto the dot-com peak with the title riding the camera, and with the title shrunk to a corner tag; before / mid / after; the parent reads both
- Evidence: pending

### T26: Row 18 (6:04-7:13) - the turn: reset 2, PROP 3, camera 3, the halving compare
- Status: done (row 18 - BUILD-NOTES-H 17; refreshed 17b, lane A 020a68f: the desk card profile, the certificate 0.30 + whole-card ring, camera 3 chrome fit); follow-ups R26-290, R26-291; HG4 open
- Owner: implementation_luna
- Depends on: T25, T26a, T26b, the lane-B merge (the prop's alpha), P69-HG2 (read at the end)
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; dips 4 and 5 at world changes; prop 3 `prop-tech-sp500-concentration-v1` with camera 3 on the 20 datum tied to the stamp's contact (E51); the `chart_to compare` halving on the bars page, built on R26-190 (T6); the certificate ring on its figure (E56)
- Validate: the shared Validate
- Evidence: pending

### T27: Row 19 (7:13-7:52) - skips a gear: the breakthrough bars 20 years vs 5
- Status: done (row 19 - BUILD-NOTES-H 18: the railway index melts on "Railway steel", the 20 lands on "twenty", a GPU stamped on "compute" becomes the 5 bar (T26e), the SOLD OUT chip, the retitle, one callout per bar; the object cites E99 s95; + R26-290/291 on row 18); gate 2 FAIL (M11, M31 pre-existing) / 5 WARN (M25 new: PROP 3 in the safe bands at the 1.2x push); HG4 open
- Owner: implementation_luna
- Depends on: T26
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the `sold out` pill; two callouts, one per bar ADDED 2026-09-23 (coverage audit, s95): a page drawing the fives (a fab's five-year build; a compute generation's ~five-year life) cites E99 s95 as its source
- Validate: the shared Validate
- Evidence: pending

### T28: Row 20 (7:52-9:04) - host window 2: the desk, the checklist, dip 6, the returning page
- Status: built (row 20 - BUILD-NOTES-H 19: the clocks page sucked into the host's three fingers, the questions as the numbered agenda on One/Two/Three, the phone stamped, four chips on their words, the test card filling row by row on "Steel answers", dip 6, the divergence page back by the spiral and retitled); gate unchanged 2 FAIL / 5 WARN. OPEN: the test card reads below the phone floor - T28b; HG4 open
- Owner: implementation_luna
- Depends on: T27
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the checklist lands row by row; the divergence page returns unwound from its point (E40 s4), never redrawn
- Validate: the shared Validate
- Evidence: pending

### T28b: The checklist card reads on a phone - a type profile for the checklist species (row 20's test card)
- Status: pending (lane B)
- Owner: implementation_luna
- Depends on: T28; lane B
- Write set: `content/video_engine/scripts/species/checklist.mjs` (a spec-level `profile: "phone"` or type/pitch option: CHECKLIST.HEAD_DY / ROW0_DY / ROW_PITCH / BAND_RISE / BAND_H scale with the type), `docs/content-video-engine/samples/scene-evidence-player.template.html` (`.chartbox .cs` / `.csr` / `.ct` sizes under the profile), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the chart dock canvas, only if the profile needs it), `content/video_engine/scripts/build_scene_timeline_f.py` (the option's validation), a test, one golden; the species card
- Acceptance: row 20's test card at the right ~60% of the stage (the host visible at left) with its row text at or above the long-form phone floor (`ledger_page.CARD_PHONE_FLOOR` 12 px at a 390 px phone = 59.1 stage px); rows fill the card (no empty lower half); the default checklist and the `test-card` golden byte-identical; then lane A rebuilds the card from a derived object with short cells (Ask / Steel / Paper)
- Regression: a new checklist-profile test
- Evidence: pending

### T29: Row 21 (9:04-10:18) - SK hynix: camera 4, PROPS 4 and 5, the wafer compare
- Status: pending
- Owner: implementation_luna
- Depends on: T28, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; camera 4 on the hynix tip; props 4 (`prop-hbm-stacked-die-v1`) and 5 (`prop-silicon-wafer-semiconductor-v1`) stamped on their words; the 1 vs 3 `chart_to compare` on R26-190 (T6); the checklist ticks ADDED 2026-09-23 (coverage audit, s104 amended x2): the row carries FOUR charts (the hynix line, the wafer compare, the DRAM line, the hynix line returning) - build it on T8b's panels + composable focus (quad / grow / recede / bring back on their words), never a cut or a fifth state; a panel grows to the page on the sentence it serves
- Validate: the shared Validate
- Evidence: pending

### T30: Row 22 (10:18-11:33) - the tripwires: PROP 6, the customs monitor, the trim proof
- Status: pending
- Owner: implementation_luna
- Depends on: T29, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; prop 6 `prop-dram-memory-module-v1` on "the RAM inside every one of these data centers"; the monitor cites its release in the strip (E52); the June datum ringed ADDED 2026-09-23 (coverage audit, s94): read the monitor on the SCRIPT'S basis - DRAM +16.4% on the July print (the bounce off June's -3.7%), HBM-class +13.9% over the last two prints; every drawn figure NAMES its basis on the page ("July print", "last two prints")
- Validate: the shared Validate
- Evidence: pending

### T31: Row 23 (11:33-13:00) - the ring: reset 3, host window 3, dips 7-9
- Status: pending
- Owner: implementation_luna
- Depends on: T30
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the certificate thrown onto the reset and ringed; the memory-arithmetic bars and the weight check; the newsroom with the weight-check card thrown onto its desk ADDED 2026-09-23 (coverage audit, s95): as T27 - any drawn five cites E99 s95
- Validate: the shared Validate
- Evidence: pending

### T32: Row 24 (13:00-13:43) - the close and the outro (dip 10)
- Status: pending
- Owner: implementation_luna
- Depends on: T31
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the divergence page one last time; the agenda returns in its slot; the outro dissolves in as "desk" ends with the recorded brand line 0.7 s under the card (`CAPABILITIES.md:64`, `channel-assets/money-physics/outro/`) and `recipe:outro-clip-life`; runtime over 8:00 (E74)
- Validate: the shared Validate
- Evidence: pending

### T33: The body adopts the s90 page
- Status: pending
- Owner: implementation_luna
- Depends on: T32; T10 merged into main and main merged into lane A at a boundary
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: every page row opts in per row (`;readability=landscape-phone`) on the builders T8 made legal, and each row whose builder is still refused is named in the build notes with its builder (never silently skipped); the whole body rebuilt; M28 and the stamp fits re-run against the new boxes (a stamp that no longer fits is refused by name and re-placed); the parent reads each page row's tile before and after
- Validate: the shared Validate, then `python content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/steel-and-paper --build build-h --long`
- Expected RED: before, `SHOT-TABLE-H.md` carries no `readability=` on any row, and the pages measure main's roughly 6.5 px type
- Evidence: pending

### T34: The whole body gated, frozen and critiqued once; P69-HG4
- Status: pending
- Owner: parent (`reviewer` reads the diff and the cut against the treatment, mechanism by mechanism, M45)
- Depends on: T33
- Write set: `.../steel-and-paper/BEAT-PLAN-H.jsonl`, `.../CRITIC-REPORT-H.md`, `.../build-h-frozen-<next>/**`, `.../build-h/reference/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`, the Evidence lines of this plan and P68 T6
- Acceptance: (1) The cues are bound, then the report stamped (R26-198). (2) `gate_motion_density` reports 0 FAIL or names each FAIL with its ruling; each of build-f's eight (M01, M03, M05, M07, M08, M10, M11, M12) is closed or named. (3) `gate_one_shot_floor --reference build-f` runs, with the shorts-reference caveat quoted. (4) `lint_species_choice --long` is clean. (5) `measure_frozen_frames` finds no freeze over 0.5 s. (6) `recall_verify` passes the nine stages. (7) `run_script_gates --long --timeline` runs, with G20 under E99 s89 (a FAIL is a next-letter finding, never a script edit). (8) The reference mp4's sha256 is verified before any frame is read. (9) A frozen copy is served on its own port. (10) The critic runs once. (11) The P69-HG4 row is written
- Validate: `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` and `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h --project content/video_engine/projects/systems-and-blowups/steel-and-paper --reference content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f` - both unpiped
- Evidence: pending

### T35: New candidate effects and recipes from P69's mechanisms, each proved as a beat (the operator, 2026-09-22)
- Status: in_progress
- Owner: implementation_luna (authoring + proofs); parent (the frame read)
- Depends on: T6 and T6b merged into lane A (the recipes use the bar figure, the compare on bars and the prop's resting shadow)
- Write set: `content/video_engine/effects/recipes/*.json` (NEW candidates only; no existing recipe edited), `content/video_engine/effects/cards/*.json` (only a new card a new recipe needs), the catalogue's generated files via `build_effects_catalog.py --write`, a private proof dir `content/video_engine/projects/_proofs/p69-recipes/**` (gitignored build output; the proof door `proof_p69_recipes.py` commits), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: the operator, 2026-09-22: "draw plausible pages and also some new potential effects/recipes" (E99 s?? (b)). Each candidate is a TIMING THAT COMPOSES from existing cards (s70), `status: candidate`, `count: 0`, with doctrine cites, and each is PROVED AS A BEAT a short or the body could carry (E99 s60 - never a golden fixture served as a scene), frames read by the parent before it reaches the queue. The proposed set: (1) `recipe:estimate-opens-as-a-wedge` - a line lands, then its projection opens as a `spread` wedge between the range's two edges with the range written as a figure (the debt page; never a midpoint); (2) `recipe:the-bar-halves-its-number` - a figure lands on its bar's top and a `chart_to compare` melts and splashes it to the comparator (row 18's 20 -> 10); (3) `recipe:the-ratio-read-in-the-gap` - two bars, the figure written in the gap between them as the ratio (row 21's 1 vs 3); (4) `recipe:the-stamp-takes-the-room-then-the-card` - a prop stamped into the page's biggest room, a card then placed clear of mark and ring (T5); (5) `recipe:the-prop-lands-with-weight` - the stamp's contact shadow hands over to the resting shadow, the ink cue on the contact and the camera's pull from it (T2-T4, T6b); (6) `recipe:two-clocks` - a breakthrough pair of bars on one unit, the long one deemphasized and the short one crimson, its figure the claim (row 19). Every recipe passes `effects_catalog_check`; the queue row `p69-candidate-recipes` carries one clip or strip per recipe
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the six recipe ids exists in `content/video_engine/effects/recipes/`
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py -q` then the proof door, then `python content/video_engine/scripts/build_review_queue.py`
- Frame acceptance: the parent reads each proof's strip beside the mechanism it composes; a recipe whose proof reads wrong is withdrawn, never queued
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: 2026-09-23 lane A - THREE candidates kept after the parent's strip read: `recipe:estimate-opens-as-a-wedge` (the debt line lands, the $130B/$150B edges open from 2025, the spread wedge bleeds between them, "$130-150B / 2026E" written - never a midpoint), `recipe:the-stamp-takes-the-room-then-the-card` (the data-centre prop stamped into the biggest room with its ring, the leases record then placed clear of mark and ring - an authored box, the E65 placer found no room for the wide record), `recipe:two-clocks` (one unit, 20 years deemphasized, 5 years crimson, its figure the claim). TWO WITHDRAWN: `the-bar-halves-its-number` (the bar never halves - R26-273) and `the-ratio-read-in-the-gap` (a bracket draws nothing on bars - R26-272). Each recipe carries a `use_when` (act, moment, data shape, use / don't) - the schema and the catalogue builder gained the field. Proof door `_proofs/p69-recipes/proof_p69_recipes.py` (builds to gitignored `build-lab-*`). Catalogue: 49 recipes, in sync; drift tests 50 passed / 3 xfailed; the check's 6 FAILs are R26-239, unchanged. Defects seen: the issuance tag crosses the wedge's start, the page narrow (T8), "20years" and clipped ticks (R26-274), the prop art's black corners. PENDING: `the-prop-lands-with-weight` after lane B merges T6b

### T35b: The Bravos candidates - SUPERSEDED by T36-T44 (2026-09-23, the harvest v2)
- Status: done
- Owner: implementation_luna (lane B for engine verbs; lane A for recipes and the beats)
- Depends on: T8-T10 (the `longform` profile the verbs are drawn in); the eight new watches (docs/research/runs/bravos-watch/, Gemini x4 + GPT x4) merged into the harvest first
- Write set: `content/video_engine/scripts/species/*.mjs` (new verbs only, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (their paint), `content/video_engine/scripts/build_scene_timeline_f.py` (their tokens' validation), `content/video_engine/effects/cards/*.json` + `content/video_engine/effects/recipes/*.json` (new only), their tests and goldens, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the harvest `docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST.md` (106 items; HAVE 55 / PARTIAL 25 / MISSING 26) names ten candidates; build the ones that need no ruling, each as a card + a recipe that composes existing cards (s70) + a golden + a body row that carries it: `level_join` (a dashed rule between two points, a ring at each end - rows 14/15/21), `axis_tag` (the named year as an accent pill on the x-axis - rows 9/15/22), `project` (the line continues dashed past its last real point - rows 16/17/23, labelled as a projection, E77), chip `lit` / `tick` states (rows 10/22), `chapter_tag` (a section pill held over an act's charts - rows 13/18/23), `the-hidden-base` (bars hanging below a waterline - row 16's leases; E53-safe), `loop` (a flow laid as a ring with money moving on its arrows - rows 16-18), `term-over-the-parked-chart` (rows 16/18). CLEARED 2026-09-23: `lit_stretch` as a TRAVELLING or blinking light, and the freeze-on-light beat (E99 s99); `blur-under-the-dock` for a busy chart plate, as a row option (E99 s98). APPROVED as E99 s101: a MEMBERSHIP-STACK exception to E53 s2 (the bar is ONE value; its tiles are equal, unvalued identities - who is in it - and the total is written; never a stack of values), ). CLEARED by E99 s100 (area is valid when it serves the story, truthful when drawn in true proportion with its figures written): the PYRAMID / ICEBERG form - Bravos's surface-vs-hidden debt pyramid, every cell's value written, cell areas proportional - joins the build list beside `the-hidden-base`. SUPERSEDED 2026-09-23 by E99 s102 (second/inverted axis) and s109 (schematics with no data; rings on every vertex when the sentence is about them; donuts/pies incl. 3D exploded) - the text that follows was the state before those rulings: STILL HELD: an INVERTED axis (E28 - a rise would draw as a fall; a second axis alone is allowed as E53 s4's overlay), rings on every point (E56), shape-only waves with no data (E52; never fabricated) ADDED 2026-09-23 (the operator: "Have you already noted in what context these actions/effects are most likely useful?" - only as one quoted instance each): before building, a SYNTHESIS pass over the harvest + the eight watches (whose template now asks for USE CONTEXT) writes, for every harvested item, its USE-WHEN - the sentence's act (SPECIES-BY-SENTENCE: names a thing / states a size / compares / shows change / reveals the hidden / turns / warns / concludes), the story moment (hook, setup, proof, turn, reveal, close), the data shape it needs, and when NOT to use it - into `docs/research/bravos-style/BRAVOS-USE-WHEN.md`; every new card and recipe carries that use-when in its own field, so an author finds the move by what the sentence is doing
- Regression: `python content/video_engine/scripts/effects_catalog_check.py` (each new id absent before)
- Expected RED: none of the candidate ids exists in `effects/cards` / `effects/recipes` / the species list
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, and each verb's own test
- Frame acceptance: the parent reads each verb in its body beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: superseded 2026-09-23 - its candidate list became slices T36-T44 on the harvest v2 (nine videos); the use-when synthesis it asked for is `docs/research/bravos-style/BRAVOS-USE-WHEN.md` (171 entries grouped by act)

**ADDED 2026-09-23 (the operator's goal: "after Lane a finishes, add relevant work to p69 and /prp-implement"):** T36-T45 replace T35b's candidate list with the harvest v2's top-ranked moves (nine Bravos videos, ranked by videos x usefulness). Verbs build in LANE B after the `longform` profile (T8-T10, T10b, T10c) so they are drawn in the new style; the recipes compose them in LANE A; the chart-heavy body rows (14-24) build after both and use them where the harvest names their row.


### T36: `lit_stretch` - a light that TRAVELS along a stretch of a line on its word (E99 s99)
- Status: pending
- Owner: implementation_luna
- Depends on: T10c; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 1 (8 of 9 videos). A relit stretch runs from `from` to `to` along the series on its word (a comet head optional), the rest of the line keeps its ink; it counts as motion because it travels (s99). Rows 9 (the crash), 14, 15, 21. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T37: `solo` - the on-word isolate for a line or a bar (dim the rest)
- Status: pending
- Owner: implementation_luna
- Depends on: T36; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 2 (8 of 9). On its word every other series or bar mutes to the E67 dim (0.45, or the spec's measured 0.3-0.38 under the longform profile) and the named one keeps its ink; `unsolo` restores. Rows 10, 16, 18, 22. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T38: `axis_tag` + drop guides - the named year becomes a pill on the x-axis
- Status: pending
- Owner: implementation_luna
- Depends on: T37; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 3 (7 of 9). On its word the year's tick springs into an accent pill and a dashed guide drops from the datum to it (E28: the axis states its rule). Rows 9, 14, 15, 22. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T39: `level_join` - a dashed rule drawn from one point to another, a ring at each end
- Status: pending
- Owner: implementation_luna
- Depends on: T38; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 4 (6 of 9). The rule draws A -> B on its word with a small ring at each end and the gap written as a figure; the label never sits on the rule (C14). Rows 14, 15, 21. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T40: `blur` under a dock over a busy chart plate (E99 s98) + the term-over-the-parked-chart recipe
- Status: pending
- Owner: implementation_luna
- Depends on: T39; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 6 (6 of 9). A dock option: the plate under a landing dock blurs (the backdrop blur `exit:blurzoom` already carries, held) while the dock reads, and clears on its leave; only over a busy CHART plate (s98), never a ledger page's plot (E63 unchanged - the harvest's open question stays with the operator). Rows 10, 11, 16, 18. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it AMENDED 2026-09-23 (coverage audit): s104 amended (composable focus: "the others blur and recede") puts blur on a ledger page's RECEDED panels - T8b owns that use; this slice's dock-over-a-plot use follows s98, and E63's "never over a ledger page's plot" gives way where the story needs the plot behind the dock (s109: forms are defaults), the read judged on the frame
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T41: `project` - a labelled dashed continuation past the last real point
- Status: pending
- Owner: implementation_luna
- Depends on: T40; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 7 (7 of 9). The line continues dashed past its last datum on its word, labelled as a projection ("consensus", "2026E"), never mistaken for data (E77); pairs with the debt page's spread wedge. Rows 16, 17, 22, 23. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T42: chip states `lit` / `tick` / `sell`
- Status: pending
- Owner: implementation_luna
- Depends on: T41; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 9 (7 of 9). The chip species gains a held halo (`lit` - an annotation, s91), a tick (the cross's sibling) and a SELL stamp-state; a blinking halo counts as motion (s99). Rows 10, 20-21, 22. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T43: `loop` - a flow laid as a ring, money moving on its arrows
- Status: pending
- Owner: implementation_luna
- Depends on: T42; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Rank 11 (6 of 9). The flow species gains a ring layout and arc-length tokens moving on its edges. Rows 7, 16, 17. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


### T43b: A second axis, and an inverted one, for a co-movement claim (E99 s102)
- Status: pending
- Owner: implementation_luna
- Depends on: T43; lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (a `y2` / `invert` key on a dense-line object), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the RHS axis, its coloured ticks, the "inverted" label), `content/video_engine/scripts/build_scene_timeline_f.py` (validation), `content/video_engine/tests/test_dual_axis.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: E99 s102. A dense-line object may put a series on a right-hand axis (`y2`) with its own unit and range, optionally `invert`ed. (1) The page's claim is co-movement / lead-lag (a `claim: "comove"` key the validator requires). (2) Each axis names its unit; an inverted axis writes "inverted" beside its unit. (3) Each axis's tick labels take their series' colour (Bravos F15). (4) The longform profile's key and badges carry both. (5) A single-axis page is byte-identical; a y2 without `claim: comove` is refused by name (E28 stands elsewhere). (6) One golden: a co-movement pair with the RHS inverted; the parent reads it beside the Bravos frame (harvest T14, e.g. HIS 00:00)
- Regression: `python -m pytest content/video_engine/tests/test_dual_axis.py -q`
- Expected RED: `y2` is an unknown key and the validator refuses the object
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_dual_axis.py content/video_engine/tests/test_longform_profile.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py -q`
- Frame acceptance: the parent reads the golden beside the Bravos frame
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T46: The schematic - a shape drawn with no data, carrying the narrative (E99 s109 (1); harvest #12 `page_builder:cycle`)
- Status: pending
- Owner: implementation_luna (LANE B, with the Bravos verbs)
- Depends on: T10b, T36 (a light that travels along it); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/scripts/ledger_page.py` (a `schematic` builder: a closed-form curve - the hype cycle, the debt cycle, a mania arc, phase waves - with named phases, no axis values), `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_schematic_page.py` (new), one golden
- Acceptance: s109 (1): "we can draw with no data - that is the art and narrative coming to life in the world". (1) A `schematic` page draws a named closed-form shape (hype cycle, debt cycle, mania arc, phase waves; a `phases` list names the stretches) with NO axis values and NO figures it cannot source, and says on the page it is a shape, not a series (a small "schematic" tag); (2) its phases light in turn on their words (T36's travelling light / `span`), a `bracket` names a lag; (3) a real series may later be laid over it on a word (the shape meets the data); (4) seek-safe; byte-identical elsewhere; one golden (the hype cycle, three phases lit)
- Use when: the sentence explains a MECHANISM's shape over time (the cycle, the phases) rather than a measured value - row 12's three manias, the debt cycle
- Regression: `python -m pytest content/video_engine/tests/test_schematic_page.py -q`
- Expected RED: `schematic` is an unknown builder
- Validate: `node --check`, `node --test` kinetics, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_golden_frames.py`
- Evidence: pending

### T47: Rings in turn on every vertex, and the valley lit - when the sentence is about those vertices (E99 s109 (3))
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T26a (a ring reads the morphed top), T36; lane B
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (the ring species' multi-target form and its check), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (only if the painter needs it), `content/video_engine/tests/test_rings_on_vertices.py` (new)
- Acceptance: s109 (3): "rings at repeating near similar peaks, and a highlight on the valley". (1) First find whether N `ring` species on N datums in turn already compile and read (`build_scene_timeline_f.py:1165` targets a datum/point/region) - if they do, this is a recipe + a use-when, not engine work; (2) a `ring` may take a list of datums ringed IN TURN on their words (each lands, the previous holds or fades by the row's word), and a `valley` light (the stretch between two peaks lit - T36's travelling light over a region); (3) E56's check accepts N rings when each is keyed to its own word; (4) byte-identical elsewhere
- Use when: the sentence is ABOUT the vertices - repeated near-equal peaks ("it topped out here, and here, and here"), the trough between them
- Regression: `python -m pytest content/video_engine/tests/test_rings_on_vertices.py -q`
- Expected RED: a ring list of three datums is refused, or the rings all land at once
- Validate: the regression, `test_the_stamp_arrival.py`, `test_golden_frames.py`
- Evidence: pending

### T48: The pie and the donut, flat or 3D exploded, and the push onto the largest slice (E99 s109 (4))
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26f (the camera free of the chrome); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `share` builder's extrusion + explode + peel), `content/video_engine/scripts/ledger_page.py` (the `share` page options), `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_share_pie_3d.py` (new), goldens
- Acceptance: s109 (4) and its amendment: "maybe a 3d pie chart exploded and then zoomed onto the largest portion when discussing NVDA's market share of AI". Find and REUSE the existing `share` builder and `peel` first. (1) A share page may be a pie or a donut, flat or EXTRUDED with a tilt (a 2.5D projection of true-angle slices), a slice EXPLODED out on its word; (2) accuracy: the slice ANGLES are the true shares and every figure is written - the perspective is the camera's, not the data's; the check refuses shares that do not sum to their whole (or names the "other" slice); (3) a camera key may push onto a named slice (T26f's free camera) while the others recede; (4) the hatch (T6b) may shade the extrusion's side from the one stage light; (5) byte-identical for existing share pages; goldens for the flat donut, the 3D exploded pie, and the push
- Use when: the sentence DIVIDES a whole and the story is one piece's weight (NVDA's share of AI compute) - the push makes the emphasis the claim
- Regression: `python -m pytest content/video_engine/tests/test_share_pie_3d.py -q`
- Expected RED: `extrude` / `explode` are unknown share options
- Validate: `node --check`, `node --test` kinetics, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_golden_frames.py`, `test_camera_keeps_the_page.py`
- Evidence: pending

### T49: The freeze beat - everything stops and one light comes on (E99 s99)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T36 (the light); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the species; `effects/cards/species.json:206` names `beat_freeze` unbuilt), `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/scripts/gate_motion_density.py` (the beat is punctuation, not stillness), `content/video_engine/tests/test_freeze_beat.py` (new), one golden
- Acceptance: s99: "a light that comes on as everything else STOPS is a punctuation beat". (1) A `freeze` species on a word: every idle, drift and ambient life on the stage holds for its duration (a 0.4-1.2 s dial) while ONE light (a named datum, mark or prop) comes on; then life resumes; (2) the gate reads it as a punctuation beat, not a still run (the frozen-frame check and E49 know it by name); (3) seek-safe; byte-identical elsewhere; one golden
- Use when: the TURN of the argument lands on one number or thing - the line the whole row builds to (row 18's turn, row 23's ring)
- Regression: `python -m pytest content/video_engine/tests/test_freeze_beat.py -q`
- Expected RED: `freeze` is an unknown species
- Validate: `node --check`, `node --test` kinetics, `sync_kinetics.py --check`, the regression, `test_gate_motion_density.py`, `test_golden_frames.py`
- Evidence: pending

### T50: Forms judged by honesty, not type (E99 s100, s109 (5); R26-263) + a bracket on a bars page (R26-272)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: none; lane B
- Write set: `content/video_engine/scripts/ledger_page.py`, `content/video_engine/scripts/build_scene_timeline_f.py` (every by-type refusal of a form), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (paintBracket on bars), `content/video_engine/tests/test_forms_by_honesty.py` (new)
- Acceptance: s100 + s109 (5): E53's form rules are DEFAULTS that give way to the story when the honesty tests hold. (1) List every place the compiler or the page refuses a FORM by type (stacked bar, area, dual axis, donut, uneven epochs) and turn each into an honesty check - true proportion, figures written, the reading unambiguous - that WARNs with numbers when it fails (s106), keeping hard refusals only for untruth (a value drawn wrong, shares that do not sum); (2) R26-272: a `bracket` on a bars page anchors to the bar tops (it paints nothing today); (3) byte-identical for rows that use none of it
- Regression: `python -m pytest content/video_engine/tests/test_forms_by_honesty.py -q`
- Expected RED: an area page / a bracket on bars is refused or paints nothing
- Validate: the regression, `test_golden_frames.py`, `test_page_boxes.py`
- Evidence: pending

### T45: The membership stack - equal tiles (logos, names) inside one bar (E99 s101, approved in this lane 2026-09-23; built nowhere yet)
- Status: pending
- Owner: implementation_luna (LANE B, with the Bravos verbs)
- Depends on: T10b (soft bars), T26d (the tiles are placed objects); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the bars painter's tile layer), `content/video_engine/scripts/ledger_page.py` (the `members` field on a bar and its check), `content/video_engine/scripts/build_scene_timeline_f.py` (the tiles' landing on a word), `content/video_engine/tests/test_membership_stack.py` (new), one golden
- Acceptance: s101: "A bar may be filled with EQUAL tiles naming who is in it (logos, names) when the bar is ONE value, the tiles carry no value of their own (equal height, never sized), and the bar's total is written on the page" - Bravos's AI-hidden-debt bar with Google / Microsoft / Amazon / Meta / Oracle tiles. (1) A bar datum may carry `members: [{name, logo?}]`; the bar is drawn at its one value and divided into equal tiles bottom-up, each a name or a logo cutout (alpha kept, T6d), the bar's total written above it; (2) the tiles land one by one on their words (or together), each with the badge-ladder spring; a tile may be lit/solo'd (T37) when its name is spoken; (3) the check refuses a `members` entry that carries a value (a stack of values is s109's to judge, not this form's) and WARNs when a name cannot fit its tile at the phone floor; (4) soft bars and the hatch follow the whole bar; (5) byte-identical for a bar with no `members`; one golden (five tiles, the total written) read by the parent before pinning
- Use when: the sentence names WHO is in a single total ("Google, Microsoft, Amazon, Meta and Oracle - all of it one bill") - never to compare the members' sizes
- Regression: `python -m pytest content/video_engine/tests/test_membership_stack.py -q`
- Expected RED: `members` is an unknown bar field
- Validate: `node --check` the engine, `node --test` kinetics, `sync_kinetics.py --check`, `measure_page_boxes.py --check`, the regression, `test_bar_style.py`, `test_golden_frames.py`
- Evidence: pending

### T44: the Bravos RECIPES composed from T36-T43, each proved as a body beat
- Status: pending
- Owner: implementation_luna
- Depends on: T43; T35; lane A; T56 (the equation row, for the formula recipe R25)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the verb's paint only), `content/video_engine/scripts/species/<verb>.mjs` (new, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the token's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/<verb>.test.mjs`, `content/video_engine/tests/test_<verb>.py`, `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: from the Bravos harvest v2 (`docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md`, section 6) and the use-when guide (`docs/research/bravos-style/BRAVOS-USE-WHEN.md`). Ranks 5, 8, 10, 13, 14, 15: `the-ratio-read-in-the-gap` + the group bracket, `the-epoch-walk`, `peak-fall-magnitude`, `isolate-then-quantify-the-tail`, `the-formula-by-its-words`, `the-hidden-base` / the proportional iceberg (s100). Each a recipe JSON (status candidate) with its use-when, proved on the H row the harvest names. Common: the card carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from the guide; a golden of the verb on a real H body beat (never a fixture served as a scene, s60); absent the token every page byte-identical; drawn in the `longform` profile when the row takes it
- Regression: the verb's own test (`python -m pytest content/video_engine/tests/test_<verb>.py -q`)
- Expected RED: the token is refused as unknown by `build_scene_timeline_f`
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_<verb>.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Frame acceptance: the parent reads the verb's beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending


**ADDED 2026-09-23 (the operator: "yes, add all of the bravos slices"):** T51-T80 carry every harvest v2 item that is still MISSING or PARTIAL and that T8-T10, T8b, T26a-T26f, T36-T50, T43b and T45 do not name (the carrier map sits under the Ruling coverage table). Every one is LANE B and builds after the verbs it composes, drawn in the `longform` profile when the row takes it. **Common to T51-T80:** (a) Find and REUSE first - `docs_find` before any new code, the capability named at the head of each Acceptance; (b) the new card or recipe carries its USE-WHEN (act, story moment, data shape, use when / don't) copied from `docs/research/bravos-style/BRAVOS-USE-WHEN.md` (cited below as `:<line>` in that file); (c) where the form carries data, s109's honesty test IS its check - drawn in true proportion, the figures the claim turns on written, the reading unambiguous - a failure WARNs with its numbers (s106), a hard refusal only for untruth (a value drawn wrong, parts that do not sum); (d) every row that does not name the move compiles byte-identical (the H door, every golden); (e) one golden per new FORM, on a real H body beat (never a fixture served as a scene, s60), read by the parent before it is pinned - a recipe-only slice has no golden, its proof strip is read instead; (f) no body row adopts the move until the parent has read its frame beside the Bravos frame it was harvested from.

### T51: The fill gauge - one share of one whole fills a capsule on its word (harvest T34)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T50 (an area form judged by honesty, not refused by type); T10b (the soft shoulder and hatch the capsule takes); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (a `gauge` variant on the `progress` path: its validation and spec), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the gauge's paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (the variant's validation only), `content/video_engine/scripts/measure_page_boxes.py` (a gauge representative), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_fill_gauge.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: docs_find 0 hits for "fill gauge"; build on the ledger `progress` variant (`ledger_page.py:24` "story values in 0..PROGRESS_MAX, or non-negative with a numeric "denominator"", `PROGRESS_MAX` `:61`, its bound check `:1077`) and the `chart_dock:shares` card (`effects/cards/chart_dock.json:320`, "Labelled tracks fill left to right to their fraction"); the prop `prop-treasury-yield-gauge-5pct-v1.png` is a still, not this form. (1) A `gauge` page (or card) draws ONE capsule - vertical by default, horizontal by option - that fills from empty to its share on its word on the min-jerk clock, its figure ("94 %", "two-thirds") written at the fill line as it lands; (2) honesty (s100, s109 (5)): the fill length is the true share of the capsule's inner length (M26: the printed value and the drawn height agree at every instant), the whole it is a share of is named on the page, a value outside 0..100 (or its denominator) is refused as untrue; (3) one gauge per page by default; two side by side only when each names its own whole - comparing shares stays a bars page (the guide's don't, `:486`); (4) composes with `;readability=longform` and `;bar_style=soft`; (5) byte-identical for every page without the variant; one golden: row 17's 94 % funding share as a gauge, read by the parent beside the bars page it would replace
- Use when: `:485` "one share of one whole ("two-thirds", "94 %")"; don't `:486` "comparing shares (use bars)". H row 17 ("Ninety-four", the funding share) and row 23 ("a fifth of the index") - the parent picks gauge or bars on the frame
- Regression: `python -m pytest content/video_engine/tests/test_fill_gauge.py -q`
- Expected RED: `gauge` is not one of `ledger_page.py`'s VARIANTS (`:66`) and the page is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_fill_gauge.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T52: Companion bars beside a held line - two magnitudes set against each other while the line stays (harvest T39)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T8b (panels and the composable focus state - the companion is a panel in a `free` layout); T26d (objects placed where the author puts them); T50 (a bracket on bars); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (the companion panel's validation), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the companion's paint and its entry beside the held plot), `content/video_engine/scripts/build_scene_timeline_f.py` (its validation), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_companion_bars.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "companion"; build on `chart_to:park` (`CAPABILITIES.md:124`, "the chart makes room by one affine transform"), `recipe:chart-parks-for-their-claim`, a `chart_dock:bars` card and T8b's panels (a panel in the `free` layout, its focus state keyed to words). The harvest (`BRAVOS-VOCABULARY-HARVEST-v2.md:78`) names the missing part: "an in-page companion inset does not" exist. (1) On its word a held line page makes room (the park's transform or a T8b focus state) and a small bars panel of 2-3 values builds in beside it - never over the plot, ticks or source (E63, E45; a WARN with numbers, s106); (2) the line keeps its ink and its idle; the bars take their badges on their words (`recipe:badge-ladder`); a `bracket` (T50) or a written multiple ("5x") may land between the bars; (3) honesty: the bars carry their own stated scale (E79: one scale for one measure, `independent` names a second), every value written, bars from zero; (4) the companion leaves on its word and the line reclaims its width by the existing un-park (`scale: 1.0`); (5) byte-identical for pages that do not name it; one golden: row 14's capital-formation line held while rail `50¢` and `28¢` build beside it
- Use when: `:289` "the line stays as context while two magnitudes are set against each other beside it"; don't `:290` "the bars cover the plot, ticks or source (E63, E45)". H row 14 ("railways took roughly half": rail 50¢ beside 28¢); row 16's issuance 28 -> 150 beside the IG line is the second candidate
- Regression: `python -m pytest content/video_engine/tests/test_companion_bars.py -q`
- Expected RED: the `companion` key on a line page is unknown and refused by the compiler
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_companion_bars.py content/video_engine/tests/test_ledger_panels.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T53: The "?" at the unknown, the collage that resolves into it, the predictions board (harvest A61, F12, R13)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T42 (the chip's states - the "?" is a chip glyph and a datum mark); T40 (the blur a collage recedes under); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the prompt's paint; the collage's resolve), `content/video_engine/scripts/species/chip.mjs` (the "?" glyph, synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json` (the predictions board), the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_unknown_prompt.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: the breakthrough's placeholder "?" (`CAPABILITIES.md:90`; `ledger_page.py:409` "`overflow_placeholder` is the mark the breaking bar prints until its number is spoken"), the icon chip and its cross (`CAPABILITIES.md:100`, `species/chip.mjs`), the press stack (`CAPABILITIES.md:101`, `dock_option:stack`); docs_find 0 capability hits for "collage". (1) A `?` mark lands on its word at a datum, a node, a chip or a region - a pulsing prompt counts as motion (s99), a held one is an annotation (s91); (2) F12: a set of docked cards (the press stack) recedes and blurs (T40) while one large `?` rises out of them on the word that asks the question; (3) R13 `recipe:the-predictions-board`: THEIR predictions as a chip rail (A28, HAVE) on their words, then struck one by one on the refuting word (the chip cross, F8's dim), each prediction sourced (a record or press card per item); (4) the check refuses a `?` on a thing the same row states a figure for (the guide's don't, `:792` "where we can state a figure"); (5) byte-identical for rows that name none of it; one golden: the "?" on a row-23 beat
- Use when: `:791` "the open question is itself the sentence"; `:1009` "a hook's collage of claims resolves into the open question"; `:1015` "other people's predictions lined up, then struck on 'six months later'". H row 23 ("Decide for yourself which of those you believe") and row 12 ("what survives it"); no H body row carries a predictions board or a collage - R13 and F12 are proved on a private test-bed beat for the next hook
- Regression: `python -m pytest content/video_engine/tests/test_unknown_prompt.py -q`
- Expected RED: a `?` species (or chip glyph) is refused as unknown; `recipe:the-predictions-board` does not exist in `content/video_engine/effects/recipes/`
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_unknown_prompt.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T54: The inset echo - a historical twin mini-chart in the plot's empty room, then the "?" (harvest T40, R36)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T8b (a `free` panel box on the page); T10c (a chart card drawn for its displayed size); T53 (the "?"); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the inset's paint and entry), `content/video_engine/scripts/build_scene_timeline_f.py` (the inset's validation and its placement read from the page's boxes), `content/video_engine/scripts/ledger_page.py` (only if the inset is a panel role), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_inset_echo.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: the chart card (`CAPABILITIES.md:74`, `chart_card.py`, T10c's `card` profile), E65's placer (`CAPABILITIES.md:31`, "the plot's empty room"), T8b's `free` layout; docs_find 0 capability hits for "inset" as a chart (the one hit is the slide transition, `:40`). (1) On its word a twin chart (its OWN series file and source) lands as a small panel in the plot's measured empty room, never over drawn ink (a WARN with numbers, s106), its title naming the era ("Utility Companies 1929"); (2) honesty: the twin states its own scale and unit - one unit shares the host's scale (E79), another is `independent` and the page says so; the twin never borrows the host's axis; (3) R36 `recipe:inset-echo-then-the-question`: the inset lands, the rhyme is spoken, then T53's `?` pulses beside it; (4) leaves on its word; byte-identical otherwise; one golden: row 9's railway index with its dot-com twin in the room. The harvest's C16 (E63 vs E65's placer) is OPEN: the question rides with the golden into the HG4 batch and no body row adopts the inset before the operator's answer
- Use when: `:295` "the shape rhymes, and the rhyme is the argument"; don't `:296` "over drawn ink (E63); without the twin's own source"; R36 `:403` "the rhyme is shown, then the open question". H row 9 (the railway mania and the 2000 internet crossing) and row 12 (the three manias)
- Regression: `python -m pytest content/video_engine/tests/test_inset_echo.py -q`
- Expected RED: an inset dock on a ledger page's plot is refused (E63) or placed outside the plot; the recipe id does not exist
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_inset_echo.py content/video_engine/tests/test_chart_card_readable.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T55: The epoch ruler - a time axis with cards pinned to its ticks (harvest T32)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T38 (the axis_tag pill on a tick); T26d (cards placed and moved where the author puts them); T50 (a bracket between two ticks); lane B
- Write set: `content/video_engine/scripts/species/ruler.mjs` (new, synced by `sync_kinetics.py --write`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the ruler's paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (the species' validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/ruler.test.mjs` (new), `content/video_engine/tests/test_epoch_ruler.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "ruler"; `species/thread.mjs:1` names "the ruler" (HF-16) but builds only the wire; build on `span.mjs` (`CAPABILITIES.md:104`), T38's axis_tag pill, `axes.marks` (`ledger_page.py:90` AXES_KEYS) and the still / chart card dock. (1) A `ruler` species wipes on a horizontal time axis on its word (A67) with its ticks at TRUE dates (even spacing per unit of time; a gap the ruler does not draw says so on the ruler); (2) cards (a still, a chip, a chart card) pin to their ticks one by one on their words, each on a short leader, the tick lighting to a pill (T38); (3) a `bracket` (T50) may span two ticks with the measured lag written ("7 years"); (4) honesty: the tick positions are the dates, never re-spaced to fit the cards - a card that cannot fit WARNs and offsets along its leader (s106); (5) seek-safe; byte-identical otherwise; one golden: row 9's three crossings (1845, 2000, today) pinned on one ruler, read by the parent
- Use when: `:879` "a lag of years between cause and payoff ("the fibre came first")"; don't `:880` "a single date (use A10)". H row 9 (the railway, the internet, today) and row 19 ("twenty years" to the payoff)
- Regression: `python -m pytest content/video_engine/tests/test_epoch_ruler.py -q`
- Expected RED: the `ruler` species is refused as unknown by `build_scene_timeline_f`
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_epoch_ruler.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T56: The equation row - the inputs, the relation and the signed result, built in spoken order (harvest T38, A60)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T50 (forms judged by honesty); lane B. T44's `the-formula-by-its-words` (R25) composes this species, so T44's formula recipe waits on it
- Write set: `content/video_engine/scripts/species/equation.mjs` (new, synced by `sync_kinetics.py --write`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the species' paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (the species' validation and the arithmetic check), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/equation.test.mjs` (new), `content/video_engine/tests/test_equation_row.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "equation" (the hits are 46 §46.4's script spine only); build on `species/figure.mjs` (the figure species), the flow diagram's chips and clothoid arrows (`CAPABILITIES.md:103`) for the operators' hand, and `chart_to compare` (`CAPABILITIES.md:29`) when the result becomes the felt number. (1) An `equation` species lays one row - input, operator, input, "=", result - each term landing on its own spoken word in the sentence's order (A60), the result last, signed and coloured by E28 (a negative result red); (2) honesty: the compiler COMPUTES the result from the inputs and refuses a row whose written result disagrees (an untruth); each input names its source or its tier (s93; E77, a derived figure is our layer); (3) up to three inputs; a term may later dock into a page as its figure; (4) byte-identical otherwise; one golden: row 18's "if the AI names fall by half, that erases ten percent" (20 % x 1/2 = 10 %), read by the parent beside the compare it precedes
- Use when: `:597` "the arithmetic IS the claim ("real yield = coupon − inflation")"; `:675` "a narrated sum or difference, each input spoken before the result"; don't `:676` "the inputs are unsourced, or the result is not spoken". H row 18 (the halving), row 17 ("Ninety-four"), row 23 ("a fab: 5 years / a chip 2x")
- Regression: `python -m pytest content/video_engine/tests/test_equation_row.py -q`
- Expected RED: the `equation` species is refused as unknown by `build_scene_timeline_f`
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_equation_row.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T57: Hub-and-spoke - one institution to many, and a link that fails (harvest T31, A26)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T43 (the flow's ring layout and edge tokens); T42 (the chip's `lit`); lane B
- Write set: `content/video_engine/scripts/species/flow.mjs` (the `hub` layout and the failed edge, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`flowLayout` and the edge paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/flow.test.mjs`, `content/video_engine/tests/test_hub_and_spoke.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "spoke" and none for "hub" beyond the remotion-ui registry (`CAPABILITIES.md:136`); build on the flow diagram (`CAPABILITIES.md:103`, `species/flow.mjs`; its `flowLayout` at `scene-evidence-engine.mjs:14890` lays a row or a column only), T43's ring layout and tokens, the chip's DIM and T42's `lit`, and the vector map arc's struck X (`CAPABILITIES.md:105`). (1) A flow `layout: "hub"` puts one node at the centre and 3-8 on a ring, each spoke drawn out on its word (dashed or solid), each rim node landing on its name; (2) A26: any flow edge (a spoke or a chain link) FAILS on its word - an X struck on the link, the link reddened and severed - and its nodes stay (the guide: "the link breaks, not the node"); (3) T43's tokens may travel the spokes; (4) honesty: a spoke carries no value by default; a row that writes weights draws widths in true proportion with the figures written, and unequal widths with no figures are refused as decoration posing as data; (5) byte-identical for every existing flow; one golden: row 16's bond market at the hub, the borrowers on the rim, one spoke failing
- Use when: `:523` "one institution connects to many ("the IMF stepped in for six")"; don't `:524` "a chain (use `flow`)"; `:609` "'lending dries up': the link breaks, not the node". H row 16 (who is paying) - derived; the parent confirms the hub on the frame
- Regression: `python -m pytest content/video_engine/tests/test_hub_and_spoke.py -q`
- Expected RED: `layout: "hub"` is refused by the flow validation; an edge `fail` key is unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_hub_and_spoke.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T58: The decomposition brace - one quantity braced into its named parts (harvest T24)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T50 (the bracket anchored on a bars page, R26-272); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the brace form of the bracket's paint), `content/video_engine/scripts/build_scene_timeline_f.py` (the form's validation and the sum check), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_decomposition_brace.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "brace"; build on `page_species:bracket` (`CAPABILITIES.md:118`; "The hand draws a measured span between two data, the number as its label"), T50's bar-top anchoring and the flow box's dashed group rectangle (A30, HAVE). (1) `bracket` takes `form: "brace"`: a curly brace from one total (a bar, a figure, a chip) to its 2-4 named parts, each part's figure written, landing on their words; (2) honesty: the parts must sum to the whole within the rounding written on the page - the compiler REFUSES a brace whose parts do not add (the guide's don't, `:468` "the parts are not additive"); (3) byte-identical otherwise; one golden: row 17's capex braced into its cash-funded and debt-funded parts
- Use when: `:467` "one quantity is the sum of named parts ("the rate = policy + term premium")". H row 17 (the arithmetic)
- Regression: `python -m pytest content/video_engine/tests/test_decomposition_brace.py -q`
- Expected RED: `form: "brace"` is refused on a bracket
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_decomposition_brace.py content/video_engine/tests/test_forms_by_honesty.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T59: The balance scale, and the balance tips (harvest T27, A40)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26d (the pans' loads are placed objects); T6b (the one stage light and the resting shadow); lane B
- Write set: `content/video_engine/scripts/species/balance.mjs` (new, synced by `sync_kinetics.py --write`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the species' paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/balance.test.mjs` (new), `content/video_engine/tests/test_balance_scale.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "balance scale" (doc 48 §48.2 is a figure's balance); build on stop-action throw and land (`CAPABILITIES.md:78`, `kinetics/stopaction.mjs`), `kinetics/spring.mjs` for the beam's settle, the chip for each pan's name, T6b's resting shadow. (1) A `balance` species draws a beam on a fulcrum with two pans; each pan's load (a chip, a prop, a flag) lands on its word and the beam settles level on the spring; (2) A40: on the verdict word the beam TIPS to one side on the spring with one overshoot - a mass, never a fade; (3) honesty: the balance carries NO figures - its tip is the sentence's verdict, not a measurement; a row that writes numeric weights is refused by name, pointing to two bars (the guide's don't, `:646` "a real balance of figures (use two bars)"); (4) seek-safe; byte-identical otherwise; one golden: row 19's "Both are true at once" level, then a tip on a verdict word
- Use when: `:591` "two forces weighed ("threat" vs "opportunity", US vs Japan)"; `:645` "two forces are weighed and the sentence says which way it tips". H row 19 ("Both are true at once") and row 23 ("Decide for yourself which of those you believe") - derived
- Regression: `python -m pytest content/video_engine/tests/test_balance_scale.py -q`
- Expected RED: the `balance` species is refused as unknown by `build_scene_timeline_f`
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_balance_scale.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T60: Verdict tiles with a check state, two verdict panels, and the BUY tab (harvest T26, R14, A59)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T42 (the chip's `tick` and `sell` states); T10c (a chart card drawn at its displayed size); T8b (two panels on one page); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the tile's state layer), `content/video_engine/scripts/chart_card.py` (a `tile` size of the `card` profile, only if T10c's profile cannot carry it), `content/video_engine/scripts/build_scene_timeline_f.py` (the state keys' validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_verdict_tiles.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find "verdict" names the VERDICT STACK (`CAPABILITIES.md:193`, `species/verdict.mjs`) - the evidence wall, a different move; build on the chart card (`CAPABILITIES.md:74`) under T10c's `card` profile, T8b's panels and T42's states. (1) A mini-chart TILE (a chart card at tile size, drawn from a sourced series) takes a verdict STATE on its word - ✓ held (green), ✗ struck (dimmed under the cross, F8), or a BUY / SELL tab (A59: T42 carries SELL; this adds BUY on the same state grammar); (2) R14 `recipe:two-verdict-panels`: two tiles side by side, each explained on its words, each verdict landing on its own confirming or refuting word; (3) honesty: a tile's chart is drawn from its own sourced series (the guide's don't, `:980` "the panels carry no sourced data"); a BUY / SELL tab is a scenario label, never a trade record (`:670`); (4) byte-identical otherwise; one golden: row 21's three questions as tiles, each ticking on its word
- Use when: `:979` "the close rejects two easy options, one panel each"; `:1021` "the close rejects two strategies side by side"; `:669` "who must sell, who buys (H row 10's SELL ticket)". H row 21 ("So ask it the three questions" - the rows tick) and row 23; row 10's SELL stays T42's
- Regression: `python -m pytest content/video_engine/tests/test_verdict_tiles.py -q`
- Expected RED: a `verdict` state key on a chart card is unknown; `recipe:two-verdict-panels` does not exist
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_verdict_tiles.py content/video_engine/tests/test_chart_card_readable.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T61: The chapter pill held over an act, and the in-place badge swap (harvest A34, A44)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T26f (the page's chrome as objects - the pill is chrome); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the chrome pill and the text swap), `content/video_engine/scripts/build_scene_timeline_f.py` (the keys' validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_chapter_pill.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "chapter"; build on `page_species:retitle` (`CAPABILITIES.md:77`; "The page's title rewrites by the hand"), `species/tippill.mjs` and T26f's chrome layer. (1) A `chapter` chrome pill ("Act 2: the turn") lands on its word at a corner and HOLDS across every page of the act - it rides recasts, parks and returns without re-landing, and leaves on the act's last word; (2) A44: any held pill (the chapter pill, a span's, an axis_tag's) may SWAP its text in place on a word - the pill stays, its glyphs rewrite by the hand (retitle's glyph write), its width springing to the new text; a swap onto a different period is refused by name (the guide's don't, `:774` "the rename changes the period (move the pill instead)"); (3) byte-identical otherwise; one golden: the pill carried across a recast, then its swap. The harvest keeps the chapter pill "for rows 13 / 18 / 23 only if the operator wants act markers" (§6): it is built as an option and no body row adopts it before the operator's word at HG4
- Use when: `:971` "a long form has named acts and each chart should say which act it is in"; `:773` "the same period is renamed ("Dot-Com Bust" → "Lost Decade")". H rows 13, 18, 23 (the three resets) on the operator's word; A44 on row 22's "The flip"
- Regression: `python -m pytest content/video_engine/tests/test_chapter_pill.py -q`
- Expected RED: a `chapter` chrome key is unknown; a pill `swap` key is unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_chapter_pill.py content/video_engine/tests/test_page_chrome_moves.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T62: Illustrations drawn as schematics - candlesticks over a ghost wave, the axis-free motif line with X marks, and a ✓ / ✗ on a datum (harvest T8, T46, A14)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T46 (the schematic builder); T42 (the tick and the cross as glyphs); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (the schematic's `candles` and `motif` shapes), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (their paint; the datum badge), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_schematic_illustrations.py` (new), `content/video_engine/tests/golden/**` (one golden per new form)
- Acceptance: Find and REUSE first: docs_find 0 capability hits for "candlestick" (one icon, `prop-icon-candlestick-price-action-v1.png`) and for "motif"; build on T46's `schematic` page (no axis values, the "schematic" tag), the chip cross (`CAPABILITIES.md:100`) and the ring's datum target (`build_scene_timeline_f.py:1165`). (1) A schematic `candles` shape: a ghost wave (the schematic's closed form, muted) with illustrative candlesticks drawn along it on the word - bodies and wicks generated from the wave, NO axis values, NO figures, the "schematic" tag on the page (s109 (1)); (2) a schematic `motif` line: an axis-free line named by one word ("Market") that repeats a shape, an X struck at each named vertex on its word; (3) A14 on a datum: a ✓ or ✗ badge lands on a datum of a REAL chart on its word (T42's glyphs, anchored as a ring is) - the tick for what held, the X for what failed; (4) honesty: the check refuses any axis value, tick label or figure on a schematic page (s109 (1): it "carries no axis values and no figures it cannot source"); (5) byte-identical otherwise; one golden per new form (the candles, the motif). T8 serves no H row (the guide, `:574`: "no H row needs it") - it is built for the catalogue on s109 (1) and proved on a private test-bed beat
- Use when: `:573` "rarely; price action as illustration"; `:991` "(rarely) the close strips the chart to a symbol of 'the market'"; `:997` "a set judged item by item: a tick for what held, an X for what failed". H rows: none for T8; row 24 is the motif's candidate; A14 on data serves row 22 (the tripwires' endpoints)
- Regression: `python -m pytest content/video_engine/tests/test_schematic_illustrations.py -q`
- Expected RED: `candles` and `motif` are unknown schematic shapes; a ✓ / ✗ badge on a datum is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --check`, `python -m pytest content/video_engine/tests/test_schematic_illustrations.py content/video_engine/tests/test_schematic_page.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T63: The 2.5D tilted map with its routes lighting in turn, the origin ping, the chart beside the map (harvest T33, A37, R17)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26f (the camera free of the chrome); T43 (tokens moving on an edge); T8b (a map and a chart on one clock, as panels); lane B
- Write set: `content/video_engine/scripts/species/vecmap.mjs` (the tilted plane, the route sequence and the ping, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the map world's projection only), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/kinetics/vecmap.test.mjs`, `content/video_engine/tests/test_tilted_map.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: the ledger page at a depth (`CAPABILITIES.md:155`, `;plane=tilt:<deg>` by the ART-embed homography), `;form=tilted_line` (`:156`), the vector map (`CAPABILITIES.md:105`: a country lights, an arc crosses by length with the nib), T43's tokens; docs_find 0 hits for "sonar". (0) A37 is Gemini-only in both videos: first read D40 13:54-14:18 on the frames on disk (`docs/research/runs/bravos-watch/u70oUWgVoYU/frames_survey/`); if no frame shows the ping, A37 is withdrawn and the slice builds (1), (2) and (4) only; (1) `vecmap;plane=tilt:<deg>`: the map world projected on a tilted plane by the one homography, routes (arcs) lighting in sequence on their words, T43's tokens travelling them; (2) R17 `recipe:the-chart-beside-the-map`: a map and a line page on one clock (T8b's panels or a park), the route lighting on the chart's word; (3) A37: a ping ring expanding from an origin pin on its word - a blink, so motion (s99), never a ring on a region (E56); (4) honesty: nothing is area-encoded on the tilted map unless it is true in the flat geometry with its figure written - the tilt is the camera's, not the data's (s109 (4)); (5) byte-identical for untilted maps; one golden: row 22's memory route leaving Korea on the tilted map
- Use when: `:529` "a physical network built out over time (power lines, fibre)"; `:559` "the chart and the place on one clock"; `:541` "(unverified) an origin that keeps emitting". H row 22 ("what memory costs leaving Korea, by the kilo", the customs line beside the route) - derived
- Regression: `python -m pytest content/video_engine/tests/test_tilted_map.py -q`
- Expected RED: `;plane=` on a `vecmap` world is refused (it is a ledger-page option); a route `sequence` key is unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_tilted_map.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T64: The stacked bar of values, and the stacked-bar-plus-line combo (E99 s110 (1); harvest T29)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T50 (the stacked-bar refusal turned into an honesty check); T43b (a second, labelled scale for the line); T10b (soft bars); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (the `segments` field on a bar datum and its check; the `combo` builder's stacked bars), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the stacked segments' paint), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/scripts/measure_page_boxes.py` (a stacked-combo representative), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_stacked_combo.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: E99 s110 (1): "allowed, I think one legitimate case I can think of in finance is it's usually like when you're looking at financial metrics against business metrics or something like that, where you could have a stacked bar and a line." Find and REUSE first: the `combo` builder already exists (`ledger_page.py:218` `pick_builder`, bars + a pts series -> combo; its shape check `:1031`; its block `:1146`; P47 T9's `line_unit` right axis `:1104`); docs_find "stacked bar" has 0 capability hits (the one hit is the research blueprint's perception warning). (1) A bar datum may carry `segments: [{name, value}]`: the bar stacks bottom-up from zero, each segment drawn true to its value, each segment's figure WRITTEN and the bar's total written above it; (2) the COMBO: stacked bars of the financial metrics with the business metric's line over them; when the units differ the line takes its own labelled right axis on s102's conditions (each axis names its unit, its ticks coloured with its series) - T43b's `y2` / `claim` keys, or the combo's `line_unit`, never a third axis system; (3) T29, the partitioned horizontal bar (income vs bills): the same `segments` on a horizontal bar, a total past the whole drawn past it ("105 %"); (4) honesty (s109): the segments sum to the bar's written total (a mismatch is refused as untrue); a segment too thin for its figure WARNs and its figure takes a leader (s106); the segments' order and colours are keyed once for the page; (5) every existing combo and bars page byte-identical; one golden: row 17's capex stacked cash-funded / debt-funded with the revenue line over it on its own labelled scale
- Use when: s110 (1) "financial metrics against business metrics ... a stacked bar and a line"; `:473` "your bills are 105 % of your income: segments drawn true to their values, figures written". H row 17 (the arithmetic)
- Regression: `python -m pytest content/video_engine/tests/test_stacked_combo.py -q`
- Expected RED: `segments` is an unknown bar field and the page is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_stacked_combo.py content/video_engine/tests/test_dual_axis.py content/video_engine/tests/test_forms_by_honesty.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py -q`
- Evidence: pending

### T65: A ring may circle the thing the sentence points at - a picture, a card or a prop (E99 s110 (2))
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T47 (it edits the same ring check - sequenced after it); T26d (a prop's authored box, which the ring reads); lane B
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`_validate_callout` `:1993`, the ring species' targets `:1165`, and E56's messages), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (only if a dock or prop target needs the ring to read the dock's live box), `content/video_engine/tests/test_ring_on_the_named_thing.py` (new), `content/video_engine/tests/test_the_stamp_arrival.py`
- Acceptance: E99 s110 (2): "a ring may circle a picture, a card or a prop when the sentence points at THAT thing ("look at that certificate again") and carries its number beside it; E56's one-use now reads: the ring marks what the sentence points at." Find and REUSE first: E56 as code is `_validate_callout` (`build_scene_timeline_f.py:1993`: "A callout on a press card with no form is a ring around a picture, and E56 still refuses it by name"), the ring species' targets (`:1165`, `("datum", "point", "region")`), the dashed-ellipse ring (`CAPABILITIES.md:45`), the ring inside a centred dock (`CAPABILITIES.md:86`). (1) A callout or `ring` may target a DOCK or a PROP (`{"kind": "dock", "dock": "<asset id>"}`) and reads the dock's LIVE box - a parked or stacked card moves and the ring moves with it, as the underline already does (`:1177`); (2) the check keeps E56's narrowed use: a ring on a dock or a prop needs its word anchor on the phrase that points at it AND a number beside it (a figure species or the ring's label) - with no pointing phrase or no number it is refused by name, the message citing s110 (2); (3) every existing ring and callout compiles byte-identical; (4) row 18's ring on the certificate card's figure compiles as a ring on the card; a check change, so no golden - the parent reads row 18's frame
- Use when: s110 (2) "when the sentence points at THAT thing ... and carries its number beside it". The guide's A7 don't (`:750` "a picture (E56: a ring only on a chart)") predates s110 and is superseded by it. H row 18 ("So look at that certificate again") and row 23 (the certificate card, the ring on its figure)
- Regression: `python -m pytest content/video_engine/tests/test_ring_on_the_named_thing.py -q`
- Expected RED: a callout targeting a still dock is refused ("a ring circles a NUMBER or a POINT ON A CHART (E56)")
- Validate: `python -m pytest content/video_engine/tests/test_ring_on_the_named_thing.py content/video_engine/tests/test_rings_on_vertices.py content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T66: The broken cross-era axis - one line across two eras on one x-axis, the break drawn (E99 s111; harvest T35, C13 closed)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T50 (forms judged by honesty, not refused by type); T8b (panels - E79's route for unlike measures stays beside it); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (a `break` key on a dense-line x axis and its check), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the drawn break and each era's ticks), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/scripts/measure_page_boxes.py` (a broken-axis representative), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_broken_axis.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: E99 s111 (the operator, "yes"): "A line may run across two eras on ONE x-axis with a visible break when the claim is that the LEVELS are comparable era to era; the y is one unit for both, both eras are labelled, and the break is drawn so the gap is never read as continuous time (E53 s3's "never a continuous axis" is met by the break, not broken). When the claim is that the SHAPES match, the rebased overlay (row 15's "years from each era's start") stays the form." Find and REUSE first: docs_find "broken axis" hits the breakthrough bars' scale break (`CAPABILITIES.md:90`) and E60 (`OPERATOR-RULINGS.md:1959`) - a bar breaking its SCALE, not an x axis; the dense-line page and its `axes.xticks` (`ledger_page.py:90` AXES_KEYS), E53 s8's end tags and the `span` species (`CAPABILITIES.md:104`) for each era's name. (1) A dense-line object may carry `axes.break: {after, before}` (the last x of the first era, the first x of the second): the x axis is cut once, a `//` DRAWN across the axis line and the trace, each era's ticks true within its own stretch and each stretch scaled on the same years-per-pixel; (2) the y is ONE unit for both eras - a series pair whose units differ is refused by name (that claim is E79 panels, `axes.independent`); (3) both eras are LABELLED on the page (an era name or its span over each stretch - the `span` species or a tag), and the gap is written at the break ("1849 // 1985"); (4) a `claim: "level"` key is required with a break; a page whose claim is the SHAPE is refused with the pointer to the rebased overlay (row 15's two-eras page, s111); (5) the trace never draws across the break - each era's line ends and restarts at it; the `build=lines` clock (R26-226) draws era by era; (6) honesty (s109): the levels are the sourced values on the one y, the break is visible at every instant the axis is; (7) byte-identical for every page without `break`; one golden: a railway-era and a today-era share-of-GDP line on one broken axis, read by the parent beside the Bravos frame (HIS 7:18-8:01)
- Use when: s111 "when the claim is that the LEVELS are comparable era to era"; `:271` "railway 1840s and AI 2020s on one share-of-GDP axis with a visible `//`"; a SHAPE claim stays the rebased overlay (s111). H row 9 ("In two thousand the internet crossed seven percent ... AI spending just crossed eight": the railway era's share of GDP set against the internet's and AI's is a LEVEL claim - only if a railway-era share-of-GDP series is authored and sourced beside `ev-equip-ipp-gdp-v1`) and row 14 ("railways took roughly half": rail's 50¢ against today's 28¢ on the capital-formation line, a level across eras). Row 15's two-eras rate page is a SHAPE claim and keeps the rebased overlay (s111)
- Regression: `python -m pytest content/video_engine/tests/test_broken_axis.py -q`
- Expected RED: `break` is not one of `ledger_page.py`'s AXES_KEYS (`:90`) and the object is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_broken_axis.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T67: A card joins its date on the line, and the proof walk (harvest A19, R4)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T36 (the stretch lit); T38 (the era tagged); T40 (the blur under a dock); T26d (the parked chip placed at its datum); T62 (the ✓ / ✗ on a datum); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the park-to-a-datum target and its leader), `content/video_engine/scripts/build_scene_timeline_f.py` (the dock's `park_at` datum validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_card_at_its_date.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: the dock that reads then parks (`CAPABILITIES.md:91`), the press card (`:101`), `axes.marks` (the dot, chip and dashed leader), E65's placer, T40's blur. C2 is OPEN (E63: "a card never READS over a ledger page's plot"), so the honest route the guide names is built: (1) on its word a card (press or record) READS in its slot, then PARKS to a small chip AT its datum on the line, a leader from the chip to the date - the join IS the claim; the plot behind the reading card may blur (T40, s98 / s104 amended) when the row names it; (2) R4 `recipe:the-proof-walk`: one long line, its episodes walked in turn - the stretch lit (T36), the era tagged (T38), the card read and parked at its date, a ✓ / ✗ on the datum (T62) or a bracket (T50) - one episode per sentence; (3) a card READING over the plot at its date (Bravos's own form) is an option only after the operator answers C2 - the question goes into the HG4 batch; (4) byte-identical otherwise; one golden: a card parking to its date on row 9's railway index
- Use when: `:105` "a headline belongs to one date on the line, and the join IS the claim ("the warnings began here")"; `:933` "one long line proves a pattern by walking its episodes, each with its card". H row 9 (the railway index's episodes) and row 16 ("right there in the filing")
- Regression: `python -m pytest content/video_engine/tests/test_card_at_its_date.py -q`
- Expected RED: a dock `park_at` naming a datum is unknown; `recipe:the-proof-walk` does not exist
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_card_at_its_date.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T68: The future box, the push to now then the unknown, the evidence then the conditional future (harvest A56, R5, R26)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T41 (`project`); T26f (the camera free to push to today's end); T53 (the "?" and "???"); T36 (the now lit); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the future box's paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (the box's validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json` (two recipes), the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_future_box.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: T41's labelled dashed continuation, `recipe:estimate-opens-as-a-wedge` (T35, kept), `focus_zoom` and `chart_to:rescale` (`CAPABILITIES.md:119`); docs_find 0 capability hits for "scenario". (1) A56: on its word a dashed box draws round the empty future window (right of the last datum to the projection's horizon), labelled with its horizon ("to June 2027"), before the path draws; (2) R5 `recipe:push-to-now-then-the-unknown`: a rescale or a push on a named datum lands on today, then a labelled scenario path (T41) or T53's "???" runs off the edge - never a continuous push (E59); (3) R26 `recipe:evidence-then-the-conditional-future`: the evidence held ~10-14 s (named averages, the now lit by T36, a bracket), THEN the projection in a visibly new grammar - dashed, its label and tier written (E77, s93); (4) honesty (C15): every projected path names itself a projection and its source tier; a box with no path inside it before its hold ends WARNs; (5) byte-identical otherwise; one golden: the future box on row 16's consensus capex
- Use when: `:423` "the future window needs to read as empty before the path draws"; `:429` "the camera or a rescale lands on today, then a labelled "???" or scenario runs off the edge"; `:435` "hold the evidence ~10-14 s, then a projection in a visibly new grammar". H row 16 ("four hundred and eighty… six hundred and ninety") and row 23 ("booked solid through twenty twenty-six")
- Regression: `python -m pytest content/video_engine/tests/test_future_box.py -q`
- Expected RED: the future box key is unknown; neither recipe id exists
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_future_box.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T69: The rig - a metaphor prop arrives in a puff under its load (harvest A35, R16)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26d (the prop at its authored place); T6b (the resting shadow); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `poof` arrival's paint only), `content/video_engine/scripts/build_scene_timeline_f.py` (`poof` in ARRIVALS and its validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_poof_arrival.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: docs_find 0 hits for "poof"; build on the stamp arrival and the bare prop (`CAPABILITIES.md:79`), stop-action (`:78`), the melt's splash (`CAPABILITIES.md:38`, `species/melt.mjs`) for the puff, T6b's resting shadow and T26d's authored place. (1) `arrive: poof`: a prop appears inside a short puff (a ring of particles bursting and fading on the spring, one cue) under a load already placed above it; (2) R16 `recipe:the-rig`: a metaphor carries a load - the support lands, the load poofs onto it, leaders name each part (the risk, the thin support) - props from the catalogue only; (3) the prop never stands in for a figure (s106's truth rules stay hard): a rig row that writes a number on a prop is refused by name; (4) byte-identical otherwise; one golden: the poof arrival. No H body row names a rig: row 17's "The paper just got heavier" is the candidate beat and the parent decides on the frame; otherwise it is proved on a private test-bed beat
- Use when: `:633` "a metaphor prop (the rig lane)"; `:717` "a metaphor carries a load (the risk sitting on a thin support)"; don't `:718` "a data claim". H row 17 (candidate only)
- Regression: `python -m pytest content/video_engine/tests/test_poof_arrival.py -q`
- Expected RED: `arrive: poof` is not one of the compiler's ARRIVALS
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_poof_arrival.py content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T70: Chart-and-diagram recipes - rise, turn, consequence; the doubt then the budget evidence; the total that points back (harvest R19, R34, R35)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T36, T37, T40, T42, T50; T44 (R18's peak-fall-magnitude, which R19 extends); lane B
- Write set: `content/video_engine/effects/recipes/<new>.json` (three new recipes; no existing recipe edited), the catalogue's generated files via `python content/video_engine/scripts/build_effects_catalog.py --write`, `content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py` (three new proof beats; the build output stays gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: Find and REUSE first: every part is HAVE or built by T36-T50 (s70: a recipe is a timing that composes existing cards); the pattern is T35's candidates with their `use_when` (`effects/recipes/two-clocks.json`). (1) `recipe:rise-turn-consequence` (R19): R18's peak-fall-magnitude, then the chart dims (T40 / `lpPlateRecede`) under a tile, a flow branches out of it and ✓ land on what survived (T42); (2) `recipe:doubt-then-the-budget-evidence` (R34): the question as a flow above, the bars answering below, the source card last with its highlighted phrase (F5); (3) `recipe:the-total-points-back` (R35): a headline total lands, a curved leader points back to the bar it dwarfs, then the multiple (a bracket, T50) - the total never competes with the data (a placement WARN); (4) each recipe `status: candidate`, `count: 0`, carries its `use_when`, and is proved as a beat on its H row (s60), the strip read by the parent before it is queued; a proof that reads wrong is withdrawn. No new form, so no golden
- Use when: `:723` "after the fall is quantified, the chart dims and what survived branches out with checks (H row 13's "The steel kept working")"; `:735` "the question as a diagram above, the bars answering below, the source card last (H row 11's Uber)"; `:839` "a headline total, then a leader back to the bar it dwarfs, then the multiple". H rows 12-13 (row 13 is a plate reset, so R19 lands on row 12's page before the dip - the parent confirms on the frame), row 11, and row 16 for R35 (the 150 total pointing back to the 28 bar) - derived
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the three recipe ids exists in `content/video_engine/effects/recipes/`
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py -q`, `python content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py`, `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T71: Line recipes - the trace to its level, the divergence spread, today's boom against past booms (harvest R21, R27, R32)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T37 (`solo`); T38 (`axis_tag`); T39 (`level_join`); T50 (a bracket on the gap); lane B
- Write set: `content/video_engine/effects/recipes/<new>.json` (three new recipes; no existing recipe edited), the catalogue's generated files via `python content/video_engine/scripts/build_effects_catalog.py --write`, `content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py` (three new proof beats), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: Find and REUSE first: `page_enter:axes`, `recipe:pill-rides-the-line`, `ring`, `page_species:spread` ("The region between two drawn series bleeds full of ink on a word"), `bracket`, and T37-T39; `recipe:estimate-opens-as-a-wedge` (T35) stays the projection's form. (1) `recipe:trace-to-the-level` (R21): the line draws, the tip blooms, a ring lands on it, the level_join (T39) runs to the named level, the pill lands - the label off the rule (C14); (2) `recipe:the-divergence-spread` (R27): two lines, their end pills, the gap fills (`spread`), a bracket on the gap with its figure; (3) `recipe:today-against-past-booms` (R32): the rebased cycles (harvest T36, HAVE; the rebasing stated on the page as our derived layer, E77), today's cycle bright with its x and y read off by axis_tag pills (T38), the past cycles drawn after it and muted (T37); (4) each `status: candidate`, `count: 0`, with its `use_when`, proved on its H row, the strip read by the parent before it is queued. No new form, so no golden
- Use when: `:821` "draw, bloom the tip, ring it, run the dashed level, land the pill (H row 15's 5.5)"; `:951` "H rows 1, 20, 24, and row 10's "chips doubling, customers flat""; `:391` "the newest cycle drawn bright, its x and y read off by pills, the past cycles drawn muted after it". H rows 15 (R21), 1 / 10 / 20 / 24 (R27), 9 for R32 only if a rebased series is authored for it - else a private test-bed beat
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the three recipe ids exists in `content/video_engine/effects/recipes/`
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py -q`, `python content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py`, `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T72: Bars re-valued - then to now, the ratio span after it, and the ranked dim-the-rest (harvest A48, R28, R30)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26a (a bar changes its own value; `ghost=yes`); T37 (`solo` on bars); T50 (the bracket on bars); T44 (the ratio recipe); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the compare's then -> now two-key path in `lpBarMorphs`), `content/video_engine/scripts/species/compare.mjs` (synced by `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the `from` value's validation), `content/video_engine/effects/recipes/<new>.json` (two recipes), the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_bar_revalue.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: T26a's `lpBarMorphs` (the bar's height morphs on the compare's clock; `ghost=yes` keeps the old outline), `chart_to compare` (`CAPABILITIES.md:29`, `species/compare.mjs`), `recipe:emphasized-bar-lit`, `recipe:badge-ladder`. (1) A48: a bar's compare may run THEN -> NOW: the bar shrinks to its sourced old value, holds, then grows to today, a ghost dashed level at each top with its figure AT the bar top, never on the rule (C14); (2) R28 `recipe:revalue-then-the-ratio`: A48, then T50's bracket to its neighbour with the multiple written; (3) R30 `recipe:ranked-dim-the-rest`: a ranked field rises, holds ~1 s, ONE bar ignites while the rest dim (T37), a leader pill, then a second pill; (4) honesty: both states' values sourced (the old value's source named - the guide's don't, `:1062`); M26 holds at every instant of the morph; (5) byte-identical otherwise; one golden: the then -> now re-value at rest (row 16's 28 -> 150)
- Use when: `:1061` "H row 16's "28 → 121 → 150". Keep the figures at the bar tops (C14)"; `:1091` "then-and-now on one bar, then how 'now' compares with its neighbour"; `:215` "bars rise, hold ~1 s, ONE ignites while the rest dim, a leader pill, then a second pill". H row 16 (A48, R28) and row 18 (R30: the 20 bar against the 2-4 band)
- Regression: `python -m pytest content/video_engine/tests/test_bar_revalue.py -q`
- Expected RED: a compare with a `from` value is refused as an unknown key; neither recipe id exists
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --check`, `python -m pytest content/video_engine/tests/test_bar_revalue.py content/video_engine/tests/test_bar_value_morph.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T73: Fills to a level - the underwater fill, the fill below zero, the negative spike's glowing trough (harvest A45, A46, R29)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T39 (a level drawn from a datum, C14); T36; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `spread` to a level's paint), `content/video_engine/scripts/build_scene_timeline_f.py` (the `spread` level target's validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_fill_to_a_level.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: `page_species:spread` ("The region between two drawn series bleeds full of ink on a word"; on chart states, `CAPABILITIES.md:118`), T39's level_join, the dashed `ring` (A7, HAVE). (1) A45: a `spread` may fill between a series and a LEVEL taken from a named datum (the prior peak) forward until the series regains it - the stretch "underwater", its duration written ("11 years"), the level's figure at its datum, not on the rule (C14); (2) A46: a `spread` to the zero rule at a signed dip, in the sign's colour (E28); (3) R29 `recipe:the-glowing-trough`: the axes, the line draws, the fill below zero, a dashed ring on the trough, its record figure; (4) honesty: the fill's bounds are the true series and the true level; the duration is computed, never typed; (5) byte-identical otherwise; one golden: the underwater fill
- Use when: `:915` "a period spent below a prior peak is the claim ('lost decade')"; `:779` "a record low below zero"; `:833` "H row 22's "one soft month in June"". H row 9 (the railway index below its 1845 peak) - derived; row 22 (R29)
- Regression: `python -m pytest content/video_engine/tests/test_fill_to_a_level.py -q`
- Expected RED: a `spread` naming a datum level (not a second series) is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/build_effects_catalog.py --check`, `python -m pytest content/video_engine/tests/test_fill_to_a_level.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T74: The scale-out reveal and the projected overtake (harvest A50, A51, R31)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T41 (the projection's label and tier); T50 (the bracket on bars); T37; lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the projected bar's paint and the rank pill), `content/video_engine/scripts/ledger_page.py` (a bar datum's `projected` field and its check), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_scale_out_overtake.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: `species:pull_back` ("The hook holds on one large number, then one decelerating pull-back reveals..."), `chart_to:extend` (`CAPABILITIES.md:120`) and `rescale` (`:119`), `overflow:burst` (`CAPABILITIES.md:90`), `bracket`; the harvest (`:142`) says "the composition is unproven". (1) A50: one bar shown alone at its reading size, then on its word the axis widens (extend / rescale) to the whole field and its RANK lands as a pill ("18th largest"); (2) A51: a PROJECTED bar surges past the field to its forecast - drawn hatched or dashed as a projection, its label and tier written (E77, s93, C15) - and a bracket to #1 with the gap; (3) R31 `recipe:scale-out-then-the-overtake` composes (1) and (2); (4) honesty: the field is the true field (every bar sourced, the rank computed, not typed); an unlabelled projection is refused; (5) byte-identical otherwise; one golden: the projected bar's form
- Use when: `:1067` "one value shown alone first, then its place in the whole field"; `:853` "a sourced projection passes today's leader, labelled as a projection"; `:865` "one value alone, then its rank in the field, then the projection passing the leader". H row 18 (the 20 bar alone, then the field) and row 16 (the 690 consensus) - derived
- Regression: `python -m pytest content/video_engine/tests/test_scale_out_overtake.py -q`
- Expected RED: `projected` is an unknown bar field; the recipe id does not exist
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_scale_out_overtake.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T75: Lead and lag - the ring travels to the lagging peak, the lead-lag bracket across two series, the phase-shift slide (harvest A52, A53, A54)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T36 (a travelling light); T46 (the schematic wave A54 slides); T47 (rings in turn); T43b (two series on unlike scales need s102's conditions); lane B
- Write set: `content/video_engine/scripts/species/ring.mjs` (the travelling ring, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the bracket across two series; the schematic's slide), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/ring.test.mjs`, `content/video_engine/tests/test_lead_lag.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: `ring` (`CAPABILITIES.md:45`), `bracket` (`:118`), T46's schematic, T47's rings in turn; docs_find "lead-lag" hits only the BUB reference report (`content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/REPORT.md:104`). (1) A52: a ring lands on the leading peak, then TRAVELS along the path to the lagging peak on its word - motion under s99; (2) A53: a `bracket` may span two data on TWO series (their peaks), its label the measured lag ("1.5 years") - T46 carries the schematic's lag, this is the measured one; (3) A54: on a schematic (T46) one wave slides along x by its lag on the word, with no lag figure it cannot source (s109 (1)); (4) honesty: a measured lag is computed from the two data's x and written; two series on unlike scales need s102's conditions (T43b); (5) byte-identical otherwise; one golden: the travelling ring on row 9
- Use when: `:785` "the second peak answers the first (s99: a travelling light is motion)"; `:927` "one series leads another by a stated time"; `:651` "(s109 (1), C9 cleared) one indicator leads another by a fixed lag". H row 9 (the ring from the 2000 7 % crossing to the AI 8 % datum) and row 12 (the three manias' lag) - derived
- Regression: `python -m pytest content/video_engine/tests/test_lead_lag.py -q`
- Expected RED: a ring `to` target (a travel) is unknown; a bracket naming two series is refused
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_lead_lag.py content/video_engine/tests/test_rings_on_vertices.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

### T76: The line painter - the trace before the furniture, the line changing ink at a point, the white-hot core (harvest A41, A21, F18)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T8 (the `longform` profile); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (a `trace` page enter, the series' ink key, the two-layer stroke), `content/video_engine/scripts/ledger_page.py` (an `ink_from` series key and its check), `content/video_engine/scripts/build_scene_timeline_f.py` (the enter's validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_line_painter.py` (new), `content/video_engine/tests/golden/**` (one golden per new form)
- Acceptance: Find and REUSE first: the page enters (`page_enter:axes`, `recipe:hook-opens-on-the-axes`), R26-228's bloom (`CAPABILITIES.md:76`), E67's inks and `highlight_from` (`ledger_page.py:90` AXES_KEYS, a static relight); docs_find 0 capability hits for "white-hot" and for "trace first". (1) A41 `page_enter:trace`: the series draws on a bare ground FIRST, the title, axes and key landing after it; E73 still binds the hook (row 1 opens on its axes), so this is an option for a row whose SHAPE is the hook; (2) A21: a series may change ink at a named x on its word (`ink_from: {x, color}`) - a declared colour wins over the sign default only where it does not lie (E53 s7, E28); (3) F18: under `;readability=longform` the hero series draws as a two-layer stroke - a white-hot core over its hue body (the spec's (d) 6, `BRAVOS-LONGFORM-CHART-SPEC.md`), context series stay single; (4) byte-identical for rows that name none of it; one golden per new form (the trace-first entry, the ink change)
- Use when: `:349` "the SHAPE is the hook, before the viewer knows what it is"; `:343` "a regime changes at a named moment ("the call", "the peak")"; `:379` "the hero series of a page". H rows: none for A41 (E73 fixes row 1 on its axes); A21 row 9 (the railway line turning red after the peak on "crashed"); F18 the hero lines of rows 4, 9, 14 and 21
- Regression: `python -m pytest content/video_engine/tests/test_line_painter.py -q`
- Expected RED: `page_enter:trace` and `ink_from` are unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --check`, `python -m pytest content/video_engine/tests/test_line_painter.py content/video_engine/tests/test_longform_profile.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T77: Glow edges - a glow outline on a region or bar, a glowing perimeter on a headline card, the bevelled stamp slab (harvest F2, F14, F19)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T6b (the one stage light and its shadow); T10b (the bar's soft rect); T42 (`lit` - one light grammar); lane B
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the glow outline, the card perimeter, the slab's bevel and shadow), `content/video_engine/scripts/build_scene_timeline_f.py` (the options' validation), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/test_glow_edges.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: the burst's glow (`overflow:burst`, `CAPABILITIES.md:90`), `recipe:emphasized-bar-lit`, the press card (`CAPABILITIES.md:101`), the stamp arrival (`:79`) and T6b's resting shadow; docs_find 0 hits for "bevel" and for "stamp slab". (1) F2: a `glow` outline on a named bar or region on its word - a held glow is an annotation (0 events, s91), a blink is motion (s99), never the move when a thing should arrive (s71); (2) F14: a press or record card may carry a red glowing perimeter when the row names it an alarm - at most one per row (the guide's don't, `:142` "every card (the glow stops meaning anything)"); (3) F19: a stamped verdict word lands as a slab with a bevel and a drop shadow from the one stage light (T6b's dials); (4) byte-identical otherwise; one golden: the slab
- Use when: `:197` "the part the sentence names must read as lit, not just coloured"; `:141` "the headline is an alarm and the sentence turns on it"; `:809` "the verdict word needs weight (s92's resting shadow)". H rows 18 (the 20 bar lit), 16 (the leases filing), 22 ("The flip")
- Regression: `python -m pytest content/video_engine/tests/test_glow_edges.py -q`
- Expected RED: a `glow` species option, a card `perimeter` option and a stamp `slab` form are unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_glow_edges.py content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T78: The longform chrome finish - the key chip turns accent on `solo`, the two-line source, the title in an accent capsule (harvest S9, S10, S11)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T10 (badges as the key); T37 (`solo`); T26f (the chrome as objects); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (the longform source and title options), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the key chip's accent on solo, the two-line source, the title capsule), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/tests/test_longform_chrome.py` (new), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: T10's key rail and badges (`badges_for`, `ledger_page.py:1000`), T8's longform title / sub / source column, T26f's chrome layer; docs_find 0 capability hits for "two-line source", "legend chip" and "title capsule". (1) S9: when `solo` isolates a series, its key chip and end badge take the accent and the others mute with their series, on one clock; (2) S10: under longform the source foot may be two lines - "Date: …" / "Source: …" - wrapping inside the safe column, never into the caption strip; (3) S11: the title may sit in an accent capsule (`;title=capsule`); (4) every page without the options byte-identical; M28 (text on text) clean; no new form, so no golden - the parent reads the three off / on beside HG3's card
- Use when: STYLE items carry no guide entry (the guide covers types, actions, effects and recipes); from the harvest §5: S9 `BRAVOS-VOCABULARY-HARVEST-v2.md:239` "The legend chip turns accent when its series is isolated", S10 `:240` the two-line "Date: ... / Source: ..." foot, S11 `:241` "The chart title sits in an accent capsule". H rows: every longform page; S9 on row 22 (DRAM against HBM)
- Regression: `python -m pytest content/video_engine/tests/test_longform_chrome.py -q`
- Expected RED: a solo'd series' key chip keeps its own colour; the two-line source and `;title=capsule` are unknown
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_longform_chrome.py content/video_engine/tests/test_longform_profile.py content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T79: Labels - a category pill over axis-less story bars, logos as data labels, the bar ladder that ends on a membership bar (harvest S5, S6, R2)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T45 (the membership stack); T10 (the key rail keeps the names); lane B
- Write set: `content/video_engine/scripts/ledger_page.py` (the story builder's `axes: none` and a datum's `pill` and `logo` fields), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (their paint), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/scripts/measure_page_boxes.py`, `content/video_engine/effects/cards/<new>.json`, `content/video_engine/effects/recipes/<new>.json`, the catalogue's generated files via `build_effects_catalog.py --write`, `content/video_engine/tests/test_story_bar_labels.py` (new), `content/video_engine/tests/golden/**` (one new golden), `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: Find and REUSE first: the story bars builder (`ledger_page.py`, `story`), `recipe:badge-ladder`, T45's `members`, the cutout's alpha (T6d); docs_find 0 capability hits for "category pill" and for a logo label. (1) S5: an axis-less story bars page (2-4 bars; E99 s97 asks for the look) with a category pill over each bar and its value badge - the written values state the scale; the breakthrough's stated scale (`CAPABILITIES.md:90`) stays wherever a row names it; (2) S6: a series or a bar may carry a `logo` (a catalogued cutout, alpha kept) as its label at the line end or under the bar, its name kept in the key (logos only where the rights spec allows, `docs/content-video-engine/11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md` §4); (3) R2 `recipe:bar-ladder-to-membership`: then against now as badged bars, the NOW bar filled with its members (T45); (4) honesty: an axis-less page writes every value, and its bars stand from zero in true proportion; (5) byte-identical otherwise; one golden: the axis-less page with its category pills
- Use when: harvest `:235` "Story bars: no axis, a category pill" (s97 asks for it) and `:236` "Logos as data labels"; `:209` "then vs now, and the "now" bar is made of named members". H rows 14 and 19 (the breakthrough bars read as story bars), 16 (the 150 of the five borrowers, their logos)
- Regression: `python -m pytest content/video_engine/tests/test_story_bar_labels.py -q`
- Expected RED: `axes: none` is refused on a story page; a datum `logo` field is unknown; the recipe id does not exist
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_story_bar_labels.py content/video_engine/tests/test_membership_stack.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: pending

### T80: The camera - a pedestal down through the waterline, the magnifier lens (harvest A33, A57)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T26f (the camera free of the chrome); T44 (the hidden base / iceberg the pedestal reveals); lane B
- Write set: `content/video_engine/scripts/kinetics/camera.mjs` (the pedestal key, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `lens` species' paint), `content/video_engine/scripts/build_scene_timeline_f.py` (validation only), `content/video_engine/scripts/gate_motion_density.py` (the camera mirror, only if the pedestal changes what M14 reads), `content/video_engine/effects/cards/<new>.json`, `content/video_engine/tests/kinetics/camera.test.mjs`, `content/video_engine/tests/test_pedestal_and_lens.py` (new), `content/video_engine/tests/golden/**` (one new golden)
- Acceptance: Find and REUSE first: `kinetics/camera.mjs` (`CAPABILITIES.md:89`, one persistent 2D similarity), `focus_zoom`, the blur-zoom's magnify (`CAPABILITIES.md:71`); docs_find 0 hits for "pedestal". (1) A33: a camera key may PEDESTAL down (a pure vertical move of `look`) over a stage taller than the frame, on its word, after the build has settled (M14: never over a build) - T44's hidden base revealed below the waterline; (2) A57: a `lens` species - a circular magnifier over a named region of a long line, drawing that region at k x inside the circle while the rest stays at 1x; the lens resamples the same series and invents no values; (3) honesty: the pedestal and the lens change the view, never the data; the gate's camera mirror agrees (M14); (4) seek-safe; byte-identical otherwise; one golden: the lens
- Use when: `:491` "the stage is taller than the frame and the hidden part is below (P49's one camera)"; `:1105` "a small region of a long line must be read without losing the rest"; don't `:1106` "invent zoomed values". H row 16 ("another eight hundred and twenty-two billion in lease commitments", T44's hidden base) and row 22 ("one soft month in June" on the long customs line)
- Regression: `python -m pytest content/video_engine/tests/test_pedestal_and_lens.py -q`
- Expected RED: a camera `pedestal` key and the `lens` species are unknown
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_pedestal_and_lens.py content/video_engine/tests/test_camera_keeps_the_page.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py -q`, `node --test content/video_engine/tests/kinetics/*.test.mjs`
- Evidence: pending

## Verification

Run from the slice's worktree root, unpiped:

1. `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`
2. Per engine slice (T4, T6, T8, T9, T10, T12):
   - its Validate line;
   - `python content/video_engine/scripts/sync_kinetics.py --check`;
   - `python content/video_engine/scripts/measure_page_boxes.py --write`;
   - `python -m pytest content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`.
3. The pre-merge checklist, every merge:
   - `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py -q`;
   - `python content/video_engine/scripts/measure_page_boxes.py --check`.
4. After T6, after T12 and after T34: `python -m pytest content/video_engine/tests -q -x` and
   `node --test content/video_engine/tests/kinetics`, with the tails written to a file.
5. Body slices: the door, `self_watch.py`, `measure_frozen_frames.py`, `gate_motion_density.py`. T34 adds
   the floor, the lint, `recall_verify.py` and `run_script_gates.py --long`.
6. `python scripts/prp_status.py`.

## Evidence And Handoff

- **Each slice's Evidence line** holds the command, its verbatim tail, the artifact paths and the merge
  SHA. The parent re-runs the Validate before integrating; a summary is not evidence.
- **Frames are judged as frames:**
  - T5's stamp-plus-card frame;
  - T6's halving;
  - T11's off/on pages;
  - T12's golden pair;
  - T13's strips;
  - T23's prop 1;
  - every row's tiles beside build-f's.
- **Never in git:** `build-h*/**`, the proof dirs, `player.html`, the contact sheets, the reference
  frames, the take, the renders.
- **What commits:** the door, the proof door, `SHOT-TABLE-H.md`, `BEAT-PLAN-H.jsonl`,
  `CRITIC-REPORT-H.md`, the tests, the goldens, the page-box fixture, and one evidence series if it is
  authored.
- **Handoff out (parent):**
  - the four queue rows;
  - the rulings, as `E99 s??` at merge;
  - the states of rows R26-241, R26-247, R26-190, R26-230, R26-222 and R26-231;
  - P68's T6 routed here;
  - lane B's row closed when T12 merges.

## Decisions for the operator (still open after 2026-09-22)

1. **P69-HG1:** the chip's landing (`springPop` or the stamp), and whether the stamp's contact instant
   stays at 0.1542 s.
2. **P69-HG2:** does the first stamped prop (the Fed, row 15) read right, before five more are stamped?
3. **P69-HG3:** should the s90 page become the default for every 16:9 full-stage page? The body uses it
   per row either way.
4. **P69-HG4:** the body, read beside the reference.
5. **Not resolvable from disk:**
   - `ev-debt-issuance-v2`. If no primary source for "$121B 2025" is on disk, the page is PLAUSIBLE-tier
     (a secondary dossier line). The operator decides whether a PLAUSIBLE series may draw as a page, or
     the row stays a PNG card.
   - P68 HG3's open answers (caption size, voice, plate balance). They re-time the body later; they do
     not block it.
