---
name: worktree-read-scope
description: Isolation governs PROJECTS, not worktrees (operator revision 2026-08-31) - read AND write across worktrees freely; never smear one project's changes into another project's files
metadata:
  type: project
---

**Operator revision (2026-08-31), replacing the old write-isolation
rule:** worktrees are just checkouts - read AND write across them when
the work belongs there (e.g. installing components into the p29 editor,
fixing a tool in the main checkout). What must stay isolated is the
PROJECT - and the boundary is COARSE (operator, same day):
systems-and-blowups, martial-matters, both channels, all series = ONE
creative project (the Outreach Program); tools, doctrine, and
conventions flow freely across all of it. The real wall is Outreach vs
the BJJ REGISTRY project (WA JiuJitsu Registry / nationalbjjregistry) -
those two never smear into each other.

Still true: always search the MAIN checkout and other worktrees when
hunting for existing assets/tools (things live in many places); do not
rename/move another project's assets; worktrees are isolation, not
storage - durable output merges to main when its stage completes.

Related: [worktree-sprawl](worktree-sprawl.md), [recall-system](recall-system.md).

**2026-09-16 (P62):** every checkout has a row in `docs/WORKTREE-REGISTER.md`; read it at start. The four August worktrees are dormant (their unmerged counts on the rows); the parent's session cwd (sweet-villani) is one of them - its work lands in main. See [worktree-sprawl](worktree-sprawl.md).

**2026-09-24 (BOOM):** a harvest said "no frames on disk" for Bravos BOOM (`jx3Ll-GJtMY`) and P71 gated 8 items on a Gemini fetch - the video + transcript sat in the MAIN checkout's `scratch/` since 09-23. Before commissioning any fetch, `find` every checkout (incl. `scratch/`, repo root) for the id. Reading the real frames showed Gemini's timings off by up to ~11 s and two of its effects (a travelling ring, a phase slide) invented - a G-only witness is a lead, never a spec. Note: worktree sessions are blocked from writing the main checkout; write gitignored run output in the worktree.
