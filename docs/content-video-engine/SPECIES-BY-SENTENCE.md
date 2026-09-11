# SPECIES BY SENTENCE — which species, on which sentence (P50 T1, 2026-09-11)

The operator, 2026-09-10: *"Do we already have an understanding mapped in docs to how/where to know when to use these
capabilities if we build them?"* The surfaces were mapped (29 §9.28: page, dock, plate life, none - A1-A3 earn the page,
B1-B4 keep the dock); the species and the verbs were not. This is that map. Three places carry it and a test keeps them
in agreement: this file, `SPECIES_WHEN` / `CHART_TO_WHEN` beside `SPECIES_KINDS` in `build_scene_timeline_f.py` (§4 below
is generated from them), and the `episode-build` skill's authoring step. The lint that reads a shot table against it:
`lint_species_choice.py` (§3).

**The laws it sits under.** One thing per sentence (E25): a chart proves one sentence and leaves. The sentence decides
the species (E58): when the next thing the sentence needs is the same data at another scale, with more of it, in another
form, or a different series in the same frame, the page changes state and never cuts. The chart is the world (E61): a
long form is authored on the ledger page by default; a plate appears for one of three uses and names which. A species
points only at a DECLARED target (29 §9.27: a datum, a point, a region, a word span); nobody eyeballs a pixel. Sign is
geometry (E28); a ring has one use, a number or a point on a chart (E56); a picture's focus is a light.

**How to use it.** Read the take sentence by sentence (the build's `timeline.json` carries `sentences` with their times).
Classify each sentence's ACT from §1-§2 (a sentence may carry two; pick the one it turns on). Take the row: the surface,
the species or verb, the target it needs declared, the gate letters that will read it. Author the shot row. Run the lint;
it prints every sentence with an available species and no row - INFO, for the author's eye, never a FAIL.

## 0. The acts at a glance (one line each; the rows are §1-§2)

### The quoting sentence (QUOTES)
Their claim, their words, their pledge -> the record dock (the typewriter, the highlighter on the phrase); the press card (built 2026-09-11: a headline cut from a screenshot, its masthead stamped, stacking on the plate - the older cards dim and slide back, the newest lit - with the underline drawn under the quoted phrase); the dock read->park when the card then stays beside the chart. Row 1.

### The ranking sentence (RANKS)
Who is biggest, which comes first -> the bars page (the emphasised bar), the race builder over time, the callout on the ranked value; the burst when one bar cannot fit. Row 2.

### The comparing sentence (COMPARES over time)
Rose, fell, since, monthly -> the line page with terminal tags; `build_to` the datum, `rescale` the window, `extend` the next points, `figure` at the datum. Row 3.

### The dividing sentence (DIVIDES a whole)
A share, a tenth, half of it -> the share page, the `peel` for the slice that leaves; the treemap (T6) for breadth. Row 4.

### The naming sentence (NAMES places and flows)
Crosses the border, from Ontario, the money went home -> the `trace` with hops on a still today; the vector map (T5) when built. Row 5.

### The explaining sentence (EXPLAINS a mechanism)
A causes B via C, "when you ..., then ..." -> the `chip` board (a named thing as one of a set, landing on its word) and the `flow` diagram (built 2026-09-11: the chips in a dashed box, clothoid arrows between them, one node SWAPPED on a later word while the rest stands, a year tag); a narration plate that names its use, or the page's `note`. Row 6.

### The turning sentence (TURNS on a number)
The sentence's weight is one figure -> the `figure` at its datum, the light on it (`spotlight`, held), the ring on it (`callout`), a `note` when there is no room. Row 7.

### The breaking sentence (BREAKS the honest scale)
A number one bar cannot fit -> the burst (E60: `domain` + `overflow: "burst"` on the object; the comparator's level, the hold, the shoot while the scale rewrites); `stack` when named. Row 11.

### The spanning sentence (SPANS a period or a distance)
From the peak to June, the gap between two series, the run-up, the decade -> the `bracket` (its label the number, its sub the second thing), the `spread` bled full, the `span` (built 2026-09-11: a shaded stretch of time with its NAME), the `relight` on return. Row 8.

### The agenda sentence (SETS an agenda)
"Two numbers", "three things" -> the page parks (`chart_to park`) and the numbered figures or the card take the room; `scale: 1.0` un-parks when they leave. Row 9.

### The retracting sentence (RETRACTS a claim)
"The opponent isn't the Fed", "none of this happened" -> the `retitle` that replaces the false frame; the `chip` crossed out on the word (`cross_at`, built 2026-09-11 - Bravos's icon board); a `squiggle` strike on the word. Row 10.

### The same data again (E58's verbs), the read-then-kept card, the camera, the plate
Rows 12-15: the five `chart_to` verbs and the park laws; the dock `read` / `read_s` / `park_s`; E59's four reasons a camera moves; E61's three plate uses (`;use=landing|bridge|reset`).

## 1. The ten sentence acts

| # | the sentence ... | sounds like | surface (§9.28) | species / verb | target it declares | gates that read it | built | example (take · t) |
|---|---|---|---|---|---|---|---|---|
| 1 | **QUOTES** someone - their claim, their words, their pledge | "X said / announced / pledged ..." | DOCK (B1: it is THEIR claim) | the **record** dock (`drawRecord`: the typewriter, the highlighter on the phrase as it is said; portrait type in cqw on a short); the **press-card** dock for a headline with a masthead (P50 T3); the dock **read->park** when the card must then stay beside the chart (§2 #13) | none on a page - the highlight span is the take's own words (`record_words`); the card's box (`centre`, `read`) | M03 (evidence <= 45 s apart), M12 (a chart dock leaves), M16 (the exit is a beat), E56 (never a ring on a picture) | record YES; press card + the stack YES (2026-09-11) | Tokyo 53.4 *"Tokyo has pledged ten trillion yen to chips"* -> `dock-k-pledge-record` reads centred, parks beside the parked bars |
| 2 | **RANKS** - who is biggest, which comes first, the order of a set | "our biggest lender", "the top three", "first ... second ..." | PAGE (A1-A3) when the ranking is ours from a series we own; else a chart card (B2) | the **bars** page (`variant: bars`, the emphasised bar `:<emphasize>`); the **race** builder for a ranking that changes over time; the **breakthrough** when one bar cannot fit (§2 #11); a **callout** on the ranked value | the emphasised bar's index; a datum for the callout | E28 (a drop goes DOWN, blood red), E53 (values printed), E50 (deployed 6-8 s from the last mark), M21 | YES | Tokyo 17.0 *"our biggest lender"* -> the cut keeps the line page and LIGHTS the June datum (`spotlight`); the rank is a fact about the series, so the light, not a new bars page - one thing per sentence |
| 3 | **COMPARES over time** - rose, fell, since, monthly, a decade | "it's been selling since February", "over the last ten years" | PAGE: the **line** page (`dense-line`), its terminal tags naming each series at its end (E53); a dense-line **chart card** for a 2-3 s beat | `build_to` to the datum the sentence reaches; `chart_to rescale` to the window the sentence is about; `extend` for "and then May"; `figure` at the datum | a datum index (`build_to`, `figure`); a window `[x0, x1]` (`rescale`); `to_index` (`extend`) | E50 (the deployed clock), M21 (the chart's life), M23 (every chart_to listed; none inside the build beat), E25 | YES | Tokyo 20.8 *"and it's been selling since February"* -> `rescale` to the Feb-Jun window on "The Treasury's table"; 44.0 *"Since February, Japan has sold ..."* -> the bracket from the peak to June |
| 4 | **DIVIDES a whole** - a share, a tenth, half of it, the slices | "a tenth of the pile", "the share of the price that's profit" | PAGE: the **share** page (the proportion bars / the donut); the **peel** for the slice that leaves; the **treemap** for breadth or a named subset (E53 §1 census exception; P50 T6) | the slice by name (`peel`); the emphasised share | E53 §1 (a size claim takes its bar; the subset marked, its share written), E28 | share + peel YES; treemap T6 | Tokyo 44.0 *"a tenth of the pile"* -> the bracket's SUB carries the share (the cut chose the span over a share page: the sentence turns on the drop, the tenth is its sub) |
| 5 | **NAMES places and flows** - crosses the border, from Ontario, through the strait, the money went home | "its parts cross the border six separate times" | a STILL with a region (the crossings map) today; the **vector map** world (P50 T5: a light on a country, an arc between two, a stamp) when built | a region on the still (`trace` with `hop {from, to}`); a country / a point on the map | M18 (no frozen frames), E56 (a light, never a ring, on a picture), M14 (no camera move over a build) | trace hops YES; vector map T5 | tariff 13.1 *"its parts cross the border six separate times"* -> `trace` hops on `plate-gates`, six stamps stacked (25 % x3 Detroit, x2 Ontario, x1 Mexico) |
| 6 | **EXPLAINS a mechanism** - A causes B via C; "when you ..., then ..."; the name of the move | "we call this the double squeeze", "when your biggest customer walks, the auction sets your price" | the **flow diagram** on the page (P50 T2 the icon chip + arrows; the swap for a rhyme) when built; today a **narration plate** (E61: a bridge) or the page's **note** | chips by name; the arrows' ends | E61 (a plate names its use), E21 (the plate lives), M04/M05 (plate density and hold) | note YES; chip + flow diagram YES (2026-09-11) | tariff 60.2 *"we call this the double squeeze: the competitor got cheaper parts and built silicon"* -> a plate; Tokyo 27.3 *"when your biggest customer walks, the auction sets your price"* -> the host on the page |
| 7 | **TURNS on a number** - the sentence's weight is one figure | "over a trillion dollars", "that print is your first number", "forty-five hundred dollars in tariffs" | PAGE: the **figure** stamp written at its datum; the **light** on the datum (`spotlight`, `dur: "hold"` until the sentence has a reason to leave); the **ring** on the number (`callout`, E56); a **note** when the figure has no room at its datum | a datum index; for a note none | E56 (the ring's one use), HOLD_MIN_S (a light with < 1 s is dropped, not flashed), E25 amended (the light holds) | YES | Tokyo 23.1 *"over a trillion dollars"* -> `figure` $1,239.3B at the peak; 49.3 *"that print is your first number"* -> a `note` in the quiet zone (a figure at the June bar crossed the May bar - measured) |
| 8 | **SPANS a period or a distance** - from the peak to June; the gap between what the Fed charges and what America pays | "a hundred and twenty-two billion dollars of it", "The Fed still hasn't moved" (the distance from the low) | PAGE: the **bracket** between two data, its label the number, its sub the second thing the sentence says; the **spread** between two series, bled full of ink; the **relight** when the sentence returns to it | `from` / `to` datum indexes (bracket); `from_index` + a rule or a second series (spread); `from` / `to` x positions + `label` (span) | E52 (the bracket's label has room or it is a note), E50 (the bracket is a data mark - the clock restarts), M21 | YES (span 2026-09-11) | Tokyo 44.0 -> `bracket` "-$122.6B / a tenth of the pile" from the peak to June; 74.3 *"The Fed still hasn't moved"* -> the ring on the February low, then the `spread` from it |
| 9 | **SETS an agenda** - "two numbers", "three things", "here's what nobody says" | "Two numbers show where the money went: a Treasury page, and your phone" | PAGE parked (`chart_to park`) + the numbered **figures** or the fingers card in the room the park frees; a **retitle** when the agenda renames the page | the park's `scale` / `anchor`; the card's box | E58 (a park moves no data, restarts no clock; it STANDS until the next park), M23 | YES | Tokyo 36.1 *"Two numbers show where the money went"* -> `park` 0.55 up-left on "Two", the two-fingers card lands beside it (`arrive: land, mass: metal`) |
| 10 | **RETRACTS a claim** - "none of this happened", "the opponent isn't the Fed", "but look at what nobody explained" | "The opponent isn't the Fed; it's a Japanese balance sheet" | PAGE: the **retitle** that replaces the false frame; the icon board **crossed out** (P50 T2's chips + the strike) when built; a **squiggle** strike on the caption's word span (stage mode) | the title text; a word span (squiggle) | E21 (a caption event in stage mode only), M08 | retitle + squiggle YES; the chip crossed out YES (2026-09-11) | Tokyo 32.7 *"The opponent isn't the Fed; it's a Japanese balance sheet"* -> `retitle` "The opponent: a balance sheet" by the hand |

A sentence that carries none of the ten is a **bridge** (E61 #2): the page holds on its idle, the captions carry the
motion in stage mode (M08), or a narration plate takes the sentence and names its use.

## 2. The widened rows (2026-09-10 / 11: E58, E59, E60, the dock read->park, E61)

| # | the sentence ... | the mechanism | its beat | declared on the row | gates | example |
|---|---|---|---|---|---|---|
| 11 | **BREAKS the honest scale** - TURNS on a number one bar cannot fit: "it beats our bonds", "1.4 billion barrels" against 413 million | the **burst** (E60: a rescale). The bars object STATES a scale one value cannot fit (`domain: [lo, hi]` + `overflow: "burst"`); the breaking bar builds to the COMPARATOR's level with the others, holds `BT_HOLD` 0.5 s, then shoots to its true height over `BT_RUN` 0.6 s while the scale rewrites to the nice ceiling above it - the honest bar shrinks to a sliver, old ticks slide and fade, new ones fade in, the overshoot settles, the pill rides the tip and counts to the exact string, the bar glows. `overflow: "stack"` (the scale holds, the bar grows one comparator per `BT_STEP_S` off the page) when the row names it. Never a break glyph. The furniture (the "?" track, the axis-mounted capsule, the dotted leader) is P50 T10; the stop-motion blend is R26-30 / T13 | the hold starts at the END of the page's `build_s`; the shoot lands on the WORD (`_breakthrough_run_s` in the gate; a recast into an overflow state lands at end + build_s + run) | `domain` + `overflow` on the `.series.json` (`_validate_overflow`: a stated domain, one bar above it, one bar honest, bars only); the state named by `;then=` | E28, E53 (the scale and the value printed at every instant), M23 (`_transition_land`) | Tokyo 53.4 *"and if that works, it beats our bonds"* -> `recast` to `ev-bonds-vs-chips-10y-v1` (bonds 1.52 % on 0-8 %) on "to chips,", the burst to 36.59 % on "bonds." with the scale at 40 % |
| 12 | **the SAME data in another form or window** | E58's five verbs, one per sentence, the page changes state - never a cut to a second chart of it: **`rescale`** `{window, ymin, ymax}` - the same series at another scale ("since February", "at full width"); **`extend`** `{to_index}` / `{series}` - more of the same series ("and then May"), a later series of the same file; **`recast` keyed** `{state, keyed: true}` - n lines into n bars by series ("where the four stand today"; `RECAST_PAIRS` only); **`recast`** `{state}` - another chart of the data with no correspondence (a line into the monthly bars: the hand-over); **`morph`** `{state}` - a different LINE series in the same frame (the area hands over by ARAP; `MORPH_BUILDERS`); **`park`** `{scale, anchor}` - room for the next thing | one clock, min-jerk; the plot box is the pin during a rescale; a recast/morph erases the sub and source by the hand and writes the target's; a transition's end is a landing and a data mark (E50/E51) | `chart_to {at, dur, to, ...}` in the row's species list; the states on the plate id `;then=<object>` (three states at most, `STATE_MAX`) | M23 (listed; WARN inside the build beat or the last 0.5 s; FAIL on a state built for nothing), E58 | Tokyo: `rescale` on "The Treasury's table" (21.1), `recast` state 1 on "The Treasury prints" (49.3), `recast` state 2 on "to chips," (56.9) |
| 12b | **the park's laws** (E58 amended, measured on the Tokyo frames) | a park STANDS until the next park - a later recast does not un-park (the new state stands in the parked slot); a park moves from where the chart stands, so **`scale: 1.0` is the UN-PARK** that grows the chart back when the cards leave (the operator: *"if they're going to leave the chart should either re-take center stage, or they might as well stay til the transition"*); the page's source line rides the park with its chart | `PARK_SCALE` (0.3, 0.95) or exactly 1.0; `anchor` top / bottom / left / right | `chart_to {to: "park", scale, anchor}` | E58, M23 | Tokyo: park 0.52 at t_pledge - 0.4 (the bars make room); un-park `scale: 1.0` at "And here's" + 0.3 as the record and the plant leave |
| 13 | **a card that must be READ, then KEPT beside the chart** | the dock **read->park** (the operator: *"pop the card centered exactly as it is, and move it and resize it to that slot on the right when we pop the next card"*): the card pops at its reading box, holds `read_s`, then parks over `park_s` (min-jerk, a LAYOUT move - a seek lands the same frame) to its slot; its type scales with its width | the pop on the word; the park as the next card lands | the dock's 5th element: `centre: True` + the park box (`card_aspect`, `centre_w/x/y`) + `read: {centre_w, centre_x, centre_y, card_aspect}` + `read_s` + `park_s` (`DOCK_OPTS`; a centred card is placed on either slot) | E45 (a dock never covers the chart's middle), M16 | Tokyo `dock-k-pledge-record`: read centred in the fab band from "pledged", parked beside the parked bars on "to chips," (1.41 s, 0.7 s) |
| 14 | **the camera** - the four reasons it moves (E59), and the nevers | ONE persistent 2D similarity per timeline (`kinetics/camera.mjs`), LOCKED by default. It moves for: (1) a **landing** - a dock that arrives pulls the eye 1.06 from the contact frame, held while the card is up (`attention: "landings"`); (2) **between focal points on a stage wider than the frame** - a map, a wide diagram: ONE move per composition, then still (authored `keys`); (3) **the arrival** - `enter=camera=<dock>`: the card lands, the eye goes to it, the world switches at the match; (4) **the three species** (punch, focus_zoom, pull_back) through the same camera. **Never**: a continuous push on a held chart; a move to sell weight; a move over an evidence build (M14); two moves in one window (M09); captions riding it; docks riding it (until ruled) | min-jerk or the species' ease; a settle after every move | the row's 8th element `{"keys": [...], "attention": "landings"}`; `enter=camera=<dock>` on the plate id; the species on the row | M09, M14, M24 (`__camera(t, target)`: what is in frame before it is rendered) | Tokyo (the camera cut, "8742>8738"): the pull toward the panel and the fingers on row 2; the arrival on the ring's Fed card |
| 15 | **a plate** - one of three uses, named on the row (E61) | (1) a **landing surface** - a plate thrown onto the art world with evidence docked on it (the art embed, P50 T7), or evidence docked straight onto the chart; (2) a **bridge** - a narration plate between ideas, B-roll; (3) a **reset** - a plate that covers the world so the evidence clears and the next page mounts clean or on a new topic. Every plate lives (E21, the idle) | the plate's own idle; the dip / mount at its seams (E47) | `;use=landing|bridge|reset` on the plate id. **The lint reads the token; the compiler's `PLATE_OPTS` learns it with P51 T0 (the authoring kit owns the row grammar) - until then a long-form table's plate rows are listed and WARNed by the lint, and the token is not yet written** | the lint (E61: a long-form plate with no named use is a WARN), M04/M05 | tariff `plate-gates` (the crossings: a landing surface for the trace), `plate-podium` (the hook's bridge) |

## 3. The lint - `lint_species_choice.py`

```
python content/video_engine/scripts/lint_species_choice.py <project dir> [--build <dir>] [--table <SHOT-TABLE.py>] [--words <timeline.json>] [--long]
python content/video_engine/scripts/lint_species_choice.py --when            # the compiler's `when` on every kind, as a table
```

It reads the project's written shot table (`SHOT-TABLE-SHORT.py`, the `W` literal the build writes) and the build's
`timeline.json` (the take's `sentences` with their times - the same clock the captions and the docks use). For every
sentence it classifies the act by a keyword table - **crude on purpose, like V05**: a sentence about "the border" is
NAMES, one with a figure in it TURNS, "beats" BREAKS - then prints one line:

```
t0-t1 · "the sentence" · ACTS · available: <the built species the map lists for those acts> · row has: <what fires inside the sentence, or none>
```

"row has" is what the table actually does in the sentence's window: a species firing (`kind` at its `at`), a `chart_to`
verb, a dock entering (with its kind), a world change (the row that starts inside it: `ledger` / `plate` / `clip`), and
`burst`/`stack` when the row's page (or one of its `;then=` states) carries an `overflow`. A sentence with an act, an
available species and nothing firing is marked `· no row` - INFO. The report ends with the counts and, for a long-form
table (runtime >= 180 s or `--long`), E61's plate list: every plate row with its `;use=`, `WARN` where none is named.
Exit 0 always (a usage error is 2); it never blocks a build. It runs on the two shipped shorts as the regression
(`tests/test_lint_species_choice.py`) and on every new table before the operator's watch (P51 T3: the self-watch).

## 4. The compiler's `when` on every kind (generated: `--when --md`; the test compares)

Rendered from `SPECIES_WHEN` / `CHART_TO_WHEN` in `build_scene_timeline_f.py`; the block between the markers is generated -
edit the compiler, then `lint_species_choice.py --write-doc` (`--check-doc` and the test fail while it is stale).

<!-- SPECIES_WHEN:BEGIN -->
| kind | when (the sentence that calls for it) |
|---|---|
| `punch` | the sentence lands on ONE named object already on stage (the ring token, a datum, a plate object) and the eye must hit it - punctuation tied to a landing (E51), never filler |
| `callout` | the sentence names a NUMBER or a POINT on a chart to ring (E56: a ring's one use); the label is the sentence's figure |
| `focus_zoom` | after a chart or document has entered, the sentence turns to ONE region of it and holds there dead still |
| `spotlight` | the sentence's focus is a PICTURE or a datum and the rest may dim - the light lands on it and holds until the sentence has a reason to leave (dur 'hold', E25 amended) |
| `squiggle` | a caption WORD span the sentence stresses or strikes, stage mode only - drawn under the word as it is said |
| `pull_back` | a hook that opens on ONE large number, then recontextualizes it - the detail holds, one pull-back reveals the headline around it |
| `plate_life` | a bare world plate with no evidence must live (E21) - our cutouts stepped at 10 fps for the window |
| `beat_freeze` | leaving a chart as a HIT - the final state freezes, then a directional cut (declared in 29 s9.27, NOT built) |
| `radial` | revealing the ring token or a callback object FROM the point the narration names (declared in 29 s9.27, NOT built) |
| `push` | dock A hands off to dock B on the sentence - the evidence hand-off SHIPPED as the press STACK (a dock kind: `press` + `stack`, P50 T3, 2026-09-11): declare a press stack; the `push` species itself stays unbuilt |
| `steam` | STILL LIFE: a named region of an approved still breathes (steam, smoke) so the plate never goes still (E49) |
| `trace` | the sentence NAMES places and flows on a still - a route draws with hops between named points, stamps stack at them |
| `ticker` | STILL LIFE: a tape of figures ticks across a named region of an approved still |
| `life` | a DECLARED claim that this world animates on its own (a rendered clip, the outro) - the gate credits it; the agent verifies by eye |
| `build_to` | the sentence turns to a DATUM before the series' end - the line draws to it and stops (the peak now, the drop on the next sentence) |
| `bracket` | the sentence SPANS two data ('from the peak to June', 'a tenth of the pile') - the hand draws the span, the number is its label, the second thing its sub |
| `retitle` | the sentence renames what the page is about ('The opponent isn't the Fed') - the title rewrites by the hand; a returning page arrives retitled |
| `relight` | the sentence RETURNS to a number already on the page (the ring's echo) - the bracket or the title re-fires |
| `undraw` | the sentence has LEFT the chart's argument (E50) and the next thing is not a chart - the line unwinds to a datum or to nothing |
| `figure` | the sentence TURNS on a number - the hand writes it at its datum's spot (a note when the datum has no room) |
| `note` | the sentence adds a side fact the chart cannot show - a line of handwriting in the page's quiet zone |
| `chart_to` | the sentence needs the SAME data at another scale / with more of it / in another form / beside a card - the page changes state (E58; CHART_TO_WHEN names the verb); never a cut to a second chart of it |
| `peel` | the sentence names a slice of a whole that LEAVES - the share page's slice peels off and goes blood red |
| `spread` | the sentence's argument IS the gap between two series (or a series and a rule) - the region bleeds full of ink |
| `chip` | the sentence names a THING as one of a set (a prediction, an actor, a plant) - a chip lands on its word; RETRACTS crosses it out on a later word (Bravos's icon board) |
| `flow` | the sentence EXPLAINS a mechanism - A causes B via C - as named things and the arrows between them; a later word SWAPS one node and the rest stands (Bravos's rhyme) |
| `span` | the sentence SPANS a period on a chart - a regime, an epoch, 'the decade' - shaded behind the line with its name; a bracket measures two data, a span names a stretch of time |
| `chart_to` -> `recast` | the same data in another form: keyed (n lines -> n bars by series, 'where the four stand today'; RECAST_PAIRS) or the hand-over (a line into the monthly bars, into a pie of the holders) |
| `chart_to` -> `rescale` | the same series at another scale - 'since February', 'at full width': the window the story is about; never a window that drops the sentence's point |
| `chart_to` -> `extend` | more of the same series ('and then May') or a later series of the same file ('then consumption') - drawn on at the pen |
| `chart_to` -> `park` | room for the next thing beside the chart (a card, a second diagram); scale 1.0 is the UN-PARK when the cards leave; it moves no data and restarts no clock |
| `chart_to` -> `morph` | a different LINE series in the same frame ('what the Fed charges against what America pays') - the area under the line becomes the target's by ARAP |
<!-- SPECIES_WHEN:END -->

## 5. Not built yet, by task (the map already names them so the lint can say "available" the day they land)

| species | act | task |
|---|---|---|
| the vector map world (a light, an arc, a stamp) | NAMES | P50 T5 |
| the treemap (E53 §1 census exception) | DIVIDES | P50 T6 |
| the art-embed plate (a declared embed surface on a narrative plate: E61 #1) | a landing surface | P50 T7 (gate 3: ask before a Flow order) |
| the burst's furniture (the "?" track, the axis capsule, the dotted leader) | BREAKS | P50 T10 |
| line-end tags become the next chart's bars | COMPARES -> RANKS | P50 T11 |
| the stop-motion burst (R26-30) | BREAKS | P50 T13 |
| the continuity three (arriving from the edge, the three threads, the occlusion cue) | any | P50 T15 |
| beat-freeze exit, radial reveal (29 §9.27, declared but not built); the `push` species (its hand-off shipped as the press STACK, a dock kind, 2026-09-11) | leaving a chart; a callback | open |

Sources: 29 §9.27 (the motion menu), §9.28 (the surface grammar); E25, E28, E50-E53, E56, E58-E61
(`docs/portable/OPERATOR-RULINGS.md`); `SPECIES_KINDS`, `PAGE_SPECIES`, `CHART_TO_KINDS`, `DOCK_OPTS` in
`content/video_engine/scripts/build_scene_timeline_f.py`; the two shipped tables `japan-tariff-trick/SHOT-TABLE-SHORT.py`
and `tokyo-tea-break/SHOT-TABLE-SHORT.py`; the plan `.claude/PRPs/plans/P50-BRAVOS-GRAMMAR.plan.md` T1.
