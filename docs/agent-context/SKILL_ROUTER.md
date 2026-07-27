# Skill And Agent Router

Status: current
Last reviewed: 2026-07-26

The repository uses an allowlist-first skill policy. Load the smallest set that
matches the task. Skills outside this router are disabled for this project by
`scripts/configure_codex_skill_allowlist.py`.

## Active Skill Lanes

| Trigger | Skills |
| --- | --- |
| PRP, planning, goals, backlog | `prp-router`, `prp-plan`, `prp-implement`, `prp-status`, `define-goal`, `agentic-tpm-and-execution`, `scrum-master` |
| pSEO, directory, indexability | `modern-seo-optimizations`, `seo`, `seo-content-writer` |
| Design and frontend | `frontend-patterns`, `modern-design-frameworks`, `product-design:*` |
| Content and marketing | `content-engine`, `seo-content-writer`, `market-research`, `elite-cro-and-marketing` |
| Backend, API, and persistence | `backend-patterns` |
| Performance and rendered QA | `web-perf`, `e2e-testing`, `playwright` |
| Structural code search | `ast-grep`, `ast-grep-outline` |
| Context control | `strategic-compact` |

Release management, workspace cleanup, broad infrastructure, unrelated
industry operations, and generic agent-framework skills are disabled by
default. Their durable safety rules remain in `AGENTS.md`; activate a specific
skill manually only when a task genuinely requires it.

## Tool Routing

1. Use `python scripts/sigmap_context.py ask "<question>"` before broad code
   discovery.
2. Use `rg` for exact text and paths.
3. Use `ast-grep outline` before opening large candidate files.
4. Use `ast-grep` for syntax-aware Python/JavaScript search and review matches
   before any rewrite.
5. Use primary documentation or the `docs_researcher` role for current library
   and SDK behavior.
6. Use browser or Playwright for rendered UI and interaction QA.
7. Use repository adapters only within their migration, security, and
   human-gate contracts.

## Named Agent Routing

- **Parent task**: owns the critical path, shared-file integration, protected
  actions, final verification, and completion truth.
- **`speedster`**: deterministic microtasks only: one-line fixes, mechanical
  updates, exact discovery, formatting, focused tests, or narrow commands.
  Re-route immediately when judgment or ambiguity appears.
- **`junior_developer`**: small, explicitly bounded implementation and scoped
  fixes with exact files or symbols, a small read/write set, acceptance, and
  focused validation. Re-route when root cause, design, or scope is uncertain.
- **`implementation_luna`**: bounded moderate implementation with an explicit
  write set, acceptance criteria, tests, and validation. No major refactors or
  protected boundaries.
- **`architect_sol`**: repository research and implementation-ready PRP
  drafting. It does not implement product code or approve its own plan.
- **`explorer`**: read-only evidence gathering.
- **`docs_researcher`**: read-only API, framework, and release-note research.
- **`reviewer`**: fresh correctness, security, and missing-test review.
- **`release_steward`**: mechanical staging and commit work after review. It
  may push only when current explicit user authorization is included.

Use the smallest capable role. Use `fork_turns: "none"` for narrow worker
dispatches. Do not parallelize overlapping writes. Migrations, auth/security,
payments, deploys, shared contracts, and external actions remain parent-owned.

Full delegation rules live in
[`../runbooks/PRP_EXECUTION.md`](../runbooks/PRP_EXECUTION.md).

## Maintaining The Allowlist

Preview:

```powershell
python scripts/configure_codex_skill_allowlist.py --check
```

Apply:

```powershell
python scripts/configure_codex_skill_allowlist.py --write
```

The tracked `.codex/config.toml` and `.codex/agents/*.toml` files define
named-agent registration and models; the generator owns only the generated
skill-disable block. Restart Codex after applying allowlist changes.
