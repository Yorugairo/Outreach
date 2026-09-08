# PLATE ORDER — the crossings map (the geography beat)

Operator, 2026-09-08: *"One thing we didn't make use of that I think we should
have here is our map components that we borrowed from remotion, that's an easy
Detroit/Tokyo use case."*

## Why this beat and not the others

I looked at the three signature plates before proposing anything.

- **`sig-c-two-lanes` stays.** Toyota with a single duty tag hanging off it,
  Detroit's pickup buried under a tower of duty slips. That is the asymmetry and
  it reads instantly. It is not the problem.
- **`sig-d-ship-once` stays.** One crossing, stated plainly.
- **`sig-b-six-gates` is the one to replace.** It is a good drawing — the truck,
  six booths, the character counting on his fingers — but it is a **metaphor
  standing in for information**. Six barriers on one road can say *"six times"*.
  It cannot say Ontario, then Mexico, then back, taxed each way. And the VO
  immediately before it is *"auto parts taxes **compounded** against Detroit"* —
  compounding is precisely what a straight road with six booths cannot show.

Direction and repetition are inherently spatial. That is the whole case for a map
here, and it is the only beat in the short that needs one.

## "Why not MapLibre?" — the honest answer, and a revision

Operator, 2026-09-08. Citing the harvest was not a reason, so here is the check.

**MapLibre at RENDER time breaks the renderer, specifically.** `render_baseline.
frame_png` sets the scrub and screenshots on the next tick; the only async thing
it waits on is `__clipsSeeked` for video seeks. Remotion holds every frame with
`delayRender()` until the map fires `idle` — **our player contains zero
`delayRender`/`continueRender` calls**. A tile that lands one frame late is a
different frame, and the contract is byte-identical seek-exactness (frame N
evaluated directly == frames 0..N stepped). Add a network fetch at render time,
which makes the visual unreproducible from the repo, and `maplibre-gl`'s weight
inside a single-file player.

**That is an argument against MapLibre at RENDER time. I over-generalised it into
"no map", and that was wrong.** Two options beat the generated image plate:

**(a) MapLibre at BUILD time.** Render the basemap once, headless, to a high-res
PNG; commit it with its sha256. Real coastlines, styled to our tokens, no runtime
dependency, no `delayRender` problem. The borrowed component used where it helps.

**(b) The coastline as a PATH — recommended.** A simplified coastline is just an
SVG path, and drawing paths in ink is the whole identity of this engine. Drawn
with `stroke.mjs`, **the map draws itself on** like every other line on a ledger
page: on-brand, seek-exact, no tiles, no network, no new dependency. And
`greatCircleLine` from the harvested `map-utils.ts` is a **pure function** — it
ports as a formula, which is the standing rule (mechanisms port, code does not).
It gives the Tokyo→Detroit arc for free.

(b) also makes the route and the map the same machinery, so the six crossings and
the Pacific arc are the same species we already ship.

## Four places in one frame — one map, two framings

The operator wants Mexico, Detroit, Tokyo and Canada. All four in one frame is a
hemisphere view, which walks straight back into RU-3's recorded failure: at that
altitude it is mostly open water, and the Great Lakes detail — the thing that
makes the six crossings legible — disappears.

**So: one basemap, two camera framings**, which is RU-3's other transferable idea
(*split the drawn route from the camera route*) and needs no new capability:

| beat | framing | what draws |
|---|---|---|
| the six crossings (13.7 s) | tight on the Great Lakes, Mexico's border at the lower edge | `trace` hops + the 25% stamps |
| Toyota crosses once (31.3 s) | `pull_back` to reveal the Pacific and Tokyo | one `greatCircleLine` arc, one 15% stamp |

The pull-back IS the argument: the same map, and one crossing where there were
six. `focus_zoom` and `pull_back` already exist as camera species.

## The plate — READY TO GENERATE

**The beat is now 9.5 s, not 4.57 s.** Moving `t_gates` from `cut("When you buy")`
to `cut("Auto parts")` hands the map the whole crossings passage, and fixes a
mismatch on the way: *"Auto parts taxes compounded against Detroit"* is currently
spoken over the **Japan Treasury holdings chart**, which has nothing to do with
it. On the map it is the caption for the picture.

| boundary | s02 span | map beat |
|---|---|---|
| now — `cut("When you buy")` | 11.91 s | 4.57 s |
| `cut("But look")` @ 11.90 | 10.08 s | 6.40 s |
| **`cut("Auto parts")` @ 8.88** | **6.98 s** | **9.50 s** |

At 9.5 s the six hops and six stamps read at a human pace, and s02 still lands
its whole hook claim (arriving built, spotlight at 2.3 s) above the 6 s floor.

**Prompt** — same house style, same character binding, same `no on-screen text`
rule as the other signature plates (`sig-b-six-gates_meta.json` is the format of
record). Written for a route that will be drawn OVER it, so the geography is
uncluttered and the three plants are far enough apart for six hops to be legible:

> 9:16 vertical, full bleed. A light application of woodblock print and vox
> newspaper meets rich anime colors. A hand-drawn map seen from directly above,
> filling the page: the Great Lakes and the narrow river between Detroit and
> Ontario in the upper half, the long southern border with Mexico across the
> lower quarter, the land warm and the water pale. A car plant with smoking
> stacks stands on the Detroit side of the river, a second plant faces it across
> the water on the Ontario side, and a third plant sits below the southern
> border. The three plants are widely separated with open, uncluttered land
> between them. No roads, no route lines, no arrows, no borders drawn as dashes.
> The character, in his indigo suit and copper tie, stands very small at the
> lower right corner looking up at the map. A single still frame, no on-screen
> text.

- `references`: `["HollowStickMike"]` · `requested_ratio`: `9:16` · `mode`: `image`
- lands as `omni-video/stills/sig-b-crossings-map.png` + `_meta.json`

**Why no route, no arrows, no dashed borders in the plate:** all three are the
animation. A baked line cannot count, cannot accumulate, and cannot be timed to
the VO — and a drawn arrow would fight the `trace` that follows it.

## DISPATCH — one operator launch away (corrected 2026-09-08, post-compact)

**The blocker I recorded before was the wrong one.** I named `flow_enqueue_batch`
and its `capability_snapshot`; that is the browser-extension bridge lane, **retired
2026-09-03** (CAPABILITIES.md). The live lane is the CDP driver behind the
`video-engine` MCP (`create_flow_image`), which is how the four `sig-*` plates
were rolled on 2026-09-07 — and it does not need the MCP attached to a session:
`mp-host-transitions-v1/dispatch_batch.py` set the precedent of speaking JSON-RPC
to `mcp/server.mjs` over stdio. Verified here: the server answers `tools/list`
with `create_flow_image` (2026-09-08).

What IS missing is the browser. The driver connects to the dedicated automation
profile `C:\Users\Snipe\.flow-chrome-profile` on **9223** (9222 default profile
as fallback); neither is listening now (the profile was last touched 09:46
today, so it was up this morning). Launching it means a signed-in Google
session, which is the operator's — never entered by a script.

- **Order, frozen:** `omni-video/sig-b-crossings-map.order.json` (prompt above,
  `HollowStickMike`, 9:16, project `d171ec1f`, zero-credit Nano Banana Pro).
- **Dispatcher:** `omni-video/dispatch_crossings_map.py` — checks the CDP
  precondition and ABORTs (exit 2, proven) without it; refuses to overwrite an
  existing plate (a re-roll is a new order file); logs to
  `dispatch-crossings-map.log`; the frame lands quarantined in `stills/`.

The two steps:

    & "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir=C:\Users\Snipe\.flow-chrome-profile --remote-debugging-port=9223
    python content/video_engine/projects/systems-and-blowups/japan-tariff-trick/omni-video/dispatch_crossings_map.py

## ROLLED — the character A/B (operator, 2026-09-08)

*"We should try the same prompts testing @MikeMasterV3 vs @Mike2 and @HollowStickMike."*
Same frozen prompt, three references, zero credits, all via `dispatch_crossings_map.py`:

| order | reference | landed | what came back |
|---|---|---|---|
| `sig-b-crossings-map.order.json` | HollowStickMike | `60a65258…` | the richest painting — but no Mexico at all; the third plant sits on open US ground, so a "Mexico crossing" would cross nothing (E28: sign is geometry) |
| `…-mikemasterv3.order.json` | MikeMasterV3 | `2cbc69fe…` | a clean, near-real map: five lakes, Baja, the Gulf — but the Mexico plant landed in Texas, north of the line |
| `…-mike2.order.json` | Mike2 | `38fbf595…` | the Mexico plant inside Mexico below a drawn border, a wide empty middle, place names DETROIT / GREAT LAKES / ONTARIO baked in — but the Ontario plant stands on the SOUTH shore and reads as US |

The operator's calls, in order: *"HollowStickMike produced the best outcome"* →
on the Mike2 re-roll, *"better because of the Detroit / Great Lakes / Ontario"* → then
*"not great because it has Ontario's manufacturing plant looking like it's in the US"* →
**"HollowStickMike is the truest."** So: **the reference is HollowStickMike** (the world it
drags in is the channel's), and the geography is a PROMPT defect, not a character one —
none of the v1 frames puts Ontario's plant on Canadian ground with a boundary between it
and Detroit, which is the one thing a crossings map must do (E28: sign is geometry).

**v2 orders** (`…-v2-hollowstick.order.json`, `…-v2-mike2.order.json`): the boundary drawn
as a line through the river and the lake, Detroit's plant on the south bank / US side,
Ontario's plant directly across on the north bank / Canadian side with Canada continuing
north of it, the Mexico plant south of the Mexican border. **Place names allowed** —
DETROIT, ONTARIO, CANADA, MEXICO only: the v1 labels were the part that helped, so the
"no on-screen text" rule takes a recorded exception for place names on a map, nothing else.

**The v2 → v7 ladder (HollowStickMike throughout, zero credits).** Operator on the v2
pair: *"at the small size the HollowStick Mike character reads more clearly; the manufacturing
plant stickers are better on Mike v2 though"* — and *"don't we need to prompt these to be
2.5D?"*, settled as the style atom **"A light application of 2.5D woodblock print and vox
newspaper meets rich anime colors."** (E39 amended 2026-09-08; the record had the atom without
the depth word, and none of the twelve shipped prompts carried it).

| order | change | landed | read |
|---|---|---|---|
| v2 | boundary through the water, Ontario on the north bank, place names allowed | `3cfd88a9…` | geography right, plants flat silhouettes |
| v3 | + plants "like detailed pen-and-ink stickers" | `32851c87…` | "sticker" taken literally (white die-cut borders, huge); Ontario's plant back on the south shore |
| v4 | + plant drawing described (brick, sawtooth, stacks, small against the land); *"Layered 2.5D … far/mid/near plane"* as on the two Tokyo plates | `a5271f61…` | plants right; Ontario south again; a misspelt sign ("ONTARIA") |
| v5 | the amended atom, no layered-plane phrasing | — | **infra**: the pill was absent for a moment after v4 and the driver threw at 0 s; the pill was back when probed. `configureSettings` now retries four times with a growing wait |
| v6 | + geography stated compositionally (Ontario ABOVE the lake, upper right, open Canada to the top edge; a line between the plants must cross water) | `87cf3ed1…` | **geography finally reads** and the plants are the good ones — but the description came back as lettering (BORDER LINE, GREAT LAKE, CANADA ×3) and the lakes flattened into one diagonal river |
| v7 | four place names whitelisted, written once each; the boundary "drawn as a line only, never written as a word"; the lakes' real coastline back | `dc6a34f8…` (recovered) | the whitelist works (one leak: GREAT LAKE), the boundary is a line, geography reads, plants good — but the coastline never came back: a diagram, not the map. The driver downloaded v6's file again for this order; the real output was pulled from the library by id and recorded by hand (`_meta.json` says so) |
| v8 | an EDIT of v2: the v2 PNG rides as a file reference, only the three plants change | written, **not rolled** | operator took the Flow session to prompt the building swap by hand (*"hold on"*); the order stays on disk |

**Where it stands (operator, on the v2-hollowstick frame): *"remains our best option because
of its geographical accuracy I think, it just has the weakest buildings."*** Six rolls later
that is still the read: the fresh rolls trade the coastline for the buildings or the buildings
for the coastline, and the two never arrive together. So the ground is v2 and the buildings
are the remaining work — the operator is prompting that swap in Flow directly; v8 is the same
idea as a driver order, unrolled.

**A fourth driver defect, found on v7.** The observer's seen-set lived on the driver instance,
and every stdio dispatch is a fresh process — so a previous roll's output was "new" to the next
one whenever the baseline missed it (v7 downloaded v6's file, byte-identical; earlier the Mike2
v1 downloaded MikeMasterV3's). The set now persists in `runtime/seen-image-ids.json`, seeded with
every id this project has downloaded, and it is the one piece of state two sessions on the same
Flow project must share — which is the multi-agent question in miniature.

What the ladder taught, for the next map order: **"north bank" does not place a plant** — three
of four rolls put it south; a compositional statement (above / upper right / open land to the
edge) does. **Anything named in the prompt is liable to be lettered on the page**; the fix is a
whitelist of what may be written, not a ban on text. And **"sticker" is a shape to this model,
not a drawing style** — describe the drawing.

**Two driver defects found and fixed on the way** (`tools/google-flow-driver/src/cdp-driver.mjs`):

1. **Flow's composer now has an Agent mode** (a chat bar with *Agent instructions* and a
   `tune` icon) and it hides the settings pill the driver keys on (`🍌 Nano Banana Pro
   crop_9_16 x1`). Every roll died with *"Flow settings pill not found"*. The chip sticks
   per project, so `configureSettings` now toggles `flow-agent-mode-toggle-chip` OFF when
   the pill is missing. Proven live: the log shows the toggle, then *Settings already match*.
2. **`listProjectCharacters` scanned the All-media grid and returned on its first hit**, which
   is the three tiles of the Characters strip — so `Mike2`, `Mike` and `StickMike` were
   reported "not found" while live. It now reads the library's **Characters view**
   (`flow-character-tile .character-tile-name`, six names) and puts the view back. The first
   version of that fix introduced a third defect: leaving the view empties the media grid,
   and the generation observer's baseline taken before it refilled saw MikeMasterV3's
   output as "new" and downloaded it again as Mike2 (byte-identical sha). The driver now
   waits for the grid to refill to its pre-navigation count before returning. The orphaned
   real first Mike2 roll (`89337b8f…`, labelled "Detroit River", no Mexico) stays in the Flow
   library; the re-roll is the one on disk.

The three frames and their metas are in `omni-video/stills/` (PNGs gitignored, metas
tracked); the JSON-RPC results sit beside the orders. The duplicate Mike2 result is kept as
`…mike2.result-INVALID-dup-of-mikemasterv3.json`.

**Plate of record: not yet chosen** — it will be a v2 frame (768×1376, same as the other
signature plates) once the operator picks one; then `build_short.py:59` `plate-gates` →
that file.

## THE PLATE OF RECORD and THE BEAT AS BUILT (2026-09-08, evening)

**Plate:** `omni-video/stills/sig-b-crossings-map-v9-operator-edit.png` — the operator's own
edit of the v2-HollowStickMike ground in Flow: v2's real coastline and boundary, the three
plants replaced by 2.5D woodblock chips (*"i can probably prompt to replace the buildings
with 2.5d wood block print with rich anime colors"*). Pulled from the library by id
(`86509336…`), meta by hand. Candidate until the word "approved"; one flaw to know: the
Detroit chip's base clips the DETROIT lettering. `build_short.py` `plate-gates` → this file,
both arms.

**Boundary:** `cut("But look")` = **11.78 s**, not `cut("Auto parts")`. The 9.5 s plan in
the table above was never a legal cut — the voice runs straight from "Toyota." into "Auto
parts" with no M13 gap (≥ 0.30 s), and `cut_before` refuses it. The next breath is 11.78, so
the map carries *"But look at what nobody explained. When you buy an American truck, its
parts cross the border six separate times"* — 6.5 s. "Auto parts taxes compounded" stays
over the holdings chart; that mismatch survives and is the script's to fix, not the cut's.

**The beat** (`crossings_species()` in `build_short.py`): six hops, six stamps.

| what | species | law |
|---|---|---|
| a hop | `trace` with the new opt-in **`hop`** `{from, to, bow, draw_s, width}` — one bowed arc plant to plant, drawn once over 0.55 s and HELD to the cut | route D→O, O→D, D→M, M→D, D→O, O→D; every hop crosses a drawn line; one bow sign, so the return bows to the other side by itself (an alternating sign cancelled that and the first render showed three lines for six) |
| a stamp | `callout` on a point, `label: "25%"`, `pad: 22`, the new opt-in **`label_scale: 2.2`** | lands 0.55 s after its hop leaves; repeat landings stack like passport stamps (Detroit up-left ×3, Ontario up-right ×2, Mexico ×1) — **six on the page, which IS the count**; the first render stacked them on one pixel and "six" never appeared |
| timing | first hop leaves 0.2 s before "When you buy" (13.66); the sixth STAMP lands on "six" (16.79); the rest evenly between | the picture accumulates to the word |

Both opt-ins ride through the validator (which now checks `hop`'s fields; three tests in
`test_targeted_species.py`) and leave the goldens byte-identical (13 passed, twice). The
motion gate on the rebuilt timeline: 0 FAIL, M16 longest gap 2.3 s.

**Judged on the frame, not the diff** (four renders): the arcs and the count read at phone
size; the caption strip sits mid-map over open land. Not done: a `focus_zoom`/`pull_back`
pair (the Mexico plant is at 0.87, so the crossings need the whole frame — the pull-back
idea belongs to the Toyota beat, which still carries `plate-ship`).

## The choreography over it — what the engine draws

The beat runs 13.73 → 18.30 s, on *"when you buy an American truck, its parts
cross the border six separate times."*

| beat | species | what it does |
|---|---|---|
| the route | `trace` × 6 | one hop per crossing, Detroit → Ontario → Detroit → Mexico → Detroit …, each drawn on the pen's own speed so the back-and-forth is felt as repetition rather than shown as a diagram |
| each landing | `figure` or a stamped badge | **25%** struck on the plant it arrives at — six stamps, accumulating, never clearing |
| the count | the stamps themselves | the sixth stamp IS the payoff; no counter needed |

`trace` takes a `region` target, so each hop is authored as its own species row
with its own word. The stamps land on the crossings, not on a legend.

**The counter-shot is already built.** `plate-ship` at 31.28 s carries Toyota's
single crossing, and `sig-c-two-lanes` carries the result. The map does not need
to make the comparison — it only needs to make the *repetition* legible, and the
existing plates finish the argument.

## Timing — resolved

Six single crossings, not three round trips: at 9.5 s there is room. The boundary
move and the plate must land TOGETHER — handing 9.5 s to the existing static
six-gates image would trip M16's short-form pulse (no gap over 2.5 s between
visual events), because a still with idle drift cannot hold nine and a half
seconds.

## Status

Operator said generate (2026-09-08). The prompt is final and the beat has its
9.5 s. **Dispatch is one operator launch away** — see above; the order file and
the dispatcher are on disk. Route (b), the drawn coastline, remains the cheaper
long-term answer and needs no plate at all; this order is route (a), the painted
ground, which is what "generate" asked for.

**Lands together with the plate (not before):** `build_short.py:184`
`t_gates = cut("When you buy")` → `cut("Auto parts")`, and `plate-gates` →
the map plate (`build_short.py:59`), plus the six `trace` hops and stamps whose
coordinates need the generated geometry. Moving the boundary onto the existing
still alone trips M16.
