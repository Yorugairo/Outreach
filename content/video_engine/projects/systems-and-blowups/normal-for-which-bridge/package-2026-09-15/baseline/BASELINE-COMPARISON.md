# Baseline comparison

Audit date: 2026-09-15. The selected current build was `build-review`; 33 files were copied into `baseline/build-review/`. `review-v1` remains a read-only historical comparison and was never rebuilt.

| Measure | review-v1 | build-review source | baseline after gates |
|---|---:|---:|---:|
| Compiled timeline SHA-256 | `a0d4c505a26ce49a12220af9e4ccdc66614cb9ea669706b3ad2f26567ae802d9` | `19a9ec48ba13e862a0aaf3781ec7a6e9024abc4cf34aa3c10ed8e45073d8db99` | `19a9ec48ba13e862a0aaf3781ec7a6e9024abc4cf34aa3c10ed8e45073d8db99` |
| Runtime seconds | 56.904014 | 56.904014 | 56.904014 |
| Compiled scenes | 6 | 6 | 6 |
| Caption pages | 39 | 39 | 39 |
| Docks | 0 | 0 | 0 |
| Targeted species entries | 8 (historical report) | 8 (historical report) | 11 (compiled entries) |
| Narration sentences | 19 | 19 | 19 |
| Fresh motion gate | 0 FAIL / 1 WARN / 18 PASS / 1 JUDGE / 5 INFO (historical report) | same historical report | 0 FAIL / 2 WARN / 20 PASS / 1 JUDGE / 6 INFO |
| Fresh one-shot floor | not measured under E96 | current floor expected to judge | 5 FAIL / 1 WARN / 0 PASS / 1 JUDGE / 1 INFO |
| Fresh self-watch | TODO after historical report | TODO after historical report | exit 1; NOT CLEAN, first failure M35 |

The probe gate exited 0 and found 25 instants. Motion, floor, and self-watch exact stdout/stderr are in `logs/02-motion-gate.log`, `logs/03-floor-gate.log`, and `logs/04-self-watch.log`; exact commands and exits are in `RUN-SUMMARY.tsv`. Self-watch also recorded script/layout PASS, viewer absent, publish WARN, and generated the baseline self-watch artifacts. No render was performed.

All source, take, engine, player, asset, audio, compiled-timeline, and word-timeline SHA-256 values are recorded exactly in `HASHES.tsv`.
