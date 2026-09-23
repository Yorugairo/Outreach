# V5 private review

Opening narration now starts at zero: “No charges filed. Then Sharaf delivered a one-punch verdict.” Measured `audio/verdict-v4.words.json` places one-punch at 2.199–2.694 s. Transformation flash is at 2.200 s; full character reveal at 2.307 s. Caption timing uses that measured sidecar. The prior opening line and repeated verdict VO at 8.1 s are removed; original fight audio is restored there.

The 17.8 s Henderson/Bisping boundary now uses a short fade-through-white (17.633–17.967 s), with a whoosh at 17.5 s and bass landing at 17.8 s. Existing “Look familiar?” narration and verified v4 head-snap animation are preserved.

## Verification

- Render session 3495 completed exit 0.
- Complete final MP4 FFmpeg decode passed with no errors.
- H.264/AAC, 1080x1920, 24 fps, 590 video frames, 24.618 s container duration.
- Master WAV: 24.600 s, 48 kHz stereo, peak -1.0 dBFS; no clipping.
- Inspected actual export sheets `final-hook-review.jpg` and `final-transition-review.jpg`: new captions, anime reveal on the hook, and white flash resolving into Henderson/Bisping; no black gap.
- Hook derivative timing review: `hook-sync-review.jpg`.
- Final SHA-256: `AC2737C518E41DCB8EFEE0FD03EC0359728C0AB007F5FB7B883AE269AFE2ECD9`.

Artifact: `../assembly-v5/build/render/knockout-brain-matchcut-001-v5.mp4`.

The existing generic motion gate still reports M11 (no chart) and M16 (clip-world motion not credited). Render used a recorded private-review override; this is not a claim that all gates passed or that the operator approved release. Prior versions remain intact. Nothing uploaded or published.
