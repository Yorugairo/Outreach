# P16 T2 Compositor Evidence

Date: 2026-08-07
Status: accepted by parent review

## Changes

- `EditorialMotion` now registers `EditorialMotionComposition` directly.
- Existing `EditorialComposition` and `DocumentaryComposition` registrations
  remain intact.
- Added a deterministic two-shot local SVG/WAV fixture and a local Remotion
  render script.
- Added focused path/asset boundary tests.

## Validation

```text
npm --prefix content/video_engine/editor run typecheck -> pass
python -m pytest content/video_engine/tests/test_remotion_editorial_fixture.py -q
-> 13 passed in 0.31s
npm --prefix content/video_engine/editor run render:editorial-motion-fixture
-> pass
ffprobe -> H.264 640x360 at 15/1 fps; AAC audio; 4.053333 seconds
MP4 SHA-256 -> 8f10358be9acaef30422375777e3c0d139091e53e57104c05a4182d86dd854f4
git diff --check -> pass (line-ending warnings only)
```

Rendered artifact:

`content/video_engine/runtime/jobs/p16-fixture/editorial-motion-two-shot.mp4`

## Dependency Advisory

`npm ci` installed the committed lockfile without upgrade. `npm audit` reports
two high-severity transitive development-tool advisories:

- `fast-uri@3.1.4` through Remotion CLI -> webpack -> schema-utils -> ajv.
- `js-yaml@4.3.0` through Remotion Studio server -> svgr -> cosmiconfig.

No `npm audit fix` was run because P16 locks Remotion at 4.0.502 and forbids an
unreviewed dependency mutation. The current proof is local-only and accepts no
remote asset URL or arbitrary YAML. Reassess and constrain Studio exposure in
T7 before any network-accessible review surface.
