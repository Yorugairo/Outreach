from __future__ import annotations

import os
import secrets
from dataclasses import replace
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.config import AppConfig, ApprovalPolicy, load_config
from src.orchestrator import InsightRunOrchestrator
from src.repositories.base import InsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository


class RunCreateRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2048)
    mode: Literal["quick", "standard", "full"] = "standard"
    max_pages: int = Field(default=5, ge=1, le=100)
    approve_paid_enrichment: bool = False


class RerunRequest(BaseModel):
    stage: str
    max_pages: int = Field(default=5, ge=1, le=100)


class ResumeRequest(BaseModel):
    max_pages: int = Field(default=5, ge=1, le=100)


class RecoveryRequest(BaseModel):
    worker_id: str = Field(default="api-reaper", min_length=1, max_length=100)
    reason: str = Field(default="stale lease recovery", min_length=1, max_length=500)


def create_app(
    *,
    repository: InsightRepository | None = None,
    artifact_root: str | Path | None = None,
    config: AppConfig | None = None,
    api_key: str | None = None,
    environment: str | None = None,
) -> FastAPI:
    root = Path(artifact_root or os.getenv("SEO_INSIGHTS_ARTIFACT_ROOT", "artifacts/seo_insight_runs"))
    runtime_environment = (environment or os.getenv("SEO_INSIGHTS_ENV", "development")).lower()
    configured_api_key = api_key if api_key is not None else os.getenv("SEO_INSIGHTS_API_KEY")
    if runtime_environment == "production" and not configured_api_key:
        raise RuntimeError("SEO_INSIGHTS_API_KEY is required in production")

    active_repository = repository or SQLiteInsightRepository(
        os.getenv("SEO_INSIGHTS_DATABASE_PATH", str(root / "seo-insights.db")),
        artifact_root=root,
    )
    base_config = config or load_config()
    base_orchestrator = InsightRunOrchestrator(active_repository, config=base_config, artifact_root=root)

    app = FastAPI(
        title="SEO Insights Platform API",
        version="1.0.0",
        docs_url=None if runtime_environment == "production" else "/docs",
        redoc_url=None,
    )
    app.state.repository = active_repository
    app.state.artifact_root = root
    app.state.environment = runtime_environment

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
        )
        return response

    def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not configured_api_key or not x_api_key or not secrets.compare_digest(x_api_key, configured_api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or missing API key",
            )

    auth = Depends(require_api_key)

    def orchestrator_for(approve_paid_enrichment: bool = False) -> InsightRunOrchestrator:
        request_config = replace(
            base_config,
            approval=ApprovalPolicy(allow_paid_api_calls=approve_paid_enrichment),
        )
        return InsightRunOrchestrator(active_repository, config=request_config, artifact_root=root)

    def run_or_404(run_id: str):
        run = active_repository.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"run {run_id} not found")
        return run

    @app.get("/healthz")
    def health() -> dict:
        database = active_repository.health() if hasattr(active_repository, "health") else {"status": "ok", "backend": "file"}
        return {
            "status": "ok" if database.get("status") == "ok" else "degraded",
            "environment": runtime_environment,
            "database": database,
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> HTMLResponse:
        dashboard_path = Path(__file__).resolve().parent / "static" / "dashboard.html"
        if not dashboard_path.exists():
            return HTMLResponse("<main><h1>SEO Insights Platform</h1><p>Dashboard is not installed.</p></main>")
        return HTMLResponse(dashboard_path.read_text(encoding="utf-8"))

    @app.get("/api/runs", dependencies=[auth])
    def list_runs(limit: int = Query(default=50, ge=1, le=200)) -> dict:
        return {"runs": [run.to_dict() for run in active_repository.list_runs(limit=limit)]}

    @app.post("/api/runs", status_code=201, dependencies=[auth])
    def create_run(payload: RunCreateRequest) -> dict:
        orchestrator = orchestrator_for(payload.approve_paid_enrichment)
        run = orchestrator.start(payload.url, mode=payload.mode, max_pages=payload.max_pages)
        return {"run": run.to_dict(), "validation": orchestrator.validate(run.id)}

    @app.post("/api/runs/recover-stale", dependencies=[auth])
    def recover_stale(payload: RecoveryRequest) -> dict:
        recovered = base_orchestrator.recover_stale_runs(
            worker_id=payload.worker_id,
            reason=payload.reason,
        )
        return {"recovered_run_ids": recovered, "count": len(recovered)}

    @app.get("/api/runs/{run_id}", dependencies=[auth])
    def get_run(run_id: str) -> dict:
        run = run_or_404(run_id)
        return {"run": run.to_dict(), "status": base_orchestrator.status(run_id)}

    @app.get("/api/runs/{run_id}/validation", dependencies=[auth])
    def validate_run(run_id: str) -> dict:
        run_or_404(run_id)
        return base_orchestrator.validate(run_id)

    @app.get("/api/runs/{run_id}/report", dependencies=[auth])
    def get_report(run_id: str) -> dict:
        run_or_404(run_id)
        report = active_repository.get_report(run_id, "v1")
        if report is None:
            raise HTTPException(status_code=404, detail="report v1 not found")
        return report.to_dict()

    @app.post("/api/runs/{run_id}/resume", dependencies=[auth])
    def resume_run(run_id: str, payload: ResumeRequest) -> dict:
        run_or_404(run_id)
        run = base_orchestrator.resume(run_id, max_pages=payload.max_pages)
        return {"run": run.to_dict(), "validation": base_orchestrator.validate(run_id)}

    @app.post("/api/runs/{run_id}/rerun", dependencies=[auth])
    def rerun_stage(run_id: str, payload: RerunRequest) -> dict:
        run_or_404(run_id)
        try:
            run = base_orchestrator.rerun_stage(run_id, payload.stage, max_pages=payload.max_pages)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"run": run.to_dict(), "validation": base_orchestrator.validate(run_id)}

    @app.post("/api/runs/{run_id}/approve-paid-enrichment", dependencies=[auth])
    def approve_paid_enrichment(run_id: str, payload: ResumeRequest) -> dict:
        run_or_404(run_id)
        if not base_config.dataforseo.configured:
            raise HTTPException(status_code=409, detail="DataForSEO credentials are not configured")
        approved_orchestrator = orchestrator_for(True)
        run = approved_orchestrator.rerun_stage(
            run_id,
            "pulling_search_intelligence",
            max_pages=payload.max_pages,
        )
        return {"run": run.to_dict(), "validation": approved_orchestrator.validate(run_id)}

    @app.get("/api/diff", dependencies=[auth])
    def diff_runs(base_run_id: str, comparison_run_id: str) -> dict:
        try:
            return base_orchestrator.diff_runs(base_run_id, comparison_run_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app
