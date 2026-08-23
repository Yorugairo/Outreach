# Library Build — Episode 1 (S&P 500 / Index Funds)

> **Superseded** by [LIBRARY-BUILD-EP1-V3-REGENERATION.md](LIBRARY-BUILD-EP1-V3-REGENERATION.md).
> Retained for provenance. Its Style, Camera/Lighting, Transparency and Negative
> blocks produced the 15 character poses and carry forward unchanged. Its scale
> and composition rules do not: "right third clear" was written for a single host
> and its worlds carry no human-scale anchor, which is what forced the v2 cast to
> be composited at the wrong size. See
> [23-EP1-LIBRARY-INTAKE-REVIEW.md](../23-EP1-LIBRARY-INTAKE-REVIEW.md).


Status: ready to generate
Written: 2026-08-22
Target lane: `expert_explainer`
Cast decision: host plus a two-civilian contrast pair
Style decision: paper-cut woodblock **at reduced density** — see below

Paste the **Style Block** and **Negative Block** into every prompt, then the
per-asset body. Filenames follow the existing convention in
`assets/generated/cutouts/`.

---

## The style call, and why

Your `current-bubble-episode-one-full-p34.mp4` render is better-looking than every
competitor reviewed. It is also optimised for the wrong thing, and your own
instinct about "simple white space" is correct — but the fix is not to abandon the
paper-cut style.

Sampled frames from that render show:

- **8+ distinct elements per plate** against 2–3 in Wealth Logic
- **deep navy grounds** under small cream captions, which are hard to read
- **no host in any sampled frame**

An earlier draft here also claimed "zero on-screen figures". **That was a sampling
error** — 12 keyframes across 16 minutes missed the evidence boards entirely,
because they are composited *within* held shots rather than at cuts. Dense sampling
found them. See the evidence-layer section below for what they actually do.

The density and the missing host still cut against two of the three things this
session's competitive review found track performance: a recurring host as identity
anchor, and plates that illustrate a specific number.

**So: keep the material, cut the density.** Paper fibre, torn edges, ink contour
and the existing palette are a genuine differentiator — nothing in the competitive
set looks like this. Density is the part that is fighting you: it makes captions
illegible, leaves no room for figures, and buries the host.

The rule for this library: **two to three elements per plate, a light ground where
figures or captions land, and one third of frame left deliberately near-empty.**
Your dense collage plates are not wasted — they become act openers and chapter
cards, roughly one per act, instead of the default.

**The host is not regenerated.** An earlier draft of this document asked for his
fabric weave and gradient shading to be stripped. That contradicted the retraction
recorded in `21-ART-STYLE-REFERENCE-REVIEW.md`, which established that rendition
level is neither a drift risk nor a legibility risk, and it inverted the right
order of operations: **the host is the one asset that is known good, so the
unbuilt library adapts to him, not the reverse.**

Keep `finance-host-identity-master-v3.png` exactly as it is. Generate his poses
from it as reference, in his existing rendering. Then give the new library assets
enough soft shading to sit beside him — paper texture and ink contour are the
signature, but fully flat matte props would clash with a shaded character.

The density rule is unaffected and stands on its own: it concerns **how many
elements are in a plate**, not how any one of them is rendered. The host is a
single figure and was never the density problem — the eight-element world and
mechanism plates were.

---

## Style Block — paste into every prompt

```
Style: hand-cut layered paper collage with woodblock ink contours. Visible paper
fibre and torn deckle edges. Soft directional shading with gentle depth between
paper layers — matte, never glossy, never photographic. Bold clean silhouettes
readable at small size.
Palette strictly: cream #F4E6C7, charcoal #25313C, cobalt #1769C2, teal #178C83,
sunflower #F5B72E, coral #ED6A4A. Adult editorial tone, financially credible,
never childish.
Composition: no more than three elements. Generous empty space. Keep the right
third of the frame clear and uncluttered.
```

**On element count — the budget applies to the generated plate, not the finished
frame.** Characters are composited cutouts layered on top, so they are not part of
what the image model is asked to produce. Three separate budgets:

| Layer | Budget | Why |
| --- | --- | --- |
| Generated background or world plate | **2–3 elements** | Reliability as much as design: asking a model for five specific things reliably merges or mangles one. Three is materially more dependable than five. |
| Composited characters on top | **up to 3** | Host plus the contrast pair. Three should be rare — a setup or comparison shot — and when it happens the background must be near-empty. |
| Facts and figures | **zero on this plate** | Under the illustrative-or-evidential rule they get their own composed plate. |

So "three characters plus two fact items" should not occur: the fact items are a
separate cut. In practice a busy frame tops out at 3 background elements plus 1–2
characters, and the strong references sit at **2–3 total**. Five appeared only
where zone separation was unusually strong.

---

## Composition Block — paste into every prompt

```
Use: asset for compositing into an explainer video. Isolated library element, not
a finished illustration.
Camera: eye-level, straight-on, no perspective distortion, no dutch angle.
Framing: full subject with clear margin on all sides, nothing cropped.
Lighting: soft even light from the upper left, gentle shadow falling lower right,
low contrast. Identical light direction on every asset in this library.
```

**Lighting direction is the one that breaks composites.** Assets lit from different
sides cannot sit in the same frame — the viewer reads it as wrong without being
able to say why. Upper-left is arbitrary; what matters is that it never varies.
Add it to every prompt including worlds and objects.

## Transparency Block — cutouts only

```
Background: fully transparent. The subject is isolated with nothing behind it.
No scenery, no solid backdrop, no gradient backdrop, no checkerboard pattern, no
ground plane, no cast shadow on any surface, no vignette, no border.
```

Set `background="transparent"` and `output_format="png"` on the request as well.
Saying it in the prompt *and* the parameter matters — the parameter controls the
alpha channel, the prompt stops the model painting a backdrop into the pixels.
JPEG cannot carry transparency; omit `output_compression` for PNG.

**On shading:** the host carries soft rendering, so the library must too or the
frames will not read as one picture. What is being cut is *element count and
busyness*, not rendering weight. Ask for gentle depth between paper layers; refuse
glossy highlights, photographic texture and heavy painterly detail.

## Negative Block — paste into every prompt

```
Negative: no text, no words, no letters, no numerals, no charts with labels, no
currency symbols, no logos, no watermarks, no signatures, no UI chrome. No
photorealism, no celebrity likeness, no toy or childish proportions, no extra
fingers, no malformed hands, no cropped feet, no floating props, no busy
background clutter, no dark navy full-bleed grounds.
```

**The no-text rule is absolute.** Every figure, label and caption is composited by
the renderer as real type. A plate with generated text is not render-eligible.

---

## Generation settings

| Asset class | Size | Background | Quality |
| --- | --- | --- | --- |
| Character sheets and poses | 1024×1536 portrait | **Transparent** | **High** |
| Object / mechanism cutouts | 1024×1024 | **Transparent** | Try **low** first |
| World / environment plates | 1536×1024 landscape | Opaque, light ground | Try **low** first |

**High only where identity is at stake.** Character sheets and poses are
identity-sensitive edits, which is exactly the case that justifies the cost. Worlds,
objects and mechanisms are neither identity-sensitive nor text-bearing — start them
at `low`, look at the result, and only step up if it fails acceptance. An earlier
draft here specified high across the board; that was over-cautious and slower for
no benefit.

For each character, generate the **identity sheet first**, then attach it as a
reference for every pose in that character's set. Do not generate poses from text
alone.

---

## Batch 1 — Cast (highest value; do this first)

### 1A. Host — poses only, identity unchanged

**Do not regenerate the host.** `finance-host-identity-master-v3.png` stays as the
canonical identity sheet. Attach it as reference for every pose below and ask for
his existing rendering to be preserved.

Prefix each pose prompt with:

```
Image 1: identity reference for this character.
Change only the pose. Keep everything else the same as Image 1 — same face, same
locs, same glasses, same deep-indigo suit, copper tie and gold lapel pin, same
rendering style, same level of detail, same colours. Do not simplify, flatten or
restyle him. Preserve the transparent background.
```

Repeat that preserve list on **every** pose request, not just the first. Dropping
it on later iterations is the main cause of slow identity drift across a set.

Then, with `finance-host-identity-master-v3.png` attached as reference, generate:

| File | Pose body |
| --- | --- |
| `actor-host-present-open-v1.png` | `Same character, three-quarter view, standing, one hand open and extended to his left as if presenting something beside him, palm up. Gaze follows the hand, looking to his left, not at the camera. Full body, feet visible.` |
| `actor-host-point-right-v1.png` | `Same character, three-quarter view, arm extended pointing to his right at something off-frame, index finger extended. Gaze follows the pointing hand to his right. Full body, feet visible.` |
| `actor-host-arms-crossed-v1.png` | `Same character, front view, arms folded across chest, calm appraising expression. Looking directly at the camera. Full body, feet visible.` |
| `actor-host-explain-both-hands-v1.png` | `Same character, front view, both hands raised palms-up at chest height mid-explanation. Looking directly at the camera. Full body, feet visible.` |
| `actor-host-concerned-v1.png` | `Same character, three-quarter view, one hand raised palm-out in caution, brow slightly furrowed. Looking directly at the camera. Full body, feet visible.` |

**Gaze is doing real work.** A host pointing right while staring at the camera
reads as broken. Presenting and pointing poses look *at what they indicate*;
direct-address poses look at the viewer. That single detail is what makes a
composited figure feel placed in the scene rather than pasted onto it.

### Rendering weight — the host outranks the cast

The host is the most defined figure on screen; the civilians are deliberately
lighter. Both references do this — Wealth Logic's lab-coat expert carries more
definition than the civilians he explains things to — and it does real work: it
tells the viewer who to listen to without a caption, and it keeps a two- or
three-person frame from competing with itself.

Prepend this to every civilian prompt:

```
Rendering weight: lighter and simpler than the host character. Fewer paper layers,
softer and flatter shading, less garment detail, no accessories, no pattern. Clean
readable silhouette. He should read as a secondary figure beside a more defined
presenter.
```

Keep the host's own rendering untouched — the contrast comes from making the
civilians lighter, never from reducing him.

### 1B. Civilian A — the index investor

`actor-civilian-a-identity-v1.png`
```
Character identity sheet, full body, front view, neutral standing pose.
Original fictional man in his early thirties, medium-brown skin, short cropped
hair, no glasses. Teal crewneck sweater, charcoal chinos, plain sneakers.
Ordinary and approachable, not styled or wealthy.
[Style Block] [Negative Block]
```

Then with that attached: `actor-civilian-a-present-v1.png`, `actor-civilian-a-shrug-v1.png`,
`actor-civilian-a-content-v1.png`, `actor-civilian-a-point-v1.png` — same pose bodies
as the host table, substituting "Same character".

### 1C. Civilian B — the stock picker

`actor-civilian-b-identity-v1.png`
```
Character identity sheet, full body, front view, neutral standing pose.
Original fictional man in his early thirties, light-tan skin, dark hair with a
side part. Coral open collared shirt, charcoal trousers, plain leather shoes.
Deliberately readable as a distinct person from the teal-sweater character at a
glance: different garment colour, different silhouette, different hair.
[Style Block] [Negative Block]
```

Then: `actor-civilian-b-present-v1.png`, `actor-civilian-b-shrug-v1.png`,
`actor-civilian-b-stressed-v1.png`, `actor-civilian-b-point-v1.png`.

**Why colour matters more than face:** at playback size the viewer distinguishes
these two by teal versus coral, not by facial features. Keep those garment colours
locked and never swap them within a season.

---

## Batch 2 — Worlds (light grounds, right third clear)

| File | Prompt body |
| --- | --- |
| `world-exchange-floor-v1.png` | `A stock exchange interior as cut paper: tall columns, a wide open floor, a large blank display board with no text on it. Cream and charcoal with cobalt accents. Wide empty floor space in the right third.` |
| `world-home-living-v1.png` | `A modest living room as cut paper: sofa, low table, window with daylight, a plain rug. Warm cream ground. Right third of the frame is empty wall.` |
| `world-office-desk-v1.png` | `A simple home-office corner as cut paper: plain desk, closed laptop with a blank screen, one chair, a small plant. Cream ground. Right third empty.` |

## Batch 3 — Objects

| File | Prompt body |
| --- | --- |
| `object-index-basket-v1.png` | `A woven paper basket holding many small identical paper tiles standing upright like files, in teal, cobalt, coral and sunflower. Isolated object, transparent background.` |
| `object-single-share-v1.png` | `One single upright paper tile with a blank face and a torn top edge, cobalt. Isolated object, transparent background.` |
| `object-coin-stack-v1.png` | `A neat stack of round paper discs with blank faces, sunflower and copper. Isolated object, transparent background.` |
| `object-dividend-drip-v1.png` | `A paper spout with three round paper discs falling from it into a small open paper vessel. Isolated object, transparent background.` |

## Batch 4 — Mechanisms

| File | Prompt body |
| --- | --- |
| `mechanism-capital-flow-v1.png` | `A simple cut-paper flow diagram: three small paper figures on the left, a wide arrow band flowing right into a single large paper container. Two elements plus the arrow, nothing else. Transparent background.` |
| `mechanism-growth-comparison-v1.png` | `Two blank cut-paper bars side by side on a shared baseline, one clearly taller than the other, teal and coral, with no scale markings, no axis and no labels. Transparent background.` |
| `mechanism-risk-concentration-v1.png` | `A cut-paper pie form split into one very large wedge and several thin slivers, cobalt for the large wedge and cream for the slivers, with no labels or percentage marks. Transparent background.` |

**On the two chart mechanisms:** they are deliberately blank. The renderer draws
the bars to the real values and composites the numbers as type. A generated chart
with generated numbers is the failure mode that visibly damages the weakest
references in the review.

---

## Acceptance — reject and regenerate if

1. **Any text, numeral or label appears anywhere in the image.** No exceptions.
2. The right third is not clear enough to place a host or a figure.
3. Density exceeds three elements.
4. The ground is dark navy full-bleed on anything meant to carry captions.
5. Glossy highlights, photographic texture or heavy painterly detail are present.
   Soft directional shading is wanted, not banned — it is what lets an asset sit
   beside the host.
6. A character's garment colour drifts from its locked value.
7. Hands are malformed or feet are cropped on a full-body cutout.
8. Palette strays outside the six declared colours.

---

## Evidence layer — diagnosis from the p34 render

Dense sampling of 02:00–03:30 corrects an earlier claim that the render carries no
on-screen figures. It does. Two findings, one a bug and one a design issue:

**Bug: the second evidence board often does not appear.** Operator-confirmed. An
earlier draft here described a blank cream board rendering and holding on the
right; **that was an artefact of frame extraction, not something on screen** — the
operator does not see it in playback. The real, confirmed symptom is simply that
the second board frequently fails to show up. Do not chase the cream rectangle.

**Design: the boards are built like citations, not broadcast graphics.** The
populated boards carry a title, three subsections and paragraphs of small body
text plus a diagram — for example "Bridging the AI Bandwidth Gap" with HBM,
High-Bandwidth Flash and eSSD sections. That is a source document. The performing
references put **one figure, huge**: `YR 1: $55,000`, or `$50K + $36K = $86K TOTAL
IN.` A viewer has roughly eight seconds of narration per slot; they can read one
number, not three paragraphs.

Both instincts are right and they should be **split, not merged**:

- **The figure** goes on a composed plate, one number at broadcast size. `T13`
  already renders exactly this (`figure_board`, `arithmetic_stack`,
  `comparison_pair`, `stat_row`) with verified arithmetic.
- **The citation** stays as a small persistent chip, or moves to the description.
  The "This is not proof" labelling discipline visible in the render is a real
  differentiator and worth keeping — just not competing with the figure for
  attention.

**Alternate plate types rather than overlaying.** Wealth Logic does not overlay
figures onto illustration; it cuts between an illustrative plate and a plate that
*is* the whiteboard. A plate is either illustrative or evidential, not both. That
removes the collision problem entirely and needs no contextual awareness from the
art.

The `right third clear` rule above then only has to serve the cases where an
overlay genuinely belongs on artwork — a callout or a label, not a document.

## Count

25 assets: 15 character (3 sheets plus 12 poses), 3 worlds, 4 objects, 3 mechanisms.

## After generating — and one field you must not skip

Drop everything into `assets/generated/cutouts/`, then register each asset in
`asset-catalog.v1.json` with the fields it already uses: `asset_id`, `path`,
`sha256`, `kind`, `semantic_tags`, `visual_worlds`, `identity_lenses`,
`resolution_tier`, and the eligibility flags.

**Add `style_version: "paper-cut-reduced-density-v2"` to every asset in this
batch.** The catalogue currently has no style binding, and these 25 assets are
generated under a *different* style from the 18 already in it — reduced density,
restored paper texture, host-matched shading weight. Without that field an agent six months from
now will composite a sparse v2 actor onto a dense v1 world and the frame will not
read as one picture. Backfill `style_version: "crinkle-cut-v1"` onto the existing
18 at the same time; it is a one-line edit each and it is far cheaper now than
after the library has grown.

Until an asset is registered it cannot be composited into a slot.
