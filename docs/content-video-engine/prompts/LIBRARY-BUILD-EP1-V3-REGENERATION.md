# Library Build — Episode 1 v3 Regeneration

Supersedes [LIBRARY-BUILD-EP1-INDEX-FUNDS.md](LIBRARY-BUILD-EP1-INDEX-FUNDS.md).
Scale, placement, and depth rules are specified in
[24-COMPOSITION-AND-SCALE-SPEC.md](../24-COMPOSITION-AND-SCALE-SPEC.md).

## What this batch is, and what it is not

**Keep, do not regenerate: all 15 character poses.** Host and both civilians came
back correct — identity holds across poses, garment colours locked, feet visible,
no text, and the rendering-weight hierarchy landed at roughly 2:1 on saturation
and detail. They are done.

**Regenerate: 3 worlds and 7 objects/mechanisms.** Two distinct reasons:

| Batch | Count | Why |
| --- | --- | --- |
| Worlds | 3 | Drawn at the wrong human scale, and flat instead of layered |
| Objects | 4 | Photographic surface, accumulated filler, oversized |
| Mechanisms | 3 | Same |

**Total: 3 layered worlds (10–12 planes) + 7 cutouts.**

---

## Blocks that carry forward unchanged

These produced the cast, which is the part that worked. Do not edit them.

### Style Block

```
Style: hand-cut layered paper collage with woodblock ink contours. Visible paper
fibre and torn deckle edges. Soft directional shading with gentle depth between
paper layers — matte, never glossy, never photographic. Bold clean silhouettes
readable at small size.
Palette strictly: cream #F4E6C7, charcoal #25313C, cobalt #1769C2, teal #178C83,
sunflower #F5B72E, coral #ED6A4A. Adult editorial tone, financially credible,
never childish.
```

### Camera and Lighting Block

```
Use: asset for compositing into an explainer video. Isolated library element, not
a finished illustration.
Camera: eye-level, straight-on, no perspective distortion, no dutch angle.
Framing: full subject with clear margin on all sides, nothing cropped.
Lighting: soft even light from the upper left, gentle shadow falling lower right,
low contrast. Identical light direction on every asset in this library.
```

Lighting direction is the single setting that breaks composites. Upper-left is
arbitrary; never varying is not.

### Transparency Block — every plane except `-far`

```
Background: fully transparent. The subject is isolated with nothing behind it.
No scenery, no solid backdrop, no gradient backdrop, no checkerboard pattern, no
ground plane, no cast shadow on any surface, no vignette, no border.
```

Set `background="transparent"` and `output_format="png"` on the request as well —
the parameter controls the alpha channel, the prompt stops the model painting a
backdrop into the pixels.

---

## New: Scale Block — every world plane

This is the change that matters most. The v2 interiors were generated as close-up
rooms whose furniture commits to an adult at 0.92 of frame height, so the cast had
to be shrunk to fit and read as dolls beside giant furniture.

State proportions on screen, not metres — image models handle fractions far better.

```
Scale: wide shot at standing eye level. A standing adult on the clear floor would
be half the image height. So: a chair back reaches about a quarter of the image
height, a sofa back about a quarter, a desk or table surface about a fifth, a
doorway a little over half, and the ceiling about two-thirds. Furniture is small
in the frame. Most of the image is wall and floor.
```

### Composition Block — worlds

```
Composition: no more than three elements, all in the left half. The right 55% of
the frame is clear floor and empty wall, with nothing standing in it and nothing
overlapping it. Generous empty space. The floor line runs unbroken across the
clear zone.
```

The old rule said "right third clear." That was written for the host alone. Two
figures at working scale need about 55% of frame width, so the clear zone widens.

---

## New: Layer Block — worlds ship as 2.5D

Generate each world as separate planes at identical dimensions, **in one pass with
the same prompt and seed** where the tool allows. Separately generated planes will
not register, and misalignment is far more visible in motion than in a still.

| File | Contents | Alpha |
| --- | --- | --- |
| `<world>-far.png` | Walls, windows, architecture, floor, floor line. Nothing free-standing. | Opaque |
| `<world>-board.png` | The blank display surface only, if the world has one. | Transparent |
| `<world>-mid.png` | All free-standing furniture, at the Scale Block proportions. | Transparent |
| `<world>-near.png` | One near occluder — a plant edge or table corner entering from a frame edge. | Transparent |

`-board` and `-near` are optional; `-far` and `-mid` are required. The cast
composites between `-mid` and `-near`.

Per-plane prompt suffix:

```
This is one depth plane of a layered background. Draw only the elements listed
for this plane, on a transparent background, in exactly the same position and
scale they occupy in the full scene. Do not redraw or include elements from any
other plane.
```

### The three worlds

| World | `-far` | `-mid` | `-board` | `-near` |
| --- | --- | --- | --- | --- |
| `world-exchange-floor-v2` | Columned hall interior, stone floor with inlay lines | Podium and balustrade | Large blank display board, no text | Column edge entering from frame left |
| `world-home-living-v2` | Wall, window with daylight, floor, floor line | Sofa, low table, rug, potted plant | — | Plant leaves entering from frame left |
| `world-office-desk-v2` | Wall, floor, floor line | Desk, chair, closed laptop with blank screen, small plant | — | Desk corner entering from frame left |

Worlds are 1536x1024 landscape.

---

## Objects and mechanisms — same subjects, corrected surface

The engraved direction is approved. The problem was never the style; it was
**photographic surface and accumulated filler**. Every v2 object arrived carrying
scatter the prompt never asked for: loose coins, banknote collage, newspaper
backing, postage stamps, laurel branches, a bulldog clip.

Add to the Negative Block for these seven:

```
Subject only, on empty ground. No scattered coins, no loose banknotes, no
newspaper or printed backing, no postage stamps, no laurel or foliage, no clips,
no decorative filler of any kind. Nothing behind or around the subject.
No photographic texture and no legible micro-detail. No silver or grey metal.
```

And a substrate instruction, which is the half that was missing:

```
Built from matte paper: visible paper grain, torn and layered edges, flat tone.
Engraved line quality is welcome; engraved surface is not.
```

### Subjects — unchanged from v2

| File | Prompt body |
| --- | --- |
| `object-index-basket-v2.png` | `A woven paper basket holding many small identical paper tiles standing upright like files, in teal, cobalt, coral and sunflower. Isolated object.` |
| `object-single-share-v2.png` | `One single upright paper tile with a blank face and a torn top edge, cobalt. Isolated object.` |
| `object-coin-stack-v2.png` | `A neat stack of round paper discs with blank faces, sunflower and copper. Isolated object.` |
| `object-dividend-drip-v2.png` | `A paper spout with three round paper discs falling from it into a small open paper vessel. Isolated object.` |
| `mechanism-capital-flow-v2.png` | `A simple cut-paper flow diagram: three small paper figures on the left, a wide arrow band flowing right into a single large paper container. Two elements plus the arrow, nothing else.` |
| `mechanism-growth-comparison-v2.png` | `Two blank cut-paper bars side by side on a shared baseline, one clearly taller than the other, teal and coral, with no scale markings, no axis and no labels.` |
| `mechanism-risk-concentration-v2.png` | `A cut-paper pie form split into one very large wedge and several thin slivers, cobalt for the large wedge and cream for the slivers, with no labels or percentage marks.` |

Objects and mechanisms are 1024x1024.

### Negative Block — all assets

```
Negative: no text, no words, no letters, no numerals, no charts with labels, no
currency symbols, no dollar signs, no logos, no watermarks, no signatures, no UI
chrome. No photorealism, no celebrity likeness, no toy or childish proportions,
no extra fingers, no malformed hands, no cropped feet, no floating props, no busy
background clutter, no dark navy full-bleed grounds.
```

`no dollar signs` is new and explicit. Five of the seven v2 assets carried `$`
glyphs despite "no currency symbols" already being present.

---

## Generation settings

| Asset class | Size | Background | Quality |
| --- | --- | --- | --- |
| World planes | 1536×1024 landscape | `-far` opaque, others **transparent** | High — planes must register |
| Object / mechanism cutouts | 1024×1024 | **Transparent** | Try low first |

---

## Acceptance — reject and regenerate if

1. **Any text, numeral, label or currency symbol appears anywhere.** No exceptions.
2. A world's furniture implies an adult at anything other than ~0.50 of frame
   height. Measure one object and divide: `drawn_height × (1.75 / real_height_m)`.
   Reference heights are in the spec.
3. The clear zone is under 55% of frame width, or anything overlaps it.
4. World planes do not register — an element shifts position or scale between
   planes, or an element appears on two planes.
5. `-far` is not opaque, or any other plane is not transparent.
6. Photographic texture, legible micro-detail, specular metal, or filler objects
   the prompt did not name.
7. Density exceeds three elements on a world, or one subject on a cutout.
8. Lighting direction is not upper-left.
9. Palette strays outside the six declared colours.

Criteria 2, 3, 4 and 5 are new; they are the ones the v2 batch failed.

## On delivery

Register each asset with `asset_id`, `path`, `sha256`, `kind`, `semantic_tags`,
`visual_worlds`, `identity_lenses`, `resolution_tier`, and `style_version`. Worlds
additionally carry `placement`, `scale_reference`, and `layers`.

Follow the tier convention already in the catalogue: `actor`, `prop`,
`world_board`, `world`, `cast_board` at tier 2; `mechanism` at tier 3.

**Do not set `rights_state: approved`, `review_state: approved_reusable`, or
`render_eligible: true`.** Promotion is an operator action. The v2 batch arrived
self-promoted, which would have made seven off-spec plates render-eligible.
Register everything as `original_review_only` / `review_only` /
`render_eligible: false`.

`load_catalog` will reject a world whose `scale_reference` disagrees with its
declared `figure_height` by more than 15%, and will reject malformed depth planes.
Run it before handing the batch over.

## Related

- [24-COMPOSITION-AND-SCALE-SPEC.md](../24-COMPOSITION-AND-SCALE-SPEC.md) — the rules of record
- [23-EP1-LIBRARY-INTAKE-REVIEW.md](../23-EP1-LIBRARY-INTAKE-REVIEW.md) — why each rule exists
