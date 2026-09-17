# The recipe lab - approval rate per feature

_Derived 2026-09-17T20:22:58+00:00 from `content/video_engine/effects/lab/judgements.jsonl`, itself derived from `docs/content-video-engine/review-answers.jsonl` only (P65 T5). Never hand-edited._

**The limit.** THE LEARNER IS A TABLE, NOT A MODEL. Every cell is a count and a shrunk share; no ranking model and no head-to-head preference model is fitted anywhere in lab_log.py, and none will be until this log holds 300+ judgements (arXiv 2411.04991). The reason categories are carried beside every rate and never collapsed into it (Gao et al. 2022): the rate says how often, only the reason says why, and the reason is the part an agent can act on. A cell's rate is its count shrunk toward the log's own prior, so a feature seen once never reads 1.00 or 0.00 - read the n before the rate.

Citations: arXiv 2411.04991 (a preference model fitted at small N is noise wearing a number); Gao et al. 2022 (optimising an imperfect proxy at small N costs the thing you wanted).

**The numbers.** 6 live judgements over 6 candidates (2 approve / 4 deny; 1 superseded and kept). The prior is Beta(a=0.6667, b=1.3333) - strength 2.0 pseudo-judgements at the log's own approval rate 0.3333, held inside [0.1, 0.9] so no cell can read 1.00 or 0.00 on one observation. Every cell: rate = (approvals + a) / (n + a + b).

| feature | kind | n | approve | deny | raw | shrunk | reasons (carried, never collapsed) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `shape:return` | shape | 3 | 1 | 2 | 0.33 | 0.33 | good x1; off-doctrine x1; reads-as-noise x1 |
| `shape:open-on-the-chart` | shape | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `shape:page-number-lands-at-n` | shape | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `shape:plate-carries-a-card` | shape | 1 | 1 | 0 | 1.00 | 0.56 | good x1 |
| `member:dock_kind:image` | member | 2 | 1 | 1 | 0.50 | 0.42 | good x1; off-doctrine x1 |
| `member:dock_option:badge` | member | 2 | 1 | 1 | 0.50 | 0.42 | good x1; off-doctrine x1 |
| `member:dock_option:read` | member | 2 | 1 | 1 | 0.50 | 0.42 | good x1; off-doctrine x1 |
| `member:page_enter:snap` | member | 2 | 0 | 2 | 0.00 | 0.17 | off-doctrine x1; reads-as-noise x1 |
| `member:arrival:throw` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:dock_payload:chart` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:exit:wipe` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:idle:drift` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:page_enter:mount` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:page_species:build_to` | member | 1 | 1 | 0 | 1.00 | 0.56 | good x1 |
| `member:page_species:figure` | member | 1 | 1 | 0 | 1.00 | 0.56 | good x1 |
| `member:page_species:retitle` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:plate_option:ken` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:plate_option:world` | member | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `member:species:spotlight` | member | 1 | 0 | 1 | 0.00 | 0.22 | reads-as-noise x1 |
| `clock:window_s=6.0` | clock | 3 | 2 | 1 | 0.67 | 0.53 | good x2; off-doctrine x1 |
| `clock:window_s=11.0` | clock | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
| `clock:window_s=12.0` | clock | 1 | 0 | 1 | 0.00 | 0.22 | reads-as-noise x1 |
| `clock:window_s=31.0` | clock | 1 | 0 | 1 | 0.00 | 0.22 | off-doctrine x1 |
