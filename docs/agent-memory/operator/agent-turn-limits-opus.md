---
name: agent-turn-limits-opus
description: "The role agents' maxTurns were Codex-era (explorer 40); raised 2026-09-15 for Opus 5 - explorer/docs_researcher/junior/reviewer 120, luna/architect 200, steward 60; stop writing sub-limit \"Turn budget\" lines in briefs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-15T16:45:59.785Z
---

Agent definitions live in main's `.claude/agents/*.md` (the worktree has no copy; subagents load main's). Their
`maxTurns` were sized for the GPT/Codex-era roles: explorer and docs_researcher 40, junior_developer and reviewer 60,
release_steward 30, luna and architect 120. An explorer sent a ten-item recall hit 40 turns with nothing written.

**Why:** the operator, 2026-09-15: *"It seems like we need to increase our tool limits. I think part of the problem is
that we are using what were GPT's agents, so they're being treated like Luna, when Opus 5 can go longer horizon than
Luna can."* Raised the same day: explorer, docs_researcher, junior_developer, reviewer 120; implementation_luna,
architect_sol 200; release_steward 60; bridge_handler 40; speedster (Sonnet) stays 30.

**How to apply:** don't write "Turn budget 40/45/60" into briefs below the definition's limit - the number in the
brief was cutting lanes short too. Size a recall by items (a ten-item recall is two or three explorers, or one at 120)
and tell an agent to WRITE its report incrementally so a limit never loses the work. See [fable-parent-opus-roles](fable-parent-opus-roles.md).
