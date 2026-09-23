# V6 contact/interview revision

## Requested changes

- Opening pre-punch motion runs in optical-flow slow motion through 1.2 s; freeze starts after measured “filed” end at 1.197 s. Existing anime flash remains at 2.2 s on “one-punch.”
- The first right connects by source frame 10 / 0.333 s, with follow-through through frame 12 / 0.400 s. Hook segment now ends after that frame rather than running into the lead-left impact.
- At edit time 3.533 s, cut to the attributed interview. Original picture and audio both use source 3.840–8.340 s; no old clipped audio mix is reused.
- Resume fight at edit time 8.033 s, source frame 13 / 0.433 s. Lead-left contact at source frame 24 / 0.800 s is included, followed by recoil and fall through source 3.5 s.
- Existing head-snap effect and flash transition into Henderson/Bisping are retained as an unchanged tail, now starting at 11.1 s. Total edit 24.1 s.

## Verified evidence

- Parent and Luna inspected source contact sheets under `source-review/`; parent inspected actual final `final-right-boundary.jpg` and `final-quote-hook-boundary.jpg`.
- Actual final frames show the right-hand contact before the interview, complete visible “2019” caption, then follow-up lead hook and head recoil.
- `lead-motion-review.jpg` shows opening motion before the freeze.
- Direct source audio is retained without shortening the terminal year. Local faster-whisper small.en and base.en checks of `final-news-audio.wav` detected the complete final year ending at 4.10 s / 4.02 s within the 4.50 s window. Both ASR models rendered its digits as “2009” rather than the source caption's “2019”; ASR is endpoint evidence, not independent verification of the spoken digits. No synthetic replacement or correction was made.
- Master 48 kHz stereo, 24.1 s, peak -1.0 dBFS, mean -20.2 dBFS.
- Corrected render session 97360 completed exit 0; full final FFmpeg decode passed.
- Final H.264/AAC, 1080x1920, 24 fps, 578 video frames, container duration 24.106 s.
- SHA-256: `21DCA691C2F2707D8FBE4D33E52A7AAEB8A8BD1DF3642A500BB54ED808B9E655`.

Artifact: `../assembly-v6/build/render/knockout-brain-matchcut-001-v6.mp4`.

Initial provisional render 60393 was stopped by the parent after distinguishing the right hand from the later lead left; its exit was 1. It was not delivered. The corrected render is the final above.

Generic motion gates M11 (no chart) and M16 (clip-world motion not credited) remain recorded failures, overridden for private review only. No claim of all-gates pass, operator release approval, upload, or publication. Earlier versions preserved.
