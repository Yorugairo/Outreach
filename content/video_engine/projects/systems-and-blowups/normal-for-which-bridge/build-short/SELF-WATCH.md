# SELF-WATCH - normal-for-which-bridge - build-short - 2026-09-12 - short (1 min opening)
player.html sha256 86e394b40e5f - timeline bridge-short.timeline.json - runtime 1:10 - aspect 9:16 - script SCRIPT-SHORT

## 1. The gates (mechanical - a FAIL here ends the report)

| row | verdict | detail |
|---|---|---|
| motion gate (M01-M24) | WARN | [WARN] M06 40 caption pages = 34/min, 3.9 words/page; [WARN] M11 first chart ledger:s01 enters at 0.0s, its build lands at 7.4s, with callout at 7.9s; WARN no sound cue within 1.5s of the enter at 0.0s (no evidence species in the timeline - every dock treated as a…; [WARN] M21 1 page(s) deployed under 6s after the last data mark: s03 2.3s deployed of a 15.0s span (arrive+build 0.0s), 3.7s short - it ARRIVES BUILT and is cut before it can be read. A page that draws is exemp… · RESULT: 0 FAIL / 3 WARN / 15 PASS / 1 JUDGE / 4 INFO |
| M25 layout | PASS | no settled card on the chart's data, on a line of the page's ink or in the caption strip over 34 instants probed; smallest type read 14.4 CSS px on a phone (floor 11) \| INFO, listed not scored (CSS px on a phone): source (the citation) 9.4 |
| species by sentence | INFO | 19 sentences · 10 carry an act · 12 have a row firing · 3 have an available species and no row · 0.40- 2.70 · "Five percent was normal once." · TURNS · available: figure, spotlight, callout, note · row has: none · no row ‖ 56.12- 57.70 · "The load just went up." · COMPARES · available: line page, tiers page, build_to, chart_to:rescale, chart_to:extend, figure · row has: none · no… ‖ 58.42- 61.88 · "So when someone calls five percent normal, ask them:" · TURNS · available: figure, spotlight, callout, note · row has: none · no row |
| E61 plates (long only) | n/a | a short |
| the viewer (P36) | absent | absent |
| the script gates | PASS | VERDICT: PASS |
| the publish package (R26-8) | WARN | publish/: CHECKLIST.md, DESCRIPTION-FACEBOOK.md, DESCRIPTION-YOUTUBE.md, MANIFEST.json, PINNED-COMMENT.md, SOURCES.md, TAGS.txt, first-frame.png · not on disk: the evidence dossier (EVIDENCE-DOSSIER.md); the fetched sources' links (evidence/sources/*); the 1440p master (render/); the thumbnail (*thumb*.png) |

## 2. The opening, read (the agent fills these by reading the sheets - never by the gates alone)

sheets: self-watch/ opening.1.png, opening.2.png, opening.3.png (30 tiles at 2 s steps from 0:00 to 0:58, 360 px, 12 per sheet)

the operator's copy: SELF-WATCH.html - one plain question per row, the frames at the instants named here, each a link to the served player (`--html` after the read)

| # | check | verdict | evidence (t, what the tile shows) |
|---|---|---|---|
| O1 | the package is answered on sentence 1 (E24 / E27): the first frame and the first sentence deliver the title's claim | FAIL - the SENTENCE answers the title ("Five percent was normal once."), but the FIRST FRAME does not: 0.0 s is bare cream with no type and no page (opening.1 tile 1). The title types on at 4 s. R26-65 | opening.1.png, opening.2.png, opening.3.png |
| O2 | the promise lands by 0:45 (G09; a short: the mechanism by 0:10) | PASS - the mechanism sentence ends at 7.9 s and the page is on stage from ~4 s with the light on today's load at 7.9 s (opening.1 tiles 3-5) | opening.1.png, opening.2.png, opening.3.png |
| O3 | the first chart enters 0:08-0:20 lit (M11) and reads at a glance (E28: sign is geometry, the scale printed) | WARN - it reads at a glance (title, % of GDP, 0/50/100, the decades, the line to 123) and the callout lights the apex at 7.9 s, but the callout's label crowds the page's own series label at 10 s (opening.1 tile 6); and it enters at 0.0 s rather than 0:08-0:20 because the page IS the opening | opening.1.png, opening.2.png, opening.3.png |
| O4 | every sentence-act with an available species has a row, or the bridge is deliberate (each `no row` line answered: bridge / the light holds / cut) | PASS - three acts carry no row on purpose: the hook (the page is still arriving), "Nothing defaulted" (a reflect - its span was pulled after M28 caught the label under the figure), and the stakes line, which the note already carries | opening.1.png, opening.2.png, opening.3.png |
| O5 | no dead band: no 2 s tile pair identical to the eye inside the opening; nothing held still past its sentence (E21, E49) | FAIL - three holes where the stage has a caption and no world: 14.0-17.5 s (the suck, under "Two weeks ago the ten-year paid four point six six"), 41.5-45 s (the melt, under "And the load sends a bill"), 58.5 s (the vortex return). 8% of the runtime. R26-66 | opening.1.png, opening.2.png, opening.3.png |
| O6 | no overlap the probe could not see: a card over ink, a label under a card, paper in the strip (M25 read against the tiles) | FAIL - two the probe cannot see: the span's SHADE covers the line and swallows the series label at 38-40 s (R26-68), and the ring's flag chip is painted half outside the page's card at 69.0 s (self-watch/close/opening.png, R26-67) | opening.1.png, opening.2.png, opening.3.png |
| O7 | the citations readable at the phone scale (>= 11 CSS px; the source line clear of every card) | PASS - the source line (FRED / Treasury/BEA / Sep 2026) is clear of every mark on all five pages and legible at the phone scale; the probe's smallest read is 14.4 CSS px | opening.1.png, opening.2.png, opening.3.png |
| O8 | the captions read as phrases, never chased (shorts: PHRASE captions; the strip never covers a figure; E62: under a card the caption keeps its size and MOVES to the free band - a shrink is a FAIL unless no band fits) | PASS - phrase captions, 3.9 words a page, never over a figure (M25 clean over 34 instants). The k-word highlight blocks read loud at this size - the shipped style, the operator's call. M06 WARNs the rate (34 pages/min against the 4-6 word target) | opening.1.png, opening.2.png, opening.3.png |
| O9 | every card lands on its word and leaves at the turn (E25 / E50): the landing tile and the exit tile named | n/a - this build docks nothing: five ledger pages and no cards, on purpose (what is under test is the page, the chart and the species vocabulary) | opening.1.png, opening.2.png, opening.3.png |
| O10 | the chart is the world (E61): every plate row in the opening names its use; a plate that proves nothing and docks nothing is a bridge, said so | WARN - every row is a page that proves its own sentence, and the close returns the page already drawn (60.0 s, correct). But the MIDDLE return re-draws: the row's build_to walks the line back to 1981, so the second visit shows LESS than the first (28-38 s) - E40 says a returning page unwinds from its point, never redraws. Authoring, not the engine: a return takes relight/undraw, not build_to | opening.1.png, opening.2.png, opening.3.png |

## 3. Verdict

READ 2026-09-12 (the parent, on the sheets and the close): 4 PASS / 2 WARN / 3 FAIL / 1 n-a. NOT CLEAN - the three FAILs are R26-65 (frame 0 has no page), R26-66 (the stage empties under a live sentence) and R26-67/R26-68 (the flag chip off the page, the span's shade over the ink). This build is a CAPABILITY TEST on a scratch clock and is not offered for a watch.
