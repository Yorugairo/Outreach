---
name: agentic-tpm-and-execution
description: Frame an unplanned, multi-slice coding request when acceptance, ownership, or verification is still unclear. Skip for bounded work orders and approved PRPs; use their existing execution route.
---

# Task Framing for Unplanned Work

Use this skill only when a coding request still needs a decision about scope, acceptance, ownership, or verification before implementation. It is not a mandatory preflight for every code change.

## Route first

- If an approved PRP or bounded agent work order already states the outcome, write set, acceptance, and tests, follow it directly. Do not reopen requirements, create a second task tracker, or block on this skill's planning checks. Use the project's PRP execution route where applicable.
- For an unplanned request, consult the project's actual entrypoint and router, then identify only the unresolved decisions that would change implementation. Ask the user only for consequential choices that cannot be resolved from the repository or existing rulings.
- Treat named document paths in examples or older plans as conditional references. Check that a document exists and is relevant before opening it. A missing optional planning document is a setup note, not an implementation failure or a reason to create a replacement.

## Produce the smallest executable order

Record the intended outcome, acceptance evidence, anti-goals, owner/write set, relevant source paths, verification commands, and any real human gate in the project's existing plan or tracker. Reuse an active record rather than mirroring it into a generic `task.md` or backlog. A one-file fix may need only a short work order; a multi-slice change may need a PRP.

Then implement or dispatch against that order. Verify the artifact and behavior before claiming completion. Count a failed attempt when the bounded task actually fails, not when a nonessential discovery lookup finds no file. Preserve the original permissions and approval gates across retries.
