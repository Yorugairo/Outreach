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

## Second read, ~2 h after posting (n = 51 viewers, 282 views, 6 fifteen-second views, 3 interactions, 0 follows)

| metric | value |
|---|---|
| average watch time | 25 s of 89 (28 %) — down from 50 s at n = 8, up from ep1's 7 s of 73 (9 %) |
| watch time | 25 m 50 s |
| biggest drop-off | **0:07** (was 0:11 at n = 8) |
| views vs the page's typical curve | above typical through the first 2 h (~80 vs ~40); the typical line's jump to ~620 at 4 h is ep1's own spike and is not a baseline |

**The curve, read against the scene list** (`build-short/tokyo-short.timeline.json`):

| window | retention | scene(s) | world |
|---|---|---|---|
| 0:00–0:03 | 100 % | s01 | clip (the host enters) |
| 0:03–0:15 | 100 % → ~30 % — **the cliff** | s01 tail, s02 (5.09–8.99), s03 (8.99–17.17) | **three clip scenes in a row, no page** |
| 0:15–0:40 | **flat at ~30 %** | s04 (17.17–33.05) ledger, s05 clip (33.05–38.96) | the first ledger page lands at 17.17 and the bleed stops |
| ~0:42 | step to ~25 % | s06 (38.96–44.88) | the `suck` transition scene (steam / trace / ticker), no page |
| 0:45–0:55 | flat | s07 (44.88–54.52) ledger | page |
| ~0:55 | step to ~18 % | s08 (54.52–61.76) | clip |
| 0:55–1:02 | flat, then a step to ~12 % | s09 (61.76–75.73) ledger | page; the step is one or two viewers |
| 1:02–1:29 | flat at ~12 % | s10 clip, s11 outro | — |

**What it says (n = 51, still a sample):** every bleed is inside a clip scene; every plateau is a ledger page. The cliff is
the twelve seconds of clips before the first page, and the flattening starts the moment the page rolls out. This is the
E44 pattern with 51 viewers instead of 8. It says nothing yet about the voice: the voice is the same across the plateaus
and the bleeds.

## Third read, ~3 h after posting (n = 254 viewers, 303 views, 25 fifteen-second views, watch time 51 m 21 s)

| metric | value |
|---|---|
| average watch time | **12 s** of 89 (13 %) - 50 s at n = 8, 25 s at n = 51, 12 s at n = 254: the sample settling toward the cold audience |
| biggest drop-off | **0:04** (most of the audience); a second at **0:12** (= the average watch time) |
| views vs the page's typical curve | this post ~300 at 3 h; the typical line's 620 at 4 h is ep1's spike |
| curve | 100 % to 0:03, **50 % by 0:08, ~30 % by 0:22**, then a slow slide to ~10 % by 1:07, flat to the end |

**Read against the scene list:** the cliff is still the clip chain - 0:03 to 0:12 is s01's tail, s02 (dial and bill) and
s03 (the panel with the press cue and the cut); half the audience is gone before the first ledger page at 0:17. With 254
viewers the plateaus have smoothed into a slope, but the slope is shallowest across the page sections (0:17-0:40,
0:45-0:55) and steepest across the clips. Operator's read, same hour: *"rate of drop-off is flattening but still looks
telling that the chart performs higher. Audience doesn't appear happy with the way videos are chained in, for sure."*
Against ep1 (7 s of 73, 9 %): 12 s of 89 (13 %) at a comparable sample. v2 (the page mounted at 0:02, docks over it, no
clip chain) is the test of this read.
