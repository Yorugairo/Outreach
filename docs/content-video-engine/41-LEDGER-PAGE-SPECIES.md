# 41 — THE LEDGER PAGE SPECIES (component doc)

Status: BUILT 2026-09-03 (P35 T0–T9); the field and the plates are decided (the deckle); the font and the race read stay open. Ruling E22 + addenda
(docs/portable/OPERATOR-RULINGS.md); doctrine doc 29 §9.26 (the page), §9.27
(the motion menu), §9.28 (surface grammar). This page is the component
contract an implementer or reviewer needs; the *why* lives in doc 29.

## 1. What it is

A world plate that IS a chart. Not a dock: the page fills the frame, the
chart is built on it from a series we own, and docks may still land on it in
its declared quiet zone. It is the channel's signature and the payoff chart
of every episode by default.

## 2. The seven beats (all derived from `t`, seek-safe)

| # | Beat | Window | Mechanism (player) |
|---|---|---|---|
| 1 | Unravel | 0 – 0.7s | the plain cream page rolls out left→right (`translateX`, never clip-path), a curl-shadow band riding the front |
| 2 | Half savor | 0.7 – 1.5s | the page holds, empty |
| 3 | The field | 1.5 – 3.9s | **DECIDED (E22 addendum 4): the deckle is the feature.** The inked plate (`page.field_plate`, made procedurally from the blank page: charcoal fills the paper up to its deckle edge, 94% so a whisper of fibre survives) cross-fades over the plain page; the deckle edge appears only as the ink arrives. Fallbacks when no inked plate exists: `page.field = "scribble"` or `"soak"` filling the board box |
| 4 | Ink | 3.9s → (+2.0s) | **E22 addendum 7 (2026-09-03): the outline is RETIRED** - "it looks like a cool animation, but it's useless here, not pulling weight." The charcoal arriving on the cream ground IS the edge. Title and source are written per glyph in Kalam (HG2 decided) with a seeded ±1.6° tilt, as the punch begins. `page.board` stays (punch centre, chart box); `page.edge_path` is accepted and inert |
| 5 | Punch in | 3.9 – 4.4s | the page zooms about the board's centre (×1.16), cropping the deckle margin out — the room we spend (E22 addendum 6) |
| 6 | The build | 4.4 – 7.4s | `story`: bars grow from the baseline in reading order, labels then values, the emphasized datum takes the accent pill whose number rolls and lands on the exact string · `dense-line`: dash-offset draw with a tip head, inline series names de-collided (§9.23b). Axes and grid appear only in this beat |

| 7 | The focus | 7.4s → | the page's declared `focus` (callout / spotlight / punch) fires on its datum — the page ends pointing at the proof, never as homework (E25) |

Constants: `const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, PUNCH: 0.5, INK: 2.0, BUILD: 3.0 }`, focus at 7.4s, in the template. The gate reads the same offsets (`PAGE_BEAT_OFFSETS`).

Refused on sight (do not retry): blob bloom-and-contract "bleed"; the
drawn outline itself (addendum 7); any gap between ink and edge; coffee-ring stains on the margin; a charcoal halo
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
| `punch` | `false` on a host plate: the punch is skipped, his gesture is the direction |
| `chart_box` | `{x, y, w, h}` measured clear of the host's hand (derive_host_boards); the chart fits it instead of the board |
| `caption` | `"anchor"` pins the captions to the lower third for the page (a host plate's quiet zone is the host's) |
| `focus` | `{kind: callout \| spotlight \| punch, target?, label?, dur?}` — the focus action fired at the build's end; target defaults to the emphasized datum |
| `board` | `{x, y, w, h}` fractions of the frame — the deckle's innermost rectangle, MEASURED from the blank plate's paper mask; the line, the field fallback and the chart share it; default 0.06 / 0.08 / 0.88 / 0.84 |
| `edge_path` | accepted and inert since E22 addendum 7 (the deckle boundary was traced for the retired outline) |
| `plate_zoom` | overscan for a page plate (not used for the deckle page: the white beyond the deckle is part of the look) |

E28 (2026-09-03) rules in the validator: a bar's value is SIGNED (a drop goes down from the
zero baseline; the sign hidden in a `note` is a FAIL); a date axis with uneven gaps raises
a `[JUDGE]` row (printed by the CLI, carried on the spec as `judge`) naming the gaps and the
file's `selection` rule, which the sub must state on the page. `unit` (e.g. `%`) is written
on the zero tick and every value. The hand is **Kalam** (Human Gate 2, decided 2026-09-03).

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

- `world-ledger-blank-page-v1` — the blank cream washi page with its deckle (delivered on white).
- `world-ledger-inked-board-v1` — the delivered rounded-board version (retired: the deckle is the feature).
- `world-ledger-blank-page-cream-v1` / `world-ledger-inked-deckle-cream-v1` — DECIDED: the page composited onto the cream token, and the same with the charcoal filled to the deckle (made procedurally from the blank page).

DELIVERED 2026-09-03 (Codex headless; `claim-resume` scanned: 2 flagged, 0 failed). The inked board measures x 0.0635 / y 0.0694 / w 0.8693 / h 0.8602 of the frame; the blank page carries a white deckle rim (overscan 1.05 in the proof; re-order full-bleed). Proof with both plates: scene 1 of `ledger-species-proof.html`. Output stays
in `review/claims/<claim>/` until the operator approves the contact sheet;
only then do `plate` / `field_plate` point at approved ids.

## 5b. The host at the board (C5 addendum, 2026-09-03)

Host-on-board plates are page plates (`plate` / `field_plate`) in which the
host stands at the inked board in the page's quiet zone. The chart builds
in the board he points at; the focus action lands on the datum, never on
him. Claim `steel-and-paper-host-board-v1`: three poses (presenting at the
board, pointing at its upper area, turned to it from the left), each
delivered as the inked-board state; the blank state is derived by
returning the board region to cream paper so the host is identical across
the beats. DELIVERED 2026-09-03 (claim-resume: 3 flagged, 0 failed): `host-board-present-v1`, `host-board-point-v1`, `host-board-turned-v1`; blank states derived (`*-blank.png`, only charcoal pixels return to paper so the host's arm survives); boards, hand clearance and quiet zones measured into `host-boards.json`. The pointing pose runs scene 1 of the proof. Interim: the host cut-outs in
`assets/generated/cutouts/actor-host-*.png` may throw in via plate life on
the quiet zone (proof scene 1), but the brand sheet's rule stands - the
host lives in the plate, never as a cut-out over evidence.

## 6. Sound

`sound/SOUND-PLAN.json` → `page_cues` (page-relative): paper slide at
roll-out, drop settle at +2.8s, chalk stroke re-cued to the punch (3.9s) now
that the outline is retired (addendum 7).
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

1. ~~The field~~ DECIDED: the two-plate build with the charcoal filled to the deckle.
2. **The font** for the ink writes (Inter until picked; no generic cursive).
3. **Race on a page** — confirm it reads as a ledger, not a dashboard.
4. **The plates** — approve `world-ledger-blank-page-v1` / `-inked-board-v1`.

## 9. Review checklist for this component

- [ ] Proof: `http://localhost:8731/ledger-species-proof.html` (episode-player server on build-f) — seek 1.2 / 2.8 / 4.5 / 8.5 / 15.8 / 21.5
- [ ] Hyperframes candidates (the first stitch, for the record): `content/video_engine/hyperframes/renders/ledger-page-v1-{A,B,C}.mp4`
- [ ] Doc 29 §9.26 addenda read in order; refusals honoured
- [ ] `SURFACE-CENSUS.md` PAGE candidates vs the re-script's three pages
- [ ] Claim delivery contact sheet
