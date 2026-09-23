# Knockout short — production ledger

Status: v12 frozen-tail correction exported and verified. Replaced frozen effect tail with continuous source frames60–104; effect/timing/exact audio stream retained. Final freeze check detects only intended opening freeze, none around6s. Full decode and actual tail frame review passed.

- Final `production/assembly-v12/build/render/knockout-brain-matchcut-001-v12.mp4`, 18.648 s, SHA-256 `e22a43540deaf1d6bcc0beb81d9bd0f068cc0802978d5ba6c74c4665e81f9a35`. Review `production/edit-v12/REVIEW.md`. No pending render or publication.

- V11 session 92302 completed exit 0. Full decode and actual opening impact/ground frames inspected. Final `production/assembly-v11/build/render/knockout-brain-matchcut-001-v11.mp4`, 18.648 s, 1080x1920, 24 fps, SHA-256 `597A17065CFE0F2DDE3E480CCDF071026D9D158C4EB93157AE911294C2AA58DF`. Review `production/edit-v11/REVIEW.md`. No pending required render.

- V10 session 96007 stopped after latest user direction, exit 1. V11 reuses existing effect unchanged, adds source-contiguous ground tail (frames 82–104), and rebuilds effect audio with no stretched fight sound. Contact 4.1 s, brain launch 4.2 s, interview 7.333 s. Verify final frame sequence and speech before delivery.

- V9 full decode, unchanged video-stream hash, bed continuity and final interview ASR checks passed. Final `production/assembly-v9/build/render/knockout-brain-matchcut-001-v9.mp4`, SHA-256 `1ae133b70d7d634764d4403ed544fcc5c994b79fa1bcb12657ecddc858b666ea`. Review `production/edit-v9/REVIEW.md`; no pending required work or live render.

- V8 final session 32419 completed exit 0. Full decode and actual ground/referee/interview frame review passed. `production/assembly-v8/build/render/knockout-brain-matchcut-001-v8.mp4`: 1080x1920, 24 fps, 568 frames, 23.670 s. SHA-256 `CFACF390109F56701BABB28CC274325F2A0FE92D14E31C9314AE3FE6195B03FB`. No pending required render; detailed review under `production/edit-v8/REVIEW.md`.

- V8 source speed 1x and fresh original-rate action audio prepared; supplied music excerpt ducked underneath. Mixed duration 23.666667 s, peak -1.0 dBFS. Initial render 19040 stopped after audio offset detected (exit 1); corrected mix speech/duration checks passed. Live final render 32419. Evidence `production/edit-v8/REVIEW.md` and `timing-audio-proof.json`.

- V7 final render 72132 completed exit 0, full decode and actual ground/interview frame review passed. Final `production/assembly-v7/build/render/knockout-brain-matchcut-001-v7.mp4`, 24.106 s, 1080x1920, 24 fps. SHA-256 `53B2F195467FE664C6CA03E75678F55B0AA53F2083026C45C1450F9ADB44769B`. No pending required render. Review: `production/edit-v7/REVIEW.md`.

- V7 initial render 93338 stopped after user changed interview scope; confirmed exit 1. New source quote window 5.84–7.273333 s. Local small.en transcript of 1.44 s test: “This guy raped the woman”; full terminal word detected, no year. Preserve original speech rather than synthesizing “a” in place of “the.”

## V6 live execution

- Source first right contact at approximately frame 11 / 0.367 s; lead left hook at frame 24 / 0.800 s. New interview cut after source frame 12 / 0.400 s; resumes at frame 13 / 0.433 s.
- Opening motion slowed through 1.2 s, after measured “filed” end 1.197 s; anime flash remains 2.2 s.
- Interview uses picture AND original source audio 3.84–8.34 s. No recycled clipped master for this quote.
- Initial provisional render session 60393 stopped by parent after hand-attribution review; confirmed exit 1. Corrected export session 97360 running. No duplicate render requested.
- Current edit duration 24.1 s; interview starts 3.533 s, follow-up resumes 8.033 s, preserved replay tail starts 11.1 s. Verify final output and quote endpoint before delivery.
- Completed: corrected session 97360 exit 0. Full decode passed; parent inspected final right-hand/interview and year/follow-up boundaries. Original source audio retained through the full terminal year, with approximately 0.4 s remaining after ASR-detected speech.
- Final: `production/assembly-v6/build/render/knockout-brain-matchcut-001-v6.mp4`, 1080x1920, 24 fps, 578 frames, 24.106 s. SHA-256 `21DCA691C2F2707D8FBE4D33E52A7AAEB8A8BD1DF3642A500BB54ED808B9E655`. Evidence: `production/edit-v6/REVIEW.md`. No pending render or publication.

## Acceptance criteria

- Playable vertical short with recovered fight footage and audible, intelligible sound.
- Keep the news beat attributed to Sean and show the documented no-charge outcome on screen.
- Use promotional “10 seconds”; official result remains 0:12 in source notes. Do not assert a universal UFC start delay.
- Replay Sean's punch with a fast aura flare and One Punch Man transformation before contact.
- Contact leads into a rendered Blender head/brain recoil insert, then Henderson–Bisping footage.
- Inspect actual rendered frames and verify complete video/audio decode, duration and dimensions.
- Deliver the MP4, editable project sources and review notes. No upload or release approval implied.

## Execution

- [x] Read existing recovery receipts, source captions and case wording.
- [x] Inspect original punch sequence; the impact happens very early in official clip.
- [x] Blender insert: generated by agent, corrected and rendered by parent; 90 frames / 3 s, full decode passes.
- [x] Engine assembly: existing player/compiler rendered 1080x1920 MP4; final frame and decode review complete.
- [x] Narration and sound sourcing: local Kokoro and existing CC0 effects; parent corrected source audio and voice offsets.
- [x] Anime image edit and transformation: parent owns production/anime/; generated image matched to pre-punch pose, effect rendered and inspected.
- [x] Portrait footage modules rendered; all nine MP4 derivatives pass complete ffmpeg decode.
- [x] Narration generated locally; three takes and measured word sidecars exist.
- [x] Parent final editorial assembly and inspection. See production/REVIEW.md for output hash and gate limitations.

## Decisions

1. Use a compact sourced news insert rather than repeating the reference publisher's unqualified accusation as narration. The real press-conference quote stays visibly attributed, with “2019 allegation • no charges filed.”
2. User's build instruction authorizes rendering recovered assets into this review cut. Original custody records stay untouched.
3. This is a footage-driven sports short. Financial-chart count rules do not describe this requested edit; authored punch timing, readable news context and actual 3D motion are its acceptance measures.
4. The brain insert is stylized motion, not a claim that a particular person's injury has been clinically diagnosed.

## Recall

- Recall(package): docs/portable/PACKAGING-PLAYBOOK.md:13 "Packaging is a promise the hook must keep." (The promised anime punch appears in the replay.)
- Recall(script): docs/portable/VOICE-PACK.md:137 "The first sentence is the grab." (Ten seconds opens the hook.)
- Recall(voice): docs/portable/VOICE-PACK.md:142 "Attribution before assertion." (The case statement is labelled as Sean's statement before it is heard.)
- Recall(world): docs/portable/OPERATOR-RULINGS.md:396 "Style is a knob, not a constraint." (Live sports footage moves into anime and Blender at the replay peak.)
- Recall(evidence): docs/AGENTS-VIDEO-ENGINE.md:79 "are never fabricated" (Source records retain the official 0:12; ten seconds is the user's promotional rounding.)
- Recall(motion): docs/portable/SOUND-SOURCING.md:68 "A landing sound sits on the contact frame" (Contact controls the impact sound and transition.)
- Recall(sound): docs/portable/SOUND-SOURCING.md:65 "a whoosh starts about 0.3 s early" (The power-up cue leads the transformation.)
- Recall(publish): docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md:78 "Nothing promotes out of review quarantine without an operator-approved" (Deliver a review artifact; no upload.)
- Recall(rulings): docs/AGENTS-VIDEO-ENGINE.md:78 "`approved` is set by the operator" (Do not self-approve.)

## Live handles

- Image generation functions cell 58: completed; generated image copied into production/anime/saitama-transform.png.
- Agents: blender_insert, assembly_path, audio_track.
- Additional independent visual review: cut_review_luna. Original reviewer dispatch failed because its configured Spark model is unsupported for this account.

## Corrections during review

- Blender preview camera was reversed; corrected view now faces the text and visible brain convolutions. Parent requested reduced relative displacement, removal of distracting orbit rings and punch sphere, then final render.
- Audio receipt exposed Henderson audio under Sean's first knockout. Parent requested replacement with the exact official Sharaf source and addition of the real replay-contact audio before final mux.
- Assembly wrapper initially resolved the nested content/video_engine/AGENTS.md as repository root. Parent reproduced the import failure; worker corrected root discovery and --help now runs.
- Intro captions use measured Kokoro word times, not evenly divided caption durations.

## Delivered artifact

`production/assembly/build/render/knockout-brain-matchcut-001-1080x1920.mp4` — 24.618 s container, 1080x1920, 24 fps, H.264/AAC. SHA-256 `76C99104D5E07827B354F3077B5452C6980EC96EE8D1298FCAEE36F94EBBEB71`.

Blender render session 14318 completed exit 0. No pending required render or external action. Original footage and receipts preserved; no commit, upload or publication.

## V2 continuous X-ray revision

- Acceptance: preserve the contact frame and arena, push into the victim's head, reveal an X-ray skull, fracture it, and eject the brain fully off-screen. No standalone diagram cutaway, labels, blood or flesh.
- Parent inspected the real source contact at 0.733333 s and generated matched X-ray, empty fractured skull, and detailed brain assets under `production/impact-v2/`.
- Timing: replay lead 16 frames at 30 fps; effect 95 frames at 30 fps; merged 3.7 s module replaces both old impact and diagram at 14.1–17.8 s.
- `production/edit-v2.json` and `production/audio/master-v2.wav` exist. Master checked: 24.600 s, 48 kHz stereo, peak -2.2 dBFS.
- Motion owner: `impact_v2_motion`, writes only `production/impact-v2/motion/`. Pending actual rendered frames and picture review.
- Assembly adapter: `production/assembly-v2/build_assembly_v2.py`; isolated paths, two tests passed. No render yet, waiting for merged effect module.
- Next runnable step: inspect motion render, run `prepare_revision.py --picture`, render via v2 adapter, decode and visually review full export before delivery.

## V3 operator correction — genuine modeled brain

- Operator rejected the flat brain sprite, including its black background artifacts. Do not render/deliver that implementation.
- Parent stopped the motion worker and corrected transparency/camera framing locally; these technical fixes do not satisfy the new mesh requirement alone.
- New acceptance: brain is an actual volumetric triangle mesh, visible within the radiographic skull, with changing silhouette, lighting and multi-axis rotation during ejection. No brain-textured billboard or black rectangle.
- `assembly_path` assigned bounded anatomical mesh recovery into `production/impact-v3/assets/`; parent owns all animation/integration.
- Next: inspect mesh vertices/bounds/materials, render sampled impact frames, then complete the same isolated revision assembly and review.
- Parent recovered the actual Nilearn fsaverage5 pial surfaces directly after the mesh worker produced no artifacts, converted both hemispheres into `production/impact-v3/assets/brain.obj`, and replaced the sprite with physically lit geometry.
- Verified: 20,484 vertices, 40,960 triangles, zero image textures on the brain. Actual Blender projections prove depth and rotation; the mesh is fully outside the frame by effect time 2.1 s.
- Denoised sample frames inspected: brain fits the skull cavity, launches with motion blur, and leaves the fractured skull empty. Packed editable scene: `production/impact-v3/knockout-xray-3d.blend`, SHA-256 `09849364A80BB0E1B2B6B9C871CCA54F15ACDBD7B767CDD389CC563562FA58CB`.
- Live render session: 71861, rendering frames 17–111 into the 95-frame effect module. Remaining: merge the live lead, full scene-engine export, end-to-end decode and boundary review.
- Session 71861 completed exit 0; full assembly session 10709 completed exit 0 after correcting the adapter's motion-gate import. No pending render jobs.
- Delivered revision: `production/assembly-v2/build/render/knockout-brain-matchcut-001-v2.mp4`, 24.618 s, 1080x1920, 24 fps, H.264/AAC. SHA-256 `529174A7E639533CEDDD830F109C8B1C150955DB68823C06912CB211D6B3653A`.
- Complete decode passed and parent inspected actual final impact/exit/Henderson boundary frames. Detailed model and export evidence: `production/impact-v3/REVIEW.md`. No publication or operator approval claimed.

## V4 — resume footage and launch on the head snap

Acceptance: brief X-ray freeze, then actual footage resumes; skull remains intact before contact; real 3D brain stays with the head until the visible recoil and ejects on that snap. No new diagram, sprite, early fracture or frozen-arena ejection. Rest of the 24.6 s edit remains unchanged.

- [x] Inspected source at 30 fps around contact. Source frame 22 / 0.733 s is the pre-contact hold; frame 24 / 0.800 s is contact; frame 25 / 0.833 s is visible head snap.
- [x] New `impact-v4/build_contact_motion.py` resumes actual source frames at one-third speed after the flash/push. Head/skull are tracked; brain detaches on output frame 41, not during the flash. `timing-proof.json` records every source/output frame.
- [x] Inspected sample frames 35, 41, 48. Tightened the head mask to eliminate duplicated cage-banner imagery from the moving overlay.
- [x] Luna generated `audio/verdict-v4.wav`: “No charges filed. Then Sharaf delivered a one-punch verdict.” The proposed “found not guilty” was corrected because the source records no charges, not an acquittal. Measured narration duration 3.500 s; used at 8.1–11.6 s.
- [x] `audio/master-v4.wav` built with resumed/stretched source audio, contact sound at 15.333 s and head-snap/launch sound at 15.433 s. Verified duration 24.600 s, peak -1.0 dBFS.
- [/] Blender full render session 97631; 95 effect frames. Wrapper `assembly-v4/build_assembly_v4.py` keeps prior assemblies untouched.
- [ ] Merge live lead, render v4 via existing scene-evidence engine, decode and inspect final contact/recoil boundary before delivery.
- [x] Both Blender passes completed; full v4 scene-engine export completed in session 44865. Final decode and actual frame review passed.
- Final: `production/assembly-v4/build/render/knockout-brain-matchcut-001-v4.mp4`, 1080x1920, 24 fps, 590 frames, 24.618 s. SHA-256 `7DA9A6CFD01986952115DA2CA04C3BBE70B26CAC2A405F88E26F750D3712BB36`.
- `production/impact-v4/REVIEW.md` records timing, narration, preserved prior version and final artifact checks. No pending required work or running render.

## V5 — verdict hook and Bisping transition

Acceptance: start immediately with “No charges filed. Then Sharaf delivered a one-punch verdict”; align the anime transformation flash to the measured “one-punch” at 2.199 s; remove the repeated narration at 8.1 s; add a short impact-flash transition into Henderson/Bisping at 17.8 s. Keep the verified head-snap choreography and overall 24.6 s edit.

- [x] Recut first 3.5 s with transformation flash at 2.2 s and matching measured captions.
- [x] Move verdict VO to time zero, restore real fight sound at 8.1–11.6 s, add transition cue.
- [x] Add fade-through-white on the existing 17.8 s boundary without shifting Henderson timing.
- [x] Isolated v5 assembly, complete decode, actual hook and transition frame review.
- Final: `production/assembly-v5/build/render/knockout-brain-matchcut-001-v5.mp4`, 1080x1920, 24 fps, 590 frames, 24.618 s. SHA-256 `AC2737C518E41DCB8EFEE0FD03EC0359728C0AB007F5FB7B883AE269AFE2ECD9`.
- Session 3495 completed exit 0. Review evidence: `production/edit-v5/REVIEW.md`. No pending render or publication.
- V6 acceptance: opening moves through the end of “filed” (1.197 s); first right-hand contact is visible before the interview; interview retains complete “2019”; return resumes the follow-up and shows the lead hook landing. Preserve attributed allegation/no-charge context, anime word sync, and later effects. Verify source and final frames, audio endpoint, full decode. No new effects or publication.
