# Footage-backed anime exchange accents

Private-review proof only. This is a source-footage composite with subtle authored anime accents. It does not establish a transformation or a strongly stylized fight variant and must not be presented as one; it is not a full anime remake or an approved effect recipe.

The source clock is the pinned 105-frame production/edit-media/knockout.mp4: output frame 0 maps to raw FIGHT frame 0 at 0.0 s. Contact candidates are compared at f10 and f24. Straight acceleration streaks play at f8-f9; a curved hook arc plays at f22-f23; the chosen one-frame impact marks land at f10 and f24. f25 remains clear for the receiving head snap. No source frame is held, retimed, or recolored. The source clip has no audio stream, so the preview is silent.

## Rebuild

Run from the repository root with the pinned media and timing fixture available by their exact hashes.

    python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/anime-overlay/build_anime_overlay.py --source-video "<base checkout>/content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/edit-media/knockout.mp4" --raw-source "<base checkout>/content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/ufc-sharaf-steveson-high.mkv" --timing-fixture "<base checkout>/content/video_engine/tests/fixtures/modeling/motion/source-exchange-clock.v1.json" --previews-only

Inspect review/candidate-treatments.png at phone size. Then rebuild the final proof with one selected option.

    python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/anime-overlay/build_anime_overlay.py --source-video "<base checkout>/content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/edit-media/knockout.mp4" --raw-source "<base checkout>/content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/assets/raw/source-short/ufc-sharaf-steveson-high.mkv" --timing-fixture "<base checkout>/content/video_engine/tests/fixtures/modeling/motion/source-exchange-clock.v1.json" --style broken-ring

The script refuses inputs whose SHA-256 values, format, duration, frame count, source origin, or fixture contact frames do not match the work order. It writes six transparent per-event PNG layers, the MP4, a hash-bearing manifest, a 9:16 phone-size contact sheet, and ffprobe/full-decode evidence under this directory.

## Deliverables

- anime-exchange-overlay.mp4
- manifest.json
- layers/ transparent event-layer PNGs
- review/candidate-treatments.png contact-treatment comparison
- review/source-000.png through source-010.png extracted source frames f8-f12 and f22-f27 used for contact-clock/anchor review
- review/contact-sheet-9x16.png frames f8-f12 and f22-f27
- review/detail-crops-f10-f24-f25.png native-size impact and clean head-snap comparison
- review/verification.json source rechecks, ffprobe, and full decode receipt
- review/VISUAL-ASSESSMENT.md manual phone-size review

The separately timed transformation prelude is omitted because the existing stills are not verified against the 105-frame source poses. Native scene-evidence assembly and final visual approval remain parent-owned.
