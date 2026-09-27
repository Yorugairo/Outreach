---
name: prp-plan
description: Create a grounded, implementation-ready Product Requirement Prompt for complex Outreach repository work.
---

# PRP Plan

Read `docs/runbooks/PRP_EXECUTION.md`. Run the repository SigMap wrapper first.
Use the planning role and model specified for the active provider in that
runbook. The parent briefs and reviews the draft, retains final architecture
decisions and human gates, and does not treat an architect's draft as approval.

1. Confirm intent, acceptance, anti-goals, risks, and human gates.
2. Trace current implementation, contracts, tests, and evidence.
3. Use `backend-patterns` for API, pipeline, persistence, jobs, or security
   boundaries; use `frontend-patterns` for dashboard work.
4. Start from `.claude/PRPs/templates/prp-template.md`.
5. Have the planning owner write dependency-aware slices with bounded write
   sets, exact validation, and the smallest capable owner: `speedster` for deterministic microtasks,
   `junior_developer` for limited scoped implementation,
   `implementation_luna` for moderate implementation, `explorer` or
   `docs_researcher` for read-only research, and `reviewer` for independent
   review. Keep final architecture authority and integration in the parent.
6. Run `python scripts/prp_validate.py <plan>`.
7. Present the draft for approval unless plan-and-execute was explicitly
   requested.

Do not invent architecture or implement while the plan remains unapproved.
