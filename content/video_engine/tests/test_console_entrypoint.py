from __future__ import annotations

import pytest

import content.video_engine.console.__main__ as entry
from content.video_engine.src.services import editor_studio


@pytest.fixture()
def fake_serve(monkeypatch):
    served: list[dict] = []
    monkeypatch.setattr(entry.uvicorn, "run", lambda app, **kw: served.append(kw))
    return served


def test_without_the_flag_studio_is_never_touched(fake_serve, monkeypatch):
    touched: list[str] = []
    monkeypatch.setattr(editor_studio, "start", lambda: touched.append("start"))
    monkeypatch.setattr(editor_studio, "stop", lambda: touched.append("stop"))

    assert entry.main([]) == 0

    assert touched == []
    assert len(fake_serve) == 1, "the console served exactly as before"


def test_with_editor_starts_studio_before_serving_and_stops_after(fake_serve, monkeypatch):
    order: list[str] = []
    monkeypatch.setattr(editor_studio, "start",
                        lambda: order.append("start") or {"state": "starting", "pid": 1, "port": 3000})
    monkeypatch.setattr(editor_studio, "stop", lambda: order.append("stop") or {"state": "stopped"})
    monkeypatch.setattr(entry.uvicorn, "run", lambda app, **kw: order.append("serve"))

    assert entry.main(["--with-editor"]) == 0

    assert order == ["start", "serve", "stop"]


def test_keyboard_interrupt_still_stops_studio(monkeypatch):
    order: list[str] = []
    monkeypatch.setattr(editor_studio, "start",
                        lambda: order.append("start") or {"state": "starting", "pid": 1, "port": 3000})
    monkeypatch.setattr(editor_studio, "stop", lambda: order.append("stop") or {"state": "stopped"})

    def interrupted(app, **kw):
        order.append("serve")
        raise KeyboardInterrupt

    monkeypatch.setattr(entry.uvicorn, "run", interrupted)

    assert entry.main(["--with-editor"]) == 0

    assert order == ["start", "serve", "stop"]


def test_a_dead_editor_never_takes_the_console_down(fake_serve, monkeypatch, capsys):
    def refuse():
        raise editor_studio.EditorStudioError(["npm is not on PATH"])

    monkeypatch.setattr(editor_studio, "start", refuse)
    stopped: list[str] = []
    monkeypatch.setattr(editor_studio, "stop", lambda: stopped.append("stop"))

    assert entry.main(["--with-editor"]) == 0

    assert len(fake_serve) == 1, "the console served anyway"
    assert stopped == [], "nothing to stop — studio never started"
    assert "npm is not on PATH" in capsys.readouterr().out
