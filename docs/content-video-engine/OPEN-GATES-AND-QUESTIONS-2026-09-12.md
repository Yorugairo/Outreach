# Open gates and open questions - 2026-09-12

Everything waiting on a decision after P52 THE SWEEP, in one place. Written because the gates and the questions
were scattered across a plan's status block, eight BACKLOG rows and a session's messages, and a decision nobody can
find is not a decision waiting - it is a decision lost.

- **Head**: 290a481, `main`, pushed. P52 is `status: complete` (`.claude/PRPs/plans/P52-THE-SWEEP.plan.md`).
- **Nothing here blocks a build.** Every gate's subject is built; the gates rule on form, not on whether it works.
- **The paths** are on the session's machine, under the main checkout
  (`C:/Users/Snipe/Downloads/Outreach Program`). The private build dirs (`build-short-t10`, `-t16`, `-t17`) are
  gitignored and stand where they were built. **A served review copy is never rebuilt** - these are frozen.
- Source of record for each item stays its own row; this page points at it and never restates the ruling.

---

## Part 1 - The seven human gates (all built, all framed, none ruled)

Plan section: `.claude/PRPs/plans/P52-THE-SWEEP.plan.md:146`.
Frame paths below are relative to `content/video_engine/tests/golden/frames/` unless the line says otherwise.

### Gate 1 - The band's strip law (T6, the newsreel band)

| | |
| :--- | :--- |
| Open | `newsreel-band.png` (16:9, a head docked above the crawl), `newsreel-strip-9x16.png`, `newsreel-strip-above.png` |
| The decision | On a 9:16 strip, does the caption keep its E62 band ABOVE the crawl, or does the band yield the strip to the crawl and the caption sit under it? |
| Shipping now | The first: caption keeps the band, crawl below. `newsreel-strip-above.png` is the alternative (`cap_band: "above"`). |
| What it changes | The module's default and the strip law every later newsreel inherits. |
| Also in this frame | The head docks as a FRAMED CARD, which is R26-59, not this gate. Read the strip law past the frame. |

### Gate 2 - The melt's four instants and its dials (T9)

| | |
| :--- | :--- |
| Open | `melt-page@proof-015.png`, `@proof-045`, `@proof-075`, `@proof-100`, and `melt-splash.png` |
| The decision | Is the chain right at those four instants - the polygon, the threshold, the blob on 2s, the throw or splash - before the melt is offered to any cut? |
| The dials | `MELT` in `content/video_engine/scripts/species/melt.mjs` |
| Tied to | R26-60: a page under a melt must declare `:cut` or the melt drips a blank sheet. |

### Gate 3 - The three species on one proof page (T7, T8)

| | |
| :--- | :--- |
| Open | `species-proof@proof-count.png` (22.5 s), `@proof-agenda.png` (28.5 s), `@proof-ring.png` (12.6 s); in motion on the `species-proof` surface |
| The decision | The count array, the numbered agenda, and the ring's dashed-ellipse form with its flag chip - are these the forms, as frames and then in motion? |
| Note | The ring obeys E56: it circles a number or a point on a chart only, compiler-gated. |

### Gate 4 - The stagger against the pop (T10)

| | |
| :--- | :--- |
| Open | `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-t10/proof/GATE4-SHEET.png` - pop / control / stagger at 25.23, 25.33, 25.43 s, plus the nine single frames beside it |
| The decision | Which caption arrival ships, by eye and by ear. |
| The dials | `DUR_S` 0.34 (the stagger envelope) and the pop's 0.05 s anticipation. |
| Constraint | A private build dir, never a render. Tokyo is the test bed. |

### Gate 5 - The race A/B (T17)

| | |
| :--- | :--- |
| Open | `.../tokyo-tea-break/build-short-t17/proof/race-strip.png` plus twelve paired frames (`race-A-*.png` / `race-B-*.png` at 5.7, 6.3, 6.9, 7.5, 8.7, 9.9 s) |
| The decision | Does the race adopt the clothoid fitter, or does the choppiness get fixed on the clock? |
| What the measurement says | TIMING, not curvature. Every mark stops at every period because each segment eases with smoothstep. The fitter is NOT adopted in the build; the lever is the clock. |
| So the gate is | Confirm that reading, or overrule it after looking at the pairs. |

### Gate 6 - The publish folder's first use (T16)

| | |
| :--- | :--- |
| Open | the folder `.../tokyo-tea-break/build-short-t16/publish/` - `CHECKLIST.md` first, then `DESCRIPTION-YOUTUBE.md`, `DESCRIPTION-FACEBOOK.md`, `PINNED-COMMENT.md`, `SOURCES.md`, `TAGS.txt`, `MANIFEST.json`, `first-frame.png` |
| The decision | Is this what a posting pass actually needs, on the next short? |

### Gate 7 - The press card's face (T18)

| | |
| :--- | :--- |
| Open | `press-stack.png` (house, the default), `press-stack@face-serif.png`, `press-stack@face-condensed.png` |
| The decision | Which display face the press card wears as its stand-in. |

### Gate 8 - Push authorization

**Granted**, standing for 2026-09-12. Every commit of the sweep is pushed. Not a read.

---

## Part 2 - Open rulings that are not gates

1. **Does a DOCK's own landing license a transient cue inside 0:05-0:12?** M29 as built reads E44 2a literally:
   only a PAGE landing licenses a transient cue in that window. A dock that lands is not a page. If the ruling is
   that a dock's landing counts, M29 widens and the check moves with it. Found by P52 T13.
2. **R26-59 - the head above the band is a framed card, not a cutout**
   (`docs/content-video-engine/BACKLOG.md:464`). Every dock renders inside the template's card frame; a head cutout
   wants no frame and no paper. Wants a `cutout` dock kind, or the occluder's `fg:` route from P50 T15. Two smaller
   halves ride with it: `centred_place` does not yet take the band's `reserve`, and `cap_band: "above"` only moves
   the caption where E62 wrote a band on a dock entry.
3. **R26-60 - authoring rule, or compiler stamp?** (`BACKLOG.md:465`) A ledger page under a `suck` or a `melt` must
   declare `:cut` or it retracts itself first and the transition takes a blank sheet. Today it is an authoring rule.
   The compiler could stamp it: when a scene's next exit is `suck` or `melt`, the page's own exit defaults to `cut`
   and says so.
4. **R26-64, decision one - `STOP.IMPACT_S`** (`BACKLOG.md:469`). Superseded, not missing. Its note claims the
   impact squash's speed-driven part decays over two frames, and that decay IS implemented - by the material, not by
   a time constant: `impactSquash` counts frames off the stepped clock and scales `IMPACT_SQUASH` by
   `1 - (f - 1) / squash_frames`, paper 1 frame, liquid 2, metal 0
   (`content/video_engine/scripts/kinetics/stopaction.mjs:102`). What makes a throw land harder is `IMPACT_SQUASH`,
   the material's `impact`, `DIP_PX`, `SHAKE_PX`, `squash_frames` and `e`. **Delete `IMPACT_S`
   (`stopaction.mjs:51`), or state in its place why a time decay should return.**
5. **R26-64, decision two - `CADENCE.STROBE_PX_S`** (`stopaction.mjs:26`). A ceiling with no enforcer: `cadence()`
   consults only `ON1_PX_S` 250 (`stopaction.mjs:77`), so anything over 300 px/s is already on 1s and the threshold
   can never bind on the helper's own choice. It binds where a cadence is DECLARED against the speed - a
   `break_cadence: "stop"` burst, a boil on 3s, an authored hold - and nothing checks that case, with P50 T13's own
   burst at 359 px/s. **This is a gate row to write: a thing stepping on 2s or 3s faster than `STROBE_PX_S` strobes
   and must go on 1s.**

---

## Part 3 - Open measurements (no ruling needed, someone has to run them)

1. **R26-57 - the stage-space text at default `text-rendering`** (`BACKLOG.md:470`). R26-48's cure covers the page's
   glyphs; `#species .lab`, `.chiplab`, `.flowtag`, `.vmstamp` and the chartbox tier write SVG text at `auto` and
   carry the same latent warm/cold defect, unmeasured because Tokyo exercises none of them. Measure on the first
   build that does (a chip board, a flow diagram, a map), widen the rule in that commit, regenerate the goldens it
   moves on purpose.
2. **R26-58 - a thrown dock's flight differs warm versus cold** (`BACKLOG.md:463`). At Tokyo 75.79 the contact
   shadow sits 1390 px apart between a walked page and a cold seek while every text box is identical. The flight law
   is a pure function of t, so the cure is in the dock loop's contact placement, not the throw. Reproduce with
   `determinism_check.py build-short-t4 --instants 75.79` and `px_diff.py`.
3. **`ON1_PX_S` 250 against the brief's own 100 px/s** (E2 7). Neither number is measured on our own motion. Do
   that before either is trusted. Rides with R26-64.

---

## Part 4 - Settled in the sweep, listed so nothing reads as missing

| Row | Disposition |
| :--- | :--- |
| **R26-61** the rig's bibliography (`BACKLOG.md:466`) | **Deferred with a trigger**, on the operator's word 2026-09-12. The trigger: the first short that asks a figure to gesture, bend or hold weight. Until then the row IS the disposition. |
| **R26-62** the ground's physics and the transform chain (`BACKLOG.md:467`) | **Tracked** where our own rows already bound them - E22 and 44 44.3's JUDGE row for the wicking, P42 / 43 43.3 / A6 for the transform stack. Deprioritised, not open. |
| **R26-63** the four the triage withdrew (`BACKLOG.md:468`) | **WITHDRAWN 2026-09-12** - the 2026-09-05 triage's own verdict, finally executed. |
| The animation registry's orphan bucket | **0 records.** 812 records, 535 implemented, 87 tracked, 14 retired. Five classifier defects fixed; the region parse now agrees with `sync_kinetics.REGION` exactly. |

**The rule that came out of it:** a triage verdict is not real until a row carries it verbatim. The 2026-09-05
triage had ruled on all 20 orphaned names and nobody wrote the rows, so the registry read them as unattached
findings for a week and the capability count was wrong in both directions.

---

## Part 5 - Known defects and loose ends

1. **One known red, pre-existing**: `test_measure_motion_energy::test_headless_sampling_returns_stage_elements_smoke`
   runs against the stale single-file `build-short/player.html`. Not caused by the sweep, and that build is a frozen
   review copy, so the fix is the test's target, not a rebuild.
2. **The plan's `updated:` line says 2026-09-13** while the commit clock says 09-12
   (`.claude/PRPs/plans/P52-THE-SWEEP.plan.md:10`). A one-line correction nobody has made.
3. **A bridge reply is waiting**: `f4541f7f6808`, a review of "The Myth of Historical Normal" returning REQUEST
   CHANGES. Unread as of this page.
