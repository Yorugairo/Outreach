# Script viewer recheck — 2026-09-22

**Status: DIAGNOSTIC ONLY. This recomputation is not an operator review or approval.**

## Current recomputation

Recomputed `viewer_score.score` from the current script, viewer windows, and reader reports: **61/63 declared beats perceived (97%)** across 51 windows and 51 reports. V01 remains `FAIL`; the only current misses are:

```text
  [FAIL ] V01 61/63 declared beats perceived (97%); unperceived: [archetype] w1, [ring] w2
          P36 beat recall (rule R2 laundering, measured from the outside)
  [PASS ] V02 no run of 2+ windows without a concrete new thing
          doc 31 retention clock: something genuinely new every 15-30s
  [PASS ] V03 open loop live in 51/51 windows (100%)
          open-loop coverage floor 50% (doc 31)
  [INFO ] V04 nothing the reader could not follow
          comprehension outranks structure (STRENGTH-LOOP precedence); window-cut artifacts excluded
  [INFO ] V05 gain per window: median 3, 0 dead of 51 reported
          a new thing is CONCRETE when it carries a numeral, or a capitalised name, or a word this window introduced that the memory did not already hold - crude on purpose, and constant-cited

RESULT: 1 FAIL / 0 WARN / 2 PASS / 2 INFO
```

These parser-facing summary rows are the recomputed diagnostic view. The table below names the two missed beats; the historical source markdown remains separate.

| Beat | Script sentence | Recomputed reader evidence |
|---|---|---|
| `archetype:w1` | “Imagine you own a workshop.” | No matching line in the reader reports within the scorer’s one-window recall range. |
| `ring:w2` | “Your machine still works.” | No matching line in the reader reports within the scorer’s one-window recall range. |

The current report for window 15 (3:45–4:00) says “The old loan’s interest rate was 2%.” That is a match for the `new:w15` beat “Your old loan charged two percent.”, so `new:w15` is perceived in the current recomputation.

## Historical record reconciliation

The existing `SCRIPT-VIEWER.md` remains a historical record. It says 60/63 and records `new:w15` as unperceived, reflecting an earlier report snapshot. The current `SCRIPT-VIEWER-REPORTS.json` has the window-15 evidence quoted above. This recheck records the difference without rewriting either source record.

The score was recomputed with `viewer_score.score` from `content/video_engine/scripts/viewer_score.py` using these byte-identifiable inputs:

| Scorer | SHA-256 |
|---|---|
| `content/video_engine/scripts/viewer_score.py` | `814994e53c5d8bf1ee8ee6d7b1b6dacbf022c4e60e2000922bed6a3d66f45c9d` |

| Input | SHA-256 |
|---|---|
| `SCRIPT-VO.txt` | `30d24ba99d7ffb0f858cff49ae2245044ad4ba82def55ba6a4d6b65d3f251c88` |
| `SCRIPT-VIEWER-WINDOWS.json` | `9273fe0c74ef83fcf2f9910ece8940c91958b1a1337f7d9c67fe17376e75568c` |
| `SCRIPT-VIEWER-REPORTS.json` | `914fe54dbf47bbd310b57f20eab4c554aa84770d0a293a0bc449500f967e68c0` |
| Historical `SCRIPT-VIEWER.md` | `c18c236471d738e59d39a21f4ea96201648e8aace0f2f4bb352bda8b9f8ea38f` |

## Approval and acceptance state

No `review/PILOT-VIEWER-REVIEW.json` approval sidecar was present when this diagnostic was written. This document does not supply one. The validator consumes this dated recheck as its viewer input and still requires a separate sidecar with explicit operator authorization, exact current misses, and matching artifact hashes. A sidecar that names or hashes the historical `SCRIPT-VIEWER.md` is rejected. Synthetic authorization is used only in temporary unit-test fixtures.
