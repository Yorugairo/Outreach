---
name: claude-md-imports-agents-md
description: "Claude Code never reads AGENTS.md; every repo/worktree needs a CLAUDE.md (or CLAUDE.local.md) that imports it, and untracked CLAUDE.md files block merges"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T04:42:18.818Z
---

Claude Code loads CLAUDE.md (cwd and every parent, `.claude/CLAUDE.md`,
`CLAUDE.local.md`, `~/.claude/CLAUDE.md`) and NOT AGENTS.md — documented at
code.claude.com/docs/en/memory ("Claude Code reads CLAUDE.md, not
AGENTS.md"). Codex, Hermes, Cursor read AGENTS.md. Until 2026-09-02 the
Outreach repo had AGENTS.md and no CLAUDE.md, so every Claude session
started without the playbook.

**Why:** the operator assumed AGENTS.md was the cross-agent standard ("well
over 7% of developers think agents.md is the standardized answer") and
blamed the resulting re-discovery loops on the agents.

**Standing rule R9 (operator, 2026-09-02):** lane capabilities come from
the docs and the template, never from memory - cite the file before
claiming what the lane can/can't do. Twice in one day I asserted things
the repo contradicted (static charts; hyperframes unused).

**How to apply:**
- Root `CLAUDE.md` = `@AGENTS.md` import + a few fast routes; keep the
  guidance itself in AGENTS.md. Committed on the content-generation branch
  and `main` (b4c71a7).
- For checkouts/worktrees on branches that predate the tracked CLAUDE.md,
  write `CLAUDE.local.md` (gitignored, loaded the same way) — NEVER an
  untracked `CLAUDE.md`, because git refuses to checkout/merge over an
  untracked file of the same name and the branch could never take `main`.
- Any new repo with an AGENTS.md: add the CLAUDE.md import on day one.
- Wire a CLAUDE.md→AGENTS.md reference ONLY after reading the AGENTS.md:
  the operator is trimming bloat and wants no global ECC instructions
  (`~/.claude/AGENTS.md`, 192 lines, is dead weight - no agent reads it;
  ECC's own 82-line CLAUDE.md is the better copy). TradesInsights'
  AGENTS.md files are SigMap gen-context.js signature dumps, not guidance
  (root = 1,167 lines - never import; package stubs got CLAUDE.md pointers
  2026-09-02). SCML "Claude Files": CLAUDE.md now imports AGENTS.md.
- Stale-model statements: the operator's June 2026 read of Gemini as
  "weaker as a hands-on coder" is retired (rewritten in scml-ledger
  AGENTS.md/CLAUDE.md 2026-09-02). Current standing: Gemini is a competent
  coding agent used for front-end, research, and graphical work; scope
  limits are ownership rules, not capability judgments. WA registry's
  "Gemini/Antigravity read-only" line survives only on five old worktree
  branches (root dropped it) - a permissions policy, left to merge out.
- `~/CLAUDE.md` created 2026-09-02, importing `~/AGENTS.md` (11 lines:
  nearest project AGENTS.md is the contract; sqz only for genuinely
  verbose output). It loads for every project under the home folder.
See [worktree-sprawl](worktree-sprawl.md), [full-video-map-location](full-video-map-location.md).
