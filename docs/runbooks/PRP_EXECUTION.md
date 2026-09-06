| Sonnet 5 | **not adopted as a searcher** (a `searcher` variant was tried and removed the same day) | round 3, the easy five with the docs index available: 3.5/5 (mislabelled a ruling E46 for E38; named the flag default, not the build that sets it), 238 k tokens vs Opus's 156 k for the same five (the fixed overhead dominates, so the cheaper model is not cheaper per lookup), 336 s vs 138 s |
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

### Hand-off policy (measured 2026-09-05, `evals/RETRIEVAL-BENCHMARK-2026-09-05.md`)

**What a dispatch costs.** A fresh subagent pays ~20-25 k tokens before its first tool call (system
prompt, rules, repo instructions); a lookup then runs 30-60 k on the agent's model. What returns to
the parent is the result text only - ~300 tokens - and *nothing* of the agent's context. What the
parent reads inline is different in kind: every byte of tool output stays in the parent's context
for the rest of the session and is re-sent on every later turn. Rule of thumb: 1 KB of tool output
≈ 300 tokens, forever. One inline asset hunt this session pulled 1.75 MB (~450 k tokens) into the
Fable context; the same hunt delegated would have cost the parent 300.

**When to delegate (any one is enough):**
- the hunt will take more than ~5 tool calls, or you cannot name the file before starting;
- you need a part of a file over 200 lines and do not know which part;
- the question is "does X exist / did we build X" (a search across worktrees, sources, git history);
- the work is review, test runs, gates regeneration, git mechanics, or doc maintenance.

**When to do it inline:** one `rg` on `docs/DOCS-INDEX.jsonl` or SigMap plus one `sed -n` window
under ~40 lines answers it; or the fact is already in context. Below ~5 tool calls the dispatch
overhead is the larger cost.

**The brief** names: plan path / task id, allowed files, acceptance, the exact validation command,
the answer cap (≤ 200 words as `path:line` + values), and where the full evidence goes.

**The return contract:** the agent returns the ≤ 200-word answer inline. Anything longer (a
research pack, a diff review, a transcript of runs) is written to `docs/research/runs/<slug>/`
(gitignored disk-as-bus) - boilerplate stripped, command logs through `sqz compress --mode safe`
- and the return names the path. The parent reads that file only with `sed -n` windows, never
whole. A delegated agent reports **"not found in <the places I searched>"**, never "does not
exist"; the parent verifies every negative claim with one grep, reads every diff, and runs the
slice's validation itself before integrating.

**Model routing, from the benchmark:**

| model | use | evidence |
| --- | --- | --- |
| Fable 5.1 | the parent only: design, planning, animation reasoning, the operator's conversation, briefs, JUDGE verdicts, diff review | it is the scarce model; nothing delegated runs on it |
| Opus 5 | `explorer` for any hunt with judgement in it (evidence layer, research bundle, open-ended "what is documented but unbuilt"); `implementation_luna` / `junior_developer` for slices; `reviewer`; `architect_sol`; `release_steward` | round 1: 5/5 at 36 % fewer tokens than Fable; round 2 (hard): 4.5/5 at 26 % fewer and half the time; one false negative |
| Sonnet 5 | `searcher` - well-specified lookups where the file is nameable and the index or memory points at it | round 3: fast (9-20 s) but mislabelled a ruling (E46 for E38) and answered "which build turns it on" with the default only; tokens per dispatch NOT lower than Opus (the fixed overhead dominates) - use for volume, verify the labels |
| Haiku 4.5 | `speedster` - deterministic edits with the exact line given; never a lookup with a judgement in it | 23 k tokens for a one-line edit: correct, but the overhead is the whole cost |

Separate search and implementation agents: yes - their memories are different maps (`explorer`:
where things live; `implementation_luna`: patterns and pitfalls) and contexts never share in this
harness anyway. Persistence is per-agent memory (`memory: user` - sessions run in worktrees, so
`project` scope would fragment per worktree), which accumulates *where things live* across
sessions and cuts tool calls, not the fixed overhead; `/resume` continuation is CLI-only.

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
