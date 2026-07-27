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

## 2. Architecture summary

- **Run-centric**: everything is anchored to an `InsightRun` (see `src/models.py`).
- **Repository abstraction**: all persistence goes through `InsightRepository` (`src/repositories/base.py`). Current implementation is file-backed (`src/repositories/file_repository.py`); a Postgres/Supabase backend is a later swap behind the same Protocol.
- **Service layer**: each pipeline stage is a service under `src/services/`.
- **Single orchestrator**: `InsightRunPipeline` (`src/pipeline.py`) sequences the stages and records stage events.
- **One entrypoint**: `scripts/run_insight_pipeline.py` (CLI).

---

## 3. Canonical run object

`InsightRun` (`src/models.py`) is the core execution unit.

Stages are defined in `src/pipeline.py` as `DEFAULT_STAGES`:

```python
DEFAULT_STAGES = [
    "normalizing_target",
    "discovering_sitemaps",
    "fetching_pages",
    "pulling_search_intelligence",
    "scoring",
    "scoring_technical_health",
    "scoring_ai_readiness",
    "scoring_conversion_readiness",
    "assembling_report",
]
```

Every stage emits a `RunStageEvent` (`src/models.py`) with `stage_name`, `status`, `started_at`, `completed_at`, and `output_summary`. Events are persisted as JSON files under `artifacts/seo_insight_runs/runs/<run_id>/events/`.

---

## 4. Stage definitions

| Stage | Owner service | Output |
|---|---|---|
| `normalizing_target` | `TargetIntakeService` | `SEOTarget` (normalized domain/URL) |
| `discovering_sitemaps` | `CrawlDiscoveryService` | sitemap inventory + candidate page URLs + `DiscoveredAsset` records |
| `fetching_pages` | `PageAnalysisService` | `PageRecord` per analyzed URL |
| `pulling_search_intelligence` | `SearchIntelligenceService` | keyword/SERP enrichment (skips if DataForSEO unconfigured) |
| `scoring` | `ScorecardService` | metrics + `overall_score` |
| `scoring_technical_health` | `TechnicalSEOHealthService` | issue-density Technical SEO Health v2 + Evidence Confidence |
| `scoring_ai_readiness` | `AIReadinessV3Service` | separate versioned AEO/GEO/AIO readiness output |
| `scoring_conversion_readiness` | `ConversionReadinessService` | deterministic, vertical-aware conversion evidence |
| `assembling_report` | `ReportAssemblyService` | immutable v1/v2, technical, AI, and conversion reports |

---

## 5. Definition of done (evidence-first)

A run is **not** "done" until artifacts exist on disk and are readable. The agent must verify, not assert.

Before reporting a run complete, confirm ALL of:

- [ ] `run.json` exists at `artifacts/seo_insight_runs/runs/<run_id>/run.json` with `status == "completed"`
- [ ] All 9 v5 stage events exist under `.../events/` with `status == "completed"` (legacy/v3/v4 contracts retain 6/7/8)
- [ ] `reports/v1.*`, `reports/v2.*`, `reports/seo-health-v2.*`, `reports/ai-v3.*`, and `reports/conversion-v1.*` exist for v5 runs
- [ ] `summary` on the run contains `overall_score`
- [ ] If DataForSEO was configured, search intelligence output is present; if not, the skip is recorded in the stage event

For any other task type in this repo, apply the same rule: **point to the artifact, not the claim.**

---

## 6. Verification commands

Run a quick pipeline and inspect output:

```bash
cd "C:/Users/Snipe/Downloads/Outreach Program"
python scripts/run_insight_pipeline.py python.org --mode quick --max-pages 5
```

Inspect a completed run's status:

```bash
python - <<'PY'
import json, glob
from pathlib import Path
runs = sorted(Path("artifacts/seo_insight_runs/runs").glob("*/run.json"))
for p in runs[-3:]:
    data = json.loads(p.read_text())
    print(data["id"], data["status"], data.get("summary", {}).get("overall_score"))
PY
```

List stage events for the most recent run:

```bash
python - <<'PY'
import json, glob
from pathlib import Path
runs = sorted(Path("artifacts/seo_insight_runs/runs").glob("*/run.json"))
latest = runs[-1].parent
for ev in sorted((latest / "events").glob("*.json")):
    e = json.loads(ev.read_text())
    print(e["stage_name"], e["status"])
PY
```

---

## 7. Artifact layout

```
artifacts/seo_insight_runs/
  targets/<target_id>.json          # normalized target anchors
  runs/<run_id>/
    run.json                        # run state + summary
    events/<ts>_<stage>_<status>.json
    assets/<asset_id>.json          # discovered sitemap/images
    pages/<page_id>.json            # per-page SEO evidence
    reports/v1.json                 # structured report
    reports/v1.md                   # operator-readable report
    reports/v2.json                 # commercial evidence report
    reports/v2.md
    reports/seo-health-v2.json      # issue-density technical health
    reports/seo-health-v2.md
    reports/ai-v3.json              # current AI Readiness evidence
    reports/ai-v3.md
    reports/conversion-v1.json      # deterministic conversion readiness
    reports/conversion-v1.md
```

Never hand-edit artifacts manually. They are produced by the repository layer only.

---

## 8. Repo conventions

- **Python**: run with the 3.11 interpreter. If a venv exists use it; otherwise `python` resolves to 3.11.15 on this host.
- **Imports**: project root is added to `sys.path` in `scripts/run_insight_pipeline.py`. Services import as `from src...`.
- **Config**: loaded via `src/config.load_config()`; secrets via `.env` (`docs/local.env` is a local example — keep real secrets out of commits).
- **Models**: `src/models.py` dataclasses use `slots=True` and `to_dict()`. Do not add constructors that break `to_dict()` serialization.
- **Stages**: when adding a stage, update `DEFAULT_STAGES` in `src/pipeline.py` AND record start/complete events via `_stage_start`/`_stage_complete`.
- **No silent skips**: if a stage is skipped or degraded, the stage event `output_summary` must say why.

---

## 9. Agent routing and durable execution

Use [`docs/runbooks/PRP_EXECUTION.md`](docs/runbooks/PRP_EXECUTION.md) for
complex, multi-slice, architectural, data-model, security, or release work.
Active plans live under `.claude/PRPs/plans/` as agent-neutral durable state.

- The parent task owns architecture, integration, protected actions, and the
  final completion claim.
- `speedster` handles exact deterministic microtasks only.
- `junior_developer` handles bounded limited implementation, scoped fixes,
  explicit line changes, and small reads/writes.
- `implementation_luna` handles bounded moderate implementation with tests.
- `architect_sol` researches and drafts implementation-ready PRPs.
- `explorer` performs read-only repository tracing and evidence gathering.
- `docs_researcher` performs read-only primary-documentation verification.
- `reviewer` performs read-only correctness, security, and regression review.
- `release_steward` performs reviewed Git mechanics only; push still requires
  current explicit user authorization.
- Keep write sets disjoint and review delegated diffs before integration.
- Subagent summaries are not proof. Require artifact paths, run IDs, diffs, or
  command output.
- Keep task state in the PRP, not in transcripts or this file.

---

## 10. Local code-navigation workflow

Use the portable wrapper from the repository root when a named symbol, service, or architecture path needs ranked evidence:

```bash
python scripts/sigmap_context.py build
python scripts/sigmap_context.py query "sitemap discovery" --top 5
python scripts/sigmap_context.py evidence "CrawlDiscoveryService" --markdown
```

Every wrapper command regenerates the local index first with `--no-track`. Its configuration writes only the gitignored `.github/copilot-instructions.md`; it does not modify `AGENTS.md` or `CLAUDE.md`, register MCP clients, or invoke Codex/Claude adapters.

Route questions to the smallest suitable tool:

- **SigMap**: declared symbols, ranked architecture discovery, and evidence packs.
- **ast-grep**: structural patterns and exact call-site sweeps. Always set `--lang`, use a narrow pattern, and scope it to repo-relative paths; one-shot `run` needs no `sgconfig.yml`, while reusable configured rules use `scan`.
- **Text search** (`git grep` or `search_files`): literals, configuration keys, SQL, docs, and test descriptions.
- **SQZ**: compress noisy command output or logs only after saving the original evidence. Use `sqz compress --mode safe --verify --no-cache --cmd <producer>`; do not compress hashes, exact test verdicts, security evidence, or small outputs, and never use SQZ as a search or correctness tool.

Windows path rule: set the command/tool workdir to the exact repository root and pass `.` or repo-relative paths. The native Windows `rg` used by `search_files` does not accept MSYS-style absolute paths such as `/c/Users/...`; if an absolute-path search fails, retry from the exact workdir with a relative path before concluding that nothing matched.

Bound a structural sweep and preserve its raw output before optional compression:

```bash
ast-grep run --lang python --pattern 'class $C: $$$BODY' src/services --json=stream > .context/ast-grep-classes.jsonl
sqz compress --mode safe --verify --no-cache --cmd ast-grep < .context/ast-grep-classes.jsonl
```
