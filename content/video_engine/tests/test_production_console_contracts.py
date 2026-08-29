from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
CONFIGS = ROOT / "content" / "video_engine" / "configs"
TEMPLATES = ROOT / "content" / "video_engine" / "templates"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        _load(CONFIGS / name),
        format_checker=FormatChecker(),
    )


@pytest.mark.parametrize(
    ("schema_name", "template_name"),
    [
        ("production_console_snapshot.schema.json", "production_console_snapshot.v1.json"),
        ("editorial_visual_revision.schema.json", "editorial_visual_revision.v1.json"),
    ],
)
def test_templates_validate(schema_name: str, template_name: str) -> None:
    _validator(schema_name).validate(_load(TEMPLATES / template_name))


def test_revision_rejects_protected_script_field() -> None:
    revision = _load(TEMPLATES / "editorial_visual_revision.v1.json")
    revision["script"] = "replace narration"
    errors = list(_validator("editorial_visual_revision.schema.json").iter_errors(revision))
    assert errors
    assert "script" in errors[0].message


def test_revision_rejects_unknown_operation() -> None:
    revision = _load(TEMPLATES / "editorial_visual_revision.v1.json")
    revision["operations"] = [
        {"op": "run_shell", "target": {"scene_id": "scene-001"}, "command": "echo nope"}
    ]
    assert list(_validator("editorial_visual_revision.schema.json").iter_errors(revision))


def test_revision_rejects_transform_outside_bounds() -> None:
    revision = _load(TEMPLATES / "editorial_visual_revision.v1.json")
    revision["operations"] = [
        {
            "op": "set_transform",
            "target": {"scene_id": "scene-001", "layer_id": "evidence"},
            "x": 0,
            "y": 0,
            "scale": 9,
            "opacity": 1,
            "z": 2,
        }
    ]
    assert list(_validator("editorial_visual_revision.schema.json").iter_errors(revision))


def test_snapshot_rejects_absolute_and_traversal_paths() -> None:
    base = _load(TEMPLATES / "production_console_snapshot.v1.json")
    validator = _validator("production_console_snapshot.schema.json")
    for unsafe in ("C:/secret/file.json", "/etc/passwd", "../escape.json"):
        payload = copy.deepcopy(base)
        payload["artifacts"][0]["path"] = unsafe
        assert list(validator.iter_errors(payload)), unsafe


def test_render_job_contract_has_no_command_surface() -> None:
    payload = {
        "schema_version": "local_render_job.v1",
        "job_id": "job-001",
        "request_id": "request-001",
        "revision_id": "revision-001",
        "operation": "render_preview",
        "state": "queued",
        "created_at": "2026-08-10T00:00:00Z",
        "updated_at": "2026-08-10T00:00:00Z",
        "artifacts": [],
        "error": None,
    }
    validator = _validator("local_render_job.schema.json")
    validator.validate(payload)
    payload["command"] = "powershell -Command whoami"
    assert list(validator.iter_errors(payload))
