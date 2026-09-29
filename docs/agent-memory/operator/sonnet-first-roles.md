---
name: sonnet-first-roles
description: operator 2026-09-29 - delegated roles START on Sonnet 5.5 with step-up to Opus 5.5; Opus starts only architect_sol (plans); Sonnet gets small, specifically scoped slices
metadata:
  type: feedback
---
The operator (2026-09-29, Sonnet 5.5 released): "set a good portion of our agents to use Sonnet 5.5 with stepup to Opus 5.5, reserving Opus start primarily for architect/plan-writing. Sonnet should receive appropriately scoped and bounded executions, it is smaller and faster than opus and should receive smaller, more specifically scoped work also."

Done: `model: sonnet` on explorer, docs_researcher, implementation_luna, junior_developer, reviewer, release_steward (project `.claude/agents/` AND user `~/.claude/agents/`); speedster already Sonnet; architect_sol stays Opus; bridge_handler moved to Sonnet too (the operator, same day). Policy + step-up triggers + slice sizing: `docs/runbooks/PRP_EXECUTION.md` "Model policy".

**Why:** Sonnet is faster and cheaper; Opus judgement is spent on plans and on the slices that need it.

**How to apply:** cut briefs to ONE item or one function's cluster, exact write set, named regression + tests, <= 1 new golden (P72 T53 (i)-(l)'s seven items hit the turn limit twice even on Opus). Step up with the Agent call's `model: "opus"` when: a shared engine surface / >1 subsystem, a design call inside a build (better: architect_sol first), THREE consecutive substantive failures of a Sonnet developer role on the same task (the Codex Luna -> Sol rule mirrored, the operator 2026-09-29: architect_sol diagnoses/re-plans, then re-scope for Sonnet or step the build up; tool-call mistakes don't count), or a suite-wide re-pin / lane merge. Verify Sonnet's labels (Sonnet 5 once mislabelled a ruling) until re-measured. Related: [fable-parent-opus-roles](fable-parent-opus-roles.md), [agent-turn-limits-opus](agent-turn-limits-opus.md), [opus-5-5-parent-trial](opus-5-5-parent-trial.md).
