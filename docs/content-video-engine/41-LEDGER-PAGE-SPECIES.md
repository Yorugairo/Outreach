# 41 — THE LEDGER PAGE SPECIES (component doc)

Status: BUILT 2026-09-03 (P35 T0–T4, T9); picks open. Ruling E22 + addenda
(docs/portable/OPERATOR-RULINGS.md); doctrine doc 29 §9.26 (the page), §9.27
(the motion menu), §9.28 (surface grammar). This page is the component
contract an implementer or reviewer needs; the *why* lives in doc 29.

## 1. What it is

A world plate that IS a chart. Not a dock: the page fills the frame, the
chart is built on it from a series we own, and docks may still land on it in
its declared quiet zone. It is the channel's signature and the payoff chart
of every episode by default.

## 2. The five beats (all derived from `t`, seek-safe)

| # | Beat | Window | Mechanism (player) |
|---|---|---|---|
| 1 | Unravel | 0 – 0.7s | the plain cream page rolls out left→right (`translateX`, never clip-path), a curl-shadow band riding the front |
| 2 | Half savor | 0.7 – 1.5s | the page holds, empty |
| 3 | The field | 1.5 – 3.9s | **preferred:** the generated inked plate (`page.field_plate`) cross-fades over the cream page · **fallback:** `page.field = "scribble"` (seeded strokes drawn one at a time, nib at the front) or `"soak"` (feathered seeps that creep, flood and saturate). Either fills the BOARD (left 6% / top 8% / 88% × 84%, radius 46px) to a definite edge |
| 4 | The line + ink | 3.9 – 4.7s (+ ink to 5.9s) | the outline draws clockwise EXACTLY on the board's box and radius (conic sector, hollow centre); title and source are written per glyph with a seeded ±1.6° tilt |
| 5 | The build | 4.7 – 7.7s | `story`: bars grow from the baseline in reading order, labels then values, the emphasized datum takes the accent pill whose number rolls and lands on the exact string · `dense-line`: dash-offset draw with a tip head, inline series names de-collided (§9.23b). Axes and grid appear only in this beat |

Constants: `const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, OUTLINE: 0.8, INK: 2.0, BUILD: 3.0 }` in the template. The gate reads the same offsets (`PAGE_BEAT_OFFSETS`).

Refused on sight (do not retry): blob bloom-and-contract "bleed"; any gap
between ink and outline; coffee-ring stains on the margin; a charcoal halo
overrunning the board unevenly; fibre texture on the paper. The operator's
line: *"just a plain cream background, then the scribble/soak, then the line
draw."*

## 3. The page spec (`ledger_page.v1`) — what the template consumes

Produced by `content/video_engine/scripts/ledger_page.py` from a
`series.json`, embedded on the scene as `world.page`:

| Field | Meaning |
|---|---|
| `builder` | `story` (≤12 values) · `dense-line` (>12 points or >1 series) · `race` · `decline` · `combo` — picked by data shape and variant (`pick_builder`), never merged |
| `variant` | `line` / `bars` / `race` / `decline` / `progress` |
| `title`, `sub`, `source` | written on the page; `source` is mandatory (no source, no page) |
| `values`, `labels`, `value_strings` | `value_strings` are the file's own tokens, verbatim — the callout lands on them, nothing re-rounds |
| `series`, `axes` | dense shapes only, passed verbatim (log, xticks, hlines, panels…) |
| `emphasize`, `quiet_zone` | the accented datum; `left` / `right` — the side docks may land on and where stage captions sit |
| `plate` | asset id of the GENERATED blank washi page (world plate, spine register). CSS cream `#F4E6C7` is the fallback and reads dull |
| `field_plate` | asset id of the generated page with the board inked; cross-faded in beat 3 |
| `field` | `scribble` / `soak` — the procedural fallback when no `field_plate` is approved |

Validation: `python content/video_engine/scripts/ledger_page.py <series.json> --variant bars --emphasize 7 --quiet-zone right`
refuses a missing source, unaligned labels, a race without periods, a
checklist table ("keep it a dock").

## 4. Authoring — the shot-table row

```
( start, end, "ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>]]", ken_burns, [docks], exit )
```

`build_scene_timeline_f.world_for_plate` resolves it to
`{"kind": "ledger", "page": <spec>, "ken_burns": …}`; a missing series or a
validator error fails the build naming the row. Ken Burns on a page is a slow
push only (capped at 0.03). The compiled timeline declares `species:
["ledger", …]`.

Surface choice is decided by doc 29 §9.28 (A1–A3 earn the page; B1–B4 keep
the dock; C1–C6 choreography at a boundary; D1–D4 density) and recorded per
window in `build-f/SURFACE-CENSUS.md`.

## 5. Plates

Claim `steel-and-paper-ledger-page-v1` (style family
`woodblock-vox-newsprint-v2`, reference `world-ledger-page-v1.png`):

- `world-ledger-blank-page-v1` — the blank cream washi page, 1920×1080, no objects, no text.
- `world-ledger-inked-board-v1` — the same page with the board inked solid charcoal in the exact geometry above.

Fulfilled headless by Codex from the rendered `WORK-ORDER.md`; output stays
in `review/claims/<claim>/` until the operator approves the contact sheet;
only then do `plate` / `field_plate` point at approved ids.

## 6. Sound

`sound/SOUND-PLAN.json` → `page_cues` (page-relative): paper slide at
roll-out, drop settle at +2.8s, chalk stroke at the outline's draw-complete.
CC0, matched to the whoosh at −14 LUFS ±1 LU; `sound/SOURCES.md`.

## 7. Gates

- `gate_motion_density.py`: a page's five beats count as visual events, its
  start as an evidence entry (M03), its hold is still (needs a dock, plate
  life or stage captions past 12s). Dock events come from the timeline's own
  `scenes[].docks`.
- `render_episode.py` refuses a full render while `GATES-MOTION.md` says FAIL.
- Determinism: two seeks to the same second give an identical stage
  (`innerHTML` sha checked on the proof); no `Math.random`, no wall clock.

## 8. Open picks (the operator's)

1. **The field** — inked plate (two-plate build) vs scribble vs soak, from the
   contact sheet and the proof.
2. **The font** for the ink writes (Inter until picked; no generic cursive).
3. **Race on a page** — confirm it reads as a ledger, not a dashboard.
4. **The plates** — approve `world-ledger-blank-page-v1` / `-inked-board-v1`.

## 9. Review checklist for this component

- [ ] Proof: `http://localhost:8731/ledger-species-proof.html` (episode-player server on build-f) — seek 1.2 / 2.8 / 4.5 / 8.5 / 15.8 / 21.5
- [ ] Hyperframes candidates (the first stitch, for the record): `content/video_engine/hyperframes/renders/ledger-page-v1-{A,B,C}.mp4`
- [ ] Doc 29 §9.26 addenda read in order; refusals honoured
- [ ] `SURFACE-CENSUS.md` PAGE candidates vs the re-script's three pages
- [ ] Claim delivery contact sheet
