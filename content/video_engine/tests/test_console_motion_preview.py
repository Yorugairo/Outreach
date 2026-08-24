from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.settings import load_settings
from content.video_engine.console.routes import preview as preview_module

CONSOLE_PKG = Path(preview_module.__file__).resolve().parents[1]


def _client() -> TestClient:
    return TestClient(create_app(load_settings(env={})))


def _fake_run(record: list, *, returncode=0, stdout="ok", stderr=""):
    def run(cmd):
        record.append(cmd)
        return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr=stderr)

    return run


def _wait_done(client, unit, tries=50):
    for _ in range(tries):
        job = client.app.state.motion_previews.get(unit or "remotion-smoke")
        if job and job["status"] != "running":
            return job
        time.sleep(0.02)
    raise AssertionError("preview job never finished")


def _motion_swept_files():
    """Console package plus the P17 loop modules: none may compute motion."""

    services = CONSOLE_PKG.parent / "src" / "services"
    watchdog = CONSOLE_PKG.parent / "watchdog"
    extra = [
        services / "claim_resume.py",
        services / "delivery_scan.py",
        services / "generation_claim.py",
        services / "paid_gate.py",
        *sorted(watchdog.rglob("*.py")),
    ]
    return [*CONSOLE_PKG.rglob("*.py"), *[p for p in extra if p.exists()]]


def test_the_console_package_implements_no_motion_arithmetic():
    """The structural guarantee: no camera, easing or parallax code in here.

    A preview rendered by a different engine than the render lane can disagree
    with the render; the console must only invoke the lanes. Copying
    `parallax_factor` verbatim (the commit path moves it from a manifest entry
    to a catalogue entry) is the required passthrough; computing with it is the
    violation.
    """

    banned = re.compile(r"easing|\binterpolate\b|cubic[-_]?bezier|keyframe", re.I)
    parallax_math = re.compile(r"parallax\w*\s*[*+/-]|[*+/-]\s*[\w\[\]\"']*parallax", re.I)
    for path in _motion_swept_files():
        source = path.read_text(encoding="utf-8")
        # Strip comments and docstrings' explanatory prose is allowed to name
        # the concept; executable lines are not.
        lines = [
            line for line in source.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        in_doc = False
        code_lines = []
        for line in lines:
            stripped = line.strip()
            quotes = stripped.count('"""') + stripped.count("'''")
            if in_doc:
                if quotes:
                    in_doc = False
                continue
            if quotes == 1:
                in_doc = True
                continue
            if quotes >= 2:
                continue
            code_lines.append(line)
        hits = [l for l in code_lines if banned.search(l) or parallax_math.search(l)]
        assert not hits, f"{path.name} contains motion arithmetic: {hits}"


def test_the_hyperframes_lane_is_invoked_through_render_unit(tmp_path, monkeypatch):
    unit = tmp_path / "unit.json"
    unit.write_text(json.dumps({"unit_kind": "animatic_preview"}), encoding="utf-8")
    calls: list = []
    monkeypatch.setattr(preview_module, "_run_command", _fake_run(calls))
    client = _client()

    r = client.post("/preview/motion", data={
        "lane": "hyperframes", "unit": str(unit), "dry_run": "true",
    }, follow_redirects=False)

    assert r.status_code == 303
    job = _wait_done(client, str(unit))
    assert job["status"] == "done"
    assert calls and "render-unit" in calls[0]
    assert str(unit) in calls[0]
    assert "--dry-run" in calls[0], "'would this render' uses --dry-run"


def test_the_remotion_lane_is_invoked_through_verify_editor(monkeypatch):
    calls: list = []
    monkeypatch.setattr(preview_module, "_run_command", _fake_run(calls))
    client = _client()

    client.post("/preview/motion", data={"lane": "remotion"}, follow_redirects=False)

    job = _wait_done(client, "")
    assert job["status"] == "done"
    assert "verify-editor" in calls[0] and "--smoke" in calls[0]


def test_a_lane_failure_surfaces_its_own_stderr(tmp_path, monkeypatch):
    unit = tmp_path / "unit.json"
    unit.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        preview_module, "_run_command",
        _fake_run([], returncode=1, stderr="unit rejected: timing_basis estimated"),
    )
    client = _client()
    client.post("/preview/motion", data={"lane": "hyperframes", "unit": str(unit)})
    _wait_done(client, str(unit))

    body = client.get("/preview/motion", params={"unit": str(unit)}).text

    assert "FAILED" in body
    assert "unit rejected: timing_basis estimated" in body


def test_the_pending_state_is_visible_and_the_ui_stays_responsive(tmp_path, monkeypatch):
    unit = tmp_path / "unit.json"
    unit.write_text("{}", encoding="utf-8")
    release = {"go": False}

    def slow_run(cmd):
        while not release["go"]:
            time.sleep(0.01)
        return subprocess.CompletedProcess(cmd, 0, stdout="done", stderr="")

    monkeypatch.setattr(preview_module, "_run_command", slow_run)
    client = _client()
    client.post("/preview/motion", data={"lane": "hyperframes", "unit": str(unit)})

    body = client.get("/preview/motion", params={"unit": str(unit)}).text
    assert "RUNNING" in body
    # Another route answers while the render is in flight.
    assert client.get("/catalog").status_code == 200

    release["go"] = True
    _wait_done(client, str(unit))


def test_a_missing_unit_file_is_refused_before_any_process_starts(monkeypatch):
    calls: list = []
    monkeypatch.setattr(preview_module, "_run_command", _fake_run(calls))
    client = _client()

    r = client.post("/preview/motion", data={
        "lane": "hyperframes", "unit": "Z:/absent/unit.json",
    })

    assert "Unit not found" in r.text
    assert not calls


def test_an_unknown_lane_is_refused(monkeypatch):
    calls: list = []
    monkeypatch.setattr(preview_module, "_run_command", _fake_run(calls))
    client = _client()

    r = client.post("/preview/motion", data={"lane": "pillow", "unit": ""})

    assert "no lane named" in r.text
    assert not calls
