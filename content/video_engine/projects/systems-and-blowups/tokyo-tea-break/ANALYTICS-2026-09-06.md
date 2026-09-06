# Analytics — the Tokyo short on Facebook, first read (2026-09-06, ~1 h after posting)

Operator screenshots, 2026-09-06 (Sunday, posted during the NFL as a timing test). **n = 8 viewers** — a sample, not a
result; recorded because the retention curve is the one ground truth we hold (BACKLOG "The ground truth we hold").
Compared against episode 1's reel (the chip-machine short, 1:13, 4 days old, n = 315).

| metric | ep1 reel (1:13, n=315) | Tokyo short (1:29, n=8) |
|---|---|---|
| average watch time | 7 s | 50 s |
| average percentage watched | 9 % | 56 % |
| player 20-second view rate | 4.5 % | 14.3 % |
| 3-second views | 315 | 8 |
| 1-minute views | 32 | 2 |
| watch time | 2:08:07 | 25:07 |
| biggest drop-off | 0:05 | **0:11** |
| curve shape | a cliff to ~30 % by 0:10, then a slow bleed to ~5 % | 100 % to 0:05, a step to ~45 % by 0:11, flat to 0:55, a step to ~25 %, flat to the end |

## Where 0:11 falls in the build (`build-short/tokyo-short.timeline.json`)

| scene | span | world | what happens |
|---|---|---|---|
| s01 | 0.00–5.09 | clip (the host enters the bar) | the hook; exit **cut** |
| s02 | 5.09–8.99 | clip | exit **cut** |
| s03 | 8.99–17.17 | clip | **the `press 3` cue fires at 8.99 (gain 0.16)** and the host **cuts** onto the scene; the drop-off sits inside this scene |
| s04 | 17.17–33.05 | **ledger** (the first chart page: holdings) | the first proof, 17 s in |

Three operator observations, same day, all in this window:
1. the camera-flash / press sound is too aggressive at the cut;
2. the character **cuts** onto scene 3 instead of entering the way he entered scene 1;
3. the chart plates are the strongest mechanism we have and the first one does not appear until 0:17. *"On 'Tokyo took a tea
   break. And left America with an unfunded bar tab.' we're supposed to roll out the graph. That's what makes us different.
   That's the only thing the stick-figure companies can't just drown me against."* → ruling **E44**.

## What this does not yet say

Eight viewers cannot separate the hook from the timing test from the audience. The second step at 0:55 (s08, a clip
between two ledger pages) is one viewer. Re-read at n ≥ 100 and after the Monday/Tuesday post; the comparison that
matters is Tokyo against the next short built under E44, not Tokyo against ep1.
