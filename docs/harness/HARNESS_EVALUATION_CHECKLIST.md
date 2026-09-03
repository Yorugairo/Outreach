# 📋 Repository Agentic Maturity Checklist

Use this scorecard to rate any codebase's agentic readiness before and after adopting the 2026 Harness.

---

## Maturity Scorecard (100 pts Total)

| Dimension | Evaluation Criteria | Max Pts | Target |
| :--- | :--- | :---: | :---: |
| **1. Tool & Context Efficiency** | Subagents use Disk-as-Bus (`docs/research/runs/`); context token consumption is bounded under 500 tokens per subagent return. | 20 pts | 20 |
| **2. Deterministic Quality Gating** | AST-Grep (`sgconfig.yml` + `.ast-grep/rules/`) runs in <50ms and deterministically catches structural violations. | 20 pts | 20 |
| **3. Continuous Evaluation Bench** | Frozen task journey suite in `evals/` tests autonomous error recovery, tenant RLS, and ledger integrity. | 20 pts | 20 |
| **4. Durable Project Memory** | Repository maintains `.claude/memory.md` and active context tracking (`AGENTS.md` / `GEMINI.md`). | 20 pts | 20 |
| **5. Fault Tolerance & Safety** | Intent-driven save-stating comments on edits; mutating commands enforce `--dry-run` previews; single-coordinator SQLite writer. | 20 pts | 20 |

---

## Grading Scale
- **80 – 100 pts:** 🟢 **Production Grade 2026 Agentic Harness** (Deterministic, zero-bloat, resilient).
- **50 – 79 pts:** 🟡 **Partial Harness** (Subject to prompt drift and occasional context exhaustion).
- **< 50 pts:** 🔴 **Unstructured Legacy Agent** (High token costs, hallucination risks, silent failures).
