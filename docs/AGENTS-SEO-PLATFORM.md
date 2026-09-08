# AGENTS — SEO Insights Platform (sections 2–8)

Moved out of the always-loaded `AGENTS.md` on 2026-09-05 so video-engine sessions and every subagent dispatch stop paying for it. Load this file for any SEO-platform work (pipeline, stages, artifacts, verification commands, repo conventions). Nothing here changed.

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

