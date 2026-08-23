# Content Video Engine

## Pipeline

- Treat `storyboard.json` as immutable after Gate A; measured timing belongs in artifacts.
- Audio is the render clock. Never stretch or trim narration to fit video.
- Keep provider keys in environment variables and fail before a paid call when configuration
  is incomplete.
- Gate A and Gate B are operator actions. Tests may simulate them; product code may not
  auto-approve them.
- All stages are deterministic and idempotent from persisted inputs. Record failures and
  degraded behavior in stage events.
- Runtime output belongs under `runtime/jobs/` and is never hand-edited.

## Asset catalogue

- **Promotion is an operator action.** Product code and generating agents never set
  `rights_state: approved`, `review_state: approved_reusable`, or `render_eligible: true`.
  Register new assets as `original_review_only` / `review_only` / `render_eligible: false`.
- Register by `asset_id` plus `sha256`, never by raw path. A path with a mismatched
  digest is a rejection, not a warning.
- Follow the tier convention: `actor`, `prop`, `world`, `world_board`, `cast_board` at
  tier 2; `mechanism` at tier 3. Tier 3 is restricted by kind, so an actor registered
  there is invisible to the resolver and every actor slot silently falls through to
  `bespoke_plate`.
- Resolution ranks by **match strength first, cascade second**. The cascade breaks ties
  between candidates that match equally well; it must never let a one-word coincidence at
  an early tier pre-empt a real match at a later one.
- An episode may not mix art directions, but raw `style_version` equality is too blunt a
  test — one coherent cast can span two version strings. Group them in `style_families`
  and compare families.

## Composition

[24-COMPOSITION-AND-SCALE-SPEC.md](../../docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md)
is the specification of record. The rules that get violated most:

- **Figure size is set by the plate, not the compositor.** The furniture already drawn in a
  world commits it to a figure height. If that height is wrong, regenerate the world;
  shrinking the cast to fit makes them read as dolls and no setting undoes it.
- `world_figure_scale` (what the furniture is drawn for, 0.50) and `cast_figure_height`
  (what the cast composites at, 0.76) are **two independent numbers**. Conflating them is
  the single most common source of scale errors.
- Every world declares `placement` — clear-floor span, baseline, figure height, max figures.
  Without it a compositor will stand figures on the furniture.
- Figures sharing a frame share a scale. Hierarchy is carried by rendering weight alone
  (~2:1 on saturation and internal detail); do not stack scale or brightness on top of it.
- Keep the host's rendering untouched. Contrast comes from making supporting cast lighter.
- 2.5D world planes are declared back to front, must include `building_or_environment`,
  and must be generated in one pass so they register.

## Asset review

- Verify delivery before reading it: every declared `sha256` against the bytes, dimensions
  against the spec, and alpha where transparency was required.
- Measure before asserting. Density, saturation, detail, clear-zone flatness and implied
  human scale are all cheap to compute and routinely contradict a visual impression.
- **Then composite and look.** Metrics predicted the v2 props would outrank the host by
  size; they did not. The real defect was representational register, and only a composited
  frame showed it.
- Separate *medium* (an editorial choice, the operator's) from *function* (density,
  legibility, scale, registration). Rejecting a delivery on medium when the operator has
  already chosen it wastes a batch.
