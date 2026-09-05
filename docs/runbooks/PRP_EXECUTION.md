# PRP Execution

Status: current
Last reviewed: 2026-07-25

PRPs are durable execution contracts for work too broad or risky to manage
from chat history. Store active plans under `.claude/PRPs/plans/`; the legacy
path is agent-neutral storage.

## Workflow

1. **Route** by operation, risk, human gates, and owner.
2. **Plan** from current code and evidence.
3. **Approve** required high-risk or external actions.
4. **Implement** dependency-aware, non-overlapping slices.
5. **Review** delegated diffs and prove acceptance.
6. **Close** only after tests and evidence are recorded.

Use a PRP for architecture, cross-module features, persistence changes,
security boundaries, external integrations, deployment, or work requiring
multiple coherent slices.

## Named Agents

| Agent | Use | Hard stop |
| --- | --- | --- |
| `speedster` | Exact microtask, tiny write set, exact validation | Ambiguity, architecture, security, release |
| `junior_developer` | Limited implementation, scoped fixes, explicit line changes, small reads/writes | Expanding write set, cross-module design, unclear acceptance |
| `implementation_luna` | Bounded moderate implementation with tests | Major refactor or unclear contract |
| `architect_sol` | SigMap-led research and PRP draft | Product implementation or self-approval |
| `explorer` | Read-only repository trace and evidence pack | Any write or implementation decision |
| `docs_researcher` | Read-only primary documentation verification | Product implementation or undocumented inference |
| `reviewer` | Read-only correctness, security, regression, and test review | Editing or integrating its own findings |
| `release_steward` | Reviewed stage/commit/authorized push mechanics | Unexpected diff, conflict, absent approval |

The parent owns architecture, integration, protected actions, and completion
truth. Keep concurrency at four threads and depth one. Do not overlap write
sets.

Use `speedster` only when judgment is unnecessary. Prefer `junior_developer`
for a small bounded fix that still requires implementation reasoning, and
`implementation_luna` for coherent moderate slices. Use `explorer`,
`docs_researcher`, and `reviewer` as read-only evidence producers.

### Dispatch mapping

**Since 2026-09-05 the eight roles ARE dispatchable types on both sides.**
Codex: `.codex/config.toml` + `.codex/agents/<role>.toml` (OpenAI models).
Claude Code: `.claude/agents/<role>.md` (project scope, committed) — pass the
bare role name as `subagent_type`. Each definition carries its own model, tools
and the role's stop conditions, so a slice no longer has to be squeezed into
`general-purpose` / `Explore` / `Plan`.

**Model policy (operator, 2026-09-05).** Fable is the scarce model (a 50 %
weekly cap) and the clearly stronger one, so it is spent only where judgement
compounds: the PARENT session — architecture, integration, protected actions,
operator conversation, completion truth. Everything delegated runs on Opus 5;
`speedster` runs on Haiku 4.5 because judgement is unnecessary by definition.
Never launch a delegated role with `model: fable` / an inherited Fable model;
never pull a role's work back into the parent to "save a dispatch" — the
dispatch is the saving.

| Role | Claude type | Model | Write access |
| --- | --- | --- | --- |
| `speedster` | `speedster` | Haiku 4.5 | Yes — the slice's write set only |
| `junior_developer`, `implementation_luna` | same name | Opus 5 | Yes — the slice's write set only |
| `explorer`, `docs_researcher`, `reviewer` | same name | Opus 5 | No (read-only Bash: git/sigmap/tests) |
| `architect_sol` | `architect_sol` | Opus 5 | `.claude/PRPs/plans/` and named planning evidence only |
| `release_steward` | `release_steward` | Opus 5 | `git add <paths>` / `git commit`; push only with the operator's CURRENT authorization quoted in the brief |

What stays with the parent regardless of model: the decision to dispatch, the
brief, the review of every delegated diff, the human gates, and anything
outward-facing. Where a harness lacks a role (a bare `claude -p` run, an older
build), fall back to the previous mapping — `general-purpose` for writers,
`Explore` for readers, `Plan` for the architect, parent for git — and say so in
the PRP's deviations.

Whatever the mapping, four rules survive it:

- **Every delegated diff is reviewed before integration.** A completion claim is
  not evidence. The parent reads the diff and runs the slice's validation itself.
- **Write sets never overlap.** Dispatch together only slices that touch disjoint
  files. Shared integration points — router registration, module exports, config
  files — stay with the parent, because two agents editing one file is how a
  parallel run corrupts itself.
- **A dispatch brief names the plan path, task id, allowed files, acceptance, and
  the exact validation command.** Never a vague brief.
- Architecture, protected boundaries, human gates, and ambiguous debugging stay
  with the parent regardless of slice size.

## PRP Format

New plans use YAML frontmatter:

```yaml
---
id: P2-EXAMPLE
title: Example
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---
```

Statuses: `draft`, `approved`, `running`, `review`, `blocked`, `complete`.

Required sections:

- `## Summary`
- `## Intent And Acceptance`
- `## Scope`
- `## Not Building`
- `## Human Gates`
- `## Mandatory Reads`
- `## Execution Path`
- `## Patterns To Mirror`
- `## Task Slices`
- `## Verification`
- `## Evidence And Handoff`

Task slices use:

```markdown
### T1: Short title
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `path/a`
- Acceptance: observable outcome
- Validate: exact command
- Evidence: pending
```

Validate with:

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/example.plan.md
python scripts/prp_status.py
```

Checkpoint after approval, before protected actions, and after each validated
slice. Persist state in the PRP rather than active instructions or transcripts.
