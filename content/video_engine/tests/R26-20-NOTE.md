# R26-20's other half: the STAMP arrival and the BARE prop (E99 s85), 2026-09-22

Recall: docs_find "badge-stamp" -> `docs/content-video-engine/CAPABILITIES.md:73` (the remotion-ui harvest row, "badge-stamp priority integration (a clamped scale spring plus a free trailing rotation spring ...)") and `docs/content-video-engine/REMOTION-UI-INTAKE-2026-09-07.md:1`
Recall: docs_find "two-spring offset" -> `docs/content-video-engine/REMOTION-UI-INTAKE-2026-09-07.md:37` ("Priority integration - cheap, sound, and lands in work already in flight"); the RU-2 row is `:41`
Recall: docs_find "impact ring" -> `CAPABILITIES.md:38` (the melt) and `:78` (stop-action). Neither has an impact ring; the stop-action row has the contact shadow, the squash and the ground dip, and this row reuses them
Recall: docs_find "prop cutout" -> `docs/agent-memory/operator/generated-images-stay-out-of-git.md` only (E99 s31). The golden therefore carries a 141x129 PROXY of the cutout, made the way the agenda page's icon proxy is made, not the file
Recall: the docs layers report themselves stale (`build_docs_layers.py --refresh`). I did not rebuild them: they are generated artifacts and outside this row's write set, so the new CAPABILITIES row will not show up in `docs_find` until the parent refreshes them

## The source, read and ported (not re-derived)

The source is on disk at `content/video_engine/remotion-ui/src/remotion/primitives/badge-stamp.tsx`, with `lib/motion-tokens.ts` and `lib/timing.ts`. Each dial in `kinetics/stopaction.mjs` `STAMP_ARRIVAL` (:286) names the source line it came from:

| ours | source | value |
|---|---|---|
| `FROM` | `:88` `interpolate(land, [0, 1], [2.1, 1])` | 2.1 |
| `LAND_DEG` / `WIND_DEG` | `:58` rotation / `:59` windUp | -9 / 16 deg |
| `LAND` (clamped) | `:75-79` `damping 14, stiffness 220, mass 0.9, overshootClamping: true` | zeta 0.4975, w0 15.635 |
| `TURN` (free) | `:82-86` `damping 11, stiffness 120, mass 1` | zeta 0.5021, w0 10.954 |
| `FADE` | `:93` opacity over land [0, 0.35] | 0.35 |
| `INK` | `:96` "heavy on impact, easing back as the pressure comes off" | 1 -> 0.86 |
| `SHOCK_S` | `:104-109` 14 frames at `timing.ts:3` DEFAULT_FPS 30 | 0.4667 s, linear |
| the expansion | `:114-117` `EASING.enter` = `timing.ts:6` cubic-bezier(0.16, 1, 0.3, 1) | eased |
| `RING_TO` | `:156` `r * (1 + shock)` | 2x |
| `RING_W_PX` / `RING_W_FADE` | `:159` 2.6 viewBox units at size 220 = 4.77 px, `(1 - life * 0.7)` | 4.8 px |
| `RING_A` | `:160` `0.55 * (1 - shockLife)` | 0.55 |
| `EXIT_S` + curve | `:62`, `:119-125` exitInFrames 16, `EASING.exit` = `timing.ts:9` `Easing.in(Easing.cubic)` | 0.5333 s |

Remotion's `spring({damping, stiffness, mass})` is the same mass-spring-damper `massParams` already uses, so the two configs port as plain numbers and `spring.mjs`'s closed form evaluates them. A seek is still the play. Remotion implements `overshootClamping` by stopping the spring at its target. Here the first crossing is solved in closed form (`tc` = (pi - atan(wd / (zeta w0))) / wd = 0.1542 s), and the scale is exactly 1 from then on.

What did not port is the look: the gold `#E8B86D`, the two curved texts and the double border. The ring is ours. It is chalk `#F2F2F2` on the charcoal page and `#25313C` everywhere else (the template's `--lp-chalk` / `--charcoal`, written as literals; see below). It starts on the mark's own circumscribed circle.

## The two axes (the operator's final model)

1. **Arrival.** `arrive: stamp` sits beside `spring | throw | land` (`build_scene_timeline_f.py:106`). It is a motion only and carries whatever the row gives it. `B.dock_opts({"arrive": "stamp"})` is valid for a plain card.
2. **Payload.** `prop: True` sets `DOCK_KIND_PROP` (`:175`). A prop is always bare. The engine's `dockIsProp` / `dockIsBare` (`scene-evidence-engine.mjs:15618`) reuse the cutout's chrome-down class: no paper, border, radius, padding, backdrop blur or rail, and the box shadow is set to none. They also undo the cutout's foot mask (`template.html:337`), which dissolves a bust into its band and would fade the base off a building. A prop is either stamped on or thrown on (`test_a_bare_prop_is_STAMPED_ON_or_THROWN_ON...`). `ink: own|page` (`DOCK_INKS`, `:108`) is open for the operator to judge on the frame, and both options are goldened. `page` applies to the picture only: `grayscale(1) invert(1) ...` on the charcoal page (a chalk impression) and `grayscale(1) ... brightness(0.72)` on a light ground.

The vector map's `stamp` species is untouched (`SPECIES_STAMP` in `VECMAP_SPECIES`, `:326`). One word lives in two registries. In the engine the arrival's dials are `STAMP_ARRIVAL` because `species/vecmap.mjs:60` already owns `STAMP` in the one inlined namespace: the first sync failed on exactly that identifier.

## SEND-BACK #1 (the parent's frame read): the ring crossed the "+613%" end name

At 10.17 s the ring (radius 260 px) ran through "MEMORY MAKERS (hynix+Micron)". Check (c) had measured the MARK alone. The fix fitted the ring's peak extent in the compiler (`ring_obstacles` + `stamp_ring_fit`: capped, never clipped, and reported; under the 1.6x floor the mark shrinks, and under 120 px it is refused). It also capped the 2.1x approach, which had reached y 389 over the names at opacity 0.44. The floor comes from `badge-stamp.tsx:110-113` ("a ring that only grows to 1.55x is under it the whole time it is worth seeing"); 1.6 is the first round step past it. The 120 px mark floor is [DERIVED]: three quarters of the agenda page's drawn stamp.

## SEND-BACK #2 (the reviewer blocked the commit): a stamp the compiler places is fitted to what the engine draws

The reviewer's H1: through the real row loop, the same page gave `{1251, 369, 347, 205}`, centred in the end-name column, with a 322 px ring through all four names, while the compiler printed "capped at 1.60x". The first two fixes protected only the golden's hand-built box. Each part is now fixed in `build_scene_timeline_f.py`, in the door the row loop calls:

- **(a) End names on every ledger page.**
  - `ring_obstacles` takes the page's measured `tags` box. `page_boxes` reports it on a full-stage 16:9 page, and the compiler stamps every 16:9 row full-stage (`stamp_full_stage`).
  - A page that WRITES end names (`ledger_page.tag_units` > 0) but reports no box is REFUSED by name ("writes inline end names (tag_units 696) but reports no measured `tags` box ... cannot be fitted blind"). That is exactly the reviewer's page (not stamped full-stage).
  - Two more obstacles came out of rendering the fixed row:
    - The anchored caption's band.
    - The BASIS LABEL (`axes.ylabel`). `page_boxes` folds it into `plot`'s top, so it has no box of its own and the data mask doesn't carry it. It is taken as the plot's top strip, one tick-label line high. Measured: the label at (151, 208, 435x33) inside the strip (151, 208, 947x36). The first render of the new placement put the ring through it.
- **(b) One box for the whole arrival (decided).** A stamp lands at its fitted box and stays there.
  - The loop writes `centre: True`, which is the engine's own "box from the first frame" switch (`dockGeom`: `d.centre && !d.read_place`).
  - `dock_opts` refuses `read`, `read_s`, `park_s` and `centre_band` on a stamp.
  - So the rect that is fitted, rung and landed on is one rect.
- **(c) No silent skip.** `stamp_dock_place` runs for EVERY `arrive: stamp` dock, before the slot rule, so slot 1 is fitted like slot 0.
  - Off a ledger page it fits against the frame's own caption band inside its safe box (`FRAME_BANDS`, pinned against `page_boxes`).
  - A plate stamp with no `room` and no `centre_x`/`centre_y` is refused by name.
  - Every refusal fails the row as `FAIL: shot row N ... dock <aid>`.
- **(d) The painted aspect.** The loop reads the picture's own `image_aspect` off the dock's asset (0.9184 for the Fed cutout), never a card's 0.625.
- **Where it lands.** With no authored centre, the E65 room the placer answers (`dock_place`) is searched on an 8 px grid for the centre with the most clearance.

**The golden needs no hand clip any more.** `_prop_room`, `PROP_TAGS_BOX` and `PROP_TAG_CEIL` are deleted. The fixture calls `stamp_dock_place` on the full-stage page, and `test_A_REAL_STAMP_ROW...` asserts that the committed dock is byte-for-byte the one the loop's door produces.

**H2.** `stampXf`'s `h` read `P.SHADOW_H_PX`, which is not on `STAMP_ARRIVAL`, so it was NaN on every call and the contact shadow stood at its at-contact state before the mark arrived. It now reads `STOP.SHADOW_H_PX` (an `o` may still override it). The node test asserts every numeric field is finite (`deepEqual` passes NaN against NaN). It also asserts that `h` is 160 at the contact, falls monotonically as the mark comes down, and is 0 from the scale's landing (0.1542 s).

**M1.** `arrive=stamp` is refused by name in the plate/pill grammar (`split_plate_opts`: "a page's pills land or are thrown, and no pill painter stamps") and with `embed` on a dock.

**M2.** `output: "perceptual-scale"` (`badge-stamp.tsx:90`) is Remotion's interpolation in SIGNED AREA, not in log space: `toSignedArea(s) = sign(s) s^2`, then the mix, then `sign(a) sqrt|a|`. Source: Remotion 4.0.502 `dist/cjs/interpolate.js:272-283, :327-330`, read in the main checkout's `content/video_engine/remotion-kit/node_modules/remotion`; the harvest pinned no node_modules of its own. It is now ported: scale = sqrt(2.1² + (1 - 2.1²)·land). The ends (2.1 and 1) are unchanged, so the fit's peak is unaffected. At land 0.5 the scale is 1.645, where the linear mix gave 1.55. `from_to` is the capped `FROM`.

**L1.** The proof-land comment in `render_baseline.py` now carries the capped numbers.

**L3.** `stamp_ring_fit` measures the clearance at the ROUNDED box it writes and rounds both peaks DOWN to 4 places. The engine draws the ring with `toFixed(1)`, which can add at most 0.05 px, and its stroke is drawn inside the radius while the fit reserved 4.8 px outside it.

On the page a real build compiles, the row prints: **"ring capped at 1.62x by the room; mark shrunk 200x183 -> 134x123 so the floor fits; approach capped 2.10x -> 1.67x"**. Room `empty` (the plot's own clear top-left), place `{228, 338, 134, 123}`, `ring_to` 1.6178, `from_to` 1.6706.

## Measured on the rendered frame (the row, which IS the committed golden; r0 = 90.95 px)

| t (s) | scale (sqrt det) | turn | mark hull | ring radius | ring / r0 | ring box | ring opacity / stroke |
|---|---|---|---|---|---|---|---|
| 10.04 | 1.5850 | +5.69 deg | x 197..393, y 276..529 | 115.7 px | 1.2721x | x 179..411, y 284..515 | 0.503 / 4.51 px |
| 10.17 | **1.0000** | **-5.61 deg** | x 222..368, y 332..467 | 142.8 px | 1.5696x | x 152..438, y 257..542 | 0.350 / 3.58 px |
| 10.20 | 1.0000 | -7.76 deg | x 220..370, y 330..469 | 144.4 px | 1.5877x | x 151..439, y 255..544 | 0.314 / 3.36 px |
| 10.46 (widest drawn) | 1.0000 | -10.14 deg | x 218..372, y 327..471 | **147.1 px** | **1.6180x** (fitted 1.6178) | **x 148..442, y 252..547** | 0.008 / 1.49 px |
| 11.30 (rest) | 1.0000 | **-8.99 deg** | x 219..371, y 328..470 | - | - | - | 0 |
| 26.40 (exit) | 1.0000 | -9.00 deg | same | - | - | - | mark opacity 0.578 |

- **(a)** At 10.17 s the scale is 1.0000 while the mark is still 3.39 deg short of its -9.00 deg landing. It rests off square.
- **(b)** The ring is capped at 1.6178x by the room: 1.27x at 0.04 s, 1.59x at 0.20 s, and 1.618x at its widest, drawn whole and never clipped.
- **(c)** The mark's centre is inside E65's `empty` room.
  - At every measured instant, 0 of the turned mark's hull and 0 of the ring's whole box (its stroke is inside it) is over:
    - the chart's lines, sampled every 3 px of their length with half their drawn stroke (a polyline's client rect is most of the plot and would overlap anything);
    - the four end names;
    - the tick labels and the basis label;
    - the title, the sub and the citation.
  - Clearances at the widest frame:
    - 8 px under the basis label's strip (y 252 vs 244);
    - 11 px right of the "640" tick label (x 148 vs 137);
    - the lines by the mask's cells.
- **Gridlines are not obstacles.** They are furniture drawn under the data, and a card placed in E65's empty room sits over them too. On this frame the ring crosses the faint 640 gridline.
- **What the cap costs.** The prop is 134 px wide and its ring peaks at 1.62x, not the source's 2x. That is the most this page's clearest room (182 px of clearance) holds at the ring floor. A bigger stamp needs a sparser page or a plate room.

## Files

Changed: `scripts/kinetics/stopaction.mjs` (new STAMP block; `stopCss` writes a scale only when the state carries one), `samples/scene-evidence-engine.mjs` (the synced region, `arriveOf`, the camera's landing clock, the stamp branch with `.dock-ring`, `dockIsProp` / `dockIsBare` / `propInkCss`), `scripts/build_scene_timeline_f.py` (additive grammar; `STAMP_FROM` / `STAMP_RING_*` / `STAMP_MARK_FLOOR_PX` / `STAMP_PROP_W` / `FRAME_BANDS`, `ring_obstacles`, `ring_clearance`, `stamp_ring_fit`, `_stamp_from`, `stamp_dock_place`, the row loop's stamp step, the stamp refusals in `dock_opts` and `split_plate_opts`), `scripts/render_baseline.py` (three `PROOF_FRAMES`), `tests/golden/build_golden_sources.py` (`_prop_room`, `_prop_stamp`, two surfaces), `tests/test_golden_frames.py` (two `SURFACES`), `CAPABILITIES.md` (one row), `BACKLOG.md` (the R26-20 status cell only).
New: `tests/kinetics/stopaction-stamp.test.mjs` (11), `tests/test_the_stamp_arrival.py` (28), golden sources and frames `prop-stamp`, `prop-stamp-ink`, `prop-stamp@proof-land`, `prop-stamp-ink@proof-land`, `prop-stamp@proof-exit`.

## Not done, with where

1. **A page without a measured end-name box refuses a stamp.** That covers any 9:16 page, and any page a build does not stamp full-stage. It is the correct answer, because the fit would otherwise be blind, but it means no stamp on a 9:16 ledger page until the page-boxes measurement reports `tags` there. That measurement is the other lane's (`ledger_page.py` / `page-boxes.v1.json`, not opened).
2. **Not this scope (the parent files them):** M3 (the motion gate, the landing cue and the camera attention do not see a stamp as an event: `gate_motion_density.py:2971`, `authoring/audio.py:142`, engine `camAttentionState`). Also L2 beyond the caption band: a scene's OTHER dock is not an obstacle. The newsreel strip is passed in the loop (`newsreel_boxes`).
3. **Page-bound leaving.** A landed prop leaves on its own `exit` with its own curve (E50). It does not join R26-219's `PAGE_BOUND_SPECIES` law: that law acts on species rows, and a dock is not a species. Having a prop dock park, rescale and leave with the page is a separate change.
4. **The ring's colour tokens.** `var(--lp-chalk)` does not resolve in the dock layer. With it, the border declaration was invalid and computed to 0 px, which is itself an impact ring nobody sees (probed 2026-09-22). The ring therefore carries the two colours as literals, and a token change will not reach it.
5. **The scrub step.** The player's `#scrub` rounds to 0.01 s, so a t of 10.1667 renders at 10.17. The PROOF frame and the test both use 10.17 so that the module's numbers and the frame's agree.
6. Nothing in `build-h/` was rebuilt, and the six H rows are not authored. They wait on the operator's ink pick.
