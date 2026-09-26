---
name: opus-5-5-parent-trial
description: From 2026-09-22 the PARENT runs on Opus 5.5 instead of Fable, on trial - benchmarks show better and cheaper, but Opus 5.1 drifted off task and orchestrated agents worse than Fable; the operator is watching exactly that
metadata:
  type: project
---

The operator, 2026-09-22: "For now we are using opus 5.5 over fable until we see otherwise, the benchmarks and reports
all show improved performance and cheaper pricing, but opus 5.1 showed similarly but wasn't able to stay on task or
orchestrate agents as well as fable did, so we will see if you're fit for the task as 5.5!"

The roles are unchanged (`model: opus` resolves to 5.5 on its own); what changed is the parent - the seat that holds
judgement, integration, the operator and the completion claim ([fable-parent-opus-roles](fable-parent-opus-roles.md) still describes the split).

**Why:** a cheaper, benchmark-stronger parent is worth it only if it keeps Fable's two strengths: staying on the task
the operator set, and orchestrating lanes without losing the thread.

**How to apply - what the trial judges, so hold to it every turn:** finish the standing goal in order instead of
wandering into adjacent fixes (file them, don't chase them); keep one lane per scope and review every delegated diff
on the frame and the code before accepting it; never report a lane's claim as fact without checking; keep the operator's
decisions in front and short. Symptoms that mean the trial is failing: unrequested scope, forgotten pending questions,
a lane's report relayed unchecked, the same fix re-derived.
