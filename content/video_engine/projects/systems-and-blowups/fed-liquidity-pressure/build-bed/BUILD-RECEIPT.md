# Fed liquidity bed build receipt

Status: compiled through the existing authoring/compiler path; review and HG3 remain pending.
This receipt records measured inputs only. It does not approve media or claim a release-ready pilot.

## Clock

- take: `vo-pilot-20260919-r4/scratch-kokoro`
- script spoken hash: `3051887ec9c4554ded24751f9a6aaa1c32bfe8912a30d11833c127c77d2ba796`
- words: `vo-pilot-20260919-r4/scratch-kokoro.words.json` sha256 `ac77cbbb7de5c386917d813a7a20075a1260f796df218dd34dd10f2461f37fa1`
- audio: `build-bed/audio/episode.mp3` sha256 `ea6ff47d1dbb436957bb24fe0af7040df2950c812373b46bf8d5ce2a9c35d06c`
- closing anchor: `Your two-percent loan is coming due, and replacing it at seven percent more than triples your interest bill—without borrowing another dollar.`
- measured prefix end: `30.375000s` (word index 83; 84 words retained)
- spoken end: `29.925000s` (end word index 83; measured from take-word-clock)
- silence tail: `0.45s` (accepted only inside measured following onset/duration)
- following word onset: `30.550000s`

## Semantic rows

- rows: `3` across groups `P01`
- authoring status: `DRAFT_CURRENT_TAKE_PENDING_RENDERED_REVIEW` (not an acceptance or release verdict)
  - P01: 0.00s–30.38s
- authored incoming transitions: `['melt:splash:plate:1.2']`; registered surface arrivals are encoded in plate declarations
- narrative plates: one-direction Ken Burns; compiler `plate_idle_paints` is false

## Source custody

  - `evidence/objects/debt-wall-2025-2027.series.json` sha256 `52a5b2c56d7bfa017fed0fd41ffb1ff25412185528e56bf5fc1fbc853cea14da`
  - `evidence/objects/fed-assets-reserves-change.series.json` sha256 `24224bab426477e4c4aeb8d6d54ded647b12c4d6822ef6a9a02fac3e8343a17a`
  - `evidence/objects/fed-assets-reserves-history.series.json` sha256 `4ec92fe4a1e9736a5a149ed7772302061f8f6ffe326a00148da447dfbaf388bc`
  - `evidence/objects/fed-on-rrp-history.series.json` sha256 `d1c0ae03eb2a5b29c2bd3227be5584546d1c26d40b1aa0d530f6cc1280760895`
  - `evidence/objects/fed-runoff-offsets.series.json` sha256 `4466caf2073f67b14d6a26e16e65405f8341ea5a42a9f4c22270ef4671393fe1`

## HG2-selected assets

  - `p2-owner-loan-folio-v1`: `review/imagegen-pilot-v1/p2-owner-loan-folio-candidate-v1.png` sha256 `0a2615451066bf508ce86470714f4c8e43791a5f20961c4ca18c91c92d14cba5`
  - `w2-owner-workshop-world-v1`: `review/imagegen-complete-worlds-v1/w2-owner-workshop-world-v1.png` sha256 `066a00512921957934d685306eb6e5efad3ea2b5b89ebf0f0ffa4d60461e220d`
  - `w4-finance-evidence-hall-v1`: `review/imagegen-complete-worlds-v1/finance-evidence-hall-hosted-v3-cream.png` sha256 `5c5e68ff73da5d5f1f16c1fb6739ecb8ac0bd46fab76b7f6d40b69dd97351d92`

## Boundary

- no provider/voice generation, asset promotion, or approval was performed
- no full render was performed; the private compiled build is for review only
