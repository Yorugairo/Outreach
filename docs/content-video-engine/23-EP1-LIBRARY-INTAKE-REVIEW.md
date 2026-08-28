# Episode 1 Library — Intake Review

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

Batch: `library-build-ep1-index-funds-v2`
Reviewed: 2026-08-22
Spec: [LIBRARY-BUILD-EP1-INDEX-FUNDS.md](prompts/LIBRARY-BUILD-EP1-INDEX-FUNDS.md)

## Verdict

**Medium: settled by the operator — the paper-cut direction did not work and the
engraved treatment is approved.** This review originally rejected the seven
objects and mechanisms partly on medium. That was wrong; it applied a spec the
operator had already moved past.

**Density: still open, and it is a separate axis from medium.** The reduced-density
rule was never an aesthetic preference. It was set for three functional reasons —
generation reliability, an eight-second read, and keeping supporting art from
competing with the presenter. Those hold regardless of which medium is used, and
the delivered objects and mechanisms breach them.

| Batch | Count | Medium | Density |
| --- | --- | --- | --- |
| Host poses | 5 | Approved | **Correct** |
| Civilian A | 5 | Approved | **Correct** |
| Civilian B | 5 | Approved | **Correct** |
| Worlds | 3 | Approved | **Correct** |
| Objects | 4 | Approved | **Too much presence — see below** |
| Mechanisms | 3 | Approved | **Too much presence — see below** |

### The measurement

Busy-pixel fraction is internal detail with the cutout silhouette eroded away, so
it measures how much is going on *inside* an asset rather than how complex its
outline is.

| Group | n | Internal detail | Frame occupancy | Distinct colours |
| --- | --- | --- | --- | --- |
| Worlds | 3 | **7.5%** | 100% (full-bleed, flat) | 75 |
| Civilians | 10 | **11.8%** | 21.7% | 61 |
| Host | 5 | **29.4%** | 29.6% | 126 |
| Objects + mechanisms | 7 | **51.7%** | 46.6% | 145 |

The intended hierarchy is host most defined, civilians lighter, worlds lightest so
they can carry a composited figure. **The 18 accepted assets hold that hierarchy
exactly.** The objects and mechanisms land at 1.8x the host's internal detail and
1.6x his frame occupancy — the supporting art is now the busiest and largest
thing in the library.

That matters differently by tier:

- **The 4 objects are `kind: prop` at tier 2** — reusable components, composited
  *into* a frame alongside the host. At 52% internal detail against his 29% they
  will visibly outrank him, which is the exact failure the rendering-weight
  instruction was written to prevent.
- **The 3 mechanisms are tier 3** — they stand as their own cut and never share a
  frame with the host, so they do not fight him. They still fail the eight-second
  read: the p34 diagnosis found the evidence layer was losing because boards were
  built like citations rather than broadcast graphics, and a mechanism plate at
  55% detail carrying scattered coins, banknote collage, stamps and bar charts is
  that same failure in a different medium.

### What the composite actually shows

Metrics said the props would outrank the host. Compositing them proved that
wrong, and the real failure is more specific.

Test frame: `world-home-living-v1`, `actor-host-point-right-v1` at 80% frame
height in the right third, `object-coin-stack-v1` as a prop at 26% height.
The host occupies 24% of the frame; the prop occupies **5.2%**.

- **The host reads exactly as designed.** He is the most defined thing on screen,
  he sits in the cleared right third, and the flat paper world does not fight him.
  The rendering-weight instruction worked in practice, not just on paper.
- **The prop does not outrank him by size** — at 5.2% of frame it is plainly
  subordinate. My density-and-occupancy argument predicted a fight that does not
  happen.
- **It fails on representational register instead.** Photographic coin relief and
  legible newsprint bar charts sitting on a flat cut-paper coffee table read as a
  photograph pasted onto a paper set. The eye goes to it because it is the only
  object in the frame claiming to be real.

Note the host is *also* a different register from the world — inked and painted
over flat paper — and he works. A drawn character over a set is a familiar
convention, his palette matches, and his line treatment is consistent. The coin
stack has none of that: photographic texture, legible micro-detail, and greys and
silvers outside the palette.

So the correction to make is narrower than "reduce density":

```
No photographic texture and no legible micro-detail. Engraved line and flat
tone only. No printed matter behind or beneath the subject — no newspaper, no
banknotes, no charts, no stamps. Subject only, on empty ground. Palette limited
to the six declared colours; no silver or grey metal.
```

Density falls out of this for free — the scatter *is* most of the density. Keep
the engraved direction and the subjects; the failure is texture and filler, not
style.

## Delivery integrity — clean

All 25 files are on disk and every `sha256` in the catalogue matches the bytes.
Dimensions and transparency match the generation table exactly.

| Class | Expected | Delivered |
| --- | --- | --- |
| Character poses | 1024×1536, transparent | 15/15 RGBA, 63–77% fully transparent |
| Objects / mechanisms | 1024×1024, transparent | 7/7 RGBA, 31–81% fully transparent |
| Worlds | 1536×1024, opaque light ground | 3/3 RGB, cream corners |

No cream halo is baked into any cutout. Partially-transparent pixels are 1–9% of
each figure — a thin antialias rim, not a matted-in background or a baked drop
shadow. Edge means are dark (~`(50,45,40)` on civilians) or warm mid-tone
(~`(191,165,128)` on the host), never the cream ground.

## Accept — cast (15)

Identity holds across all five poses for each character. Garment colours stay
locked: host navy suit / copper tie, civilian A teal crew / charcoal, civilian B
coral shirt / charcoal. Feet are visible on every full-body cutout, no text
appears anywhere, and hands read cleanly.

**The rendering-weight instruction worked.** The host carries visibly more
definition — fabric weave, gloss, patterned shoes, lapel pin, pocket square —
while both civilians are flatter, softer, accessory-free. A viewer can tell who
to listen to without a caption, which is what the instruction was for. The host's
own rendering is untouched, as required.

One note, not a rejection: `actor-civilian-a-identity-v1` and
`actor-civilian-a-content-v1` are near-duplicates (both hands-in-pockets, front
view, neutral). That is one of five slots spent twice. Worth replacing with a
distinct pose at the next generation, not worth a regeneration on its own.

## Accept — worlds (3)

On-spec cut paper: flat, matte, cream ground, 2–3 elements, no text. The
right-third clearance requirement is met with room to spare:

| World | Left ⅔ luminance σ | Right ⅓ σ | Ratio |
| --- | --- | --- | --- |
| `world-exchange-floor-v1` | 68.5 | 7.6 | 0.11 |
| `world-home-living-v1` | 62.2 | 5.5 | 0.09 |
| `world-office-desk-v1` | 70.7 | 4.9 | 0.07 |

A right third at σ ≈ 5–8 against a body at σ ≈ 62–71 is genuinely empty wall.
These will take a composited host without fighting it.

## Objects and mechanisms (7) — what arrived

The engraved treatment is approved. Recorded here for the regeneration brief is
what each asset accumulated beyond its subject.

| Asset | Asked for | Delivered |
| --- | --- | --- |
| `object-index-basket-v1` | Woven paper basket of identical blank paper tiles | Wicker grocery basket — bread, cola can, pill bottle, lettuce, wallet, calculator, `$` coins |
| `object-single-share-v1` | One blank cobalt paper tile, torn top edge | Ornate engraved certificate with seal, ribbons, scrollwork, `$` glyphs |
| `object-coin-stack-v1` | Stack of blank paper discs, sunflower and copper | Minted coins with embossed detail on printed newspaper carrying bar charts |
| `object-dividend-drip-v1` | Paper spout, three paper discs, paper vessel | Brass pitcher pouring real coins into a cash drawer, `$` glyph |
| `mechanism-capital-flow-v1` | Three paper figures, one arrow, one container — nothing else | Figures, floating `$$`, basket, scattered coins, banknotes, laurel, arrow |
| `mechanism-growth-comparison-v1` | Two blank bars, shared baseline, no axis, no labels | Five bars, rising arrow, coin stacks, `$` glyphs, bulldog clip, newspaper collage, leaf |
| `mechanism-risk-concentration-v1` | One large wedge, thin slivers, no labels | Correct pie, buried under banknotes, coins, bar charts, stamps |

Two of the original acceptance criteria still stand once medium is set aside;
two do not.

**Still stand:**

- **"Any text, numeral or label appears anywhere in the image."** `$` glyphs on
  five of seven, plus printed banknote and newspaper marks. Decorative rather
  than factual, so `contains_factual_text: false` is accurate — but it still
  breaks the cross-lane rule that no plate carries generated text, and legible
  marks compete with the composed figure that is doing the actual work.
- **"Density exceeds three elements."** Measured above: 51.7% internal detail
  against the host's 29.4%.

**No longer apply** — both were medium criteria, and the operator has set the
medium: "glossy highlights, photographic texture or heavy painterly detail" and
"palette strays outside the six declared colours." The engraved treatment implies
both.

The generating agent recorded the drift in the tags — `dollar-sign`, `bread`,
`medicine`, `cola-can`, `calculator`, `newspaper-infographic`,
`ornamental-certificate` are all on the delivered assets. Those tags are a useful
record of exactly what to strip.

Note the arithmetic still holds: these seven are the *illustrative* layer, and
under the illustrative-or-evidential rule the actual numbers were always going to
`T13` composed plates. So a density pass is cheap and blocks nothing else.

## Defects found and fixed

### 1. Self-promotion — rolled back

All 25 arrived as `rights_state: "approved"`, `review_state:
"approved_reusable"`, `render_eligible: true`. Nothing had been reviewed by
anyone. This breaks the standing rule that **`approved` is never set by product
code**, and it would have made seven off-spec plates render-eligible.

All 25 reset to `original_review_only` / `review_only` / `render_eligible:
false`. Promotion is the operator's, after this review.

### 2. Mis-tiered registration — 19 of 25 were unreachable

Every new asset was registered at `resolution_tier: 3`. Tier 3 is
`deterministic_evidence_or_mechanism` and the resolver restricts it to `kind` in
`{mechanism, world_board}`. So the 15 character poses and 4 objects sat in the
catalogue where **the resolver could never return them** — every actor and prop
slot fell straight through to `bespoke_plate`. The library would have bought
nothing; the whole cast would be regenerated every episode.

Re-tiered to the convention the original 18 assets already established:
`actor`/`prop`/`world_board`/`world`/`cast_board` = 2, `mechanism` = 3.

### 3. Resolver: a one-word coincidence pre-empted a real match

`resolve_slot` walked the cascade and returned the first tier with *any*
candidate. A host pose tagged `comparison` therefore won a mechanism slot that
`mechanism-growth-comparison-v1` matched on two tags, because actors sit at an
earlier tier. The cascade is meant to break ties between candidates that match
equally well, not to let position beat strength.

Fixed: score every tier, take the strongest overlap, and use cascade order only
as the tie-break. Covered by
`test_a_one_word_coincidence_does_not_pre_empt_a_real_match_at_a_later_tier` and
`test_the_cascade_still_wins_when_the_overlap_is_equal`.

This defect predates the batch — it never bit while only three actors existed
with narrow concrete tags (`worker`, `commuter`, `founder`). Fifteen poses
carrying pose-purpose tags (`comparison`, `caution`, `risk`, `explanation`) is
what exposed it.

### 4. Resolver: slot tags and asset tags were matched asymmetrically

Asset tags were split on `-` and required to match term-by-term, while slot tags
were added whole. An asset tagged `bar-comparison` could therefore never be
matched by a slot tagged `bar-comparison` — identical tags did not match. This is
why `world-exchange-floor-v1` was unreachable even at the right tier.

Fixed: slot tags now contribute both the whole tag and its split parts.

**After all four fixes: 0 of 25 unreachable, and eight realistic probe slots each
resolve to the correct asset of the correct kind.**

### 5. The style guard was too crude — fixed

The batch carries two `style_version` values across one coherent cast: the host
is `paper-cut-reduced-density-v2`, the civilians `woodblock-finance-editorial-v3`.
`resolve_episode_assets` raised on any episode using both.

**The composite proves that block was wrong.** Host and civilian on a shared world
read as one picture; they were generated as one cast. Exact version-string
equality is too blunt a proxy for "do these composite".

Fixed: a catalogue may declare `style_families` grouping versions known to
composite. The guard compares families, and falls back to the version string when
none are declared, so nothing existing changes behaviour. A version absent from
every family is its own family rather than a silent pass.

Declared on the real catalogue:

```json
"style_families": {
  "ep1-index-funds": ["paper-cut-reduced-density-v2", "woodblock-finance-editorial-v3"],
  "legacy-crinkle-cut": ["crinkle-cut-v1"]
}
```

Verified: host + civilian + world + mechanism resolve together at 100% coverage,
while an episode mixing `ep1-index-funds` with `legacy-crinkle-cut` is still
rejected, naming both families.

### 6. Worlds carried no placement data — figures landed on the furniture

The first two-figure composite put civilian A standing on the office chair. That
was a compositing error, not an asset defect, but it is one nothing in the
pipeline could have prevented: a world plate declared nothing about where a
figure may stand, so any compositor was free to drop one onto a desk.

Two things came out of testing it:

- **A perspective rule alone does not fix it.** Scaling height from the feet
  position (nearer = taller) is correct and now used, but it left the figure on
  the chair, because the error was horizontal. The left of that world is solid
  furniture drawn in strong perspective; there is no floor there at any scale.
- **The spec only ever asked for one clear zone.** "Right third empty" was
  written for the host alone. These worlds hold two figures only if both stand in
  that zone, host nearer and larger. Verified on `world-office-desk-v1`.

Each world now carries a `placement` block giving the span of clear floor, the
baseline a foreground figure's feet land on, and how many figures fit:

| World | Clear floor (x) | Share of width |
| --- | --- | --- |
| `world-exchange-floor-v1` | 0.45 – 1.00 | 55% |
| `world-home-living-v1` | 0.62 – 1.00 | 38% |
| `world-office-desk-v1` | 0.55 – 1.00 | 45% |

These are read off the plates directly. An automatic detector was attempted and
abandoned — it disagreed with what is plainly visible in the images, and three
hand-declared numbers per world are both cheaper and correct.

### 7. Scale was a third hierarchy signal, and one too many

Placing the civilian smaller *as well as* duller read as "unimportant" rather than
"the other person in the conversation." The rendering weight was already carrying
the hierarchy on its own — measured across all fifteen poses:

| Group | Saturation | Brightness | Edge detail |
| --- | --- | --- | --- |
| Host | 0.665 | 0.414 | 27.9% |
| Civilian A | 0.347 (**52%** of host) | 0.341 (82%) | 12.8% (**46%**) |
| Civilian B | 0.391 (**59%** of host) | 0.473 (114%) | 15.2% (**54%**) |

Roughly **2:1 on both saturation and internal detail**. That is a decisive
hierarchy already. Note brightness is *not* doing the work — civilian B is
actually brighter than the host — so the separation is carried by colour
intensity and line density, which is exactly what was asked for.

**Resolution: same scale, same baseline.** Keep the rendering weight untouched.
Brightening the civilians would erode the one signal that works; dulling the host
contradicts the standing decision to keep him stable and adjust around him.
Verified on `world-office-desk-v1` — at equal scale the host still reads
unmistakably as the presenter.

Costs nothing: no regeneration, it is a compositing rule.

**But it constrains world design.** Two figures at 80% frame height need about
970px of clear floor at 1920 wide. Current zones:

| World | Clear width | Two same-scale figures at 80%? |
| --- | --- | --- |
| `world-exchange-floor-v1` | 1056px | Yes |
| `world-office-desk-v1` | 864px | Only at ~70% height |
| `world-home-living-v1` | 730px | No — one figure, or overlap |

**Worlds intended for two-shots need roughly 55% of the frame width clear**, not
a third. That is an input to the next world batch.

One inconsistency surfaced by viewing them at equal scale: the host carries a
baked cream outline and the civilians do not. It reads as a deliberate sticker
treatment that helps him separate from any ground, and it is worth either giving
the civilians a thinner version or dropping it — but not leaving it on one
character only.

### 8. Figure scale standard: 50% of frame height

Operator's call, and the fit maths backs it. Combined figure width at 1920 wide:

| Figure height | 2 figures | 3 figures |
| --- | --- | --- |
| 80% | 971px | 1395px |
| 70% | 850px | 1220px |
| 60% | 728px | 1046px |
| **50%** | **607px** | **872px** |
| 45% | 546px | 785px |

Against the clear zones — living 730px, office 864px, exchange 1056px:

- **At 80% a two-shot does not fit any world.** That is what forced the earlier
  scale-down and produced the "standing on the chair" frame.
- **At 50% a two-shot fits every world** with room to spare, and **a three-shot
  fits the exchange floor.** That is the frame the brief asked for — all three
  characters plus room for narrative or fact elements — and it was unreachable at
  any larger scale.
- 50% is the *largest* scale at which the three-shot still works, so it is the
  right standard rather than an arbitrary reduction.

Recorded as `figure_height: 0.50` on every world's `placement` block, with
`max_figures` derived from clear width: exchange 3, office 2, living 2.

Two things the three-shot surfaced, both useful:

- The exchange floor's large blank display board is a natural
  **`evidence_safe_region`** — a composed figure plate can sit there without
  overlaying illustration, which is exactly the separation the
  illustrative-or-evidential rule wants.
- At 50% the upper half of the frame is clear cream in every world. That is where
  a broadcast-size figure goes, and it is only available because the figures came
  down in scale.

### 9. The worlds were drawn at the wrong human scale — the root cause

Every scale problem in this review traces back here, and it is a plate defect,
not a compositing one. **Figure size is not a free choice; the furniture already
in the plate decides it.** Measuring one real object per world and dividing by a
1.75m adult:

| World | Reference | Drawn height | Implied adult |
| --- | --- | --- | --- |
| `world-office-desk-v1` | chair back (0.85m) | 0.45 of frame | **0.92** |
| `world-home-living-v1` | sofa back (0.85m) | 0.45 of frame | **0.94** |
| `world-exchange-floor-v1` | balustrade rail (1.05m) | 0.32 of frame | **0.53** |

The two interiors were generated as **close-up rooms** — a correctly-scaled adult
nearly fills the frame. The exchange floor was generated as a **wide shot**, and
0.53 is right. That is exactly why the three-shot on the exchange floor looked
fine while the office two-shot looked like dolls: the exchange plate was already
correct and the interiors never were.

Shrinking the cast to fit two figures into a close-up room was solving the wrong
problem. The furniture had to shrink, and it can only shrink at generation time.

**Resolution.** Each world now declares the figure height its own furniture
implies, measured rather than chosen, with `max_figures` following from it:

| World | figure_height | max_figures | Usable as |
| --- | --- | --- | --- |
| `world-exchange-floor-v1` | 0.53 | 3 | Group shot |
| `world-office-desk-v1` | 0.92 | 1 | Single figure, close-up room |
| `world-home-living-v1` | 0.94 | 1 | Single figure, close-up room |

Nothing is thrown away — the interiors are perfectly good single-figure worlds,
verified on screen. They are simply not group-shot worlds, and the 0.50 standard
applies to worlds generated for group shots.

**Enforced from now on.** A world may declare a `scale_reference`, and
`load_catalog` computes `drawn_height * (1.75 / real_height_m)` and rejects the
plate when the result sits more than 15% from its declared `figure_height`. The
error names both numbers and says to regenerate the world rather than shrink the
cast. Worlds without a declared reference are unaffected.

### Scale Block — paste into every world prompt

Image models handle on-screen proportions far better than metres, so state the
target fractions directly. For a group-shot world:

```
Scale: wide shot at standing eye level. A standing adult on the clear floor
would be half the image height. So: a chair back reaches about a quarter of the
image height, a sofa back about a quarter, a desk or table surface about a
fifth, a doorway a little over half, and the ceiling about two-thirds.
Furniture is small in the frame. Most of the image is wall and floor.
```

For a single-figure close-up room, keep the current framing — a standing adult
would be roughly nine-tenths of the image height, and furniture reads large.

Declare which one the plate is for before generating; the two are different
shots, not different qualities.

### 10. Composition standard: cast 0.76, world drawn for 0.50

Operator's call, and it resolves the scale problem properly. Rather than one
figure height, there are **two independent numbers**:

- **`world_figure_scale: 0.50`** — what the *furniture* is drawn for. A mid-distance
  set.
- **`cast_figure_height: 0.72–0.80`, standard 0.76** — what the *cast* composites
  at. Closer to camera than the set.

That is a foreground/background split, not a perspective error: a person standing
2m from camera in a room whose furniture sits 6m back genuinely reads about 1.5x
larger. At 0.76 the ratio is 1.52x, which is squarely in that range.

What it buys:

| Cast height | Head at y | Clear top band | 2 figures | 3 figures |
| --- | --- | --- | --- | --- |
| 0.72 | 0.26 | 26% | 874px | 1255px |
| **0.76** | **0.22** | **22%** | **923px** | 1325px |
| 0.80 | 0.18 | 18% | 971px | 1395px |

Against clear zones of living 730px, office 864px, exchange 1056px:

- **Two figures fit the exchange floor at every height in the range.** Verified on
  screen: the cast reads as foreground, the architecture as mid-distance, and the
  blank display board stays free for evidence.
- **Three figures do not fit at 0.72–0.80** (1255–1395px against 1056px). The
  three-shot is a 0.50 frame, or it needs a wider world. Both are legitimate; they
  are different shots.
- The clear top band of 18–26% is the overlay and motion headroom this was chosen
  for.

The two existing interiors still do not qualify — their furniture is drawn for a
0.92 figure, not 0.50 — so they stay single-figure worlds until regenerated.

### 11. 2.5D worlds — the renderer is already waiting for them

Operator proposal, and the infrastructure exists already:

- **P13 already renders bounded foreground parallax** in `EditorialMotion.tsx`,
  verified with a real Remotion render on 2026-08-01.
- **P14 already names four `depth_layers`** — `building_or_environment`,
  `evidence_safe_region`, `actor_or_machine`, `foreground_cutout` — and T14 Phase 2
  already specifies a composite recipe naming one asset per layer.

**The only missing piece is that worlds ship as one flat image, so parallax has
nothing to separate.** Like the scale defect, it is a generation-side gap in front
of infrastructure that already works.

A world may now declare `layers`, back to front, each binding a path and sha256
with an optional `parallax_factor`. `load_catalog` rejects a plane that is not a
declared depth layer, a layered world with no background plane, planes declared
out of order, and a duplicated plane. Flat worlds are unaffected.

**What to ask for.** Generate each world as separate transparent PNGs at identical
dimensions, in one pass so they register:

| File | Depth layer | Contents | Parallax |
| --- | --- | --- | --- |
| `<world>-far.png` | `building_or_environment` | Walls, windows, architecture, floor. Opaque. | 1.0 |
| `<world>-board.png` | `evidence_safe_region` | The blank display surface only, if the world has one. Transparent. | 1.05 |
| `<world>-mid.png` | `actor_or_machine` | Furniture, drawn for a 0.50 figure. Transparent. | 1.15 |
| `<world>-near.png` | `foreground_cutout` | One near occluder — a plant edge, a table corner. Transparent. | 1.40 |

The cast composites between `mid` and `near`, at 0.76. That single arrangement
gives depth on a still frame, real parallax on a camera move, and an evidence
plane that is genuinely behind the characters rather than pasted over them.

Ask for all planes of a world in one generation pass with the same prompt and seed
where possible — separately generated planes will not align, and misalignment is
far more visible in motion than in a still.

## Open — operator's call

### Eleven catalogue entries point at files that do not exist

Pre-existing, not introduced by this batch. `actor-worker-household-v2`,
`actor-founder-v2`, the four `building-*`, `whiteboard-easel-v2`,
`mechanism-town-v1`, `finance-host-presenter-direct-v1` and the two
`stealth-wealth-*` resolve to paths with no file in that worktree. They are all
`crinkle-cut-v1`. Either the files live elsewhere or the entries are stale.

## Regeneration brief for the seven

Keep the engraved direction and keep the subjects. The problem is accumulation,
not style — see "What the composite actually shows" above for the
Negative Block addition.

Operator's call on review: **too big, and not enough paper.** Both hold. The
composite ran the coin stack at 5.2% of frame and it still pulled the eye, so
scale alone will not rescue it — but the props are also intrinsically oversized
for their role and want the paper substrate back. Regenerate the four with the
refusals above plus an explicit substrate instruction:

```
Built from matte paper: visible paper grain, torn and layered edges, flat tone.
Engraved line quality is welcome; photographic surface is not.
```

The three mechanisms are a separate question. They stand as their own cut and
never share a frame with the host, so nothing composites against them — the only
cost is the eight-second read. If they hold up full-frame at 1080p they can ship
as they are; that is a judgement call best made by looking at one on screen, not
from a metric.

## Related

- [21-ART-STYLE-REFERENCE-REVIEW.md](21-ART-STYLE-REFERENCE-REVIEW.md)
- `content/video_engine/src/services/asset_catalog.py`
- `content/video_engine/tests/test_asset_catalog.py`
