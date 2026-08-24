from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.settings import load_settings
from content.video_engine.src.services import editor_studio


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(load_settings(project_root=tmp_path)))


def _serving(monkeypatch):
    monkeypatch.setattr(editor_studio, "status", lambda: {
        "state": "serving", "pid": 4000, "port": 3000, "url": "http://127.0.0.1:3000",
    })


def test_the_editor_view_shows_state_with_the_chip_vocabulary(client, monkeypatch):
    _serving(monkeypatch)

    body = client.get("/editor").text

    assert "SERVING" in body
    assert "chip-clean" in body
    assert 'href="http://127.0.0.1:3000"' in body
    assert 'action="/editor/stop"' in body


def test_a_stopped_studio_offers_start_and_no_stop(client, monkeypatch):
    monkeypatch.setattr(editor_studio, "status", lambda: {"state": "stopped"})

    body = client.get("/editor").text

    assert 'action="/editor/start"' in body
    assert 'action="/editor/stop"' not in body


def test_failure_shows_stderr_verbatim(client, monkeypatch):
    monkeypatch.setattr(editor_studio, "status", lambda: {
        "state": "failed", "pid": 4000, "port": 3000,
        "stderr": "Error: EADDRINUSE :::3000",
        "detail": "the recorded pid is not running",
    })

    body = client.get("/editor").text

    assert "FAILED" in body
    assert "EADDRINUSE" in body


def test_a_status_get_constructs_and_writes_nothing(client, monkeypatch, tmp_path):
    """Byte-snapshot: two GETs are identical and the tree is untouched."""

    monkeypatch.setattr(editor_studio, "status", lambda: {"state": "stopped"})
    before = sorted(p.as_posix() for p in tmp_path.rglob("*"))

    first = client.get("/editor").content
    second = client.get("/editor").content

    assert first == second
    assert sorted(p.as_posix() for p in tmp_path.rglob("*")) == before


def test_start_and_stop_are_thin_over_the_service(client, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(editor_studio, "start", lambda: calls.append("start") or {"state": "starting"})
    monkeypatch.setattr(editor_studio, "stop", lambda: calls.append("stop") or {"state": "stopped"})
    monkeypatch.setattr(editor_studio, "status", lambda: {"state": "stopped"})

    client.post("/editor/start", follow_redirects=False)
    client.post("/editor/stop", follow_redirects=False)

    assert calls == ["start", "stop"]


def test_a_start_failure_surfaces_the_named_error(client, monkeypatch):
    def refuse():
        raise editor_studio.EditorStudioError(["npm is not on PATH; install Node.js"])

    monkeypatch.setattr(editor_studio, "start", refuse)

    body = client.post("/editor/start").text

    assert "Studio start failed" in body
    assert "npm is not on PATH" in body
