# Fed liquidity pilot build receipt

Status: compiled through the existing authoring/compiler path; review and HG3 remain pending.
This receipt records measured inputs only. It does not approve media or claim a release-ready pilot.

## Clock

- take: `vo-pilot-20260919-r4/scratch-kokoro`
- script spoken hash: `3051887ec9c4554ded24751f9a6aaa1c32bfe8912a30d11833c127c77d2ba796`
- words: `vo-pilot-20260919-r4/scratch-kokoro.words.json` sha256 `ac77cbbb7de5c386917d813a7a20075a1260f796df218dd34dd10f2461f37fa1`
- audio: `build-pilot/audio/episode.mp3` sha256 `c2456b14640c8fca3f3dd5381d494c4ceb554983508b43bed1bccb492dc9bbd0`
- closing anchor: `Trillions of dollars of withdrawals barely helped them hold their ground.`
- measured prefix end: `177.975000s` (word index 510; 511 words retained)
- spoken end: `177.525000s` (end word index 510; measured from take-word-clock)
- silence tail: `0.45s` (accepted only inside measured following onset/duration)
- following word onset: `178.125000s`

## Semantic rows

- rows: `14` across groups `P01, P02, P03, P04, P05, P06`
- authoring status: `DRAFT_CURRENT_TAKE_PENDING_RENDERED_REVIEW` (not an acceptance or release verdict)
  - P01: 0.00s–30.45s
  - P02: 30.45s–70.08s
  - P03: 70.08s–97.45s
  - P04: 97.45s–142.10s
  - P05: 142.10s–177.97s
  - P06: 156.60s–177.97s
- authored incoming transitions: `['melt:splash:plate:1.2', 'door:left:0.9', 'melt:splash:plate:1.2', 'melt:splash:plate:1.2', 'melt:gather:throw:1.2']`; registered surface arrivals are encoded in plate declarations
- narrative plates: one-direction Ken Burns; compiler `plate_idle_paints` is false

## Source custody

  - `evidence/objects/debt-wall-2025-2027.series.json` sha256 `ab03bc336931845277de56e6c4006a94c00cf55496d7182280bdf8add9c5c7d2`
  - `evidence/objects/fed-assets-reserves-change.series.json` sha256 `24224bab426477e4c4aeb8d6d54ded647b12c4d6822ef6a9a02fac3e8343a17a`
  - `evidence/objects/fed-assets-reserves-history.series.json` sha256 `4ec92fe4a1e9736a5a149ed7772302061f8f6ffe326a00148da447dfbaf388bc`
  - `evidence/objects/fed-on-rrp-history.series.json` sha256 `d1c0ae03eb2a5b29c2bd3227be5584546d1c26d40b1aa0d530f6cc1280760895`
  - `evidence/objects/fed-runoff-offsets.series.json` sha256 `b9c9cb8138e2e3bf2455c079cecf0bdf2ad30814d214d5b28c8a50232d1c9813`

## HG2-selected assets

  - `p2-owner-loan-folio-v1`: `review/imagegen-pilot-v1/p2-owner-loan-folio-candidate-v1.png` sha256 `0a2615451066bf508ce86470714f4c8e43791a5f20961c4ca18c91c92d14cba5`
  - `w2-owner-workshop-world-v1`: `review/imagegen-complete-worlds-v1/w2-owner-workshop-world-v1.png` sha256 `066a00512921957934d685306eb6e5efad3ea2b5b89ebf0f0ffa4d60461e220d`
  - `w4-finance-evidence-hall-v1`: `review/imagegen-complete-worlds-v1/finance-evidence-hall-hosted-v3-cream.png` sha256 `5c5e68ff73da5d5f1f16c1fb6739ecb8ac0bd46fab76b7f6d40b69dd97351d92`

## Boundary

- no provider/voice generation, asset promotion, or approval was performed
- no full render was performed; the private compiled build is for review only
