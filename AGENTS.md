# AGENTS.md — Outreach Program / SEO Insights Platform

This file is the operating playbook for any agentic system (Hermes, Claude Code, Codex, OpenCode) working in this repo. It is the durable, always-loaded layer. Conditional workflows belong in skills, not here.

Read this file first, then read [`docs/AGENT_START_HERE.md`](docs/AGENT_START_HERE.md)
and its authoritative [`docs/agent-context/SKILL_ROUTER.md`](docs/agent-context/SKILL_ROUTER.md).
Load only the task route and PRP named there; do not preload the full docs tree.

---

## 1. Mission

Turn a pasted URL/domain into a **repeatable, evidence-backed SEO intelligence package** — not a one-off script run. The product is a `URL -> SEO Insight Run` engine with a stable data model, deterministic pipeline, repeatable scoring, and operator-facing artifacts.

Competitor intelligence, outbound automation, and generative content are **out of scope for v1**.

---

## 2–8. The SEO Insights Platform — moved to [`docs/AGENTS-SEO-PLATFORM.md`](docs/AGENTS-SEO-PLATFORM.md)

Architecture summary, the canonical `InsightRun`, the nine stages, the evidence-first definition of done, the verification commands, the artifact layout and the repo conventions live there unchanged. **Load it for any SEO-platform task, and whenever a doc cites its §2–§8** (the video-engine docs cite §5, the evidence-first definition of done, as universal). Moved 2026-09-05 to cut the always-loaded layer that every subagent dispatch re-pays. The rule that binds everywhere regardless: point to the artifact, not the claim.

---

## 9. Agent routing and durable execution → [`docs/runbooks/PRP_EXECUTION.md`](docs/runbooks/PRP_EXECUTION.md)

Complex, multi-slice, architectural, data-model, security or release work runs as a PRP under `.claude/PRPs/plans/`. The eight roles (`speedster`, `junior_developer`, `implementation_luna`, `architect_sol`, `explorer`, `docs_researcher`, `reviewer`, `release_steward`) are real agent types on both the Codex and Claude sides; the runbook's "Dispatch mapping", "Hand-off policy" and "Lane write sets" sections are the contract: the parent (Fable) owns architecture, integration, protected actions and the completion claim; delegated roles run on Opus 5 (`speedster` on Sonnet 5); every delegated diff is reviewed before integration; push requires current explicit user authorization; subagent summaries are not proof - artifact paths, run IDs, diffs or command output are.

## 10. Local code navigation → SigMap for code, `docs_find.py` for docs

`python scripts/sigmap_context.py query "<symbol or concept>" --top 5` ranks code paths (regenerates the index first; writes only the gitignored `.github/copilot-instructions.md`); `ast-grep run --lang <lang> --pattern ... <scope>` for structural sweeps; `rg` for literals; `python content/video_engine/scripts/docs_find.py "<term>"` for anything in the docs. Windows: set the workdir to the repo root and pass repo-relative paths (the native `rg` rejects MSYS absolute paths). SQZ compresses saved noisy output only, never test verdicts, hashes or security evidence.

## Content video engine (second workstream) — moved to [`docs/AGENTS-VIDEO-ENGINE.md`](docs/AGENTS-VIDEO-ENGINE.md)

This repo also hosts a faceless YouTube production operation (Money Physics, Building Money, Martial Matters). **Any agent doing script, visual, evidence or channel work loads that file first**; it names the two portable files (`docs/portable/DOCTRINE-CORE.md`, `docs/portable/OPERATOR-RULINGS.md`), the pipeline page, the three spine documents and the three binding rules (a dispatched work order is frozen; output stays quarantined until the operator approves; `approved` is the operator's and figures are never fabricated). Retrieval for any of it: `python content/video_engine/scripts/docs_find.py "<term>"`. Moved 2026-09-05 to cut the layer every dispatch re-pays.
