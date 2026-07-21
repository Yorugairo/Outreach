# Run Orchestration Scaffolding Notes

Prepared: 2026-07-07

## What was added

### Domain models
- `src/models.py`
  - `SEOTarget`
  - `InsightRun`
  - `RunStageEvent`
  - `DiscoveredAsset`
  - `PageRecord`
  - `InsightReport`

### Repository layer
- `src/repositories/base.py`
- `src/repositories/file_repository.py`

Current implementation is file-backed so the orchestration flow can be exercised immediately without waiting for a live Postgres repository implementation.

### Service layer
- `src/services/target_intake_service.py`
- `src/services/crawl_discovery_service.py`
- `src/services/page_analysis_service.py`
- `src/services/search_intelligence_service.py`
- `src/services/reporting_service.py`

### Orchestrator
- `src/pipeline.py`
- `scripts/run_insight_pipeline.py`

## Current run lifecycle covered
- normalizing_target
- discovering_sitemaps
- fetching_pages
- pulling_search_intelligence
- scoring
- assembling_report

## Current persistence behavior
Artifacts are written under:
- `artifacts/seo_insight_runs/targets/`
- `artifacts/seo_insight_runs/runs/<run_id>/run.json`
- `artifacts/seo_insight_runs/runs/<run_id>/events/`
- `artifacts/seo_insight_runs/runs/<run_id>/assets/`
- `artifacts/seo_insight_runs/runs/<run_id>/pages/`
- `artifacts/seo_insight_runs/runs/<run_id>/reports/`

This is scaffolding only: the file-backed repository should later be replaced or paralleled by a Postgres-backed repository implementing the same interface.

## Smoke test
The pipeline was executed against `python.org` in quick mode.

Expected outputs:
- run JSON with completed status
- stage event files
- discovered robots/sitemap assets
- page records
- final report JSON + markdown

Initial smoke test found and fixed a real issue:
- `scripts/run_insight_pipeline.py` could not import `src` when executed directly
- fixed by prepending the project root to `sys.path`
- dataclass scorecard serialization initially used `__dict__`
- fixed by serializing with `dataclasses.asdict(...)`

## Known limitations
- no Postgres repository yet
- search intelligence currently uses a minimal DataForSEO connectivity step when credentials exist
- scorecard logic is intentionally basic scaffolding
- page classification is heuristic and lightweight
