---
name: viewer-perception-test
description: "P36 the viewer - the third role (blind, windowed perception test); never ask an agent when it would drop; ep1 calibration says recall tracks the analytics and information gain does not"
metadata:
  node_type: memory
  type: project
---

Three roles check a script (ruling E26): **gates** mechanical, **judge**
doctrinal (the runtime agent), **viewer** blind. The viewer knows nothing -
no doctrine, tags, ledger or that a test is happening - and reads the script
cold in 15s windows with a two-window memory, answering four perception
questions. `viewer_windows.py` -> `viewer_run.py` (Codex headless, high
effort) -> `viewer_score.py` -> `<script>-VIEWER.md`, shown by the runner as
an advisory VIEWER block (`--viewer-gate` promotes it).

**Never ask an agent when it would drop off.** An LLM's patience is not a
human's; a made-up timestamp is worse than no measure. Ask only for
perception reports it can give stably and let a deterministic scorer judge.

**Two hard-won implementation facts.** Codex discovers `AGENTS.md` by walking
UP from `--cd`, so the viewer's calls run in an empty directory outside the
repo or the test is void. And `codex exec -i/--image` is VARIADIC: it
swallows the positional prompt unless a non-variadic flag closes the list.

**Ep1 calibration (2026-09-03, the result that matters):** beat recall and
the package measure agree with the analytics drop; **information gain does
NOT** - the 0:45-1:00 window scores above the episode median and there are no
dead windows, so a density measure cannot find a failure that is not about
density. Confusion tracks instead, once window-cut artifacts are filtered
(20 of 42 were our own noise). It caught what nothing else did: the
counterparty evaporates - "Bravos" is unfollowable from 6:45 onward while the
script keeps arguing against them. **PROMOTED 2026-09-03** (HG1 granted): recall binds as FAIL, confusion as
WARN, gain stays INFO with no authority. Gating is the runner's default;
`--no-viewer-gate` opts out. The general lesson: a measure earns authority by
firing on the known-bad case, not by being reasonable - gain was retired the
day it was built.
See [ai-baselines-operator-corrects](ai-baselines-operator-corrects.md), [package-first-e27](package-first-e27.md), [opening-minute-e24](opening-minute-e24.md).
