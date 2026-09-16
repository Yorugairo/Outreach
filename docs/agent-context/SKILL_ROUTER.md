# Skill And Agent Router

Status: current  
Last reviewed: 2026-09-14 (Updated from 2026-07-26)

The repository uses an allowlist-first skill policy. Load the smallest set that matches the task. Skills outside this router are disabled for this project by `scripts/configure_codex_skill_allowlist.py`.

---

## Active Skill Lanes

| Domain | Trigger / Task Intent | Recommended Skills & Tools |
|---|---|---|
| **Planning, TPM & Backlog** | Architecture planning, sprints, stress-testing plans, decision tradeoffs | `agentic-tpm-and-execution`, `prp-router`, `prp-plan`, `prp-implement`, `prp-status`, `scrum-master`, `grill-me`, `council` |
| **Deep Research & Intelligence** | Multi-source web research, academic papers, statutory citations, competitor teardowns | `research`, `deep-research`, `exa-search`, `tavily-web`, `web-research-agent` |
| **Visual Design & High-Taste Frontend** | Landing pages, brand design systems, Tailwind v4, Swiss/Minimalist UI, anti-slop audits | `design-engine`, `design-taste-frontend`, `high-end-visual-design`, `modern-design-frameworks`, `generative_ui` |
| **Content, Brand Voice & CRO** | High-conversion copy, voice profiles, Washington statutes, BJJ registry copy, CRO funnels | `brand-voice`, `content-engine`, `seo-content-writer`, `elite-cro-and-marketing` |
| **Technical SEO & pSEO Serving** | App Router metadata, JSON-LD schema, canonical equity, Core Web Vitals, registry read-models | `seo-engine`, `modern-seo-optimizations`, `registry-core` |
| **Video Production & Google Flow** | Google Flow zero-credit stills (Nano Banana Pro), 10s kinetic clips (Omni 1.1 Flash), Flow Worker | `google-flow-production`, `video-engine`, subagent `flow-asset-producer` |
| **Scene-Evidence Assembly & Motion** | Proprietary scene-evidence player (`scene-evidence-engine.mjs`), timeline compiler, Remotion, HyperFrames | `video-engine`, `evidence-motion-engine`, `motion-system`, `remotion-video-creation`, `remotion-to-hyperframes`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes` |
| **Video Scripting & Telemetry** | Script pattern kit, 6-phase architecture (P1-P6), strength loops, video watching/measurement | `script-writer`, `watch`, subagent `video-watcher` |
| **Backend, Database & Cloud** | Express/Next.js API routes, Postgres schemas, RLS, migrations, Supabase best practices | `backend-patterns`, `supabase`, `supabase-postgres-best-practices` |
| **Quality, Diagnostics & Perf** | Clean code review, SOLID/DRY guards, hard bug diagnosis, Core Web Vitals, E2E testing | `clean-code-guard`, `diagnosing-bugs`, `web-perf`, `e2e-testing` |
| **Structural Code Navigation** | Declared symbols, blast radius analysis, AST structural search and linting | `sigmap`, `ast-grep`, `ast-grep-outline` |
| **Context Control & Quarantine** | Minimizing token burn, subagent isolation, safe output compression | `strategic-compact`, isolated subagent delegation (`invoke_subagent`), `sqz` |
| **Operator Memory & Rulings** | Correction ledger, what was corrected and why, standing rulings | No skill — run `docs_find`, then `docs/operator-ledger/TRIAGE-DIGEST.md` and `docs/agent-memory/operator/` |
| **Effects & Motion Catalog** | Resolving named visual effects, cards, options, and proven beat recipes | No skill — run `python content/video_engine/scripts/effects_card.py "<name>"`, view `docs/EFFECTS-CATALOG.md` |

Release management, workspace cleanup, broad infrastructure, unrelated industry operations, and generic agent-framework skills are disabled by default. Their durable safety rules remain in `AGENTS.md`; activate a specific skill manually only when a task genuinely requires it.

---

## Tool Routing

1. **Ranked Code Navigation:** Use `python scripts/sigmap_context.py ask "<question>"` or `scripts/sigmap_context.py query "<symbol>"` before broad code exploration.
2. **Exact Literal Search:** Use `rg` from the repository root with repo-relative paths (Windows native `rg` rejects MSYS absolute paths).
3. **Structural AST Search:** Use `ast-grep outline` before opening large files; use `ast-grep run --lang <lang> --pattern ...` for structural sweeps.
4. **Docs & Doctrine Search:** Use `python content/video_engine/scripts/docs_find.py "<term>"` before searching the web for facts already in the repo.
5. **Output Compression:** Use `sqz compress --mode safe` on noisy test logs or command dumps. Never compress hashes, exact test verdicts, or security evidence.
6. **Rendered UI & Interaction QA:** Use Chrome DevTools MCP or Playwright for live interaction testing.

---

## Named Agent Routing

- **Parent Task (Orchestrator):** Owns the critical path, architecture, shared-file integration, protected actions, human gates, final verification, and completion truth. Never drives interactive browser loops or status polling directly in the primary context.
- **`flow-asset-producer`:** Isolated Google Flow worker subagent ([`.agents/agents/flow-asset-producer.md`](file:///c:/Users/Snipe/Downloads/Outreach%20Program/.agents/agents/flow-asset-producer.md)). Dispatched via `invoke_subagent` for executing asset generation work orders under strict context quarantine. Runs on the `flash` model tier with skills `google-flow-production` and `video-engine`. Drives MCP/CDP tools, executes `prepare_props.py --check`, and returns strictly a compact receipt JSON.
- **`animation-video-researcher`:** Specialized research agent for animation math, drawing engine architecture, video production psychology, literary pacing, and programmatic video automation.
- **`finance-narrative-researcher`:** Specialized financial intelligence agent for gathering rigorously cited raw numbers and translating them into high-tension video narratives.
- **`video-researcher`:** Specialized research agent for the drawing/ink engine, retention analytics, audio delivery, and the shorts format.
- **`video-watcher`:** Dedicated reference video observation agent using the `/watch` skill. Extracts scenes, frames, and audio transcripts, returning one structured CSV table.
- **`code-reviewer` / Language Reviewers (`react-reviewer`, `python-reviewer`, `typescript-reviewer`, `database-reviewer`):** Expert code review specialists enforcing project contracts, security, and performance.
- **`speedster`:** Deterministic microtasks only: one-line fixes, mechanical updates, exact discovery, formatting, focused tests, or narrow commands.
- **`junior_developer`:** Scoped implementation and targeted bugfixes with exact files or symbols, a small read/write set, and focused validation.
- **`implementation_luna`:** Bounded moderate implementation with an explicit write set, acceptance criteria, tests, and validation.
- **`architect_sol`:** Repository research and implementation-ready PRP drafting.
- **`explorer`:** Read-only evidence gathering.
- **`docs_researcher`:** Read-only API, framework, and release-note research.
- **`release_steward`:** Mechanical staging and commit work after review. May push only when current explicit user authorization is provided.

Use the smallest capable role. Use `fork_turns: "none"` for narrow worker dispatches. Do not parallelize overlapping writes. Migrations, auth/security, payments, deploys, shared contracts, and external actions remain parent-owned.

Full delegation rules live in [`../runbooks/PRP_EXECUTION.md`](../runbooks/PRP_EXECUTION.md).

