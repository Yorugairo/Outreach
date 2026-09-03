# MONEY PHYSICS — Brand Sheet

One page. Everything here is quoted from a governing file; the file is
named so a change lands there first and here second. Assembled 2026-09-02.

| Layer | Governed by |
|---|---|
| World plates (the look) | `projects/systems-and-blowups/style-spine.woodblock-vox-newsprint.v2.md` |
| Tokens, colour semantics, motion recipes | `configs/style_packs/woodblock.json` · `brand-tokens.json` (this folder) |
| Evidence layer + choreography | `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (Parts 1, 3, 8, 9; §9.15) |
| Packaging (titles, thumbnails) | `docs/portable/DOCTRINE-CORE.md` → TITLES + THUMBNAILS |
| Voice | `docs/content-video-engine/33-VOICE-PROFILE.md` · `36-WRITER-PERSONA.md` · `docs/portable/VOICE-PACK.md` |
| Channel copy | `CHANNEL-DESCRIPTION.md` · `PLAYLIST-market-replies.md` · `FIRST-COMMUNITY-POST.md` (this folder) |

## 1. The idea

**Money Physics** explains how money actually works — the machinery under
the market, never the tip. Tagline: **"The market isn't magic. It's
mechanics."** Triad: **Risk. Reward. Time.** Narrator: a former bank risk
analyst and dispensary owner who reads filings and builds the instrument
on camera (doc 36).

The visual thesis is a **pairing of two registers held in tension**:

1. **The world** — history and mechanism drawn as an editorial woodblock
   print. Warm, matte, hand-cut, adult.
2. **The evidence** — real charts from real data on a near-black ground,
   sharp and modern, dropped *onto* the world.

The print says "this has happened before"; the instrument says "here is
the number." Neither layer is allowed to imitate the other.

## 2. Colour — six tokens, fixed (spine; style pack)

| Token | Hex | Role |
|---|---|---|
| cream | `#F4E6C7` | paper ground — plates, banner, whiteboard |
| charcoal | `#25313C` | ink — contours, wordmark, body |
| cobalt | `#1769C2` | **brand accent** — the one highlight block |
| teal | `#178C83` | positive / "our layer" green |
| coral | `#ED6A4A` | negative / alarm; the "mechanics" word |
| sunflower | `#F5B72E` | highlight / attention (thumbnail "PAPER?") |

Semantics are fixed in the style pack: positive = teal, negative = coral,
accent = sunflower. A chart line and a plate accent must mean the same
thing. The evidence ground is near-black (`#1B1E23` family) with
near-white type; it is the only dark surface in the system.

**No other hues in generated art.** Plates are prompted with the palette
verbatim (spine STYLE block).

## 3. The world layer — woodblock vox newsprint (spine, verbatim rules)

- Carved woodblock ink contours with visible cut character; flat
  editorial newsprint colour fields; crisp registration like a fine art
  print; bold clean silhouettes readable at small size.
- Subtle newsprint grain allowed. **NO** paper-collage layering, torn or
  deckle edges, washi texture on plates. Matte, never glossy, never
  photographic.
- Light: soft, even, from the upper left; gentle shadow lower right; low
  contrast. Camera eye-level, straight on, no perspective distortion.
- **Hard rules:** no readable text, letters, numbers, logos or watermarks
  in generated art (documents show illegible engraved scrollwork); no
  real-person likeness; no flags or political symbols.
- **Quiet zone:** one side of every frame stays mostly bare cream or
  charcoal as the landing zone for evidence.
- Tone: adult editorial, financially credible, never childish. Brightness
  makes the material approachable; it never authorises toy proportions,
  glossy 3D, kawaii forms or preschool iconography.
- Reference plate: `steel-and-paper/build-f/assets/world-exchange-floor-1845.png`.

**The host (identity anchor, verbatim in every host prompt):** an adult
Black man with sculpted loc twists and a trimmed goatee, black rectangular
glasses, deep-indigo suit, copper tie, small gold lapel pin; same face,
hair, glasses and wardrobe in every image, conditioned on the reference
images. Confident, composed, warm; never caricatured. The host appears
*in-world* — presenting, pointing at a surface — never as a cut-out over
the evidence.

**Washi** (thin hand-cut paper, deckled fibre) is reserved for the
evidence-dock chrome and the whiteboard compositor. It never appears in a
plate prompt (operator correction 2026-08-25; `style-profile.v1.json`,
which describes the earlier collage look, is retired and not render-eligible).

## 4. The evidence layer (doc 29)

- Real charts built from real data; verified documents; cited source
  frames. **Never info cards.** Every chart prints its source line.
- Ground near-black; type Inter / system sans; numerals tabular
  monospace in badges (`ui-monospace, Consolas`), exact numerals verbatim.
- Each evidence moment names its document, its exact figure, its badge and
  its window. Evidence every 15–45 s; a bare stretch over 12 s needs a
  cause.
- Preferred composite is **diegetic**: the host gestures at a surface and
  real evidence lands in it.
- Reference chart: `steel-and-paper/evidence/objects/ev-divergence-v1.png`.

## 5. Motion (style pack; doc 29 Part 8, §9.15)

- **Every movement explains a causal or state change. Decorative motion
  is forbidden.**
- Recipes: `parallax_push`, `paper_transition`, `masked_reveal`, `map_trace`.
- Scene shape: one Ken Burns move per scene (1.00 → 1.04, distinct vector
  per scene; push in on arrivals and reveals, pull back on reflection,
  drift across a wide world) → evidence build (dock + badges) → wipe →
  repeat. Docks snap in; badges reveal one at a time and never retract
  inside a scene; the wipe fires only after both docks clear.
- **Do not bury the plate**: the world is never washed out under evidence.
- The locked transition is the **cross-reveal wipe with carried light**
  (§9.15): a hard inset front, outgoing wash and spotlight clipped to the
  front, swept cards hard-inset. Evidence that persists across a boundary
  holds untouched while the front passes.
- Captions: word-timed, kinetic, 4–6 words per page, bottom safe zone
  120 px at 1080-height (§9.15 r7).

## 6. Typography

| Surface | Face | Notes |
|---|---|---|
| Wordmark, banner, chrome | **Inter** 900/800/700 (Arial fallback) | letterspaced caps for MONEY PHYSICS; tight tracking on the triad |
| Evidence charts, docks | Inter / Segoe UI / system sans | numerals `tabular-nums` |
| The ledger page's hand (title, source, ticks, values) | **Kalam** 400 (SIL OFL; Inter fallback) | picked 2026-09-03 from three samples on the inked plate - an upright marker hand, the most legible at source-line size |
| Badges | ui-monospace, Consolas | exact figures |
| Thumbnails | Impact-class condensed display, upright | outlined, ≤3 punch words |
| Generated plates | **none** — text is banned on plates | |

## 7. Packaging — the one deliberate exception (DOCTRINE-CORE)

Titles and thumbnails are judged **together as one click-contract**.
Title: tension in the first ~40 characters, ≤~55 total; specificity beats
cleverness; every promise is paid. Thumbnail: ONE subject, extreme value
contrast, reads at 168 px, ≤3 punch words and only if the image is
ambiguous; title and thumb split the work and never repeat; motifs
compound across the catalogue; **no real faces**; thumbnails sell the
episode's question or thesis, never its opening prop.

The thumbnail register is YouTube's, not the woodblock's: white ground,
Impact-class type in slate + sunflower, the **robo host** cut-out
(`robo-cutout.png`), a two-bar comparison. This split is decided, not
drift. Reference: `steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png`.

## 8. Channel assets (this folder)

| Asset | File | Decision |
|---|---|---|
| Banner 2560×1440 | `money-physics-banner-2560x1440.png` | cream field, charcoal wordmark, cobalt block on "Reward.", teal/coral tagline; safe zone 1546×423 centre |
| Avatar | `mp-avatar-native-1031.png` (upload master) / `mp-avatar-800.png` | operator's woodblock portrait, Japan variant; Korea variant reserved for the memory episode |
| Watermark 150×150 | `mp-watermark-hybrid-150.png` | sprint pick; host + subscribe variants kept |
| Robo host | `robo-cutout.png` | thumbnails only |

## 8b. The signature — the ledger page (E22 / doc 29 §9.26)

The channel-defining move, settled 2026-09-03 (E22 addenda 4-7): **a
generated washi page sits on the cream ground; charcoal fills the page
to its DECKLE, so the deckle appears as the ink arrives - that arrival
IS the edge, nothing is drawn on top of it; the title and source write
in a handwriting face as the camera punches in on the board; the chart
builds from real data; then the page performs its focus action on the
datum the sentence is about.** The deckle is the feature that reads
"hand-made" without roughness - no drawn outline, no blob bleed, no
stains, halo or fibre, never a white ground. It is a chart that IS the world plate
(the "plate chart" species), not an evidence card; docks land in its
declared quiet zone and never cover the emphasized datum. Cream
`#F4E6C7`, charcoal `#25313C`, one accent token; the two plates are
generated (blank page + inked board, claim
`steel-and-paper-ledger-page-v1`); deterministic, seek-safe, real
`series.json` data with the source written on the board in chalk. The
host may stand at the developed board (C5 addendum): host-on-board
plates with a derived blank state, the chart fitted clear of the hand,
captions at the anchor. Every episode carries at least one; the payoff
chart is one by default. Docks stay near-black so the two registers
never blur. Handwriting face: Kalam (Human Gate 2, decided 2026-09-03).

## 9. Never (visual)

No photographic or glossy render · no collage, torn edges or washi on
plates · no readable text or numbers in generated art · no real faces
(plates or thumbnails) · no info cards · no decorative motion · no held
still with a hard cut · no AI-purple, no gradients outside the six tokens
· no kawaii or toy proportions · no burying the plate under evidence.
