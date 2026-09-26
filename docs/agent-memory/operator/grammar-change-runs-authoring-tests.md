---
name: grammar-change-runs-authoring-tests
description: "09-23: T26d's new dock token `place` broke 2 test_authoring_shapes tests that shipped to main unseen - any change to DOCK_OPTS/PLATE_OPTS/CHART_TO_KINDS/SPECIES runs test_authoring_*.py (the kit mirrors the compiler's vocabulary)"
metadata:
  type: feedback
---

The authoring kit (`content/video_engine/scripts/authoring/shapes.py`) mirrors the compiler's vocabulary, and its tests use example tokens (an "unknown" dock option `place`) that a new grammar slice can make valid. P69 T26d added `place`; two `test_authoring_shapes.py` tests went red and rode the 6078a11 push because every slice's validation list named only its own neighbours.

**Why:** slice validation lists are hand-picked; the kit is a second consumer of the grammar nobody listed.

**How to apply:** any slice touching DOCK_OPTS, PLATE_OPTS, CHART_TO_KINDS, SPECIES_KINDS or the chart_to/dock grammar adds `test_authoring_*.py` + `test_effects_catalog_drift.py` to its Validate; before a push, run the whole `content/video_engine/tests` suite once (or at least `-k "authoring or catalog or registry"`) and compare the failure set with origin/main's. Related: [shared-registry-process](shared-registry-process.md), [never-pipe-gated-steps-to-tail](never-pipe-gated-steps-to-tail.md).

**The full suite in ONE process is not a signal (09-24):** a test leaves an asyncio loop running and every later Playwright sync test errors ("Playwright Sync API inside the asyncio loop") - 472 failed / 88 errors, 159 of them goldens that pass alone. Run the whole suite per FILE (a process each) and diff the per-file failure set against origin/main's.
