---
name: prp-implement
description: Execute an approved Outreach PRP task by task with bounded delegation, verification, and durable evidence.
---

# PRP Implement

Read the named PRP and `docs/runbooks/PRP_EXECUTION.md`.

1. Validate the PRP, branch, approval, dependencies, and Git state.
2. Mark the plan `running`.
3. Execute ready slices in order; delegate only disjoint bounded work.
4. Review every delegated diff and verify artifacts or command evidence.
5. Record task status, deviations, validation, and evidence incrementally.
6. Run focused tests before the full suite.
7. Mark complete only after acceptance and required artifacts are proven.

Stop on an unapproved external action, overlapping writes, failed cleanup, or
new architecture conflict.
