# Knockout brain match-cut — audio receipt

Status: private review cut only; not publication-approved.

## Voice artifacts

All three clips use the existing local Kokoro-82M workflow, voice `am_michael`,
rate `1.2`; no paid API or cloud STT was used.

| clip | text | duration | word clock |
|---|---|---:|---|
| `intro.wav` | `Ten seconds. Sean Sharaf shuts the lights out.` | 3.500 s | `intro.words.json` |
| `bridge.wav` | `Now watch that again.` | 1.400 s | `bridge.words.json` |
| `outro.wav` | `Look familiar?` | 1.100 s | `outro.words.json` |

The bridge and outro remove Kokoro's leading/trailing silence; their sidecars
are shifted to the cropped audio origins. The intro is trimmed to the locked
3.5 s hook window without cutting a spoken word.

## Master map

`master.wav` is 24.600 s, 48 kHz, stereo PCM, mixed from the locked edit map.
The source media remains untouched.

| master time | layer | source / treatment |
|---|---|---|
| 0.000–3.500 | intro VO | local Kokoro `intro.wav`, +6 dB |
| 3.500–8.100 | news beat | `assets/raw/source-short/supplied-short-high.mkv`, source 3.840–8.440 s, gain 0.48 |
| 8.100–11.600 | knockout | `assets/raw/source-short/ufc-sharaf-steveson-high.mkv`, source 0.000–3.500 s, gain 0.45 (official Sean Sharaf/Steveson broadcast audio) |
| 11.600–13.000 | bridge VO | local Kokoro `bridge.wav` |
| 12.900–14.100 | anime motion cue | `fs-swirl-in-478722.mp3`, trimmed to 1.2 s, gain 0.7 |
| 14.100–14.800 | official contact | `assets/raw/source-short/ufc-sharaf-steveson-high.mkv`, source 0.200–0.900 s, gain 0.45 |
| 14.400–15.400 | main brain-contact hit | `fs-whirlpool-537920.mp3`, trimmed to 1.0 s, gain 0.65 |
| 14.800–17.800 | brain low resonance | same CC0 whirlpool source, low-pass/echo derivation, gain 0.22 |
| 17.800–22.000 | Hendo primary | source 31.700–35.900 s; first 1.1 s ducked under outro, then restored |
| 17.800–18.900 | outro VO | local Kokoro `outro.wav`, +5.6 dB; Hendo ducked underneath |
| 22.000–24.600 | Hendo replay | source 46.900–49.500 s |

## SFX provenance

The two selected repo-local FX are documented CC0 Freesound previews from
`content/video_engine/projects/systems-and-blowups/japan-tariff-trick/sound/SOURCES.md`:

- `fs-swirl-in-478722.mp3` — Freesound 478722, “Water Swirl 1_4” by
  Joao_Janz, CC0 1.0; source URL:
  https://freesound.org/people/Joao_Janz/sounds/478722/
- `fs-whirlpool-537920.mp3` — Freesound 537920, “Whirlpool Suck.mp3” by
  belanhud, CC0 1.0; source URL:
  https://freesound.org/people/belanhud/sounds/537920/

`fs-riserhit-754771.mp3` is present in the repo but has no provenance line in
the sound ledger, so it was not used. No music bed was added.

The master is reproducible with `build_master.ps1` in this directory. It uses
only the local Kokoro renders, the three locked source recordings, and the two
repo-local CC0 FX above; it does not modify source media.

## Verification

- `ffprobe`: `master.wav` decodes as 24.600000 s, 48000 Hz, stereo PCM.
- Parent integration corrected missing VO delays: bridge begins at 11.600 s, outro at 17.800 s. Rebuilt from `build_master.ps1`.
- `ffmpeg volumedetect`: master mean `-23.1 dB`, max `-2.2 dB`; limiter ceiling
  is below 0 dBFS.
- SHA-256:
  - `intro.wav`: `6BD5506AC363692BE23B31214DB619DE486B3578F33757BC117A0C7C864ADA33`
  - `intro.words.json`: `F1ABD0E2A1A497BC3A6FC73A7AAB6F919E28D8809EEDCD3160DB16D9ECFA0A06`
  - `bridge.wav`: `FC48C9E3B92E4621066258B493A92BACDAB45187ED2A52C79C3C2D6C29FA49DB`
  - `bridge.words.json`: `9B687E0CE46F4F4F5604EF939251790A172572A6EE5E6C38B5F74D25699C6FED`
  - `outro.wav`: `4D9387D9C608F379E2B4DAEF16501A47204E0B90C340C0B519219539168FC937`
  - `outro.words.json`: `0A94AD1806E348561A74410FEC3A8DF1D4CF7013CBB70DC7AF1F5D14F137736D`
  - `master.wav`: `F526C8AD802ADB838C6B8DB628D43A4110EBFA977D9D03AACE5914A170E49437`
