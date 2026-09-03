# 🏛️ 2026 Agentic Engineering Standards & Harness System

A portable, deterministic operating harness for autonomous AI coding agents (Antigravity, Claude Code, Codex, Cursor).

---

## What This Harness Solves

| Traditional Agent Pain Point | 2026 Harness Solution |
| :--- | :--- |
| **Context Window Exhaustion:** Agents dump massive logs, test runs, and web scrapes into main prompt. | **"Disk-as-Bus" Isolation:** Ephemeral subagents write raw data to `docs/research/runs/` and return only 3-bullet summaries. |
| **Silent Invariant Violations:** Agents write invalid SQL joins or bypass multi-tenant security. | **Dual-Layer AST-Grep Gating:** Instant syntax-tree rules in `.ast-grep/rules/` block violations in <50ms. |
| **No Regression Defense:** Prompts or models change, breaking agentic problem-solving. | **Deterministic `evals/` Bench:** 5 frozen task journey fixtures benchmark autonomous repair rates. |
| **Session Restart Loss:** Context drops or server restarts wipe in-progress task state. | **Intent-Driven Save-Stating:** Structured intention headers preserve in-flight logic. |
| **Multi-Agent Lockups:** Concurrent agents write to shared SQLite simultaneously. | **Single-Coordinator Writer Pattern:** Subagents use isolated files; only coordinator writes to DB. |

---

## Stamping Onto Any Repository

Run the self-contained stamping CLI:

```bash
node scripts/harness-stamp.mjs --target /path/to/target-repo --profile [full|web|video|api]
```

### Profiles Available
- **`full`** — All 33 curated skills, full subagent library, AST-grep gates, and 5-journey eval suite.
- **`web`** — Web, Next.js, Supabase, Design Engine, Content Engine, and Deep Grilling.
- **`video`** — Remotion, Google Flow driver, VideoDB, Motion System, Evidence Motion, and Taste.
- **`api`** — Backend, Database optimization, Clean Code, and Subagent Research.

---

## Documentation for Agents

- **[Agent Self-Evaluation & Adoption Guide](./AGENT_SELF_EVALUATION_GUIDE.md)** — Step-by-step instructions for an agent in an external repo to evaluate and adopt this harness.
- **[Harness Evaluation Checklist](./HARNESS_EVALUATION_CHECKLIST.md)** — Diagnostic rubric for scoring current repository readiness.
