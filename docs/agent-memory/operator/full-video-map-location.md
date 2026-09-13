---
name: full-video-map-location
description: Where the classical+micro fused doctrine lives (FULL-VIDEO-MAP and its neighbours) and which branches/checkouts actually hold it
metadata: 
  node_type: memory
  type: reference
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-02T22:17:40.939Z
---

The document the operator means by "the one that maps all the classical +
micro layers together" is `docs/content-video-engine/patterns/FULL-VIDEO-MAP.md`
("McKee Extended to the YouTube Era" — classical six-phase = the integral,
platform micro-rules = the differentials). Its companions: `patterns/
LLM-CONTEXT-CLASSICAL.md` (portable Truby/McKee/Snyder/Glass/Humes/ring
block), `32-WRITING-FOR-THE-EAR.md` ("the for the ear research"),
`patterns/SCRIPT-PATTERN-KIT.md`, `patterns/phase-guides/P1–P6.md`.

Until 2026-09-02 the whole doctrine set existed ONLY on branch
`claude/content-generation-system-52f077` — the `main` branch had none of it
and the main checkout (`C:\Users\Snipe\Downloads\Outreach Program`) sits on
`claude/outreach-api-and-tooling` with an older `docs/content-video-engine/`
subset (no `patterns/`). On 2026-09-02: `main` fast-forwarded to that branch
(79a5563; rollback sha 4b7bdf2) and the doctrine tree was copied into the
main checkout without overwriting its older 00–18 docs.

**How to apply:** when the operator asks "where is X doctrine", check
`git ls-tree main -- <path>` and the main checkout before answering — the
branch/worktree split has hidden files from them before. See
[worktree-sprawl](worktree-sprawl.md) and [worktree-read-scope](worktree-read-scope.md).
