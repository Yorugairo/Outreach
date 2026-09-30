# Skill And Agent Router

Status: current  
Last reviewed: 2026-09-14 (Updated from 2026-07-26)

The repository uses an allowlist-first skill policy. Load the smallest set that matches the task. Skills outside this router are disabled for this project by `scripts/configure_codex_skill_allowlist.py`.

---

## Active Skill Lanes

| Domain | Trigger / Task Intent | Recommended Skills & Tools |
|---|---|---|
| **Planning, PRPs & Backlog** | Use `agentic-tpm-and-execution` only to frame unplanned multi-slice work; use `prp-implement` directly for an approved PRP. Architecture, backlog, and decision work use their matching skills. | `agentic-tpm-and-execution`, `prp-router`, `prp-plan`, `prp-implement`, `prp-status`, `scrum-master`, `grill-me`, `council` |
| **Deep Research & Intelligence** | Multi-source web research, academic papers, statutory citations, competitor teardowns | `research`, `deep-research`, `exa-search`, `tavily-web`, `web-research-agent` |
| **Visual Design & High-Taste Frontend** | Landing pages, brand design systems, Tailwind v4, Swiss/Minimalist UI, anti-slop audits | `design-engine`, `design-taste-frontend`, `high-end-visual-design`, `modern-design-frameworks`, `generative_ui` |
| **Content, Brand Voice & CRO** | High-conversion copy, voice profiles, Washington statutes, BJJ registry copy, CRO funnels | `brand-voice`, `content-engine`, `seo-content-writer`, `elite-cro-and-marketing` |
| **Technical SEO & pSEO Serving** | App Router metadata, JSON-LD schema, canonical equity, Core Web Vitals, registry read-models | `seo-engine`, `modern-seo-optimizations`, `registry-core` |
| **Video Production & Google Flow** | Google Flow zero-credit stills (Nano Banana Pro), 10s kinetic clips (Omni 1.1 Flash), Flow Worker | `google-flow-production`, `video-engine`, subagent `flow-asset-producer` |
| **Scene-Evidence Assembly & Motion** | Proprietary scene-evidence player (`scene-evidence-engine.mjs`), timeline compiler, Remotion, HyperFrames | `video-engine`, `evidence-motion-engine`, `motion-system`, `remotion-video-creation`, `remotion-to-hyperframes`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes` |
| **Video Scripting & Telemetry** | Script pattern kit, 6-phase architecture (P1-P6), strength loops, video watching/measurement | `script-writer`, `watch`, subagent `video-watcher` |
| **Backend, Database & Cloud** | Express/Next.js API routes, Postgres schemas, RLS, migrations, Supabase best practices | `backend-patterns`, `supabase`, `supabase-postgres-best-practices` |
| **Quality, Diagnostics & Perf** | Code review and hard bug diagnosis, Core Web Vitals, E2E testing | `diagnosing-bugs`, `web-perf`, `e2e-testing` |
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

### Codex model policy — operator updates through 2026-09-29

| Work | Default | After three consecutive substantive task failures |
| --- | --- | --- |
| Parent default and implementation/execution: speedster, junior_developer, implementation_luna, release_steward | gpt-6-luna / max | Sol xhigh diagnoses and writes a targeted order; Luna may retry setup/spec failures, or execution_sol implements when novel reasoning or a further miss requires it |
| Larger implementation, refactors, high-risk source changes, less structured orders: lead_developer | gpt-6.1-sol / high | Direct route by scope/risk; after three substantive failures, execution_sol diagnoses at xhigh |
| Planning/architecture: architect_sol, or a parent already running Sol xhigh | gpt-6.1-sol / xhigh | Luna parent briefs and reviews the draft, retaining final architecture decisions and human gates; Astra high is an optional parent-directed step-up after three substantive Sol failures on one bounded task |
| Review and scoped quick fixes: reviewer | gpt-6.1-sol / high | Repair reviewed paths within existing ownership; parent or fresh independent review checks repairs before integration. After three substantive review failures, seek Sol-xhigh diagnosis or re-scope |
| Professional work, research/exploration, computer use | gpt-6-luna / max | Sol xhigh diagnoses and directs a targeted Luna retry for setup/spec failures, or professional_sol executes when needed |

These model IDs are explicit pins. Sol roles use GPT-6.1 Sol and Luna roles use
GPT-6 Luna as of 2026-09-29; they do not automatically move to the newest release
in a family. Upgrade the role TOML, escalation references, and
`scripts/check_codex_model_routing.py` together when the operator requests a
later model. Preserve each workload's reasoning level and permissions.

Use `professional_worker` for bounded artifact work and `computer_use_worker` for browser/computer execution. The Luna parent retains integration, human gates, and protected actions. The reviewer may repair clear local defects in the reviewed paths unless its order is explicitly read-only or narrows the repair set. Parent review or a fresh independent review checks those repairs before integration; the reviewer cannot approve its own repairs. Explorer and docs_researcher remain read-only. The parent records tool errors separately from substantive failures against a stable task and acceptance criteria. A successful tool call resets the tool-error streak; three consecutive failed tool calls trigger local inspection and a corrected retry, **not** a Sol handoff. Three consecutive substantive Luna attempts, or three substantive lead_developer attempts at Sol high, that fail the bounded acceptance trigger Sol xhigh diagnosis; respawning does not erase those failures. Sol may write one materially corrected, source-linked order for a targeted Luna retry under the same ledger and permissions, and implements only when that retry still misses, novel reasoning is needed, or risk makes another retry inappropriate. Preserve evidence, outputs, live handles and exact permissions; reconcile uncertain external writes before retrying. Escalation never adds approval or write authority. This is an orchestrator instruction, not a native TOML retry setting.

After three consecutive substantive Sol-xhigh failures on that same bounded task, the parent may use `gpt-6-astra` / `high` for independent diagnosis. Ask Astra to present a viable alternative if one exists, including a different task framing or architecture when justified, rather than confining it to another pass at the failed approach. This is optional, not automatic. Check that the acceptance criteria, failure count and evidence are stable and that the real blocker is not a missing operator decision or external dependency. Use `execution_astra` or `professional_astra` when loaded; otherwise dispatch a generic agent with explicit model/effort and the full prior role contract. Astra may propose wider work, but execution retains prior read-only/write boundaries and approvals until the parent authorizes a revised order. Preserve live handles. Tool-call failures alone never trigger this step-up.

Loaded roles can retain stale pins for this session: reload configuration or use an available generic role with explicit model/effort and the complete original role contract. Do not claim active agents switched models. This policy supersedes older OpenAI model assignments only; Claude/Gemini definitions and their provider routing remain unchanged.

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
- **`lead_developer` (Codex):** GPT-6.1 Sol/high for larger implementation, refactors, high-risk source changes, and less structured orders. Dispatch directly by scope and risk; no prior Luna failure is required. Missing product decisions or unresolved architecture return to the parent/architect_sol.
- **`reviewer` (Codex):** GPT-6.1 Sol/high review and quick repairs within the reviewed paths. Check active ownership; preserve explicit read-only orders. Broad implementation routes to implementation_luna or lead_developer. Return each repair diff for parent or fresh independent review before integration.
- **`architect_sol`:** Repository research and implementation-ready PRP drafting.
- **`explorer`:** Read-only evidence gathering.
- **`docs_researcher`:** Read-only API, framework, and release-note research.
- **`release_steward`:** Mechanical staging and commit work after review. May push only when current explicit user authorization is provided.

Use the smallest capable role. Use `fork_turns: "none"` for narrow worker dispatches. Do not parallelize overlapping writes. Migrations, auth/security, payments, deploys, shared contracts, and external actions remain parent-owned.

Full delegation rules live in [`../runbooks/PRP_EXECUTION.md`](../runbooks/PRP_EXECUTION.md).

