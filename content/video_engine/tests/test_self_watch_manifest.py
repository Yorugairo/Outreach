"""Self-watch lint must follow the compiled build manifest's shot table."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import self_watch as SW  # noqa: E402


def _manifest(build: Path, *, episode_dir: str = "..", shot_table_file: str = "build-pilot/SHOT-TABLE-PILOT.py") -> None:
    (build / SW.MANIFEST_NAME).write_text(
        json.dumps({"compile": {"episode_dir": episode_dir, "shot_table_file": shot_table_file}}),
        encoding="utf-8",
    )


def test_lint_report_uses_compiled_manifest_table(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    project = tmp_path / "episode"
    build = project / "build-pilot"
    build.mkdir(parents=True)
    table = build / "SHOT-TABLE-PILOT.py"
    table.write_text("W = []\n", encoding="utf-8")
    _manifest(build)
    captured: dict[str, object] = {}

    def fake_report(project_arg, *, build=None, table=None, long=False):
        captured.update(project=project_arg, build=build, table=table, long=long)
        return ["ok"], {"sentences": 0}

    monkeypatch.setattr(SW.L, "report", fake_report)
    assert SW.lint_report(project, build, "long") == (["ok"], {"sentences": 0})
    assert captured["table"] == table.resolve()
    assert captured["build"] == str(build)
    assert captured["long"] is True


def test_manifest_absence_preserves_lint_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    project = tmp_path / "episode"
    build = project / "build-pilot"
    build.mkdir(parents=True)
    captured: dict[str, object] = {}

    def fake_report(project_arg, *, build=None, table=None, long=False):
        captured["table"] = table
        return [], {}

    monkeypatch.setattr(SW.L, "report", fake_report)
    SW.lint_report(project, build, "short")
    assert captured["table"] is None


def test_manifest_table_escape_fails_closed(tmp_path: Path) -> None:
    project = tmp_path / "episode"
    build = project / "build-pilot"
    build.mkdir(parents=True)
    _manifest(build, shot_table_file="../outside.py")
    with pytest.raises(ValueError, match="escapes project"):
        SW.manifest_shot_table(build, project)


def test_manifest_missing_table_fails_closed(tmp_path: Path) -> None:
    project = tmp_path / "episode"
    build = project / "build-pilot"
    build.mkdir(parents=True)
    _manifest(build)
    with pytest.raises(FileNotFoundError, match="compiled shot table is not on disk"):
        SW.manifest_shot_table(build, project)


def test_malformed_manifest_fails_closed(tmp_path: Path) -> None:
    project = tmp_path / "episode"
    build = project / "build-pilot"
    build.mkdir(parents=True)
    (build / SW.MANIFEST_NAME).write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="top level is not an object"):
        SW.manifest_shot_table(build, project)
