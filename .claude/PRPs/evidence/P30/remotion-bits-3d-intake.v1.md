# Remotion Bits 3D Intake v1

Date: 2026-08-15  
Status: intake-required; not enabled in the production catalog

## Findings

- `ken-burns-effect` is already enabled through the reviewed local adapter in
  `content/video_engine/editor/src/remotionBits/adapters.tsx`.
- Upstream Ken Burns uses `Scene3D` steps and camera movement. Our adapter is
  intentionally smaller: a deterministic local image reframe with closed
  props, appropriate for a full-frame world plate or image-led crop.
- Upstream Basic 3D uses `Scene3D`, `Step`, and `Element3D`.
- Upstream Transform3D relies on matrix/quaternion interpolation and adds a
  `three@^0.182.0` dependency through its utility path.

## Recommendation

Use the enabled Ken Burns adapter for a restrained proof now. Do not enable
Basic 3D or Transform3D directly in the editor until a separate intake has:

1. recorded exact source files, hashes, license, and transitive dependency
   hashes;
2. defined closed prop schemas and duration limits;
3. proven deterministic normal and diagnostic renders;
4. demonstrated that an anchored 3D handoff preserves the world-plate hero,
   evidence hierarchy, captions, and mobile framing.

## Full-frame world-plate finding

An isolated `Scene3D` test confirmed that the component is unsuitable as a
generic transition between two dense full-frame world plates: its spatial-plane
model leaves two detailed compositions simultaneously visible during a camera
move. Use Scene3D for discrete spatial objects or presentations, not this
editorial world-to-world cut.

The isolated `KenBurnsEffectProof` instead validates Remotion's native 3D
`bookFlip` presentation: both plates remain visible through the dimensional
handoff and the effect does not introduce a blank canvas. It does create a
narrow dark fold near the outgoing edge, so it remains a selective scene-break
option requiring human visual approval, not a default transition.

## Intended use if approved

Use a 12–18 frame depth handoff only at a true scene boundary: outgoing world
plate recedes slightly, incoming world plate arrives from the same semantic
direction, and no evidence card or caption is present during the move. It is
not approved for constantly rotating cards, a faux presentation space, or
reading dense PowerPoint evidence.
