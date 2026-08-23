# Composition and Scale Spec

Specification of record for how figures, worlds, and depth planes relate in a
composited frame. Derived from the episode-1 library intake
([23-EP1-LIBRARY-INTAKE-REVIEW.md](23-EP1-LIBRARY-INTAKE-REVIEW.md)), where every
scale problem traced back to a world plate rather than a compositor setting.

## The rule that governs everything else

**Figure size is not a compositing choice. The furniture already in the plate
decides it.**

A world drawn with a chair back at 0.45 of frame height has committed to a
1.75m adult at 0.92 of frame height. Compositing the cast smaller than that makes
them read as dolls; no compositor setting can undo it. If the intended figure
scale changes, the world must be regenerated.

## Two independent numbers

The episode-1 review initially conflated these into one, which is why several
successive answers were wrong. They are separate:

| Field | Standard | Meaning |
| --- | --- | --- |
| `world_figure_scale` | **0.50** | The figure height the *furniture* is drawn for. A mid-distance set. |
| `cast_figure_height` | **0.76** (range 0.72–0.80) | The height the *cast* composites at. Closer to camera than the set. |

The cast is larger than the world's own figure scale by design. That is a
foreground/background split, not a perspective error: a person 2m from camera in a
room whose furniture sits 6m back genuinely reads about 1.5x larger. At 0.76 the
ratio is 1.52x.

What the split buys:

| Cast height | Head at y | Clear top band | 2 figures | 3 figures |
| --- | --- | --- | --- | --- |
| 0.72 | 0.26 | 26% | 874px | 1255px |
| **0.76** | **0.22** | **22%** | **923px** | 1325px |
| 0.80 | 0.18 | 18% | 971px | 1395px |

Widths are combined trimmed cutout widths at 1920x1080. The clear top band is
overlay, evidence, and motion headroom.

## Shot types

A world is generated for one shot type. They are different shots, not different
qualities, and a plate cannot serve both.

| Shot type | `figure_height` | Figures | Use |
| --- | --- | --- | --- |
| **Group-shot world** | 0.50 | 2 at 0.76, or 3 at 0.50 | Conversation, comparison, contrast pair |
| **Close-up room** | ~0.90 | 1 | Host alone in a space |

Three figures do not fit at 0.72–0.80 — they need 1255–1395px against a widest
current clear zone of 1056px. The three-shot is a 0.50 frame, or it needs a world
with a wider clear zone.

**Worlds intended for group shots need roughly 55% of frame width clear**, not a
third. The original "right third empty" rule was written for the host alone.

## Placement

Every world declares where a figure may stand. Without it a compositor has no way
to know the left of the frame is furniture, and figures end up standing on it.

```json
"placement": {
  "figure_zone": [0.55, 1.0],
  "baseline_y": 0.98,
  "figure_height": 0.50,
  "max_figures": 2
}
```

- `figure_zone` — `[x0, x1]` as a fraction of frame width; the span of clear floor.
- `baseline_y` — where a foreground figure's feet land.
- `figure_height` — the figure scale this plate's furniture implies. Verified, not chosen.
- `max_figures` — follows from clear width divided by figure width at the standard.

Read these off the plate. An automatic detector was attempted during intake and
abandoned; it disagreed with what is plainly visible, and three hand-declared
numbers per world are cheaper and correct.

**Where two figures share a frame, they share a scale.** Placing one smaller *as
well as* duller reads as "unimportant" rather than "the other person in the
conversation." Depth staging — one figure genuinely further back, feet higher and
proportionally shorter — is fine; arbitrary shrinking is not.

## In-scene plates — the third scale band

Beyond worlds and cast there is a third role, introduced by the v3 delivery and
adopted: a dense illustrative plate composited **into** a scene at a controlled
screen height, occupying space the world leaves free.

This is what makes the dense engraved mechanisms usable. The v2 review found they
were 1.8x the host's internal detail and could not sit beside him as props. At a
bounded screen height, in unoccupied space, that density reads as an in-scene
object rather than competing illustration — and it never enters the figure zone.

| Role | Screen height | Rule |
| --- | --- | --- |
| **Mechanism plate** | 0.36 – 0.44 | Takes a free wall, floor or edge slot. May share a frame with a host or an evidence card. |
| **Support object** | 0.24 – 0.34 | Supports a host or world plate; stays subordinate to any mechanism plate in frame. |
| **World** | figure scale 0.50 | Unchanged. A plate uses only space the world leaves unoccupied, and never the figure zone. |

Three consequences worth stating:

- **A plate is placed, not floated.** It should read as mounted, leaning, or
  resting on a surface the world provides. A plate hovering in open air reads as
  pasted on, which is the same representational failure as photographic texture.
- **The figure zone is inviolable.** A plate that intrudes on `figure_zone` is
  rejected regardless of how well it reads, because the zone is what makes the
  world reusable across shots.
- **Motion is optional and belongs to the render lane.** Fading a plate in and
  scaling it up on its narration beat is a legitimate treatment, and it is
  expressed as a shot behaviour in Remotion, never baked into the asset.

## Scale verification

A world may declare one real object as a scale reference:

```json
"scale_reference": { "object": "chair back", "real_height_m": 0.85, "drawn_height": 0.45 }
```

`load_catalog` computes `drawn_height * (1.75 / real_height_m)` and rejects the
plate when the result sits more than **15%** from the declared `figure_height`.
The error names both numbers and says to regenerate the world rather than shrink
the cast. Worlds without a declared reference are unaffected.

Useful reference heights: adult 1.75m, doorway 2.0m, ceiling 2.4m, chair back
0.85m, sofa back 0.85m, desk surface 0.73m, coffee table 0.42m, balustrade rail
1.05m.

## Rendering-weight hierarchy

The host is the most defined figure on screen; supporting cast is deliberately
lighter. This is the only signal carrying that hierarchy, and it is sufficient on
its own — do not stack scale or brightness on top of it.

Measured across the episode-1 cast:

| Group | Saturation | Brightness | Internal detail |
| --- | --- | --- | --- |
| Host | 0.665 | 0.414 | 27.9% |
| Civilian A | 0.347 (52% of host) | 0.341 (82%) | 12.8% (46%) |
| Civilian B | 0.391 (59% of host) | 0.473 (114%) | 15.2% (54%) |

Roughly **2:1 on both saturation and internal detail**. Note brightness is not
doing the work — civilian B is brighter than the host — so the separation is
colour intensity and line density.

**Keep the host's own rendering untouched.** Contrast comes from making supporting
cast lighter, never from reducing him.

## 2.5D depth planes

A world may ship as separated planes instead of one flat image. The renderer's
bounded foreground parallax (`content/video_engine/editor/src/EditorialMotion.tsx`,
P13) and the composite recipe (P14 T14 Phase 2) both already expect these layers;
a flat plate simply gives parallax nothing to separate.

Planes are declared back to front, and must be nameable depth layers with a
background present:

| File suffix | `depth_layer` | Contents | `parallax_factor` |
| --- | --- | --- | --- |
| `-far` | `building_or_environment` | Walls, windows, architecture, floor. Opaque. | 1.0 |
| `-board` | `evidence_safe_region` | The blank display surface only. Transparent. | 1.05 |
| `-mid` | `actor_or_machine` | Furniture, drawn for a 0.50 figure. Transparent. | 1.15 |
| `-near` | `foreground_cutout` | One near occluder. Transparent. | 1.40 |

The cast composites between `mid` and `near`. That arrangement gives depth on a
still frame, real parallax on a camera move, and an evidence plane genuinely
behind the characters rather than pasted over them.

`load_catalog` rejects a plane that is not a declared depth layer, a layered world
with no background plane, planes declared out of order, and a duplicated plane.

**Generate all planes of a world in one pass**, same prompt and seed where the
tool allows. Separately generated planes will not register, and misalignment is
far more visible in motion than in a still.

## Cutout requirements

- Character poses 1024x1536 portrait, transparent, full body with feet visible.
- Objects and mechanisms 1024x1024, transparent.
- Worlds 1536x1024 landscape; `-far` opaque, all other planes transparent.
- Edges hard-cut with a thin antialias rim. No matted-in background colour and no
  baked drop shadow — both show as a halo on any ground that is not the one the
  asset was cut from.
- An outline treatment is allowed but must be consistent across the whole cast.
  The episode-1 host carries a cream sticker outline the civilians lack; at equal
  scale that inconsistency is visible.

## Representational register

Assets in one frame must claim the same degree of reality. This is distinct from
density and is the more common failure.

A drawn character over a flat paper set works — that convention is familiar, and
the episode-1 host reads correctly over cut-paper worlds despite being a different
medium. What breaks a frame is an object with **photographic texture and legible
micro-detail** sitting in an illustrated set: the eye goes to it because it is the
only thing claiming to be real.

Concretely: no photographic surface, no legible micro-detail, no printed matter
behind or beneath a subject, and a palette locked to the declared set.

## Enforcement

| Rule | Enforced by |
| --- | --- |
| Human scale matches the declared figure height | `_scale_errors` in `asset_catalog.py` |
| Depth planes are valid and ordered | `_layer_errors` in `asset_catalog.py` |
| One episode does not mix art directions | `_style_errors`, keyed on `style_families` |
| Render uses only operator-promoted assets | `_eligible(for_render=True)` |
| Placement and scale travel with the asset | `asset_catalog.schema.json` |

## Related

- [23-EP1-LIBRARY-INTAKE-REVIEW.md](23-EP1-LIBRARY-INTAKE-REVIEW.md) — the measurements behind every number here
- [16-EDITORIAL-MOTION-SYSTEM.md](16-EDITORIAL-MOTION-SYSTEM.md) — camera motion that consumes these planes
- [prompts/LIBRARY-BUILD-EP1-V3-REGENERATION.md](prompts/LIBRARY-BUILD-EP1-V3-REGENERATION.md) — the current generation brief
