# SOURCES — steel-and-paper sound

Per-asset licence ledger (SOUND-SOURCING.md rule: an asset missing its
ledger entry does not ship). CC0 assets need no attribution; the entry is
kept so the licence is provable. Audio files themselves are gitignored in
this folder (`*.mp3|*.wav|*.flac`); re-fetch by Freesound id if missing.

## Ledger page cues (P35 T9, sourced 2026-09-02)

Human Gate 5 DECIDED: CC0 via the Freesound v2 API, zero paid audio.
Searched with `filter=license:"Creative Commons 0" duration:[0.2 TO 4]`,
`sort=rating_desc`; each pick is the highest-rated CC0 hit that fits the
cue. Downloaded the `preview-hq-mp3` (no OAuth; originals were not
fetched). Trimmed with ffmpeg (`-ss`/`-t`, `afade` 20 ms in and out),
gain-matched to the existing accent `fs-whoosh-1-706679.mp3`
(integrated **-14.06 LUFS**, TP -0.84 dBTP, 0.756 s, measured with
`loudnorm=print_format=json`), encoded `libmp3lame -q:a 2`.

| slot | file | Freesound id | title | author | licence |
|---|---|---|---|---|---|
| page roll-out | `fs-page-roll-464302.mp3` | 464302 | PaperSlide.wav | eyesonlegs | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ |
| page bleed settle | `fs-page-bleed-166322.mp3` | 166322 | Water_drop_8.wav | deleted_user_2104797 (account deleted; the CC0 grant stays with the sound) | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ |
| page outline | `fs-page-stroke-447925.mp3` | 447925 | Write/Draw with chalk on board | Breviceps | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ |

Freesound URLs: https://freesound.org/s/464302/ · https://freesound.org/s/166322/ · https://freesound.org/s/447925/

### Why these

- **roll**: query `paper slide`. 464302 rated 4.86 (35 ratings), 1.64 s, a
  single continuous paper slide — the only high-rated hit whose motion
  fits inside 1.5 s. `Paper unroll` (710764, 4.67/3) and `Paper drawn with
  rustle` (360646, 4.96/27) are 3.5–4 s pulls that lose the motion when cut.
- **bleed**: no CC0 hit ≤ 4 s for `ink drop`, `ink bleed`, `ink splash`,
  `wet brush` (count = 0). Closest analogue is a soft single water drop;
  166322 is the highest-rated single-drop transient (4.94, 31 ratings,
  0.73 s). Runner-up `Drop - Water` 533146 (mattfinarelli, 4.72/43).
- **stroke**: query `chalk write`. 447925 rated 5.00 (9 ratings), 0.48 s,
  one dry chalk stroke. `marker squeak` hits were wet/squeaky and rejected.

### Trim and loudness (every number measured)

| slot | source dur | trim `-ss` | trim `-t` | final dur | trimmed I (LUFS) | trimmed TP | gain applied | final I (LUFS) | final TP | Δ vs whoosh |
|---|---|---|---|---|---|---|---|---|---|---|
| roll | 1.64 s | 0.10 | 1.45 | 1.450 s | -20.20 | -6.18 | +6.14 dB | **-13.99** | -0.33 dBTP | +0.07 LU |
| bleed | 0.73 s | 0.20 | 0.53 | 0.530 s | -39.64 | -26.68 | +25.58 dB | **-14.09** | -1.10 dBTP | -0.03 LU |
| stroke | 0.48 s | 0.00 | 0.48 | 0.476 s | -22.35 | -7.24 | +8.29 dB, then `alimiter=limit=0.891` (-1 dBFS) | **-14.45** | -0.40 dBTP | -0.39 LU |

Stroke note: the plain +8.29 dB pass measured -14.05 LUFS but +1.06 dBTP
(its transient is at t = 0); the limiter pass costs 0.4 LU and keeps the
peak under -0.4 dBTP. All three are inside the ±1 LU window.

Preview-mp3 transient windows (50 ms RMS, >-20 dB below peak) that fixed
the trims: roll 0.15–1.45 s, bleed 0.25–0.40 s, stroke 0.00–0.45 s.

### Slots in SOUND-PLAN.json (`page_cues`, page-relative)

The three slots live under a separate top-level `page_cues` list, not in
`cues`: `build_scene_timeline_f.py` and `render_episode.mix_audio()` flatten
every `cues` entry onto the episode clock as an absolute float, so a
page-relative slot there would be scheduled at t=0.0/2.8 of the episode and
mixed into every render. The page species adds the page's start time when
it schedules `page_cues`. `at` values (from the prototype
`hyperframes/compositions/ledger-page-v1.html`): roll-out 0.0 (page
transform begins), bleed settle 2.8 (ink-bleed-reveal IN_BASE), outline
4.2 (outline starts 3.4, `draw-complete` +0.8 after the field) - the
outline value is the prototype default and is re-read from the published
sync point per page.

Gains: whoosh accent 0.9 scaled by the loudness difference,
`0.9 * 10^(-(I_cue - (-14.06))/20)`: roll 0.893, bleed 0.903, stroke 0.941.
`sound_palette.json` carries the same as dB (20·log10): -0.98, -0.89, -0.53.
These are accents like the whoosh, so the -28 LU bed rule does not apply.
Re-derive if a pick changes.

### Not sourced

Nothing left empty. The bleed slot is a water drop standing in for ink — a
judgment pick, flag at the contact sheet if it reads as "wet" rather than
"ink settling".

## Tokyo short - the whirl, the flip, the suck (sourced 2026-09-05)

Operator: the air whooshes read as a jet; the spiral and the drain want a WHIRL (water), the retract of a page that
will return a LIGHT FLIP, the suck a SLURP - and every accent as a BACKGROUND sound, 8-10 dB under the voice (the
VO is -17.9 LUFS; files matched to -14 LUFS as before, so a cue gain of 0.22 lands them at ~-27). Same process as the
page cues above: CC0 via the Freesound v2 API, `preview-hq-mp3`, leading silence trimmed at -45 dB, 20 ms fades,
gain-matched to -14 LUFS, `alimiter` at -1 dBFS, `libmp3lame -q:a 2`. The review strip carries the alternates as B/C/D.

| slot | file | Freesound id | title | author | licence | URL |
|---|---|---|---|---|---|---|
| suck (the whirlpool) | `fs-whirlpool-537920.mp3` | 537920 | Whirlpool Suck.mp3 | belanhud | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/belanhud/sounds/537920/ |
| spiral in (water swirl) | `fs-swirl-in-478722.mp3` | 478722 | Water Swirl 1_4 | Joao_Janz | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/Joao_Janz/sounds/478722/ |
| page retract whirl (water swirl) | `fs-swirl-out-478683.mp3` | 478683 | Water Swirl 2_1 | Joao_Janz | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/Joao_Janz/sounds/478683/ |
| page retract flip (quiet page turn) | `fs-pageturn-484968.mp3` | 484968 | Quiet Page Turn - 8 | SpaceJoe | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/SpaceJoe/sounds/484968/ |
| suck (alt B: sucking) | `fs-slurp-735164.mp3` | 735164 | SuckingSound1 | netsur4 | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/netsur4/sounds/735164/ |
| suck (alt C: slurping a drink) | `fs-slurp2-583716.mp3` | 583716 | Slurping A Drink | DexD73 | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/DexD73/sounds/583716/ |

| file | source dur | final dur | raw I (LUFS) | gain applied | final I (LUFS) | final TP |
|---|---|---|---|---|---|---|
| `fs-whirlpool-537920.mp3` | 1.11 s | 1.11 s | -19.0 | +5.0 dB | **-13.2** | -0.1 dBTP |
| `fs-swirl-in-478722.mp3` | 2.01 s | 2.00 s | -30.2 | +16.2 dB | **-14.1** | -0.1 dBTP |
| `fs-swirl-out-478683.mp3` | 2.22 s | 2.20 s | -21.3 | +7.3 dB | **-13.2** | 0.2 dBTP |
| `fs-pageturn-484968.mp3` | 0.48 s | 0.39 s | -inf | +inf dB | **-inf** | 9.4 dBTP |
| `fs-slurp-735164.mp3` | 0.42 s | 0.36 s | -inf | +inf dB | **-inf** | 9.6 dBTP |
| `fs-slurp2-583716.mp3` | 0.48 s | 0.48 s | -15.6 | +1.6 dB | **-13.8** | 0.2 dBTP |

## Tokyo short - the whirl, the flip, the suck (sourced 2026-09-05)

Operator: the air whooshes read as a jet; the spiral and the drain want a WHIRL (water), the retract of a page that
will return a LIGHT FLIP, the suck a SLURP - and every accent as a BACKGROUND sound, 8-10 dB under the voice (the
VO is -17.9 LUFS; files matched to -14 LUFS as before, so a cue gain of 0.22 lands them at ~-27). Same process as the
page cues above: CC0 via the Freesound v2 API, `preview-hq-mp3`, leading silence trimmed at -45 dB, 20 ms fades,
gain-matched to -14 LUFS, `alimiter` at -1 dBFS, `libmp3lame -q:a 2`. The review strip carries the alternates as B/C/D.

| slot | file | Freesound id | title | author | licence | URL |
|---|---|---|---|---|---|---|
| suck (the whirlpool) | `fs-whirlpool-537920.mp3` | 537920 | Whirlpool Suck.mp3 | belanhud | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/belanhud/sounds/537920/ |
| spiral in (water swirl) | `fs-swirl-in-478722.mp3` | 478722 | Water Swirl 1_4 | Joao_Janz | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/Joao_Janz/sounds/478722/ |
| page retract whirl (water swirl) | `fs-swirl-out-478683.mp3` | 478683 | Water Swirl 2_1 | Joao_Janz | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/Joao_Janz/sounds/478683/ |
| page retract flip (quiet page turn) | `fs-pageturn-484968.mp3` | 484968 | Quiet Page Turn - 8 | SpaceJoe | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/SpaceJoe/sounds/484968/ |
| suck (alt B: sucking) | `fs-slurp-735164.mp3` | 735164 | SuckingSound1 | netsur4 | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/netsur4/sounds/735164/ |
| suck (alt C: slurping a drink) | `fs-slurp2-583716.mp3` | 583716 | Slurping A Drink | DexD73 | CC0 1.0 — http://creativecommons.org/publicdomain/zero/1.0/ | https://freesound.org/people/DexD73/sounds/583716/ |

| file | source dur | final dur | raw I (LUFS) | gain applied | final I (LUFS) | final TP |
|---|---|---|---|---|---|---|
| `fs-whirlpool-537920.mp3` | 1.11 s | 1.11 s | -19.0 | +5.0 dB | **-13.2** | -0.1 dBTP |
| `fs-swirl-in-478722.mp3` | 2.01 s | 2.00 s | -30.2 | +16.2 dB | **-14.1** | -0.1 dBTP |
| `fs-swirl-out-478683.mp3` | 2.22 s | 2.20 s | -21.3 | +7.3 dB | **-13.2** | 0.2 dBTP |
| `fs-pageturn-484968.mp3` | 0.48 s | 0.39 s | -26.0 | +12.0 dB | **-19.1** | -0.1 dBTP |
| `fs-slurp-735164.mp3` | 0.42 s | 0.36 s | -20.7 | +6.7 dB | **-13.9** | 0.8 dBTP |
| `fs-slurp2-583716.mp3` | 0.48 s | 0.48 s | -16.0 | +2.0 dB | **-14.0** | 0.2 dBTP |
