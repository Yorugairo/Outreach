---
name: prp-router
description: Route repository work by operation, risk, human gates, and ownership before planning or implementation.
---

# PRP Router

Read `docs/runbooks/PRP_EXECUTION.md` and `docs/AGENT_START_HERE.md`.

1. Classify the operation and highest risk.
2. Identify protected actions and human gates.
3. Keep small work in the parent; use a PRP for multi-slice or risky work.
4. Route exact mechanical microtasks to `speedster`; scoped fixes, explicit
   line changes, and limited implementation to `junior_developer`; bounded
   moderate implementation to `implementation_luna`; read-only code tracing to
   `explorer`; primary-doc verification to `docs_researcher`; review to
   `reviewer`; planning to `architect_sol`; and reviewed Git mechanics to
   `release_steward`.
5. State owner, write boundaries, acceptance, validation, exclusions, and
   human gates.

The parent retains architecture, external actions, integration, and final
completion authority.
