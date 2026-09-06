---
name: map-audio-bed
description: Where music-bed loudness targets, VO/bed LUFS measurements and bed-gain math live for the Tokyo Tea Break short
metadata:
  type: reference
---

- `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` - `BED_LU` / `PLATFORM` / `VO_LUFS` / `BEDS` / `bed_gain` block - per-platform bed targets (`BED_LU`), `PLATFORM`, measured `VO_LUFS`, per-file `BEDS` LUFS, `bed_gain` lambda.
- `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` - the sound-cue table (`press_pack`, hook bed / turn bed rows) - sound-cue table: accent/click gains and the hook/turn bed cues with A/B variants.
- `docs/research/audio/SUBTHRESHOLD_BACKGROUND_MUSIC_RESEARCH_BLUEPRINT.md` - s2 loudness targets - the doctrine behind the numbers (VO anchor -14 LUFS, bed -28 LU, -22..-30 range, keep bed flat/limited).
- `docs/content-video-engine/CAPABILITIES.md` - the "Beds and the press pack" row; entry point when hunting bed assets.
- Naming trap: the on-disk episode dir is `tokyo-tea-break/` but IDs, timeline names and clip paths inside it say `il-tea-break` - grep both spellings.
- `docs/DOCS-INDEX.jsonl` "bed" matches are mostly "embed" noise; search `lufs`/`bed_gain` in code instead for audio levels.
