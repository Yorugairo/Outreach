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

## The plate — ONLY if we take route (a) or the image fallback

Route (b) needs no generated plate at all: the coastline is drawn. What follows
is the fallback if we want a painted ground under the ink.

Same house style, same character binding, same `no on-screen text` rule as the
existing signature plates (`sig-b-six-gates_meta.json` is the format of record).

**Prompt:**

> 9:16 vertical, full bleed. A light application of woodblock print and vox
> newspaper meets rich anime colors. A hand-drawn map of the Great Lakes region
> seen from above, the lakes and the river between Detroit and Ontario clearly
> shaped, Mexico's border at the lower edge of the page. A car plant with smoking
> stacks sits on the Detroit side, a second plant directly across the water on the
> Ontario side, a third plant at the southern border. No roads or route lines are
> drawn between them. The character, in his indigo suit and copper tie, stands at
> the lower right corner of the map looking down at it, small against the
> geography. A single still frame, no on-screen text.

- `references`: `["HollowStickMike"]`
- `requested_ratio`: `9:16`, `mode`: `image`
- lands as `omni-video/stills/sig-b-crossings-map.png` + `_meta.json`

**Why no route in the plate:** the route is the animation. A baked line cannot
count, cannot accumulate, and cannot be timed to the VO.

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

## Timing note

This beat's span is 4.57 s. Six traced hops plus six stamps will not fit at a
readable pace — the same rushing M21 now catches on the chart pages. Either the
beat takes seconds from the neighbouring gap, or the hops are shown as three
round trips rather than six single crossings. **Decide before generating**, since
the plate framing follows from it.

## Status

**Route not chosen.** (b) — the coastline as a drawn path — is the recommendation
and it needs no image generation, only a simplified coastline (public geodata)
and `greatCircleLine`, which we already hold. (a) is the fallback if a painted
ground is wanted under the ink. The prompt above is written either way.

Still open, and it changes the framing: the crossings beat is **4.57 s**, and six
traced hops plus six stamps will not fit at a readable pace — the same rushing
M21 now catches on the chart pages. Three round trips, or more seconds.
