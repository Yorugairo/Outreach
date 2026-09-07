# remotion-ui intake — seven components, gated and triaged (2026-09-07)

The same morning as the HyperFrames harvest, seven `remotion-ui` components were installed as references under
`content/video_engine/remotion-ui/`. This page is the triage; the per-component record — install command, landing paths,
verbatim props with `file:line`, the maths and its recorded failures — is
`content/video_engine/remotion-ui/HARVEST-2026-09-07.md`.

**Pinned CLI: `remotion-ui@0.9.0`**, quoted from `content/video_engine/remotion-ui/package.json:6`
(`"add": "npx --yes remotion-ui@0.9.0 add"`). The project it expects is Remotion 4
(`content/video_engine/remotion-ui/remotion-ui.json:5-8`).

**Licence: [UNVERIFIED]** — no `license` field in `package.json`, no `LICENSE` file in the folder, no per-file header.
Reference only until someone reads the licence off the registry.

**Installed as references; loading into a workspace is a separate step per component** — a Remotion 4 project with the
`@/remotion/lib/*` aliases (`remotion-ui.json:10-16`) on the import path and the npm deps (`remotion`,
`@remotion/transitions`, `@remotion/google-fonts`, `maplibre-gl`) present; none of that exists here. Ours is not a Remotion
player, so a port means re-expressing the maths in
`docs/content-video-engine/samples/scene-evidence-player.template.html` or in a
`content/video_engine/scripts/kinetics/*.mjs` module — mechanism only, never the runtime, exactly as the HyperFrames harvest
did.

## The seven

| id | component | landed |
|---|---|---|
| RU-1 | svg-mask-reveal | `src/remotion/primitives/svg-mask-reveal.tsx` + `lib/motion-tokens.ts`, `lib/path-morph.ts`, `lib/timing.ts` |
| RU-2 | badge-stamp | `src/remotion/primitives/badge-stamp.tsx` + `lib/motion-tokens.ts`, `lib/timing.ts` |
| RU-3 | map-flight | `src/remotion/scenes/map-flight/index.tsx` + `primitives/map-markers.tsx`, `primitives/map-route.tsx`, `lib/map-utils.ts`, `lib/layout.ts`, `lib/motion-tokens.ts`, `lib/timing.ts` |
| RU-4 | news-ticker-bar | `src/remotion/scenes/news-ticker-bar/index.tsx` + `lib/code-syntax.tsx`, `lib/motion-tokens.ts`, `lib/timing.ts` |
| RU-5 | spatial-push | `src/remotion/primitives/spatial-push.tsx` + `lib/transition-timing.ts`, `lib/springs.ts` |
| RU-6 | transition-card-flip | `src/remotion/primitives/transition-card-flip.tsx` + `lib/transition-timing.ts`, `lib/springs.ts` |
| RU-7 | transition-clock-wipe | `src/remotion/primitives/transition-clock-wipe.tsx` + `lib/transition-timing.ts`, `lib/springs.ts` (the sweep itself lives in `@remotion/transitions/clock-wipe`, not installed) |

## The triage

### Priority integration — cheap, sound, and lands in work already in flight

| component | our nearest | gap | why |
|---|---|---|---|
| **RU-2 badge-stamp** | `stopaction.mjs` (throw/land, contact shadow, ground dip), `spring.mjs` `springPop`/`springEval`, `squash.mjs`, the docks that spring/throw/land (E45), `snap`, `callout`, `bracket` | (i) a stamp/seal arrival — no page species (`build_to`, `bracket`, `retitle`, `relight`, `undraw`, `figure`, `note`) stamps a verdict; (ii) the **two-spring offset**: a clamped scale spring landing while a free rotation spring is still unwinding | The offset is the weight cue our single-spring landings lack, and it is the continuous cousin of HF-2's one-frame lag already booked into P47 T1. The split shock curves (linear life, eased expansion to 2× radius) fix a failure the source names — an impact ring nobody sees. `exitAtInFrames` ships the E50 shape: a landed mark owes an exit. Under E51 a landed stamp is a legitimate anchor for a push-in. Look does not port: charcoal-on-cream, drawn in our hand, not a gold ring. |

### Backlog — real gaps, bounded builds, nothing in flight

| component | our nearest | gap | why |
|---|---|---|---|
| **RU-1 svg-mask-reveal** | `snap` (a landed card grows to become the world), `mount`, `suck`, the restored hard-edge clip wipe, `stroke.mjs` draw-on, `undraw`, `radial`, `arap.mjs` | A shape-masked reveal from an **arbitrary origin**, with a coverage law that guarantees it covers: `reach = max hypot to the four corners`, `scale = progress · reach · 2 / 100` (`svg-mask-reveal.tsx:90-98`) | Three lines of maths, no new runtime and no new species: it is the correct generalisation of `snap` for the common case where the card that landed is off-centre. The mask is binary (rect + path fill), so it cannot read as a fade — on the right side of the 2026-08-30 rejection. `invert: true` is an E50-shaped exit: the shape shrinks back over the content instead of the thing simply staying. |
| **RU-4 news-ticker-bar** | the `ticker` species (internals [UNVERIFIED] — not read in this pass), `note`, `retitle`, the docks (E45) | The seam-free modulo wrap against a stable upper-bound width, the gradient dissolve at the crawl's right edge, and `holdSeconds` as a **life** on a standing element | The chrome is broadcast-dark and off-brand, so nothing lands as-is on a cream page; the three mechanisms are small and portable into the `ticker` we already have. `holdSeconds` is E50 applied to furniture: a deployed element that never leaves is filler. Take it the next time a script asks for a crawl. |

### Explore — a register question, to be settled by eye, not by catalogue

| component | our nearest | gap | why |
|---|---|---|---|
| **RU-6 transition-card-flip** | `dip`, `spiral`, `mount`, `suck`, `cut` (E47/E48), `snap`, HyperFrames `morph-swap` "condense" | A page that turns over to become the next page: same rectangle, other face. `snap` grows, `morph-swap` condenses through a shared silhouette, `dip` goes through black — none of them flips | On theme (the world is paper) and on the right side of the rejected-wipe precedent: a hard, opaque hand-off with backface culling and an explicit rule that the page background must never show, so it cannot degrade into the fade that killed the 2026-08-30 port. The risk is register — a full-frame flip is a game-show move unless it is earned, and E48 says the primaries are decided by the next builds' curves. Test: one authored flip on a build page, watched against `dip` and `spiral`. Take the seam rule (`transition-card-flip.tsx:81-86`, only the outgoing layer paints the backdrop) regardless — it is the general answer for any transition that can expose the page. |

### Index — recorded, not ported

| component | our nearest | gap | why |
|---|---|---|---|
| **RU-3 map-flight** | nothing geographic; `trace` + `stroke.mjs` draw-on, the chart card (`scripts/chart_card.py`), `pull_back` / `focus_zoom` | Real geography — a route on a live map | The gap is filled by a runtime (MapLibre, tile style URL, network fetch, a per-frame `delayRender` handshake), not by a formula, and a dark tile map is the opposite of the cream ledger page. If a script ever needs a trade route, the honest path is a still plate with our `trace` over it. Two ideas travel: the drawn route split from the camera route, and the altitude ramp keyed to keep a recognisable edge in frame (`index.tsx:105-117` records the failure at 2,200,000 m — open water reads as a failed render). |
| **RU-5 spatial-push** | the `push` species; `dip`/`spiral`/`mount`/`suck`/`cut`; and HyperFrames **page-slide**, already harvested with the operator's "*much cleaner page slide than ours*" | **No gap** — page-slide holds the same move plus the outgoing 0.94 parallax scale this lacks | Keep one line: the `lead: 1` lock (both panels travel the whole window; a shorter lead desynchronises them and opens a gap onto the background — `lib/transition-timing.ts:98-101`), which applies to page-slide too. Read against E51 the component splits: the translate half is a page seam and E51 does not bite; the `tilt`/`perspective`/1.06-overscan half is exactly the untethered flourish E51 calls filler — and the source itself defaults `tilt = 0` and warns it exposes bare background. If we ever author it: tilt 0 unless a card has just landed and the push carries that card. |

### Reject

| component | our nearest | gap | why |
|---|---|---|---|
| **RU-7 transition-clock-wipe** | the restored hard-edge clip wipe (E47, an effect not a primary), `radial`, `spotlight` | None | The file is plumbing: it resolves the frame size and delegates to `@remotion/transitions/clock-wipe` (`:2`, `:26-34`), a package not installed here — so there is no local maths to port and the sweep's geometry is [UNVERIFIED] from anything on disk. The wipe question is already settled by measurement: E47 §3 retired the wipe as a default and the reference wipes 0 of 99 boundaries (`HYPERFRAMES-INTAKE-2026-09-06.md` §1.3). Broadcast-sports register competing with `radial` and `spotlight` for a beat neither earns. |

## What to do first

1. **Change nothing today.** The template, the kinetics modules, the compiler and the gates stay exactly as they are; every row above is a candidate, not a task (the harvest rule, unchanged from HyperFrames).
2. **RU-2 into P47's landing work:** port the two-spring offset (clamped scale, free trailing rotation) and the split shock curves into `spring.mjs` / `stopaction.mjs` behind a flag, drawn in our hand, with the exit authored from the first build.
3. **RU-1 as a three-line law:** take `reach = max hypot to the four corners`, `scale = progress · reach · 2 / 100` into the template's `snap`/mount so an off-centre reveal always covers, and `invert` as the E50 un-draw.
4. **RU-6 as one authored beat:** flip a single build-f page and watch it against `dip` and `spiral` before it is discussed as a primary; take the outgoing-layer-paints-the-backdrop rule immediately, since it is a correctness fix for any transition that can expose the page.
5. **Then leave the rest alone:** RU-7 is rejected, RU-3 and RU-5 are indexed, RU-4 waits for a script that wants a crawl — and read a licence off the registry before any of this code is quoted into a shipped file.
