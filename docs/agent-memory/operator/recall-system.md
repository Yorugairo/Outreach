---
name: recall-system
description: "The three recall surfaces - CAPABILITIES.md, PLATE-LIBRARY, survey_worktrees.py - check them BEFORE building or searching; capabilities update in the same commit"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-08-31T09:06:27.837Z
---

Storage and recall are the operator-named bottleneck (2026-08-29: "we're
losing everything we do... everything is scattered"). Three asset classes
were rebuilt in one session because nothing indexed what existed.

The recall surfaces, in check-first order:

1. **`docs/content-video-engine/CAPABILITIES.md`** — every built capability
   (renderers, engines, gates, prototypes): what/where/state/proof. Rule: a
   capability added or retired updates this file IN THE SAME COMMIT.
2. **`content/video_engine/sources/PLATE-LIBRARY.json`** — 134 plates by
   semantic, rebuilt by `build_plate_library.py` after any wave.
3. **`content/video_engine/scripts/survey_worktrees.py`** — regenerates
   `docs/STATE-OF-WORK.md` from git+filesystem; never hand-edited, cannot
   rot. Run it whenever the question is "where is X / what is unfinished."

**Why:** the [worktree-read-scope](worktree-read-scope.md) rule already said search everywhere;
these make searching unnecessary for known classes. The bjjregistry lesson
the operator cited: work that isn't indexed with explicit status gets
dropped on the floor.

**Code search order (2026-08-31, operator):** `python
scripts/sigmap_context.py query "<question>" --top 5` FIRST for any
symbol/architecture question (it self-builds its index per worktree,
~10k tokens for the whole map) → `ast-grep` (installed, `sg`) for
structural code patterns → grep only for literals/JSON/config. Grep
confirms a hypothesis; it cannot surface what you don't know exists.

**How to apply:** before writing any builder/renderer/asset, read
CAPABILITIES.md. When a doc cites a source artifact, read the artifact
(doc 29's summaries lost the curtain mechanism, the typewriter, the chart
draw). Harvest rule: durable output merges to main when its STAGE
completes, not when the episode ships — worktrees are isolation, not
storage.

**2026-09-05 addition:** for DOCS (doctrine, rulings, capabilities, backlog) the first call is `rg -i "<term>" docs/DOCS-INDEX.jsonl` (every heading/lead/label/table row -> path:line; regenerate with `build_docs_index.py --write`); SigMap is code-symbols only and mis-ranks doctrine queries. Delegate hunts of 10+ calls to the `explorer` role (Opus, memory: project).
