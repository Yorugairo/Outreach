from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from content.video_engine.src.models import VideoRun, VideoStageEvent


_SAFE_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class FileBackedVideoJobRepository:
    def __init__(self, root: str | Path):
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def create_run(self, run: VideoRun) -> VideoRun:
        run_dir = self.job_dir(run.id)
        for subdir in ("events", "audio", "video", "captions", "package", "qc"):
            (run_dir / subdir).mkdir(parents=True, exist_ok=True)
        self._write_json(run_dir / "job.json", run.to_dict())
        return run

    def update_run(self, run: VideoRun) -> VideoRun:
        path = self.job_dir(run.id) / "job.json"
        if not path.exists():
            raise FileNotFoundError(f"video run does not exist: {run.id}")
        self._write_json(path, run.to_dict())
        return run

    def append_stage_event(self, event: VideoStageEvent) -> VideoStageEvent:
        events_dir = self.job_dir(event.video_run_id) / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        index = len(list(events_dir.glob("*.json"))) + 1
        stage = self._safe_identity(event.stage_name)
        status = self._safe_identity(event.status)
        self._write_json(
            events_dir / f"{index:04d}_{stage}_{status}.json",
            event.to_dict(),
        )
        return event

    def load_run(self, run_id: str) -> VideoRun | None:
        path = self.job_dir(run_id) / "job.json"
        if not path.exists():
            return None
        return VideoRun(**self._read_json(path))

    def list_runs(self) -> list[VideoRun]:
        runs = [
            VideoRun(**self._read_json(path))
            for path in self._root.glob("*/job.json")
        ]
        return sorted(runs, key=lambda run: (run.created_at, run.id), reverse=True)

    def list_stage_events(self, run_id: str) -> list[VideoStageEvent]:
        events_dir = self.job_dir(run_id) / "events"
        if not events_dir.exists():
            return []
        return [
            VideoStageEvent(**self._read_json(path))
            for path in sorted(events_dir.glob("*.json"))
        ]

    def job_dir(self, run_id: str) -> Path:
        return self._root / self._safe_identity(run_id)

    @staticmethod
    def _safe_identity(value: str) -> str:
        if not value or not _SAFE_IDENTITY.fullmatch(value) or value in {".", ".."}:
            raise ValueError("identity contains unsafe path characters")
        return value

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(path)
