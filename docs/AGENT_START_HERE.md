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

### Pipeline, Fetching, And Scoring

Read:

- [`seo-insights-platform-architecture.md`](seo-insights-platform-architecture.md)
- [`seo-ingestion-pipeline-spec.md`](seo-ingestion-pipeline-spec.md)
- the relevant service, repository Protocol, and focused tests

Preserve run-centric state, explicit stage events, safe HTTP behavior, and
evidence-backed outputs.

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
