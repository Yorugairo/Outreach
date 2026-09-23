# V12 unintended frozen tail repaired

Confirmed in actual v11 export: 5.875–6.583333 s (0.708333 s) frozen. The same hold exists inside `impact-v4/impact-composite.mp4` from local 2.966667 s onward, so this is baked footage, not a playback issue. Blender's source image sequence is configured with frame_duration90 while scene frames run through111; the hold starts at that boundary despite intended continuing source offsets.

Replaced delivery frames140–175 (5.833333–7.333333 s) with original source frames60–104 (2.0–3.5 s), native speed, source-contiguous with the preceding action. Brain/skull effect finishes before this repair; effect, narration, music and timeline remain intact. Exact encoded audio stream equality asserted.

- Final decode passed; 1080x1920, 24 fps, 447 frames, 18.648 s container.
- Final freeze detector finds only the intended 1.208333–1.750 s opening freeze. No freeze near6s.
- Parent inspected `final-tail-review.jpg` from actual final export: continuous ground follow-through.
- Final `../assembly-v12/build/render/knockout-brain-matchcut-001-v12.mp4`.
- SHA-256 `e22a43540deaf1d6bcc0beb81d9bd0f068cc0802978d5ba6c74c4665e81f9a35`.

Original Blender scene and v11 are preserved; this is a versioned editorial tail repair, not an unverified claim that the Blender generator was fixed. No publication or upload.
