---
id: P15-OPERATOR-CONSOLE
title: Local operator console for the content video engine
status: complete
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-23
updated: 2026-08-23
---

# Local Operator Console

## Summary

The engine has 76 CLI commands, one static read-only HTML board, and a Remotion
editor. Everything between "assets exist on disk" and "assets are trusted enough
to render" is done by hand.

The episode-1 intake made the cost concrete. Verifying 25 assets required
throwaway Python for hash checks, dimension checks, alpha checks, density
measurement and — decisively — **compositing a test frame**, because three
defects were invisible until an asset sat in a real frame at real scale. The
generating agent also self-promoted every asset to `render_eligible: true`,
which nothing caught until a human read the JSON.

This builds a local web console over the existing services: intake and
verification, live composite preview, exception-first triage, and operator
promotion. Routes stay thin — every write goes through the services that already
own the guards, so the console can never become a second, weaker implementation
of the rules.

Not a rewrite. The CLI stays the automation surface; the console is the human
surface over the same services.

## Intent And Acceptance

**Intent.** Make asset verification and promotion a first-class repeatable
surface, and lay a spine the rest of the pipeline can move onto incrementally.

Accepted when:

1. `python -m content.video_engine.console` serves a local app; no build step, no
   Node toolchain, no network dependency.
2. Pointing the console at a delivery folder produces a per-asset verification
   report — digest, dimensions, alpha, human scale, depth planes, style family,
   density and rendering weight — computed by services, not by the view layer.
3. Every asset is reviewable **as a composited frame** against a real world at
   its declared `figure_height` and inside its `figure_zone`, not only as an
   isolated thumbnail.
4. Triage is keyboard-driven and exception-first: flagged assets sort first,
   clean assets carry a default, and a decision auto-advances.
5. Promotion writes through `asset_catalog.register_assets`, so `_scale_errors`,
   `_layer_errors`, `_style_errors` and digest binding all still apply. A batch
   that fails a guard cannot be committed from the UI.
6. Nothing in the console sets `rights_state: approved`, `review_state:
   approved_reusable` or `render_eligible: true` without an explicit operator
   action on that specific asset.
7. No route performs a paid provider call.
8. Console services are unit-tested to the repo's standard; view templates are
   covered by route smoke tests asserting status and key content.

## Scope

- A FastAPI + Jinja2 + HTMX application under `content/video_engine/console/`.
- New services for work the console needs and the CLI can reuse: composite
  preview, asset measurement, delivery-folder intake.
- Read views over the existing catalogue, scene board, and `runtime/jobs/`.
- Write paths for promotion, rejection, batch registration, and scene selection.
- Keyboard-driven triage UX.

## Not Building

- **No provider calls.** Generation stays manual in the browser for now. T9 only
  compiles and exports the request pack; the API adapter is explicitly deferred.
- **No second validation implementation.** If the console needs a guard the
  services lack, the guard goes in the service with tests, and the console calls
  it. A rule enforced only in a template is a bug.
- No authentication, multi-user, or remote deployment. Localhost, single
  operator, bound to `127.0.0.1`.
- No React, no bundler, no `node_modules`. HTMX is served as a vendored static
  asset so the console works offline.
- No changes to Remotion, the render lane, or `storyboard.json` semantics.
- No database. Artifacts on disk stay the source of truth.
- No auto-promotion, no bulk "approve all" on flagged assets, and no sampling.

## Human Gates

| Gate | Who | Rule |
| --- | --- | --- |
| Asset promotion | Operator | Per-asset, in the UI. Product code never sets approval fields. Bulk promote is offered **only** for assets with zero exceptions, and names the count before it commits. |
| Batch registration | Operator | Explicit commit step; shows what will be written and refuses if any service guard fails. |
| Scene selection override | Operator | Auto-selected defaults stand until the operator changes them; the board records who chose what. |
| Gate A / Gate B | Operator | Unchanged. The console may display state and never advances a gate. |
| Any paid call | Operator | Out of scope for this plan; no route may reach a provider. |

## Mandatory Reads

- `backend-patterns` — routes, service boundaries, validation at the edge
- `content/video_engine/AGENTS.md` — engine rules, catalogue invariants, review discipline
- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md` — placement, scale, depth planes
- `docs/content-video-engine/23-EP1-LIBRARY-INTAKE-REVIEW.md` — the failures this console exists to catch
- `docs/content-video-engine/README.md` — rule ownership and authority boundaries
- `content/video_engine/src/services/asset_catalog.py` — the guards the console must route through
- `content/video_engine/src/services/scene_board.py` — existing exception-first board and its auto-select rule
- `src/api/app.py` — the repo's established thin-route/service-layer FastAPI shape

## Execution Path

Stack: **FastAPI + Jinja2 + HTMX**, all already installed. The research is
unambiguous for a single-operator internal tool — one application, one language,
no build step, and the person who owns the data model owns the UI. React's
advantages appear when the UI *is* the product with heavy client state; this UI
is a thin window onto artifacts that live on disk.

Layering, mirroring `src/api/app.py`:

```
content/video_engine/console/
  __main__.py          uvicorn entrypoint, binds 127.0.0.1
  app.py               FastAPI app, thin routes only
  routes/              intake.py, catalog.py, board.py, runs.py
  templates/           Jinja2, HTMX partials returned per fragment
  static/              vendored htmx.min.js, one stylesheet, no build
content/video_engine/src/services/
  composite_preview.py deterministic placement frames (Pillow). No camera motion.
  asset_measurement.py density, saturation, detail, clear-zone, implied scale
  delivery_intake.py   scan a folder, bind to catalogue, produce a verdict pack
```

**A route may not compute a verdict.** It calls a service, gets a structured
result, and renders it. This is what keeps the console from drifting away from
the CLI's guarantees.

Order: T1 and T2 give the first usable evening — a console that can show an asset
in a real frame. T3 to T5 make it a review tool. T6 closes the loop. T7, T8, T10 and
T11 extend it toward the pipeline console. T9 stays deferred until a provider
decision.

**Motion is not built here, and there are two lanes, not one.**
`19-HYPERFRAMES-LANE.md` gives Remotion the camera transforms and layer
composition — `EditorialMotion.tsx` already implements `foreground_parallax` per
layer with the world locked and a `parallaxFactor` the catalogue's
`layers[].parallax_factor` feeds directly. HyperFrames owns short/caption/motion
units, including `animatic_preview`, which is deterministic, estimated-timing and
"provisional by definition, never publishable" — precisely the right shape for a
console preview. T10 routes to whichever lane owns the behaviour and reimplements
neither.

## Patterns To Mirror

- **Thin routes over services** — `src/api/app.py`.
- **Exception-first triage with a deterministic default** — `scene_board._auto_select`
  and `render_board_html`, which already sort flagged slots first and state
  "you only have to touch the flagged ones". The console generalises this
  existing pattern rather than inventing one.
- **Compile / record split** — `pronunciation_dictionary.compile_sync_request`
  builds a request and performs no network call; the operator executes it.
  Generation follows the same shape.
- **Provisional by default** — assets enter as `review_only` /
  `render_eligible: false` and are rendered with pending-review chrome, matching
  the HITL "provisional state" pattern and the existing catalogue semantics.
- **Deterministic, idempotent, hash-stamped artifacts** — `artifact_io`. Preview
  renders are derived and disposable; they are written under `runtime/` and are
  never catalogue assets.

## UX Design

### Design read

**This is dense professional tooling, not a marketing surface.** Two of the three
design skills consulted rule themselves out for it, and saying so is more useful
than pretending otherwise:

- **design-taste-frontend** — its own scope section excludes dashboards, dense
  product UI and admin panels, and directs the reader to a real design system
  instead. What transfers is its accessibility and anti-tell material: button and
  form contrast, full interactive state cycles, theme lock, reduced motion, and
  its rule that decorative status dots are banned unless they carry real semantic
  state.
- **high-end-visual-design** — an agency skill. Its core moves — macro-whitespace
  at `py-24` to `py-40`, massive display typography, and double-bezel nesting
  around every container — are the direct opposite of what a density-9 review tool
  needs, and bezel chrome around an image is actively harmful when the image is
  the thing under judgement. What transfers: no generic 1px grey borders or harsh
  black shadows, custom easing curves over `ease-in-out`, GPU-safe animation,
  z-index discipline, and `100dvh` over `h-screen`.
- **ui-ux-pro-max** — directly applicable. Its style recommendation,
  **Minimalism and Swiss Style**, is explicitly scoped to "enterprise apps,
  dashboards, professional tools" and is adopted. Its returned *pattern*, "Hero +
  Features + CTA", is a landing-page shape and is rejected; the skill's own
  contract says to verify fit before applying, and a console has no hero.

Dials: **variance 3, motion 3, density 9.**

### The surround must be neutral, and this overrides the generated palette

The generated palette proposed a light navy-and-green scheme. **Rejected on a
domain constraint it could not know:** this console's entire job is judging
images, and a coloured or bright surround shifts the perceived colour, contrast
and value of whatever sits inside it. Every serious culling tool defaults to a
neutral dark grey stage for exactly this reason.

Two rules follow:

1. **The stage is achromatic.** Neutral greys only around any asset. No tint, no
   gradient, no brand colour touching the image area.
2. **The console accent must sit outside the asset palette.** The library owns
   cream `#F4E6C7`, charcoal `#25313C`, cobalt `#1769C2`, teal `#178C83`,
   sunflower `#F5B72E` and coral `#ED6A4A`. If chrome uses any of those, the
   operator will read UI as artwork. The console accent is therefore a colour the
   library never uses.

Tokens:

| Token | Value | Use |
| --- | --- | --- |
| `--stage` | `#1B1B1D` | The area behind an asset. Achromatic, deliberately. |
| `--surface` | `#0E0E10` | App background |
| `--panel` | `#151517` | Filmstrip and verdict panes |
| `--hairline` | `rgb(255 255 255 / 0.09)` | Separators. No 1px solid grey. |
| `--text` | `#E8E8EA` | Primary |
| `--text-dim` | `#9A9AA2` | Secondary, min 4.5:1 on `--panel` |
| `--accent` | `#8B5CF6` | Focus, selection. Outside the asset palette by design. |
| `--fail` | `#F0616D` | Guard failure |
| `--flag` | `#E5A13A` | Out of band |
| `--clean` | `#4ADE80` | Passed |

Type: a self-hosted geometric grotesk with a true monospace for every number and
measurement. **No CDN font link** — the console must render offline, so faces are
self-hosted or the system stack is used. Numbers are monospaced without exception;
comparing `0.92` against `0.50` in a proportional face is needless friction.

Spacing scale `4 / 8 / 12 / 16 / 24 / 32`. Density 9 means hairlines and alignment
carry grouping, not cards. Panes are separated by rules and negative space, never
boxed.

### Three findings drive the layout

**1. Never show a bare thumbnail.** The most expensive lesson of the episode-1
intake: the coin stack looked correct isolated and wrong composited, and the world
plates' scale error was invisible until a figure stood in them. Every asset view
has a composite pane, and it is the default. Isolated 1:1 is a toggle.

**2. Triage speed is the product.** Photo-culling tools converge on the same
grammar — grid then loupe then compare, keyboard ratings, auto-advance on decision.
That grammar transfers directly to 25 assets a batch. Mouse-driven review of a
long list is what makes review get skipped.

**3. Exception-first, and anti-rubber-stamp.** The HITL literature is blunt that
approving hundreds of items makes approval mechanical. Put judgement only where it
is needed: clean assets get a default and collapse, flagged assets sort first and
must be individually touched.

### Screens

| Screen | Purpose |
| --- | --- |
| **Batches** | Delivery folders found, per-batch counts, verdict summary |
| **Intake** | The core screen. Triage a batch asset by asset. |
| **Catalogue** | Browse and filter the library; coverage, gaps, pruning candidates |
| **Board** | The existing scene board, made interactive |
| **Runs** | Job state from `runtime/jobs/`, stage events, failures |

### Intake layout

Three panes: filmstrip left (fixed 240px), stage centre (fluid), verdict right
(fixed 340px). Full height via `100dvh`. The stage gets every pixel the other two
do not need.

- **Filmstrip.** Flagged first. Each row is thumbnail, `asset_id` in mono, and a
  status chip.
- **Stage.** The asset composited into a real frame: chosen world at its declared
  `figure_height`, figure inside `figure_zone` on `baseline_y`. Toggles to
  isolated 1:1, or side-by-side against the previously approved asset of the same
  id stem. Background is `--stage` and nothing else.
- **Verdict.** One row per check: name, measured value, expected value, status
  chip. Failures state both numbers in the same voice as the service errors. Then
  Promote / Reject / Skip.

### Status encoding — never colour alone

A coloured dot is the pattern both design skills flag, and colour-alone status is
a High-severity accessibility failure. Every status is encoded **three ways**:

| Status | Glyph | Colour | Text |
| --- | --- | --- | --- |
| Fail | filled square | `--fail` | `FAIL` |
| Flag | hollow triangle | `--flag` | `FLAG` |
| Clean | thin check | `--clean` | `OK` |

Shape alone must be readable in greyscale. This is not decoration; the marker
earns its place only because it carries real state, which is the exception both
skills allow.

### Keyboard

| Key | Action |
| --- | --- |
| `J` / `K` | Next / previous asset |
| `1` | Promote (advance) |
| `0` | Reject (advance) |
| `.` | Skip, leave undecided |
| `Space` | Toggle isolated 1:1 |
| `C` | Cycle composite world |
| `X` | Toggle side-by-side compare |
| `P` | Enter parallax scrub on a layered world |
| `Enter` | Open the commit dialog |
| `?` | Shortcut overlay |

A keyboard-first tool must be **keyboard-complete**: every action reachable by key
is also reachable by a visible control, and every control shows a visible focus
ring. Focus is never removed without replacement. When `J`/`K` moves the
selection, the filmstrip scrolls the focused row **fully** into view — a row half
behind a sticky header is a focus-obscured failure.

### Motion

Motion intensity 3. Transitions are 120 to 200ms on `transform` and `opacity`
only, on a custom easing curve rather than `ease-in-out`. Selection changes are
instant; a triage tool that makes you wait for a fade is broken.

Two kinds of motion, and only one of them is banned.

**Ambient motion on the asset is banned.** No fade-in on the stage, no scale
transition, no hover tilt, no idle drift of depth planes for visual interest.
Motion that alters the thing under judgement corrupts the judgement, and an asset
must be able to sit perfectly still while its colour, scale and density are read.

**Diagnostic motion is required, and it comes from Remotion.** A 2.5D world
cannot be verified as a still — plane misregistration is the defect layered worlds
are most prone to, and it is far more visible in motion.

The render lane already owns this. `EditorialMotion.tsx` implements
`foreground_parallax` as a per-layer camera with the world deliberately locked and
a `parallaxFactor` per layer, which is exactly what the catalogue's
`layers[].parallax_factor` feeds. The `render-unit` CLI already drives it.

**So the console does not implement parallax.** It calls `render-unit` against the
`EditorialMotion` composition and shows the result. Rendering a preview with a
different engine than the render lane means the preview can disagree with the
render, which is the class of bug the determinism discipline exists to prevent —
and this plan already forbids a second implementation of a rule the services own.
That rule applies to motion too.

This leaves a deliberate split, and it must be labelled in the UI rather than
blurred:

| Preview | Engine | Answers | Speed |
| --- | --- | --- | --- |
| **Placement check** | Pillow, in-process | Is the figure the right size, in the zone, on the baseline? | Instant, per keystroke |
| **Motion check** | Remotion `render-unit` | What will this actually look like, and do the planes hold? | Seconds, on demand |

The placement check is a geometry overlay and **never claims to be what the render
will look like**. The moment the question becomes "what will this look like", the
answer comes from Remotion. The console shows which engine produced whichever
frame is on screen, so the two can never be mistaken for one another.

Chrome transitions are 120 to 200ms on `transform` and `opacity` only.

**`prefers-reduced-motion` governs the console, never the artifact.** It is a
browser accessibility setting about the interface a person is operating. The video
preview is not interface — it is the product under review, and its motion is the
deliverable. Suppressing it because the operating system prefers reduced motion
would hide exactly what the operator opened the preview to judge.

So the rule is a boundary, not a global:

- **Console chrome** — panel transitions, focus movement, filmstrip scrolling —
  respects `prefers-reduced-motion` and drops to instant.
- **Video preview content** is never altered by it, or by any other display
  preference. The console does not modify what it is showing you.

Same principle as the achromatic stage: **a display or accessibility setting may
change the tool, never the artifact.** A console that quietly desaturates, slows
or stills the thing under judgement is lying to the operator.

### States

Full cycles, not only the success state: loading skeletons shaped like the final
layout rather than spinners; an empty state that says how to point the console at
a delivery folder; errors rendered inline beside the check that failed, carrying
the service's own message; and a distinct state for an asset whose file is missing
or whose digest does not match.

### Non-negotiables

- Nothing is promoted implicitly, ever.
- Every failure message quotes the measured value and the expected one.
- Status is never colour alone.
- `review_only` and `timing_basis: estimated` render as visible chrome, never as a
  silent property.
- Dark theme locked for the whole app; no pane inverts.
- Works fully offline. No CDN font, no external script, no telemetry.
- Desktop-first at 1440px and up. This is a dual-monitor tool; it does not pretend
  to be responsive to phones.

## Agent Routing

`docs/runbooks/PRP_EXECUTION.md` names roles — `speedster`, `junior_developer`,
`implementation_luna`, `architect_sol`, `explorer`, `docs_researcher`,
`reviewer`, `release_steward`. **None of those exist as dispatchable agent types
in this environment**, so a slice owned by a name alone cannot actually be
delegated. Each role is mapped to a type that dispatches, and the role is kept
because it still carries the intent — how much judgement the slice needs and
whether it may write.

| Runbook role | Dispatches as | Write access |
| --- | --- | --- |
| `speedster`, `junior_developer`, `implementation_luna` | `general-purpose` | Yes, within the slice's write set only |
| `explorer`, `docs_researcher` | `Explore` | No |
| `reviewer` | `Explore` | No |
| `architect_sol` | `Plan` | Plan and planning evidence only |
| `release_steward` | **parent only** | Git operations stay with the parent |

Rules that survive the mapping:

- **Every delegated diff is reviewed before integration.** A completion claim is
  not evidence; the parent reads the diff and runs the slice's validation itself.
- **Write sets never overlap.** Slices dispatched together must touch disjoint
  files, or they run in sequence.
- Architecture, protected boundaries, human gates and ambiguous debugging stay
  with the parent regardless of slice size.
- An agent is given the plan path, task id, allowed files, acceptance and
  validation command — never a vague brief.

## Task Slices

### T1: Console skeleton and catalogue read views
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/console/__main__.py`, `content/video_engine/console/app.py`, `content/video_engine/console/routes/catalog.py`, `content/video_engine/console/templates/`, `content/video_engine/console/static/`, `content/video_engine/tests/test_console_app.py`
- Acceptance: `python -m content.video_engine.console` serves on `127.0.0.1` with no build step and no network access; a catalogue view lists every asset with kind, tier, style version, review state and render eligibility, loaded through `asset_catalog.load_catalog` so an invalid catalogue surfaces the service's own errors rather than a stack trace; HTMX is vendored under `static/` and the page renders with JavaScript disabled apart from interactivity; routes contain no validation logic. The design tokens in **UX Design** ship as CSS custom properties in one stylesheet, fonts are self-hosted or system with no external request, and a test asserts the served HTML and CSS reference no off-origin URL so the offline guarantee is enforced rather than assumed.
- Validate: `python -m pytest content/video_engine/tests/test_console_app.py -q`
- Evidence: `console/{app,settings,__main__}.py`, `console/routes/catalog.py`, `console/templates/{base,catalog,error,empty}.html`, `console/static/console.css`. **13 tests green.** Served against the real 43-asset `systems-and-blowups` catalogue: 43 rows, style families, per-asset `figure_height`, plane counts and review state all render. An invalid catalogue surfaces `AssetCatalogError` verbatim — a world declaring `figure_height: 0.50` whose chair back implies 0.93 shows the service's own measured numbers, no traceback. Offline is enforced not assumed: a parametrised test strips comments and fails any template or stylesheet containing an absolute or protocol-relative URL or an `@import`, and a second test asserts the stylesheet defines the achromatic `--stage` and uses none of the six library palette colours. **Deviation:** HTMX is not yet vendored — T1 is read-only views and needs none, and fetching a third-party script mid-implementation was not authorised. Vendoring moves to T5, where interactivity first appears; the offline test already guards it.

### T2: Composite preview service
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/src/services/composite_preview.py`, `content/video_engine/tests/test_composite_preview.py`, `content/video_engine/console/routes/preview.py`
- Acceptance: given a world asset and one or more cutouts, renders a 1920x1080 frame honouring the world's `placement` — figures scaled to `figure_height`, feet on `baseline_y`, placed within `figure_zone`, and refused with a named error when the requested figure count exceeds `max_figures` or a figure would fall outside the zone; a layered world composites its planes back to front with the cast between `actor_or_machine` and `foreground_cutout`; two renders of the same inputs are byte-identical; output is written under `runtime/` and never registered as a catalogue asset. This renderer answers **placement only** — size, zone, baseline — and every frame it produces is labelled as a placement check rather than a render preview. It does not implement camera motion, parallax, or any other render-lane behaviour; motion is T10's job and belongs to Remotion. A layered world whose planes differ in dimensions is refused before compositing rather than producing a silently misaligned frame. Reproduces the episode-1 finding: two figures at 0.80 exceed every current world's clear zone and are refused with the measured widths.
- Validate: `python -m pytest content/video_engine/tests/test_composite_preview.py -q`
- Evidence: `src/services/composite_preview.py`. **15 tests green.** Geometry is split from pixels: `plan_composite` resolves scale, zone and baseline as pure arithmetic and is tested without images, `render_composite` composites. Layered worlds order planes back to front and place the cast after `actor_or_machine`, proven by a near-plane occlusion assertion; mismatched plane sizes are refused before compositing, naming both sizes. Two renders are byte-identical. Output lands under `runtime/` and is never registered. Every result carries `preview_kind: placement_check`. Run against the real v3 layered `world-home-living-v2`: 3 planes, zone 1056px, two figures placed at 0.50 inside `figure_zone` [0.45, 1.0]. **Two bugs found and fixed during implementation:** `(1.0 - 0.55) * 1920` truncated to 863px through binary float error, so a refusal misreported the zone by a pixel — now rounded; and `plan_composite` measured cutouts from unresolved relative paths, raising a bare Pillow `FileNotFoundError` while `render_composite` on identical inputs succeeded — it now takes `project_root` and names a missing file itself. **Finding:** the v3 worlds widened `figure_zone` to [0.45, 1.0] = 1056px, so two real cutouts now fit at 0.50 (644px), 0.76 (959px) *and* 0.80 (1008px). The v2 worlds could not seat two figures at any of those heights; the 0.76 standard is only reachable because the worlds were regenerated.

### T3: Asset measurement service
- Status: complete
- Owner: implementation_luna (dispatches as `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/src/services/asset_measurement.py`, `content/video_engine/tests/test_asset_measurement.py`
- Acceptance: reports, per asset, internal detail (silhouette eroded so it measures content not outline), frame occupancy, mean saturation and brightness, distinct colour count, alpha presence and the fraction of partially transparent edge pixels with their mean colour (the halo test), and for worlds the right-zone luminance flatness; reproduces the recorded episode-1 figures within tolerance — host detail 27.9%, civilian A 12.8%, objects 51.7%, and world clear-zone sigma of 4.9 to 7.6 against 62 to 71 — from the committed measurements in `23-EP1-LIBRARY-INTAKE-REVIEW.md`; pure measurement, no verdicts.
- Validate: `python -m pytest content/video_engine/tests/test_asset_measurement.py -q`
- Evidence: `src/services/asset_measurement.py`. **35 tests green.** Delegated to a `general-purpose` agent, diff reviewed by the parent. Split into `measure_frame` (pure arithmetic over arrays) and `measure_asset` (thin file wrapper), mirroring T2. Reports occupancy, internal detail with the silhouette eroded, alpha presence with the halo edge mean, colour statistics, and opt-in clear-zone sigma. A test walks the whole report and fails on any key that reads as a judgement, so "no verdicts" is enforced rather than asserted. **Parent found and fixed a silent total failure the agent's 34 tests all missed:** opacity was tested as `alpha == 255`, but the real episode-1 host tops out at **254** across the entire plate, so the whole figure classified as non-opaque and the service returned `fraction: None`. Every synthetic fixture used alpha exactly 255, so nothing caught it. Opacity is now a threshold (`>= 250`) with a regression test built on an alpha-254 fixture. **Calibration the agent could not do** — it searched only the Downloads worktree; the real assets live in the codex worktree. With the opacity fix, threshold 20.0 measures host 30.0%, civilian A 10.4%, objects 50.2% against the committed 27.9 / 12.8 / 51.7 — all three within 2.4 points, error falling monotonically across a 6-to-20 sweep. Residual recorded in the module: the committed figures used a central-difference gradient at threshold 12 and this uses Sobel/4 at 20, so the host:civilian ratio reads 2.9:1 rather than 2.2:1. The hierarchy claim holds; the exact ratio is operator-dependent and must be quoted as approximate.

### T4: Delivery intake and verdict pack
- Status: complete
- Owner: parent
- Depends on: T2, T3
- Write set: `content/video_engine/src/services/delivery_intake.py`, `content/video_engine/tests/test_delivery_intake.py`, `content/video_engine/console/routes/intake.py`, `content/video_engine/console/templates/intake.html`
- Acceptance: scans a delivery folder and emits one verdict per asset combining digest match, dimensions against the class contract, alpha requirement, `_scale_errors`, `_layer_errors`, `_style_errors` and the T3 measurements, each classified `fail`, `flag` or `clean` with the measured and expected values named; a folder containing the episode-1 v2 batch reproduces its known verdicts — self-promoted eligibility flags, tier-3 actors unreachable by the resolver, and the two interiors' implied 0.92 adult against a declared 0.50 — from fixtures; assets sort flagged-first; the service performs no writes.
- Validate: `python -m pytest content/video_engine/tests/test_delivery_intake.py -q`
- Evidence: `src/services/delivery_intake.py`, `console/routes/intake.py`, `console/templates/intake.html`. **15 tests green.** The verdict layer: `asset_measurement` measures, `asset_catalog` guards, this combines both into per-asset fail/flag/clean with the measured and expected values on every check. The three v2 defects are held as regressions — self-promotion fails naming the fields, a tier-3 actor fails as resolver-invisible, and the 0.93-implied interior fails with both numbers. `load_delivery` normalises review manifests (grouped lists, `far/mid/near` plane names) into catalogue shape in the service, so route and CLI cannot drift. Per-plane digests verified, not just the primary path. Run against the real v3 delivery: 15 assets, **0 fail, 7 flag, 8 clean** — the five in-scene plates flagged at world size (deliberate, why dimensions flag rather than fail) and two bright-edge halos. Console route smoke-tested against the same delivery. **Hardened during T5:** a manifest path escaping the delivery root now fails the digest check before anything reads it, and an unreadable image fails cleanly instead of crashing the scan.

### T5: Triage UI
- Status: complete
- Owner: parent
- Depends on: T4
- Write set: `content/video_engine/console/templates/`, `content/video_engine/console/static/console.js`, `content/video_engine/console/routes/intake.py`, `content/video_engine/tests/test_console_intake_routes.py`
- Acceptance: the intake screen renders filmstrip, composite stage and verdict pane as specified in **UX Design**; the documented keys work and a decision auto-advances; decisions are held in server-side session state and are reversible until commit; no route mutates the catalogue; a clean asset shows its default decision and a flagged asset requires an explicit one; the composite pane is the default view for any asset whose kind can be composited. Accessibility is acceptance, not polish: every status is rendered as glyph plus text plus colour and stays readable in greyscale, every keyboard action has an equivalent visible control, focus is never removed without replacement, moving the selection scrolls the focused filmstrip row fully into view, and console chrome collapses under `prefers-reduced-motion` while the video preview is never altered by it. The stage background is the achromatic `--stage` token and no chrome adjacent to an asset uses a colour from the library palette.
- Validate: `python -m pytest content/video_engine/tests/test_console_intake_routes.py -q`
- Evidence: `console/triage.py`, triage routes in `routes/intake.py`, `templates/triage.html`, `static/console.js`. **8 tests green.** Filmstrip, achromatic stage and verdict pane; flagged sort first and select first. Decisions are server-side (`TriageSession`), reversible via undo until commit, and policy is exhaustively small: clean defaults to promote, flags require an explicit decision, a failed asset can never be promoted from triage. The stage composites by default through T2 (1920x1080 placement frame against a catalogue world), isolates on request, and refuses a path escaping the delivery root. A catalogue byte-snapshot test proves no triage route mutates it. Keyboard is a shortcut layer over visible controls — J/K/1/0/./Space/C/Enter map to forms and links that exist on the page, so the tool is keyboard-complete rather than keyboard-only; the selected row scrolls fully into view. **Recorded deviation:** HTMX was not vendored. The triage screen needed ~50 lines of key-binding JS regardless, every action is a plain form or link (server-rendered state, full-page navigation on localhost), and zero dependencies beats fetching a third-party bundle. The offline scan now covers `.js` files too, closing review finding 12.

### T6: Commit — registration and promotion
- Status: complete
- Owner: parent
- Depends on: T5
- Write set: `content/video_engine/console/routes/intake.py`, `content/video_engine/src/services/asset_catalog.py`, `content/video_engine/tests/test_console_commit.py`
- Acceptance: commit routes every write through `asset_catalog.register_assets`, so the scale, layer, style-family, tier and digest guards all apply and a failing batch is refused with the service's own error text; promotion sets `rights_state`, `review_state` and `render_eligible` only for assets the operator explicitly promoted in this session; bulk promote is offered only for the zero-exception subset and states the count it will act on; the commit dialog lists every asset and field that will change before writing; the catalogue is written through `artifact_io.write_artifact` so the artifact hash is restamped; a commit attempt with any `fail` verdict in the batch is rejected.
- Validate: `python -m pytest content/video_engine/tests/test_console_commit.py -q`
- Evidence: commit routes in `routes/intake.py`, `templates/commit.html`, `templates/committed.html`. **8 tests green.** The dialog names every asset and every field that will change before anything is written, states the bulk count for the zero-exception subset, and lists undecided assets as excluded. Confirm writes only through `asset_catalog.register_assets` into the configured catalogue via `write_artifact`, so every guard applies and the artifact hash is restamped — both proven. Promotion fields are set exactly once, in the commit plan, on operator confirm. Defence in depth proven: a promote decision smuggled directly into the session past the triage policy is still rejected at commit; a duplicate id surfaces the catalogue service's own refusal verbatim. Paths are rebound relative to the project root, refusing files outside it. The session drops after a successful commit. **Deviation:** `asset_catalog.py` was in the write set but needed no change — `register_assets` already carried the required behaviour. **Live proof, read-only:** triage and commit dialog rendered against the real v3 delivery; with the real catalogue configured every asset flags on style because `ep1-index-funds-vox-newsprint-v3` is not yet in `style_families` — a genuine pre-commit blocker the console surfaced correctly, so no bulk was offered and no default promotion appeared. The real catalogue was not written.

### T7: Interactive scene board
- Status: complete
- Owner: implementation_luna (dispatches as `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/console/routes/board.py`, `content/video_engine/console/templates/board.html`, `content/video_engine/tests/test_console_board.py`
- Acceptance: renders the board built by `scene_board.build_board` with its existing flagged-first ordering and auto-selected defaults intact; the operator can change a selection and record it through `scene_selection`, never by writing the artifact directly; `timing_basis: estimated` renders as visible chrome carrying the existing warning that the render clock comes from audio; the static `render_board_html` output remains available and unchanged for offline sharing.
- Validate: `python -m pytest content/video_engine/tests/test_console_board.py -q`
- Evidence: `console/routes/board.py`, `console/templates/board.html`. **10 tests green.** Delegated to a `general-purpose` agent; parent verified no `approved` string exists in the route, confirmed all writes go through `record_scene_selection`, wired router and nav. Flagged-first ordering proven by flagging the *last* slot so builder order cannot fake it; auto-selected defaults pass through untouched; `timing_basis: estimated` renders the service's own render-clock warning as a visible banner. Every selection change re-records the full review through `scene_selection` — the same atomic unit the CLI uses — and a rejected candidate surfaces the service error verbatim with nothing recorded. The static `render_board_html` page is served byte-identical for offline sharing. Fixtures build all five input artifacts through the real pipeline services, inventing nothing. **Agent judgement accepted by parent:** the interactive board is metadata-only (no candidate thumbnails over HTTP) rather than widening the file-serving surface beyond the slice; the static board covers visual review.

### T8: Runs and status view
- Status: complete
- Owner: junior_developer (dispatches as `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/console/routes/runs.py`, `content/video_engine/console/templates/runs.html`, `content/video_engine/tests/test_console_runs.py`
- Acceptance: lists jobs under `runtime/jobs/` with stage state, recorded events, and failures surfaced with their stage-event text; read-only — no route advances a stage, approves a gate, or edits runtime output; a job with a degraded or failed stage is visually distinct and sorts first.
- Validate: `python -m pytest content/video_engine/tests/test_console_runs.py -q`
- Evidence: `console/routes/runs.py`, `console/templates/runs.html`. **23 tests green.** Delegated to a `general-purpose` agent, diff reviewed by the parent, router and nav link wired by the parent as planned. Reads through `FileBackedVideoJobRepository` so console and `cli.py status` see identical state; it never parses `job.json` itself. Read-only is proven three ways: route methods inspected, source scanned for write decorators, and a byte-level before/after snapshot of the runs directory across a GET. **Agent found a structural trap:** `FileBackedVideoJobRepository.__init__` calls `mkdir`, so constructing it on an absent path is itself a write — the route probes `is_dir()` first, with a test asserting an absent runs directory is not created by rendering the view. **Recorded deviation:** the slice asked for a "degraded" state that does not exist in this engine; nothing writes it. The agent mapped the real recorded vocabulary onto the three-way encoding in one documented place — fail = run failed or any failed stage event; flag = `awaiting_*`, the parked-and-not-progressing analogue; clean = everything else.

### T9: Generation request pack — export only
- Status: complete
- Owner: parent
- Depends on: T6
- Write set: `content/video_engine/console/routes/generate.py`, `content/video_engine/console/templates/generate.html`, `content/video_engine/tests/test_console_generate.py`
- Acceptance: renders the compiled visual prompt pack for a coverage artifact and offers it for copy and for export to a file, so the operator can paste it into a browser generation session; a monkeypatched socket proves no route in this slice opens a network connection; the expected delivery folder and filenames are shown so intake can bind the result; the provider API adapter is **deferred** and explicitly out of scope until a provider and spend control are chosen.
- Validate: `python -m pytest content/video_engine/tests/test_console_generate.py -q`
- Evidence: `console/routes/generate.py`, `console/templates/generate.html`. **10 tests green.** Delegated to a `general-purpose` agent; parent reviewed the diff, confirmed zero provider/key/URL references in route and template, wired the router and nav. Renders the compiled prompt pack per slot in copyable readonly blocks with the identity anchor and negative prompt; exports through `artifact_io.write_artifact` into `runtime/generation-requests/` only, with path-shaped names refused. Shows the expected delivery layout — `review/<lane>-<coverage_hash[:8]>/`, a manifest skeleton in `delivery_intake`'s exact shape, and the per-kind `CLASS_DIMENSIONS` table imported rather than duplicated — so a browser-generated batch drops straight into `/intake`. The no-network guarantee is a monkeypatched `socket.socket.connect` test; the agent found and documented a Windows asyncio quirk (the proactor loop's self-pipe uses a loopback connect) and scoped the guard to the routes rather than asyncio's plumbing. Provider adapter remains deferred and the template says so.

### T10: Motion preview through the render lanes
- Status: complete
- Owner: parent
- Depends on: T5
- Write set: `content/video_engine/console/routes/preview.py`, `content/video_engine/console/templates/`, `content/video_engine/tests/test_console_motion_preview.py`
- Acceptance: the console implements no motion of its own — no camera, parallax, easing or timing arithmetic — and a test asserts no such arithmetic exists in the console package. It routes to whichever lane already owns the behaviour, per the ownership table in `19-HYPERFRAMES-LANE.md`: **camera transforms and layer composition go to Remotion** (`editor/`, the `EditorialMotion` composition), and a **quick provisional motion look goes to HyperFrames** as an `animatic_preview` unit via `render-unit`, which is estimated-timing and explicitly never publishable — the correct status for a preview artifact. A layered world's `layers[].parallax_factor` is passed through to the composition's existing `parallaxFactor` rather than reinterpreted. Previews are operator-triggered on `P`, never on load or hover; the stage returns to its still placement frame on exit; render failures surface the lane's own stderr; the UI stays responsive while a render is in flight; `--dry-run` is used wherever the question is "would this render" rather than "what does it look like".
- Validate: `python -m pytest content/video_engine/tests/test_console_motion_preview.py -q`
- Evidence: `console/routes/preview.py`, `console/templates/motion.html`. **7 tests green.** The console presses buttons and owns no motion: HyperFrames animatic previews go through `cli.py render-unit` (with `--dry-run` for "would this render"), the Remotion lane through `verify-editor --smoke`. A structural test greps every console module and fails on easing/interpolate/bezier/keyframe code and on any *arithmetic* over `parallax` — while explicitly permitting the commit path's verbatim `parallax_factor` copy, which is the passthrough the plan requires; the first draft of the test banned the copy too and was refined rather than the code weakened. Renders run in a daemon thread with a polled pending state (meta-refresh, no JS), the catalogue route proven responsive mid-render, lane stderr surfaced verbatim, a missing unit file refused before any process starts. `_run_command` is the single process boundary and the only thing tests monkeypatch.

### T11: Preview of un-promoted assets — resolve the fail-closed tension
- Status: complete
- Owner: parent
- Depends on: T10
- Write set: `content/video_engine/src/services/hyperframes_render.py`, `content/video_engine/configs/hyperframes_unit.schema.json`, `content/video_engine/tests/test_hyperframes_preview_gate.py`
- Acceptance: **this is a real conflict, not an oversight.** The HyperFrames flow resolves assets by manifest membership, review status and sha256, and **fails closed** — while the entire point of the console is to judge assets *before* they are promoted. Resolve it explicitly rather than by loosening the gate: an `animatic_preview` unit may reference `review_only` assets **only** when the unit declares a preview intent, its output is written to a quarantine path that render and publish paths never read, and the artifact is stamped provisional; every other unit kind keeps failing closed on review status exactly as today. A preview unit that omits the intent, or a publishable unit kind that names a `review_only` asset, is rejected naming the asset. A test proves a quarantined preview cannot be promoted into an asset manifest or reached by a publish path.
- Validate: `python -m pytest content/video_engine/tests/test_hyperframes_preview_gate.py -q`
- Evidence: `hyperframes_render.py`, `hyperframes_unit.schema.json`. **7 tests green, 11 existing HyperFrames tests unbroken.** The conflict is resolved by explicit opt-in, not a loosened gate: `preview_intent: "quarantined_review_preview"` is valid only on an `animatic_preview`; with it, review-status fails open for that unit alone while digest binding, extension and presence checks stay fully enforced ("a preview of the wrong bytes is worse than no preview" — proven). Without the intent an animatic fails closed exactly as before; the intent on a publishable kind is rejected naming the kind. Output lands under `renders/quarantine/` and the summary stamps `provisional/publishable:false/quarantined`. **The quarantine is enforced, not conventional:** `resolve_assets` refuses any manifest entry pointing into the quarantine directory — even in a fully approved manifest, and even for another preview — so a quarantined render can never be laundered into the asset flow.

## Verification

```bash
python -m pytest content/video_engine/tests/ -q
```

- Full engine suite green apart from the five pre-existing
  `test_history_v4_pipeline.py` failures tracked as `task_5672544a`.
- `python scripts/prp_validate.py .claude/PRPs/plans/P15-OPERATOR-CONSOLE.plan.md`
- Manual: start the console, intake the episode-1 v2 delivery folder, confirm the
  known defects are reported without reading any JSON by hand, and confirm no
  asset is promoted without an explicit action.
- Offline check: run with networking disabled; every screen must render.

## Evidence And Handoff

**Status: complete, 2026-08-23.** All 11 slices done (10 built, T14-style deferrals none — the provider adapter inside T9 remains deferred by design, not incomplete).

- Full suite: **684 passed**, 5 pre-existing `test_history_v4_pipeline.py` failures (tracked `task_5672544a`), none introduced.
- Plan validates via `scripts/prp_validate.py`.
- Live smoke: all nine surfaces (`/`, `/catalog`, `/intake`, `/board`, `/generate`, `/preview/motion`, `/runs`, both static files) return 200 on an unconfigured app and against the real project.
- The manual verification ran against the **v3** delivery (the v2 batch predates the manifest convention and has no delivery folder): 15 assets scanned, verdicts on screen with measured/expected values, zero promotion possible without explicit action — and the scan surfaced a real blocker, the undeclared v3 style family. The v2 defects are held as regression tests in `test_delivery_intake.py` instead.
- Offline guarantee enforced by tests: no off-origin URL or `@import` in any template, stylesheet or script; fonts system/self-hosted.
- Console totals: 5 route modules, 10 templates, 2 static files, 3 new services (`composite_preview`, `asset_measurement`, `delivery_intake`), 1 session module (`triage`), ~118 console/service tests.

### Open follow-up: the stage should probably be light, not dark

Raised by the operator after delivery, and I think they are right — recorded here
rather than silently changing a closed plan, because it reverses a rule this plan
argued for.

The dark-stage rule was borrowed from photo-culling tools, whose assets carry a
full tonal range and no fixed destination. **These assets ship onto cream worlds.**
The delivery ground is light, so judging on dark is judging in the wrong viewing
condition — and specifically, the halo check flags *bright* matte edges, which are
maximally visible on a dark stage and nearly invisible on the cream world where
the asset actually lands. The dark stage was hiding the defect that matters in
delivery. Print proofing has the same rule: proof on the substrate.

Proposed, not applied:

- `--stage` becomes a neutral desaturated near-white (`#E9E8E5`), default view
- A three-way ground toggle in the stage bar keeps both truths reachable —
  **light** ("does this defect matter?"), **dark** ("does this defect exist?",
  edge artifacts pop), **delivery** (the actual cream, in context)
- The achromatic principle is unchanged; only the *value* was wrong. No tint on
  any of the three.

Cost: one token, one toggle, and the `test_console_app.py` assertion that
currently pins `--stage: #1b1b1d`. A mock-up of the light stage exists as a
Claude Design project ("Video Engine Console" → `Triage.dc.html`), reachable via
the design tooling's project list.

### Open follow-up: the v3 style family is undeclared

Triaging the real v3 delivery flags every asset on style because
`ep1-index-funds-vox-newsprint-v3` is in no `style_families` group in the
catalogue. This is the console working correctly, and it blocks commit until the
operator decides whether that version joins `ep1-index-funds` or forms its own
family. One line either way.

- Deviations recorded inline per slice: HTMX replaced by ~50 lines of vanilla JS; `asset_catalog.py` unchanged in T6; runs "degraded" state mapped to the engine's real vocabulary; T2 owner moved to parent.

Pending. On completion record: the console entrypoint, the three new service
modules with their test counts, route smoke-test counts, a screenshot of the
intake screen showing a flagged asset with its measured verdict, and the
byte-identical composite preview proof.

Open decisions carried into implementation:

- Whether the console reads the catalogue from the active worktree or takes a
  project root argument. The episode-1 delivery landed in a different worktree
  from the code, so a project-root argument is likely required from T1.
- Session state store for held decisions. In-memory is sufficient for a single
  operator; a crash losing an uncommitted triage pass is acceptable and cheaper
  than persistence.
