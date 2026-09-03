# Video Engine & Outreach Deterministic Agent Harness Eval Suite

This evaluation suite benchmarks autonomous agent workflows, Google Flow batch generation, Remotion composition invariants, and evidence choreography across 5 frozen engineering scenarios.

---

## Benchmark Scenarios

| # | Fixture Name | Category | Evaluation Target |
| :- | :--- | :--- | :--- |
| **01** | `01-google-flow-manifest-validation.ts` | Media & Flow Driver | Validates batch JSON schemas, reference chaining, and SHA-256 digests. |
| **02** | `02-remotion-timeline-invariants.ts` | Remotion React | Validates 60fps/30fps spring tokens, canvas constraints, and audio sync rules. |
| **03** | `03-evidence-dock-choreography.ts` | Motion & Evidence | Enforces Ruling B1-B3 (rebuilt charts, washi dock sizing, and 0.5s board wipe). |
| **04** | `04-script-humanizer-validation.ts` | Scripting & Brand | Enforces anti-AI Humanizer quality gates and retention hooks. |
| **05** | `05-disk-as-bus-isolation.ts` | Agentic Standards | Verifies subagent research spike isolation and zero main-context token bloat. |

---

## Running the Evals

```bash
npx tsx evals/harness-runner.ts
```
