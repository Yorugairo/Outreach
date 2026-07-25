---
name: scrum-master
description: Enforces strict Kanban discipline and the Log & Continue protocol. Prevents context-switching by requiring agents to instantly log discovered bugs/issues to the SPRINT_BACKLOG rather than fixing them mid-task.
---

# Scrum Master: Log & Continue Protocol

When executing a Sprint task, you are susceptible to "Nerd-Sniping"—discovering tangential bugs, technical debt, or optimizations that distract from the main goal. This skill enforces strict execution discipline to protect your context window.

## 1. The "Log & Continue" Protocol
If you discover a bug or issue outside the exact scope of your current task:
- **DO NOT FIX IT**, *unless* it is an immediate blocker preventing the completion of the active task.
- Stop and instantly append a new row to `Consultant input/SPRINT_BACKLOG.md`.
- Return immediately to your assigned task. Do not open files or run diagnostic commands for the out-of-scope issue.

## 2. Setting Presumed Criticality
When logging an issue to `SPRINT_BACKLOG.md`, you must assign it to the correct section by using basic reasoning:
- **`## P0`:** Critical live vulnerabilities, privilege escalations, or hard failures preventing core user journeys.
- **`## P1`:** Major data integrity issues, broken UI in conversion zones, or significant performance regressions.
- **`## P2`:** Technical debt, minor visual misalignments, or non-blocking optimizations.
*Note: This basic triage costs very few reasoning tokens and saves a future triaging step.*

## 3. Efficient Board Management
- **Direct Appending (Simple Issues):** For obvious issues (e.g., "Missing CORS header"), edit `SPRINT_BACKLOG.md` directly using your file editing tools.
- **Subagent Handoff (Complex Issues):** If an issue requires deep log reading or code tracing to understand, use `invoke_subagent` to spawn a `research` agent. Instruct the subagent to investigate the issue, write the ticket to the Kanban, and report back, keeping your primary context completely free.

## 4. Subagent Kanban Discipline
When delegating work to subagents, explicitly instruct them to use the `scrum-master` skill. If they encounter a blocker, they must log it and halt, rather than burning tokens hallucinating workarounds.
