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
