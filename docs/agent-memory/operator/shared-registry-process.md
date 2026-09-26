---
name: shared-registry-process
description: "GPT's 09-23 process (main 91701cb/a063067): a built capability updates CAPABILITIES.md + its effect card/recipe in the SAME integration commit; pushes touching them need check_shared_video_registries.py + a Claude bridge REGISTRY-ACK"
metadata:
  node_type: memory
  type: reference
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-23T23:54:37.912Z
---

Source: `docs/WORKTREE-REGISTER.md` "Shared video registries: proof, then non-destructive push check" (main 91701cb), `content/video_engine/scripts/check_shared_video_registries.py`, `test_effects_catalog_drift.py` (coverage: every DOCK_OPTS/PLATE_OPTS token needs a card or a card's option - T26d's place/rot/moves failed it).

- When a capability is built / changes state / retires: its CAPABILITIES.md row in the same integration commit, citing code + a test or review receipt; a proven effect updates its card (`effects/cards/`), a proven combination its recipe (`effects/recipes/`); never promote on an agent summary. Regenerate `build_capabilities_index.py --write` + `build_effects_catalog.py --write` and check both (outputs gitignored).
- Before an authorized push touching CAPABILITIES/cards/recipes: `git fetch`, `check_shared_video_registries.py --base origin/main --head HEAD`; send the fingerprint, candidate and one REGISTRY-CLAUDE-HEAD per Claude branch through the bridge; the Claude review reply carries `POSITION: done` + `REGISTRY-ACK: <fingerprint>`; re-run with `--ack-file`; a moved head invalidates it. The check is never push authorization.

Lesson (P69, 09-23): lane B shipped ~12 capabilities with no CAPABILITIES rows or cards - write the row and card in the slice's own commit. Related: [rulings-need-carriers](rulings-need-carriers.md), [docs-layers-and-registries](docs-layers-and-registries.md).

**Lanes take main back (09-23):** our flow ran only lane B -> lane A -> main, so lane B never got a063067's dock_kind.json fix and its catalogue check failed on every run ("I thought it was fixed" - the operator). After each merge to main, merge main back into EVERY Claude lane (lane B too), so their checks run on current cards.
