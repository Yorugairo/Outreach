from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.routes import runs as runs_routes
from content.video_engine.console.settings import load_settings
from content.video_engine.src.models import VideoRun, VideoStageEvent
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _runs_dir(project_root: Path) -> Path:
    return project_root.joinpath(*runs_routes.RUNS_SUBPATH)


def _client(project_root: Path) -> TestClient:
    """The parent registers routers in ``app.py``; the slice wires its own here."""

    app = create_app(load_settings(project_root=project_root))
    app.include_router(runs_routes.router)
    return TestClient(app)


def _seed(
    project_root: Path,
    run: VideoRun,
    *events: VideoStageEvent,
) -> Path:
    """Write a job through the repository that owns the format, never by hand."""

    runs_dir = _runs_dir(project_root)
    repository = FileBackedVideoJobRepository(runs_dir)
    repository.create_run(run)
    for event in events:
        repository.append_stage_event(event)
    return runs_dir


def _run(run_id: str, **over) -> VideoRun:
    fields = {
        "source_ref": f"source::{run_id}",
        "id": run_id,
        "status": "running",
        "current_stage": "ingesting_source",
        "created_at": "2026-08-20T00:00:00+00:00",
        "updated_at": "2026-08-20T00:00:00+00:00",
    }
    fields.update(over)
    return VideoRun(**fields)


def _event(run_id: str, stage: str, status: str, **over) -> VideoStageEvent:
    fields = {
        "video_run_id": run_id,
        "stage_name": stage,
        "status": status,
        "output_summary": {"cost_usd": 0.0, "wall_time_s": 0.0},
    }
    fields.update(over)
    return VideoStageEvent(**fields)


# --------------------------------------------------------------------------
# Listing: stage state and recorded events
# --------------------------------------------------------------------------


def test_a_job_is_listed_with_its_stage_state_and_recorded_events(tmp_path):
    _seed(
        tmp_path,
        _run("job-alpha", current_stage="drafting_script", status="running"),
        _event("job-alpha", "ingesting_source", "completed"),
        _event("job-alpha", "drafting_script", "running"),
    )

    body = _client(tmp_path).get("/runs").text

    assert "job-alpha" in body
    assert "drafting_script" in body
    assert "running" in body
    # Two recorded events, counted rather than guessed at.
    assert ">2<" in body


def test_pending_gates_are_displayed_without_being_actionable(tmp_path):
    _seed(
        tmp_path,
        _run("job-gated", gate_a_status="approved", research_gate_status="approved"),
    )

    body = _client(tmp_path).get("/runs").text

    assert "asset_gate" in body
    assert "visual_gate" in body
    assert "gate_b" in body
    assert "gate_a," not in body, "an approved gate is not pending"


# --------------------------------------------------------------------------
# Failures carry the stage event's own text
# --------------------------------------------------------------------------


def test_a_failed_stage_surfaces_its_own_event_text_not_a_generic_message(tmp_path):
    recorded = "voiceover provider returned 503 after 3 retries"
    _seed(
        tmp_path,
        _run("job-broken", status="failed", current_stage="synthesising_voiceover"),
        _event("job-broken", "ingesting_source", "completed"),
        _event(
            "job-broken",
            "synthesising_voiceover",
            "failed",
            error_text=recorded,
        ),
    )

    body = _client(tmp_path).get("/runs").text

    assert recorded in body, "the stage event's own text must reach the operator"
    assert "synthesising_voiceover" in body
    assert "FAIL" in body


def test_the_runs_error_text_is_surfaced_alongside_the_stage_failure(tmp_path):
    _seed(
        tmp_path,
        _run(
            "job-errored",
            status="failed",
            error_text="storyboard hash did not match the recorded snapshot",
        ),
    )

    body = _client(tmp_path).get("/runs").text

    assert "storyboard hash did not match the recorded snapshot" in body
    assert "FAIL" in body


def test_a_failure_without_recorded_text_says_so_rather_than_inventing_one(tmp_path):
    _seed(
        tmp_path,
        _run("job-silent", status="failed"),
        _event("job-silent", "rendering_video", "failed"),
    )

    body = _client(tmp_path).get("/runs").text

    assert "rendering_video" in body
    assert "no error text recorded" in body


# --------------------------------------------------------------------------
# Exception-first ordering, mirroring scene_board
# --------------------------------------------------------------------------


def test_a_failed_job_sorts_before_a_clean_one_regardless_of_recency(tmp_path):
    # The clean job is the newest, so the repository would list it first.
    _seed(
        tmp_path,
        _run("job-clean", status="packaged", created_at="2026-08-22T00:00:00+00:00"),
    )
    _seed(
        tmp_path,
        _run("job-failed", status="failed", created_at="2026-08-19T00:00:00+00:00"),
        _event("job-failed", "packaging", "failed", error_text="ffmpeg exited 1"),
    )

    body = _client(tmp_path).get("/runs").text

    assert body.index("job-failed") < body.index("job-clean")


def test_a_job_awaiting_a_gate_is_flagged_and_sorts_ahead_of_clean_jobs(tmp_path):
    _seed(
        tmp_path,
        _run("job-clean", status="packaged", created_at="2026-08-22T00:00:00+00:00"),
    )
    _seed(
        tmp_path,
        _run(
            "job-parked",
            status="awaiting_visual_gate",
            created_at="2026-08-18T00:00:00+00:00",
        ),
        _event("job-parked", "visual_gate", "awaiting_approval"),
    )

    body = _client(tmp_path).get("/runs").text

    assert "FLAG" in body
    assert body.index("job-parked") < body.index("job-clean")


def test_ordering_is_failed_then_flagged_then_clean(tmp_path):
    _seed(tmp_path, _run("job-clean", status="packaged"))
    _seed(tmp_path, _run("job-parked", status="awaiting_gate_a"))
    _seed(
        tmp_path,
        _run("job-failed", status="failed"),
        _event("job-failed", "packaging", "failed", error_text="disk full"),
    )

    body = _client(tmp_path).get("/runs").text

    assert body.index("job-failed") < body.index("job-parked") < body.index("job-clean")


def test_order_jobs_is_a_stable_partition_not_a_sort():
    jobs = [
        {"id": "c1", "severity": runs_routes.SEVERITY_CLEAN},
        {"id": "f1", "severity": runs_routes.SEVERITY_FAIL},
        {"id": "c2", "severity": runs_routes.SEVERITY_CLEAN},
        {"id": "g1", "severity": runs_routes.SEVERITY_FLAG},
        {"id": "f2", "severity": runs_routes.SEVERITY_FAIL},
    ]

    ordered = [job["id"] for job in runs_routes.order_jobs(jobs)]

    # Bands in order, and the input order preserved inside every band.
    assert ordered == ["f1", "f2", "g1", "c1", "c2"]


# --------------------------------------------------------------------------
# Status encoding
# --------------------------------------------------------------------------


def test_status_is_never_colour_alone(tmp_path):
    _seed(tmp_path, _run("job-clean", status="packaged"))
    _seed(
        tmp_path,
        _run("job-failed", status="failed"),
        _event("job-failed", "packaging", "failed", error_text="disk full"),
    )
    _seed(tmp_path, _run("job-parked", status="awaiting_gate_b"))

    body = _client(tmp_path).get("/runs").text

    # Glyph and colour come from the chip class; the text label survives greyscale.
    for chip, label in (
        ("chip-fail", "FAIL"),
        ("chip-flag", "FLAG"),
        ("chip-clean", "OK"),
    ):
        assert chip in body
        assert label in body


def test_the_derived_severity_vocabulary_is_exhaustive():
    for severity in runs_routes.SEVERITY_ORDER:
        assert severity in runs_routes.SEVERITY_CHIP
        assert severity in runs_routes.SEVERITY_LABEL


# --------------------------------------------------------------------------
# Read-only
# --------------------------------------------------------------------------


def test_the_module_defines_no_write_routes():
    """Read-only is structural. No route may advance a stage or approve a gate."""

    for route in runs_routes.router.routes:
        methods = set(getattr(route, "methods", set()))
        assert not methods & WRITE_METHODS, f"{route.path} exposes {methods & WRITE_METHODS}"


def test_the_module_source_declares_no_write_verbs():
    source = Path(runs_routes.__file__).read_text(encoding="utf-8")

    for verb in ("post", "put", "patch", "delete"):
        assert f"@router.{verb}" not in source


def test_reading_the_runs_view_writes_nothing_under_the_runs_directory(tmp_path):
    runs_dir = _seed(
        tmp_path,
        _run("job-alpha"),
        _event("job-alpha", "ingesting_source", "completed"),
    )
    before = {
        path.relative_to(runs_dir).as_posix(): path.read_bytes()
        for path in sorted(runs_dir.rglob("*"))
        if path.is_file()
    }

    assert _client(tmp_path).get("/runs").status_code == 200

    after = {
        path.relative_to(runs_dir).as_posix(): path.read_bytes()
        for path in sorted(runs_dir.rglob("*"))
        if path.is_file()
    }
    assert after == before


def test_an_absent_runs_directory_is_not_created_by_rendering_the_view(tmp_path):
    """``FileBackedVideoJobRepository`` mkdirs on construction; a read must not."""

    assert _client(tmp_path).get("/runs").status_code == 200

    assert not (tmp_path / "runtime").exists()


# --------------------------------------------------------------------------
# Empty and degraded input states
# --------------------------------------------------------------------------


def test_an_absent_runs_directory_renders_an_empty_state_not_an_error(tmp_path):
    response = _client(tmp_path).get("/runs")

    assert response.status_code == 200
    assert "No jobs recorded" in response.text
    assert "Traceback" not in response.text


def test_an_empty_runs_directory_renders_an_empty_state(tmp_path):
    _runs_dir(tmp_path).mkdir(parents=True)

    response = _client(tmp_path).get("/runs")

    assert response.status_code == 200
    assert "No jobs recorded" in response.text


def test_a_malformed_job_file_is_reported_rather_than_raising(tmp_path):
    runs_dir = _runs_dir(tmp_path)
    (runs_dir / "job-bad").mkdir(parents=True)
    (runs_dir / "job-bad" / "job.json").write_text("{not json", encoding="utf-8")

    response = _client(tmp_path).get("/runs")

    assert response.status_code == 200
    assert "Jobs unreadable" in response.text
    assert "Traceback" not in response.text


def test_a_job_with_an_unknown_field_is_reported_rather_than_raising(tmp_path):
    runs_dir = _runs_dir(tmp_path)
    (runs_dir / "job-odd").mkdir(parents=True)
    payload = _run("job-odd").to_dict()
    payload["unexpected_field"] = True
    (runs_dir / "job-odd" / "job.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    response = _client(tmp_path).get("/runs")

    assert response.status_code == 200
    assert "Jobs unreadable" in response.text
    assert "unexpected_field" in response.text


# --------------------------------------------------------------------------
# The runs directory is injectable
# --------------------------------------------------------------------------


def test_the_runs_directory_is_derived_from_the_configured_project_root(tmp_path):
    settings = load_settings(project_root=tmp_path)

    assert runs_routes.resolve_runs_dir(settings) == tmp_path / "runtime" / "jobs"


def test_an_explicit_runs_dir_on_settings_wins(tmp_path):
    @dataclass(frozen=True)
    class SettingsWithRunsDir:
        project_root: Path
        runs_dir: Path

    resolved = runs_routes.resolve_runs_dir(
        SettingsWithRunsDir(project_root=tmp_path, runs_dir=tmp_path / "elsewhere")
    )

    assert resolved == tmp_path / "elsewhere"


def test_an_unconfigured_console_falls_back_to_the_engine_runtime_directory():
    settings = load_settings(env={})

    assert runs_routes.resolve_runs_dir(settings) == runs_routes.DEFAULT_RUNS_DIR


def test_the_default_runs_directory_has_not_drifted_from_the_cli(tmp_path):
    """The console must read exactly where the CLI writes."""

    from content.video_engine.cli import DEFAULT_ARTIFACT_ROOT

    assert runs_routes.DEFAULT_RUNS_DIR == DEFAULT_ARTIFACT_ROOT
