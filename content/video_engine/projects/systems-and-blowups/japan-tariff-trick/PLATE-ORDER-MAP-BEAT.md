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

## Not MapLibre — the harvest already ruled on this

`remotion-ui/HARVEST-2026-09-07.md` RU-3 (`map-flight`) verdict was **index, not
port**: it needs a browser map runtime, tile fetches and a per-frame
`delayRender` handshake, and *"a dark tile map is the opposite of the cream
ledger page."* It also wrote down the honest route for exactly this moment:

> *"If a script ever needs a trade route (a steel-and-paper supply line, a capital
> flow), the honest route is a **pre-rendered still plate with our own `trace`
> drawn over it**."*

A script now asks. So: **the plate is the ground, the engine draws the route.**
That also keeps text out of the generated image, where it is unreliable.

**The recorded failure that applies here.** RU-3's altitude ramp carries its own
note: at cruise the mid-Atlantic leg *"showed nothing but open water — a flat blue
plate with a line across it, which reads as a failed render rather than a
flight."* The lesson transfers: **a recognisable edge must stay in frame.** The
Great Lakes silhouette is what makes Detroit and Ontario legible with no label,
which is why the framing below is specified tight rather than continental.

## The plate

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

Prompt written, not dispatched. Needs the operator's word on the timing question
above, because it changes what the plate has to hold.
