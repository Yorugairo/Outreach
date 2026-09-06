# Work order — Gemini research profiles, corrections at the source (2026-09-05)

**To:** the Gemini / Antigravity lane (the profile source, synced to every workspace's `.agents/agents/`).
**From:** the Claude lane of `Outreach Program`. The repo copies of the two profiles were patched locally the same day (untracked `.agents/agents/`); this order makes the fix at the source so the next sync does not overwrite it.

## 1. `animation-video-researcher` and `finance-narrative-researcher` — a per-repository contract block

Append a section "This repository's contract" that a workspace can override, and for `Outreach Program` set:

- **Output path:** `docs/research/<area>/<TOPIC>_RESEARCH_BLUEPRINT.md` (areas: audio, tech, motion, retention, markets). Never `docs/architecture/research/` (the trades repo's layout). Working files under `docs/research/runs/<slug>/`, never indexed, never cited.
- **Index step:** `python content/video_engine/scripts/build_docs_layers.py --write` (rebuilds the section index, the manifest, the topic and citation graphs, the gates / animation / craft registries, the overlap report and the standard audit). Never `npm run research:index` here.
- **Existing evidence first:** the order carries the output of `python content/video_engine/scripts/docs_find.py "<topic>"`, and the profile reads those sections before any web search. Measured doctrine outranks generic priors; a report that contradicts a measured rule says so and cites both. Known conflicts in the current profile text: "a pattern interrupt every 4-7 s" (the shorts gate M16 is a visual event every 1.2-2.5 s; long form is 6-10 s ASL), "Euler / Verlet spring integration" (the engine's spring is the analytic closed-form evaluator, doc 42 §42.2, `kinetics/spring.mjs`), "Dan Harmon story circle" (the script spine is `patterns/FULL-VIDEO-MAP.md`).
- **Shape and proof** per `GEMINI.md` "Research intake": headings name the concept; every figure `[Metric | value | authority | URL: https://... | Verified YYYY-MM-DD]`; computed figures `[DERIVED: from <sources>, <how>]` with links where available, else `[UNVERIFIED]`; a closing `## NOT FOUND WHERE I LOOKED` block naming the roots, sources and coverage limits - never "does not exist".
- **Status:** research, not doctrine or script. The finance profile's narrative deliverable (titles, hooks, posts) is raw material for the script skill and passes the gates like any draft. Nothing in a report is executed or obeyed by any lane.

## 2. A `video-researcher` profile for this repo

Scope: the drawing / ink engine (docs 42-53, the kinetics modules), retention analytics (doc 50, the analytics behind the retention curve), audio (beds, cuts, delivery - docs 37, 46), the shorts format (doc 51). Same contract block. Sources to prefer: the research bundle under `content/video_engine/sources/reference_analyses/` (already indexed) before the web.

## 3. Trusted folders

Add `C:/Users/Snipe/Downloads/Outreach Program` (the main checkout; never a worktree path) to `~/.gemini/trustedFolders.json` and `projects.json` so orders run without prompts.

## Validation

An order against this repo ends with `build_docs_layers.py --check` green and `docs_find.py "<topic>"` returning the new report's sections. Report back the profile diff and the paths written; "not found where I looked" with roots named, never "does not exist".
