"""T4 — deep links into Studio, built on verified ground.

Verification (recorded, not assumed): the installed pin's
``@remotion/studio/dist/helpers/url-state.js`` routes the SPA by
``window.location.pathname`` (``getRoute`` returns it; query-string handling
exists only for read-only studio builds). Therefore
``http://127.0.0.1:<port>/<CompositionId>`` is the deepest supported link and
props-in-URL is not offered.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.routes.editor import studio_link
from content.video_engine.console.settings import load_settings
from content.video_engine.src.services import editor_studio

_URL_STATE = (
    Path(__file__).resolve().parents[1]
    / "editor" / "node_modules" / "@remotion" / "studio" / "dist" / "helpers" / "url-state.js"
)


@pytest.mark.skipif(not _URL_STATE.exists(), reason="editor node_modules not installed")
def test_the_pinned_studio_routes_by_pathname_the_evidence_for_deep_links():
    source = _URL_STATE.read_text(encoding="utf-8")

    assert "window.location.pathname" in source
    assert "pushState" in source


def test_the_helper_builds_the_composition_path_form():
    state = {"state": "serving", "url": "http://127.0.0.1:3000"}

    assert studio_link(state, "EditorialMotion") == "http://127.0.0.1:3000/EditorialMotion"
    assert studio_link(state, "") == "http://127.0.0.1:3000", "empty id degrades to root"


def test_no_link_while_studio_is_not_serving():
    for state in ({"state": "stopped"}, {"state": "starting", "url": None},
                  {"state": "failed"}, {"state": "stale"}):
        assert studio_link(state, "Editorial") is None


def test_board_and_runs_render_the_link_only_while_serving(tmp_path, monkeypatch):
    client = TestClient(create_app(load_settings(project_root=tmp_path)))

    monkeypatch.setattr(editor_studio, "status", lambda: {"state": "stopped"})
    assert "Open in editor" not in client.get("/runs").text

    monkeypatch.setattr(editor_studio, "status", lambda: {
        "state": "serving", "url": "http://127.0.0.1:3000", "pid": 1, "port": 3000,
    })
    body = client.get("/runs").text
    assert 'href="http://127.0.0.1:3000/EditorialMotion"' in body
