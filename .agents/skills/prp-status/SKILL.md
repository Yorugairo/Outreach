---
name: prp-status
description: Report compact execution status for active Outreach PRPs.
---

# PRP Status

Run `python scripts/prp_status.py [plan]`, then confirm the result against Git
state and evidence. Report plan status, completed tasks, ready work, blockers,
human gates, pending validation, and the next critical action. Do not infer
completion from code presence alone.

Recognized delegated owners are `speedster`, `junior_developer`,
`implementation_luna`, `explorer`, `docs_researcher`, `reviewer`,
`architect_sol`, and `release_steward`. Flag unregistered owners, overlapping
write sets, write assignments to read-only roles, or release work without a
current human gate.
