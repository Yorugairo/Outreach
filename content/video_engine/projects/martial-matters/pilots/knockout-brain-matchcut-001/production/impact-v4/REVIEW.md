# Head-snap timing revision

Status: final assembly rendered and verified for private review.

## Timing contract

| Event | Source frame at 30 fps | Effect scene frame | Master time |
|---|---:|---:|---:|
| Pre-contact X-ray freeze | 22 | 17–31 | 14.633–15.100 s |
| Footage resumes, one-third speed | 22 onward | 32 onward | 15.133 s |
| Contact | 24 | 38 | 15.333 s |
| Head snap / brain detaches | 25 | 41 | 15.433 s |

- The original arena/fighters are a moving image sequence after the hold, not a stationary image with only the brain animated.
- `actual-scene-proof.json` was read from the saved Blender scene, not inferred from screenshots. It verifies source frame progression, zero fractured-skull alpha before contact, and brain movement after the head-snap key.
- Brain remains the real 20,484-vertex / 40,960-triangle cortical mesh, physically lit and rotated. No brain sprite is used.
- Parent inspected frames 35, 41 and 48. Tight head masks and a source-difference mask remove frozen glove/cage imagery while retaining the radiographic skull.
- Frames 32–62 received the matte cleanup; the final effect is re-encoded only after both render sessions complete.
- The 3.700 s merged module has 111 frames at 30 fps; full ffmpeg decode passed.

## Narration and sound

Exact new narration at 8.1–11.6 s: “No charges filed. Then Sharaf delivered a one-punch verdict.”

The user's proposed “found not guilty” was not used: the sourced 2019 outcome is no charges filed, not an acquittal. Existing attributed news context remains onscreen. Local Kokoro `am_michael` voice, 3.500 s, measured word sidecar `audio/verdict-v4.words.json`.

Source fight audio resumes at the matching slow-motion time. Contact sound is at 15.333 s; fracture/launch sound at 15.433 s; flight whoosh leads that launch. Master checked at 24.600 s, 48 kHz stereo, maximum sample level -1.0 dBFS.

## Preservation

The previous v2 MP4 is unchanged: SHA-256 `529174A7E639533CEDDD830F109C8B1C150955DB68823C06912CB211D6B3653A`.
New assembly owns only `production/assembly-v4/`; no publication, commit or release approval is implied.

## Final verification

- Output: `production/assembly-v4/build/render/knockout-brain-matchcut-001-v4.mp4`.
- SHA-256 `7DA9A6CFD01986952115DA2CA04C3BBE70B26CAC2A405F88E26F750D3712BB36`.
- 1080x1920, 24 fps, 590 frames, H.264/AAC, 24.618 s container duration; full video/audio decode exit 0.
- Parent inspected `final-contact-review.jpg`, extracted from the actual final export: intact X-ray -> moving punch/contact -> head recoil and modeled brain launch -> empty skull -> continued live footage. The final output does not remain frozen during ejection.
- Blender sessions 97631 and 37849 completed exit 0; final assembly session 44865 completed exit 0. No pending render.
- General motion gate limitations M11 (no chart) and M16 (clip-world motion uncounted) remain explicitly documented in the private-review forced-render receipt; they are not represented as passing gates.
