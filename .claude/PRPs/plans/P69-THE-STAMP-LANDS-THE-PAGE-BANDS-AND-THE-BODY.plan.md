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
- Status: pending
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
- Evidence: pending

### T6c: A bar is narrow - the cap at a five-bar page's width (E99 s96)
- Status: pending
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
- Evidence: pending

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
- Status: pending
- Owner: implementation_luna
- Depends on: T6 merged; lane B created with its register row
- Write set: `content/video_engine/scripts/ledger_page.py` (`READABILITY_PROFILES`, `_validate_readability` `:244-270`, the profile's geometry), `content/video_engine/scripts/build_scene_timeline_f.py` (a `readability` entry in `PLATE_OPTS` `:112` and its stamp onto the page), `content/video_engine/scripts/measure_page_boxes.py` (representatives with the profile), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the profile's reads at `:7907-7910`, `:9192`, `:9254-9259`, `:9549`, extended to the other builders), `content/video_engine/tests/test_fed_chart_readability.py`, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: (1) `;readability=landscape-phone` on a ledger row opts that page in without editing the evidence object. The series-file field stays, and the row option wins. (2) The profile is legal on dense-line and on the builders the body's pages use (bars / `shares`, `story`, the checklist/record pages if they are ledger pages - T14's inventory names them). On any other builder it is refused by name. (3) B's roughly 12.5 px phone type is measured on each (s90: "over main's roughly 6.5 px"). (4) Absent the option, every page is byte-identical. (5) The fixture is re-measured; the goldens are byte-identical
- Regression: `python -m pytest content/video_engine/tests/test_fed_chart_readability.py -q -k "row_option or bars"`
- Expected RED: `;readability=` is an unknown plate option (refused by the `PLATE_OPTS` check); a bars page with the profile is refused with "only supported by the dense-line builder" (`ledger_page.py:257-258`)
- Validate: `python content/video_engine/scripts/measure_page_boxes.py --write` then `python -m pytest content/video_engine/tests/test_fed_chart_readability.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_golden_frames.py -q`
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
- Evidence: pending

### T9: s90 (b) - the three layout fixes the side-by-side found (lane B)
- Status: pending
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
- Status: pending
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
- Status: pending
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
- Evidence: pending

### T10c: A chart card is drawn for its own size - the whole card, bigger type, thicker lines (the operator, 2026-09-22)
- Status: pending
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
- Evidence: pending

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
- Status: pending
- Owner: implementation_luna
- Depends on: T17
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the ticket is `arrive: throw, mass: paper`; the page recasts under it (E64)
- Validate: the shared Validate
- Evidence: pending

### T19: Row 11 (1:44-2:10) - one slot, three records (Karp, Uber, the COO line)
- Status: pending
- Owner: implementation_luna
- Depends on: T18
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; each record takes the outgoing card's slot (s80); no world change
- Validate: the shared Validate
- Evidence: pending

### T20: Row 12 (2:10-2:30) - the trough already doing its job
- Status: pending
- Owner: implementation_luna
- Depends on: T19
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `ev-three-manias` as T14 named it (a card record, not a page); the peak-to-trough move carried by the card's own marker or a callout, named in the build notes
- Validate: the shared Validate
- Evidence: pending

### T21: Row 13 (2:30-2:45) - reset 1, the dip to 1849 (dip 2)
- Status: pending
- Owner: implementation_luna
- Depends on: T20
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; `use=reset` with Ken Burns alone; the anaphora in caption STAGE mode
- Validate: the shared Validate
- Evidence: pending

### T22: Row 14 (2:45-3:20) - the yardstick: dip 3, camera 2, the breakthrough bars
- Status: pending
- Owner: implementation_luna
- Depends on: T21
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; camera 2 on the 28 datum, tied to its landing (E51); the bars page states its scale
- Validate: the shared Validate
- Evidence: pending

### T23: Row 15 (3:20-4:06) - the trigger and the concession; PROP 1 the Fed, and P69-HG2
- Status: pending
- Owner: implementation_luna (the row); parent (the HG2 card)
- Depends on: T22
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`, `.../build-h-frozen-prop1/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: the shared body rules; prop 1 `prop-federal-reserve-building-v1` as `prop: True, arrive: "stamp"` on "The Fed at six and a half" - the compiler's `stamp:` line, its cue (`landing N (stamp, ink)` or the named mass), its gate event, its exit with the page (R26-219); the concession on the same page (no bare plate 2:45-6:04); the parent freezes the row and writes P69-HG2 with enter/contact/rest frames
- Validate: the shared Validate, then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T24: Row 16 (4:06-5:25) - who is paying; PROP 2 beside the leases record
- Status: pending
- Owner: implementation_luna
- Depends on: T23, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the debt issuance beat as T14 settled it; `ev-ig-credit-weighting-v1` and `ev-capex-consensus-v1` recasts (E58); prop 2 `prop-hyperscale-datacenter-v1` stamped first with the `ev-doc-leases` record placed around it (T5), 0 px overlap, the parent's frame read
- Validate: the shared Validate
- Evidence: pending

### T25: Row 17 (5:25-6:04) - the arithmetic: the 94 bar with its figure
- Status: pending
- Owner: implementation_luna
- Depends on: T24
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the 94 figure paints on the bars page (T6); the PIMCO record in the slot
- Validate: the shared Validate
- Evidence: pending

### T26: Row 18 (6:04-7:13) - the turn: reset 2, PROP 3, camera 3, the halving compare
- Status: pending
- Owner: implementation_luna
- Depends on: T25, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; dips 4 and 5 at world changes; prop 3 `prop-tech-sp500-concentration-v1` with camera 3 on the 20 datum tied to the stamp's contact (E51); the `chart_to compare` halving on the bars page, built on R26-190 (T6); the certificate ring on its figure (E56)
- Validate: the shared Validate
- Evidence: pending

### T27: Row 19 (7:13-7:52) - skips a gear: the breakthrough bars 20 years vs 5
- Status: pending
- Owner: implementation_luna
- Depends on: T26
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the `sold out` pill; two callouts, one per bar
- Validate: the shared Validate
- Evidence: pending

### T28: Row 20 (7:52-9:04) - host window 2: the desk, the checklist, dip 6, the returning page
- Status: pending
- Owner: implementation_luna
- Depends on: T27
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the checklist lands row by row; the divergence page returns unwound from its point (E40 s4), never redrawn
- Validate: the shared Validate
- Evidence: pending

### T29: Row 21 (9:04-10:18) - SK hynix: camera 4, PROPS 4 and 5, the wafer compare
- Status: pending
- Owner: implementation_luna
- Depends on: T28, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; camera 4 on the hynix tip; props 4 (`prop-hbm-stacked-die-v1`) and 5 (`prop-silicon-wafer-semiconductor-v1`) stamped on their words; the 1 vs 3 `chart_to compare` on R26-190 (T6); the checklist ticks
- Validate: the shared Validate
- Evidence: pending

### T30: Row 22 (10:18-11:33) - the tripwires: PROP 6, the customs monitor, the trim proof
- Status: pending
- Owner: implementation_luna
- Depends on: T29, P69-HG2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; prop 6 `prop-dram-memory-module-v1` on "the RAM inside every one of these data centers"; the monitor cites its release in the strip (E52); the June datum ringed
- Validate: the shared Validate
- Evidence: pending

### T31: Row 23 (11:33-13:00) - the ring: reset 3, host window 3, dips 7-9
- Status: pending
- Owner: implementation_luna
- Depends on: T30
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`
- Acceptance: the shared body rules; the certificate thrown onto the reset and ringed; the memory-arithmetic bars and the weight check; the newsroom with the weight-check card thrown onto its desk
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
- Status: pending
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
- Evidence: pending

### T35b: The Bravos candidates - new chart verbs from the harvest, each proved as a body beat (E99 s97)
- Status: pending
- Owner: implementation_luna (lane B for engine verbs; lane A for recipes and the beats)
- Depends on: T8-T10 (the `longform` profile the verbs are drawn in); the eight new watches (docs/research/runs/bravos-watch/, Gemini x4 + GPT x4) merged into the harvest first
- Write set: `content/video_engine/scripts/species/*.mjs` (new verbs only, synced), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (their paint), `content/video_engine/scripts/build_scene_timeline_f.py` (their tokens' validation), `content/video_engine/effects/cards/*.json` + `content/video_engine/effects/recipes/*.json` (new only), their tests and goldens, `content/video_engine/assets/page-boxes.v1.json`
- Acceptance: the harvest `docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST.md` (106 items; HAVE 55 / PARTIAL 25 / MISSING 26) names ten candidates; build the ones that need no ruling, each as a card + a recipe that composes existing cards (s70) + a golden + a body row that carries it: `level_join` (a dashed rule between two points, a ring at each end - rows 14/15/21), `axis_tag` (the named year as an accent pill on the x-axis - rows 9/15/22), `project` (the line continues dashed past its last real point - rows 16/17/23, labelled as a projection, E77), chip `lit` / `tick` states (rows 10/22), `chapter_tag` (a section pill held over an act's charts - rows 13/18/23), `the-hidden-base` (bars hanging below a waterline - row 16's leases; E53-safe), `loop` (a flow laid as a ring with money moving on its arrows - rows 16-18), `term-over-the-parked-chart` (rows 16/18). CLEARED 2026-09-23: `lit_stretch` as a TRAVELLING or blinking light, and the freeze-on-light beat (E99 s99); `blur-under-the-dock` for a busy chart plate, as a row option (E99 s98). PROPOSED to the operator (P69-HG3): a MEMBERSHIP-STACK exception to E53 s2 (the bar is ONE value; its tiles are equal, unvalued identities - who is in it - and the total is written; never a stack of values), and a CENSUS exception for the pyramid under E53 s1's treemap amendment (every cell's value written, the claim surface-vs-hidden, a size claim in the same beat takes its bar). STILL HELD: an INVERTED axis (E28 - a rise would draw as a fall; a second axis alone is allowed as E53 s4's overlay), rings on every point (E56), shape-only waves with no data (E52; never fabricated)
- Regression: `python content/video_engine/scripts/effects_catalog_check.py` (each new id absent before)
- Expected RED: none of the candidate ids exists in `effects/cards` / `effects/recipes` / the species list
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`, `python content/video_engine/scripts/measure_page_boxes.py --write`, `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_effects_catalog_drift.py -q`, and each verb's own test
- Frame acceptance: the parent reads each verb in its body beat beside the Bravos frame it was harvested from
- Red evidence: pending
- Green evidence: pending
- Refactor evidence: pending
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
