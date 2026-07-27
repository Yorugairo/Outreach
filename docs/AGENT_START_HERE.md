# Agent Start Here

Status: current
Last reviewed: 2026-07-25

This is the compact routing index after [`../AGENTS.md`](../AGENTS.md). Read
only the route that matches the task.

## Discovery

For coding, debugging, review, refactoring, or architecture:

1. Run `python scripts/sigmap_context.py ask "<question>"`.
2. Use `rg` for exact text and files.
3. Use `ast-grep outline` for a cheap structural map.
4. Use `ast-grep run --lang python --pattern '<pattern>' <scope>` for syntax
   discovery.
5. Read the smallest relevant source and test set.

Use SQZ only for large human-readable output. Preserve raw security, release,
test-verdict, and generated run evidence.

## Task Routes

### Skill And Agent Router

The durable router is [`agent-context/SKILL_ROUTER.md`](agent-context/SKILL_ROUTER.md).
Use it as the authority for active skill lanes, tool order, named-agent
selection, and allowlist maintenance.

Choose the smallest role that can complete the bounded assignment:

| Work | Role |
| --- | --- |
| Exact mechanical microtask | `speedster` |
| Small scoped fix, explicit line change, or limited implementation | `junior_developer` |
| Moderate well-defined implementation with focused tests | `implementation_luna` |
| Read-only repository trace | `explorer` |
| Read-only primary documentation verification | `docs_researcher` |
| Read-only correctness/security/regression review | `reviewer` |
| Architecture research and PRP drafting | `architect_sol` |
| Reviewed Git mechanics after explicit authorization | `release_steward` |

The parent retains architecture, integration, protected actions, and the final
completion claim. Do not give write work to read-only roles or expand a
delegated write set without returning it to the parent.

### Pipeline, Fetching, And Scoring

Read:

- [`seo-insights-platform-architecture.md`](seo-insights-platform-architecture.md)
- [`seo-ingestion-pipeline-spec.md`](seo-ingestion-pipeline-spec.md)
- [`product-strength-contract.md`](product-strength-contract.md) for
  independent score surfaces, immutable report snapshots, and comparison
  compatibility
- the relevant service, repository Protocol, and focused tests

Preserve run-centric state, explicit stage events, safe HTTP behavior, and
evidence-backed outputs.

### Agentic Analysis And Client Reports

Read:

- [`agentic-analysis-contract.md`](agentic-analysis-contract.md)
- the immutable report-snapshot and evidence-pack models
- the runtime, validation, manifest, and focused security tests

Treat model output as untrusted downstream interpretation. Agentic analysis may
prioritize and draft from persisted evidence, but it cannot browse, recrawl,
alter deterministic scores, or approve customer claims.

### API, Dashboard, And Product

Use `backend-patterns` for API and persistence changes. Use
`frontend-patterns`, `modern-design-frameworks`, and product-design skills for
the operator dashboard. Verify rendered behavior in addition to static source.

### SEO Research And Marketing

Use `seo`, `modern-seo-optimizations`, `market-research`, and
`elite-cro-and-marketing`. Separate observed evidence from inference and never
fabricate search or competitor facts.

### Planning And Multi-Agent Execution

Use `prp-router`, `prp-plan`, `prp-implement`, and `prp-status` with
[`runbooks/PRP_EXECUTION.md`](runbooks/PRP_EXECUTION.md).
PRP slices may name any role in the Skill And Agent Router, but every delegated
slice must retain an explicit write/read boundary and exact validation.

### Release And External Actions

The parent task retains credential, deployment, database, billing, external
write, commit, and push authority. A named agent does not inherit approval.

## Verification

Start narrow, then broaden:

```powershell
python -m pytest tests/<focused_test>.py -q
python -m pytest -q
python scripts/agent_tooling_doctor.py
```

For pipeline behavior, also verify the run and report artifacts required by
[`../AGENTS.md`](../AGENTS.md).
