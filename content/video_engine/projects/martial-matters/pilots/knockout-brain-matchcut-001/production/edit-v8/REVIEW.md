# V8 music bed and native-speed opening

Requested: user-provided `C:/Users/Snipe/Downloads/Inspired by nang.wav` underneath, and no post-freeze opening slowdown/audio warping.

- Source action 0.2–3.5 s runs at exactly 1x from timeline 2.866667–6.166667 s. Native-rate fight audio is rebuilt from that same source interval; no atempo, pitch change, or resampling-as-speed effect. Normal sample-rate conversion only.
- First 56 pre-punch frames and 30 anime frames are unchanged. Freeze still begins after “filed”; transformation flash remains on “one-punch.”
- Full combination, follow-through, fall, canvas impact and referee intervention remain before the interview. Parent inspected `native-speed-action-review.jpg`.
- Short interview now starts at 6.166667 s, lasts 1.433333 s. Local small.en ASR on the actual mixed `quote-check.wav` returns “This guy raped a woman.” Opening ASR retains the verdict line (proper name misrecognized as Sheriff). These are speech-detection checks, not a claim of listening audition.
- Music uses the supplied track's first 23.666667 s. Stored reproducible `music-excerpt.wav`; source SHA-256 `9f1a40f5f9dec8e18f03a3b36d30646c58ce7d6a0cf08208976455bd7e5b9dda`.
- Music normalized to -27 LUFS before foreground sidechain ducking (4:1, 10 ms attack, 250 ms release), short entrance and ending fades. Full mixed master peak -1.0 dBFS, mean -19.6 dBFS, duration 23.666667 s.
- A mix timeline offset was caught by duration and speech checks. Initial render 19040 was stopped, exit 1. Anchoring the mix on zero-time narration corrected the offset; duration assertion added. Corrected render session 32419.
- Existing later X-ray choreography and stylized replay tail remain unchanged, shifted 0.433333 s earlier; this revision removes the opening slowdown, not the established animation timing.

Final export `../assembly-v8/build/render/knockout-brain-matchcut-001-v8.mp4`: session 32419 completed exit 0. Full FFmpeg decode passed. H.264/AAC, 1080x1920, 24 fps, 568 frames, 23.670 s container. Actual final ground-impact/referee/interview frames inspected in `final-boundary-review.jpg`.

SHA-256 `CFACF390109F56701BABB28CC274325F2A0FE92D14E31C9314AE3FE6195B03FB`.

Existing M11/M16 generic motion gate failures are private-review overrides, not passing-gate claims. No publication or upload. Prior versions preserved.
