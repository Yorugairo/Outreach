---
id: P43-KINETICS-WAVE-2
title: Kinetics wave 2 - the curvature stroke, Kubelka-Munk ink, area squash, and the rest of the spring
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-05
updated: 2026-09-05
---

# Kinetics Wave 2

## Summary

> **Approved 2026-09-05** by the operator ("proceed with P43"), marked running the same day. **In review 2026-09-05:** T1, T4, T5, T6 complete; T2 and T3 landed flag-off and wait on their human gates (the before/after strips sent) - **COMPLETE 2026-09-05:** the operator ruled both gates in motion - the stroke ON (from the side-by-side clip), K-M ink OFF for the soak after six rounds (kept behind its flag for ink over ink; the soak's next step is a plate reveal, BACKLOG 9). Standing: M16's one FAIL at 1:20 (the outro) is unchanged and is not this plan's.

The operator's pick from the 2026-09-05 backlog read: **items 1, 6, 7 and 8** of the
ready-to-pull-in list in [BACKLOG](../../../docs/content-video-engine/BACKLOG.md) -
the curvature-reparameterised stroke, Kubelka-Munk compositing on overlapping ink,
area-preserving squash as a shared helper, and the remaining damping cases of the spring.

This plan takes P38's T1-T4 (the testability unlock, the stroke, the spring, the squash)
and adds G-h (K-M, [44 §44.1](../../../docs/content-video-engine/44-INK-AND-SURFACE.md)).
P38 keeps T5-T8 (ARAP, the object page, DQS, prop attachment), which wait on an object page
that no build yet has. What changed since P38 was drafted, and why this is wave 2:

- the flags exist and are read from `timeline.kinetics`; the compiler writes them from an
  override and the Tokyo short turns `analytic_spring` and `min_jerk` on (2026-09-05)
- `springPop` (the underdamped case with the M_p inverse) and `minJerk` are inline in the
  template behind those flags and shipping on the short's pops, wipe and suck
- the vortex already uses the det=1 squash form by hand - the helper is a lift, not a design
- the stain soak's overlaps read as a patchwork of greys: **that is the K-M defect, visible
  on a page we ship**
- the template's math is closure-scoped: a probe from playwright cannot reach it, and there
  is still no test path to it (P38 T1's finding, confirmed by hand 2026-09-05)

## Intent And Acceptance

**Intent.** Four pure-math capabilities land in a node-testable module, each behind its
kinetics flag, each shown failing against the current implementation first, then wired
into the template with the flag off by default so every old build and all four goldens
render byte-identical. The Tokyo short turns each one on as it lands.

**Acceptance:**

1. A stroke drawn over a path with one sharp corner and one long straight satisfies
   `v(max κ) < v(min κ)` and `w(max κ) > w(min κ)`; a straight path returns finite `v`;
   the stroke starts and ends at rest. The current `spEase`-driven `drawOn` fails the
   first two. The callout ring, the phone trace, the squiggle and the line builds route
   through it when `kin("curvature_stroke")`.
2. Two overlapping ink strokes composite by K-M when `kin("km_ink")`: the overlap is
   **darker and more saturated** than either stroke, never the desaturated grey alpha gives.
   Test: the K-M reflectance of ink over ink is below the alpha result and its chroma is
   not below the single stroke's. The soak's overlapping stains and the highlighter species
   are the first callers.
3. `det(A(t)) == 1` within float tolerance for the squash tensor across a sweep of t and α,
   including α → 0 and large α; α is driven by speed and deceleration (42 §42.3). The
   vortex's inline stretch is replaced by the helper with no visual change at the flag's
   current setting.
4. The spring evaluator returns position **and velocity** in all three damping regimes;
   frame N evaluated directly equals frames 0..N stepped, bit-identical (the seek test);
   the measured peak overshoot matches `M_p = exp(−πζ/√(1−ζ²))` at `t_p = π/ω_d`; `ζ = 1`
   overshoots zero. `springPop` becomes a thin caller of it.
5. Every flag still defaults to `false`; `render_baseline.py --check` passes on the four
   goldens with the flags off; a flag-ON golden is captured beside each for the one page
   that shows the change.
6. The Tokyo short rebuilds with all four on, the motion gate stays green (M16 included),
   and the operator sees a before/after on one ledger page and the callout ring before the
   stroke lands (the human gate below).

## Scope

- `content/video_engine/scripts/kinetics/` - `stroke.mjs`, `spring.mjs`, `squash.mjs`,
  `ink.mjs` (K-M), each a pure module with its doc section in the docstring
- `content/video_engine/scripts/sync_kinetics.py` - inlines each module into the template
  between `/* KINETICS:BEGIN <name> */` and `/* KINETICS:END */` markers; `--check` fails
  when the inlined copy drifts from the module (P38 T1's design, unchanged)
- `content/video_engine/tests/kinetics/*.test.mjs` (node --test) and
  `content/video_engine/tests/test_kinetics_sync.py`
- the template's `drawOn`, the badge / caption pops, the vortex stretch, the soak's blob
  compositing and the highlighter - each wrapped in `if (kin(...))` with the old path as
  the else branch
- `KINETICS_DEFAULTS` gains `km_ink: false`; `test_kinetics_flags.py` pins the new name
- the compiler's `KINETICS` override and `build_short.py` turn the four on for Tokyo
- doc 47 §5b and CAPABILITIES rows for each capability as it lands

## Not Building

- ARAP / polar-decomposition morph, the object page, `object -> chart` (P38 T5-T6)
- DQS skinning and prop attachment (P38 T7-T8)
- the coffee-ring rim and Darcy wicking (44 §44.2-44.3) - ink surface, a later wave
- Euler-spiral procedural curves (finding build order 6)
- any change to the wipe / suck / vortex timing beyond replacing inline math with the
  shared helpers at identical output

## Human Gates

| gate | why |
|---|---|
| **T2 before merge** | The stroke changes how every drawn object in the engine looks. Operator sees a before/after on one ledger page and the callout ring first. |
| **T3 on the stain soak** | K-M darkens overlaps; the operator ruled the soak's look on 2026-09-05 ("splotchy, staining like coffee"). A before/after of the bleed at 0:19-0:21 before it lands. |
| flags on the short | each capability is turned on for Tokyo only after its own golden with the flag ON is captured and looked at |

## Mandatory Reads

- [FINDING-the-animation-math-and-what-it-changes](../../../docs/content-video-engine/FINDING-the-animation-math-and-what-it-changes.md) §1-§4 and the build order
- [42-DRAWING-KINETICS](../../../docs/content-video-engine/42-DRAWING-KINETICS.md) §42.1-§42.3, §42.5 (what is ours to tune)
- [44-INK-AND-SURFACE](../../../docs/content-video-engine/44-INK-AND-SURFACE.md) §44.1
- [47-FINDINGS-TO-CHECKS](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) §1 (the tests that fail without each item), §5b
- [P38](P38-KINETICS-CAPABILITY-LAYER.plan.md) T1-T4 as drafted; [P39](P39-RENDER-BASELINE-AND-KILL-SWITCH.plan.md) for the goldens and the flag contract
- `docs/content-video-engine/samples/scene-evidence-player.template.html`: `KINETICS_DEFAULTS`, `kin()`, `drawOn`, `springPop`, `minJerk`, `lpVortex` (the inline stretch), the soak's `goo` group
- `docs/portable/OPERATOR-RULINGS.md` E22 (the ledger page), E40 (2026-09-05)

## Execution Path

| slice | route | why |
|---|---|---|
| T1 | **parent** | the assembly decision: modules inlined at generation, the template stays standalone |
| T2 | **parent** | the largest visual change; human gate attached |
| T3 | **parent** | changes a page the operator ruled on today; human gate attached |
| T4, T5 | `implementation_luna` | bounded math with exact acceptance and node tests |
| T6 | **parent** | wiring, goldens, the short, docs |

T2-T5 write disjoint files and may run in parallel once T1 lands. T6 is last.

## Patterns To Mirror

- `content/video_engine/editor/fixtures/editorial-motion-two-shot/render.mjs` - `.mjs`
  and `node --test` are already normal here; zero new dependencies
- `build_scene_timeline_f.py` reads the template and emits a per-build player; the sync
  step lands beside that, never a new build stage
- `gate_motion_density.py`'s `SRC_*` constants - every behaviour names its doc section
- `render_baseline.py --check` - the goldens are the regression test for every template
  change; the 2026-09-05 work landed five template changes with all four goldens byte-identical, twice catching a sub-pixel drift (an inline transform cleared on an idle element; a layout read mid-paint). Idle frames touch nothing.
- `springPop` / `minJerk` in the template - the shape of a flag-guarded helper with the old path as the else branch

## Task Slices

### T1: the testability unlock - modules inlined into the template
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/kinetics/` (new), `content/video_engine/scripts/sync_kinetics.py`, `content/video_engine/tests/test_kinetics_sync.py`, the template (markers only, plus `springPop` / `minJerk` moved into `spring.mjs` / `ease.mjs` at identical output)
- Acceptance: each module is the source of truth; `sync_kinetics.py` inlines it between `/* KINETICS:BEGIN <name> */` and `/* KINETICS:END */`; `--check` fails on drift; the template still opens standalone; the four goldens are byte-identical after the move.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check && python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_kinetics_flags.py -q && python content/video_engine/scripts/render_baseline.py --check`
- Evidence: 2026-09-05 - `kinetics/ease.mjs` (minJerk) and `kinetics/spring.mjs` (springPop) are the sources; `sync_kinetics.py --write` inlined both (`in sync (2 module(s))`); `--check` proven to fail on a one-character drift, a missing region, an orphan module and a wrong import order (`test_kinetics_sync.py`, 8 tests); `test_kinetics_flags.py` 4 pass; `node --test tests/kinetics/{ease,spring}.test.mjs` 6 pass (the first test that reaches the template's math; minJerk's rest-at-both-ends vs the quadratic io's a(0)=4, springPop's peak = 1+Mp at pi/wd); `render_baseline.py --check`: PASS 4 golden frames identical. Deviation: minJerk's inline clamp is `Math.min(1, Math.max(0, u))` instead of the template's `clamp01` so the module is self-contained - numerically identical.

### T2: the curvature-reparameterised stroke
- Status: complete - HUMAN GATE RULED 2026-09-05 from the side-by-side clip `t2-stroke-side-by-side.mp4` (the holdings page's line build + focus ring, the phone trace; OFF left, ON right, 30 fps): 'curvature stroke should be on'. `curvature_stroke` ON in `build_short.py`; the short rebuilt (player kinetics: analytic_spring, min_jerk, area_squash, curvature_stroke; km_ink off)
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/stroke.mjs`, `content/video_engine/tests/kinetics/stroke.test.mjs`, the template's `drawOn` (flag `curvature_stroke`)
- Acceptance: `v(s) = γ·(|κ(s)| + κ₀)^(−1/3)·ψ(s)`, inverted to `s(t)` by Newton-Raphson, width and ink density coupled to the same profile (42 §42.1). Tests: a path with one corner and one straight gives `v(max κ) < v(min κ)` and `w(max κ) > w(min κ)`; a straight path returns finite `v`; the endpoints start and end at rest. The current `spEase` path fails the first two. `drawOn` samples κ from the path's own geometry (`getPointAtLength` at three offsets), so every caller inherits it. Human gate: before/after on one ledger page and the callout ring.
- Validate: `node --test content/video_engine/tests/kinetics/stroke.test.mjs && python content/video_engine/scripts/render_baseline.py --check`
- Evidence: 2026-09-05 - `kinetics/stroke.mjs` (menger curvature, `strokeProfile` = kappa / v / w / t(s) table, `strokeS` = the quintic clock then the inverse of t(s), `strokeAt`); `stroke.test.mjs` 7 tests pass incl. the FAILING case as a test (the sliding mask `len*spEase(k)` is faster in the corner than on the straight after it; the hand is slower); v(min k)/v(max k) > 2 on a radius-6 corner; straight path finite and linear; rest at both ends; lands on exactly L. Template: `strokeProf` (profile cache keyed by d) + `strokeFrac` (null when the flag is off) wired at SIX draw sites - `drawOn` (callout ring, squiggle, trace), the dock chart lines, the ledger decline line, the combo lines, the page's sketch strokes, the dense-line paths - each keeping its own ease as the else branch. `render_baseline.py --check`: PASS 4 golden frames identical (flag off). Human-gate strips: `t2-stroke-chart-callout.png`, `t2-stroke-ledger-page-mid-build.png` (equal time steps, OFF over ON) sent to the operator. Deviations: (1) psi(s) is realised on the clock as the min-jerk quintic rather than a spatial ramp - a spatial envelope that reaches zero makes t(s) diverge, and the quintic IS Flash & Hogan's rest-to-rest solution; (2) width/ink coupling is computed and tested in the module (`prof.w`) but not yet applied in the template - SVG stroke-width is per element, so nib pooling needs a segmented stroke; a decision for the human gate, not a silent change.

### T3: Kubelka-Munk on overlapping ink
- Status: complete - HUMAN GATE RULED 2026-09-05 after six rounds in motion: 'in a way our original applications were better, with the ink pooling/blotchiness ... the ideal feeling is that we actually paint it with ink. The fade in from cream to the ink surface has still been one of our best variants' -> 'turn ink off'. `km_ink` OFF for the short (the alpha soak ships); the module, the filter and the flag stay for ink over ink (a ring over a bar, the highlighter); the soak's next step is a PLATE REVEAL (image-generated ink on cream revealed by the stepped stains as a mask) - BACKLOG
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/ink.mjs`, `content/video_engine/tests/kinetics/ink.test.mjs`, the template's soak `goo` group and the highlighter species (flag `km_ink`), `KINETICS_DEFAULTS`, `test_kinetics_flags.py`
- Acceptance: a two-flux K-M composite for pigment over pigment (K absorption, S scattering per ink token; the charcoal and the highlighter each declare theirs) replacing alpha where two ink passes overlap. Tests: ink over ink is darker than alpha's result and no less saturated than one stroke; ink over bare paper equals the single stroke; K = 0 reduces to the paper. In the template the soak's stains composite through it (SVG `feComposite` arithmetic / a `mix-blend-mode` derived from the K-M curve, whichever reproduces the module within tolerance on a rendered probe - the module is the truth, the CSS is its approximation and the test says how close). Human gate: the bleed at 0:19-0:21 before and after.
- Validate: `node --test content/video_engine/tests/kinetics/ink.test.mjs && python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_kinetics_km_probe.py -q && python content/video_engine/scripts/render_baseline.py --check`
- Evidence: 2026-09-05 - `kinetics/ink.mjs`: the two-flux layer (`kmChannel`/`kmLayer`, K/S from R_inf by the K-M inversion), `kmStack`, `alphaOver` (the wrong operator, kept as the else branch), `kmHex`, `kmTable` + `kmFilterMarkup` (coverage -> sRGB per channel). `ink.test.mjs` 6 pass: ink over ink darker by K-M than by a calibrated film for five inks x five thicknesses; layers of one ink compose exactly (X1 over X2 = X1+X2, 1e-9); zero thickness = paper, infinite = R_inf, K=0 never darkens; sunflower over charcoal goes olive/darker where a film goes tan; the table runs cream -> exactly the ink at one full stain, monotone. RENDERED PROBE `test_kinetics_km_probe.py` PASSES: the inlined module's filter (white stains summed by mix-blend-mode plus-lighter, alpha moved to RGB, per-channel table) reproduces the module within 3/255 on single / overlap / bare paper. Template: flag `km_ink` (8th, `test_kinetics_flags.py` pinned), the soak filter (sRGB tables after displacement+blur), stains white + plus-lighter, opacity = coverage, the checklist highlighter band = `kmHex(#16181c, colour, INK.HIGHLIGHT_X)` at opacity 1. Goldens: PASS 4 identical (flag off). Gate strip `t3-km-ink-tokyo-soak.png` (OFF / S1 0.05 / S1 0.2) rendered from the shipped Tokyo player's data. Deviations: (1) 'more saturated than either stroke' is FALSE as RGB chroma for thin layers of one ink - what K-M gives is deepening and a subtractive hue; the tests state that; (2) the plan's 'K = 0 reduces to the paper' holds only at zero thickness (a non-absorbing scattering layer brightens) - tested as 'never darkens'; (3) a thin charcoal wash goes blue-grey under K-M (its blue channel absorbs least) - physically sumi-like, visually a decision for the gate; S1 is the dial (0.05 two-tone wash, 0.2 dense ink). GATE ROUND 2 (operator, 2026-09-05: 'i do like the kubelka-munk, i think i just wish it was more erratic ... the variance spread throughout, almost like a mesh with some spots having higher attraction than others'): the K-M soak now grows through an ATTRACTION FIELD - `SOAK` dials + `soakFilterMarkup` / `soakGradientMarkup` in ink.mjs; stains are soft radial coverage, the summed coverage is multiplied by (base + gain x a turbulence mesh) before the K-M stage, so high-attraction spots ink first, the front travels the ridges, dry holes fill late. Default dials = the coarser field (0.008 0.011, gain 3.4, base 0.05) after the strip `t3b-km-erratic-tokyo-soak.png`; the km_ink golden refreshed deliberately (only that frame changed, 10 identical after). ROUND 3 (operator: 'more wobble ... a higher grain ... start out more as a lighter gray than that much blue tinge', then 'wriggling/morphing/creeping/crawling to saturate the page'): WOBBLE_SCALE 210 with a busier field, a GRAIN stage (fine field multiplied in), S1 0.03 + `WASH_NEUTRAL` 0.8 (per-channel K/S blended to their mean while thin, `1 - f^4`, the exact ink at full - the wash is a warm-neutral grey, the raw model's is cold and the test says so), and the fields MOVE: `soakAnim(u)` drives feOffsets on the wobble / attraction / grain noise and breathes the displacement scale on the soak clock (pure function, applied only while the soak runs). `km_ink` turned ON in `build_short.py` for the operator to judge in LIVE play on :8733 (2026-09-05). km_ink golden refreshed; probe reads the table. ROUND 4 (operator: 'now it looks more like a burn-in, and less like ink spreading. we need the middle ground'): ATTR gain 1.8 / base 0.25, grain 0.7 / 0.65, blur 5, wobble 180 - the field decides the front but no longer scorches it. LIVE-PLAY PROOF `t3c-live-soak.png` (headless Chromium pressing the player's Play button on :8733, no seeking): the wobble offset and displacement scale change frame to frame through the soak (0,0 -> 44,94 -> 129,-54 -> 158,-97; scale 196 -> 144 -> 188 -> 227) and freeze when it ends. The in-app pane reads as frozen because a hidden tab throttles requestAnimationFrame (visibilityState hidden, 5 frames in 1.75 s) - a harness fact, recorded so it is not read as a template bug again. ROUND 5 (operator, in motion: 'it absolutely looks like a burn-in because of the boil ... tempted to just revert to the original kubelka munk, i also don't like how the spiral looks now when it soaks back up the layer', then 'can we add more wobble without causing the issues?'): `SOAK.MESH` is a dial, DEFAULT OFF - the K-M soak is round one again (flat white stains, one wobble, one blur, the table) with the lighter neutral wash kept; the retract strip `t3d-km-retract.png` shows clean stains going down the drain again. More wobble without the boil: PLAIN_SCALE 170 on a busier field (0.007 0.011) and a slow CREEP of that low-frequency noise only (PLAIN_DRIFT 90, breath 0.15) while the soak runs - no grain, no attraction gain. Live-play proof: wob 0,0 -> 27,47 -> 66,-2 -> 98,-49 then frozen at the soak's end. km_ink golden refreshed, nine identical. Strip `t3e-km-wobble-soak.png`. ROUND 6 (operator: 'the problem is that it's too smooth, it needs more step-motion / jitter / delay / time variance'): under km_ink the soak runs on a quantised clock (`SOAK_STEP.FPS` 8), each stain climbs a seeded staircase of 20 bursts of varying size with its own phase (`soakStepped`: never contracts, exactly 1 at the flood), and the outline wobble jitters per tick (`soakJitter`, 8 px); `stepClock` quantises the creep. Test: a staircase not a ramp, bursts and dwells, time variance between stains, jitter constant within a tick. Live-play proof: the stain opacity dwells 0.28 across 0.8 s then jumps; the wobble lands on tick values. km_ink golden refreshed, nine identical.

### T4: area-preserving squash as the shared helper
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T5
- Write set: `content/video_engine/scripts/kinetics/squash.mjs`, `content/video_engine/tests/kinetics/squash.test.mjs`, the template's `lpVortex` stretch and the still-life species that stretch (flag `area_squash`)
- Acceptance: `A(t) = R(θ)·diag(1+α, 1/(1+α))·R(−θ)`, `α(t) = κ_v‖v‖ + κ_a·max(0, −v̂·a)` (42 §42.3), with the velocity from T5's evaluator where the caller is a spring and from the finite difference of the map where it is the vortex. Test: `det(A) == 1` within tolerance across t and α, including α → 0 and large α. The vortex's inline `(1+a, 1/(1+a))` is replaced by the helper at identical output when the flag is off.
- Validate: `node --test content/video_engine/tests/kinetics/squash.test.mjs && python content/video_engine/scripts/render_baseline.py --check`
- Evidence: 2026-09-05 - `kinetics/squash.mjs`: `squashAlpha` (kappa_v |v| + kappa_a max(0, -v_hat.a), clamped), `squashMatrix` (R diag R^-1 as [a,b,c,d]), `det2`, `scaleBy` (the vortex's own expressions), `springSquash` (a 1-D pop's alpha from the spring's v and a). `squash.test.mjs` 5 pass: det(A) == 1 within 1e-9 for 48 angles x alpha in {0, 1e-9, ..., 1000}, symmetric (no shear); stretch along theta; alpha zero at rest, an acceleration ALONG v adds nothing, deceleration adds, clamped; scaleBy bit-equal to `s*(1+a)`, `s/(1+a)`; a pop's squash peaks on the way up and is under a tenth once landed. Template: the vortex's stretch routes through `scaleBy` unconditionally - goldens PASS 4 identical (bit-identical by construction); the badge pop appends the tensor behind `area_squash` (needs `analytic_spring` for a velocity). Deviation: routed to implementation_luna in the plan, done by the parent - that agent type is not available in this session; the still-life species do not stretch today, so the badge pop is the only pop caller; the caption pop is a pure scale with no travel direction and is left alone.

### T5: the rest of the spring - three regimes, velocity, the seek test
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/spring.mjs`, `content/video_engine/tests/kinetics/spring.test.mjs`
- Acceptance: underdamped, critical and overdamped closed forms returning position and velocity; the inverse model (`M_p -> ζ`, settle -> `ω₀`) as the one entry point; `springPop` becomes a thin caller with identical output at `M_p = 0.04`. Tests: frame N direct equals frames 0..N stepped, bit-identical; measured overshoot matches `M_p` at `t_p = π/ω_d`; `ζ = 1` overshoots zero; `ζ > 1` is monotone.
- Validate: `node --test content/video_engine/tests/kinetics/spring.test.mjs && python content/video_engine/scripts/render_baseline.py --check`
- Evidence: 2026-09-05 - `kinetics/spring.mjs`: `springParams` (Mp -> zeta, settle -> omega; Mp = 0 asks for critical), `springEval` returning x, v AND a in all three regimes, `POP`, `springPop` as the thin caller. `spring.test.mjs` 5 pass: springPop BIT-IDENTICAL to the 2026-09-05 shipping formula over 2000 u's at Mp 0.04 (and 0.1, 0.2); peak exactly 1 + Mp at pi/wd with zero velocity; zeta = 1 overshoots zero, zeta = 1.6 monotone and never crosses 1; v and a match finite differences of x in all three regimes; THE SEEK TEST - frame N direct === frames 0..N stepped (bit-identical), while a semi-implicit Euler spring reaches a different frame N when stepped through different frames. Goldens PASS 4 identical. Deviation: routed to implementation_luna in the plan, done by the parent (agent type not available here).

### T6: wire, capture, turn on, record
- Status: complete - both gates ruled 2026-09-05: the stroke ON, K-M ink OFF for the soak (kept for ink over ink); the short carries analytic_spring, min_jerk, area_squash, curvature_stroke
- Owner: parent
- Depends on: T2, T3, T4, T5
- Write set: the template (flag guards), `content/video_engine/tests/golden/` (flag-ON goldens), `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` (`C.KINETICS`), `docs/content-video-engine/47-FINDINGS-TO-CHECKS.md` §5b, `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md`
- Acceptance: flags off -> four goldens byte-identical; one flag-ON golden per capability captured and looked at; the Tokyo short rebuilt with all four on, motion gate green including M16; 47 §5b rows moved from "designed out (pending)" to shipped with the failing case named; CAPABILITIES rows; the backlog's items 1, 6, 7, 8 struck.
- Validate: `python content/video_engine/scripts/render_baseline.py --check && python content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py && python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: 2026-09-05 - a FIFTH golden surface `ledger-soak-page` (the soak field + a badge rail; the four existing sources and frames regenerated byte-identical) and FLAG-ON goldens in `render_baseline.py` (`FLAG_FRAMES`, `--flags`): `chart-callout@curvature_stroke` (t 10.3), `ledger-page-mid-build@curvature_stroke` (5.6), `ledger-soak-page@km_ink` (2.7), `ledger-soak-page@analytic_spring` and `@area_squash` (7.86, the first rail badge mid-pop). Looked at (`t6-flag-goldens.png`): each differs from its flag-off twin only where it should - the ring alone (bbox 1356-1685 x 437-483), the hand-paced lines, the caption pop, the badge's stretch (121-511 x 1004-1080), the soak. `test_kinetics_flags.py::test_each_flag_golden_differs_from_the_flag_off_render` pins that (the squash against its spring-only twin). `render_baseline.py --check`: PASS 10 golden frames identical. The Tokyo short rebuilt with `area_squash` ON (`build_short.py` `C.KINETICS`; player kinetics = analytic_spring, min_jerk, area_squash): motion gate 135 events / 97.9 per min, the one standing M16 FAIL at 1:20 unchanged (the outro, recorded in the backlog). Docs: 47 s5b four rows (G-h shipped flag-off + 42.1 / 42.2 / 42.3) and the scoreboard; CAPABILITIES five rows; BACKLOG items 1, 6, 7, 8 struck with their state, the P43 row, Tier-1 T1 / T3. pytest 72 passed (goldens, flags, sync, probe, motion gate). NOT done by design: `curvature_stroke` and `km_ink` stay OFF for Tokyo until the operator rules on the T2 and T3 strips (the plan's human gates) - one line in `build_short.py` each.

## Verification

- `node --test content/video_engine/tests/kinetics/` - every module's failing case first (47's rule), then passing
- `python content/video_engine/scripts/sync_kinetics.py --check` - the inlined copies match the modules
- `python content/video_engine/scripts/render_baseline.py --check` - flags off, four goldens byte-identical, after every slice
- `python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_gate_motion_density.py -q`
- the Tokyo short rebuilt and played in the review server (no-store) at the human gates

## Evidence And Handoff

- per slice: the test file, its first run failing, its run passing, the golden check line
- T2 and T3: a before/after frame pair, sent to the operator before the flag turns on
- T6: the flag-ON goldens beside the flag-OFF ones, the short's `GATES-MOTION.md`, the doc rows
- P38 header notes T1-T4 moved here; T5-T8 remain there, waiting on an object page
