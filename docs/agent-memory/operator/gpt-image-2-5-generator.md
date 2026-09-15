---
name: gpt-image-2-5-generator
description: GPT Image 2.5 is the operator's leading image generator (2026-09-14) - reasons with GPT 6 during generation; the new icon assets came from it; P58's prompted-layer plates should try it first
metadata:
  type: project
---

The operator, 2026-09-14: "GPT Image 2.5 released and is by far the leading image-generator, and is actually able to use GPT 6
reasoning during the image generation, so we can do some pretty spectacular things with generations that wouldn't have worked
previously, that's where the new icon assets came from" (the 44 approved finance cutouts / icon set, E93/E94).

**Why:** the plate pipeline on the record drives Google Flow over CDP (`flow-driver-traps`); a generator that reasons during
generation can hold a layout, a style and a separation instruction (four depth layers with alpha, one style) that Flow could not.
This is the operator's statement, not measured here - a capability claim to verify on our own plates before doctrine.

**Codex's capability read (the operator asked, 2026-09-14):** a strong generator/editor (Sunburst for precise iterative edits, Flare for
speed; quality levels xhigh and max; text + image inputs) - NOT a native 2.5D scene-asset generator. Promptable: a 2.5D-looking
composition, a transparent RGBA asset (PNG/WebP, `background: "transparent"`), an alpha mask for an edit. NOT: separate named layers
(output is flattened), a depth map, vector/SVG paths, semantic roles, a camera/parallax path. The practical pattern: generate EACH
LAYER as a separate transparent asset with a shared camera brief and a reference image, then clean the alpha, derive the depth, assign
the roles and author the camera path in our compositor. Prompt pattern: "Create ONLY the foreground subject as an isolated transparent
PNG asset. Match the supplied composition reference exactly: 50mm eye-level camera, subject centered at x=62%, lower edge at y=92%,
full silhouette visible. No background, no ground plane, no cast shadow, no text. Designed for 2.5D parallax compositing; clean edge
separation and no cropped limbs."

**The operator's takeaway (E98 s5):** every layer prompt is adapted to our style and the specific plate AND states the intent - "designed for 2.5D parallax compositing" - because the generator's reasoning makes the intent's choices only when told.

**How to apply:** P58 T1 route (a) = one transparent asset per layer (background / mid / subject / occluder) from GPT Image 2.5 Sunburst with a shared
camera brief + one reference image, Flow as the comparison; the depth, roles and camera path are OURS (the P58 T2 sidecar) - never ask one
generation for a layered scene; the plate library records the generator per plate; nothing on the record retires the Flow driver. Related:
[flow-driver-traps](flow-driver-traps.md), [codex-fulfillment-flow](codex-fulfillment-flow.md) (image claims), [resume-2026-09-12](resume-2026-09-12.md).
