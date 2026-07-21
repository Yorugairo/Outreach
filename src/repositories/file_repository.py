from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any

from src.models import DiscoveredAsset, InsightReport, InsightRun, PageRecord, RunStageEvent, SEOTarget


class FileBackedInsightRepository:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.targets_dir = self.root / "targets"
        self.runs_dir = self.root / "runs"
        self.targets_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def upsert_target(self, target: SEOTarget) -> SEOTarget:
        path = self.targets_dir / f"{target.id}.json"
        path.write_text(json.dumps(target.to_dict(), indent=2), encoding="utf-8")
        return target

    def create_run(self, run: InsightRun) -> InsightRun:
        run_dir = self._run_dir(run.id)
        for subdir in ["events", "assets", "pages", "reports"]:
            (run_dir / subdir).mkdir(parents=True, exist_ok=True)
        self._write_json(run_dir / "run.json", run.to_dict())
        return run

    def update_run(self, run: InsightRun) -> InsightRun:
        self._write_json(self._run_dir(run.id) / "run.json", run.to_dict())
        return run

    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent:
        safe_stamp = self._safe_filename(event.created_at)
        safe_stage = self._safe_filename(event.stage_name)
        safe_status = self._safe_filename(event.status)
        path = self._run_dir(event.insight_run_id) / "events" / f"{safe_stamp}_{safe_stage}_{safe_status}.json"
        self._write_json(path, event.to_dict())
        return event

    def save_discovered_asset(self, asset: DiscoveredAsset) -> DiscoveredAsset:
        path = self._run_dir(asset.insight_run_id) / "assets" / f"{asset.id}.json"
        self._write_json(path, asset.to_dict())
        return asset

    def save_page_record(self, page: PageRecord) -> PageRecord:
        path = self._run_dir(page.insight_run_id) / "pages" / f"{page.id}.json"
        self._write_json(path, page.to_dict())
        return page

    def save_report(self, report: InsightReport) -> InsightReport:
        run_dir = self._run_dir(report.insight_run_id)
        self._write_json(run_dir / "reports" / f"{report.report_version}.json", report.to_dict())
        if report.export_markdown:
            (run_dir / "reports" / f"{report.report_version}.md").write_text(report.export_markdown, encoding="utf-8")
        return report

    def get_run(self, run_id: str) -> "InsightRun | None":
        path = self._run_dir(run_id) / "run.json"
        if not path.exists():
            return None
        return InsightRun(**self._read_json(path))

    def list_runs(self, limit: int = 20) -> list["InsightRun"]:
        runs: list[InsightRun] = []
        for run_dir in sorted(self.runs_dir.glob("*/"), reverse=True):
            path = run_dir / "run.json"
            if path.exists():
                runs.append(InsightRun(**self._read_json(path)))
            if len(runs) >= limit:
                break
        return runs

    def list_stage_events(self, run_id: str) -> list["RunStageEvent"]:
        events: list[RunStageEvent] = []
        for path in sorted((self._run_dir(run_id) / "events").glob("*.json")):
            events.append(RunStageEvent(**self._read_json(path)))
        return events

    def get_report(self, run_id: str, report_version: str) -> "InsightReport | None":
        path = self._run_dir(run_id) / "reports" / f"{report_version}.json"
        if not path.exists():
            return None
        return InsightReport(**self._read_json(path))

    def _run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    @staticmethod
    def _read_json(path: Path) -> dict:
        import json
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _safe_filename(value: str | None) -> str:
        if not value:
            return "unknown"
        safe = value
        for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            safe = safe.replace(char, '-')
        return safe
