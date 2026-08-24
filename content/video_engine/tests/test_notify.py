from __future__ import annotations

import pytest

from content.video_engine.watchdog import notify
from content.video_engine.watchdog.notify import (
    ENV_TELEGRAM_CHAT,
    ENV_TELEGRAM_TOKEN,
    notify_all,
    telegram,
    toast,
)


def test_the_toast_goes_through_the_powershell_boundary(monkeypatch):
    scripts: list[str] = []
    monkeypatch.setattr(notify, "_run_powershell", lambda script: scripts.append(script))

    assert toast("claim batch-one: 9 clean, 3 flagged") is True

    assert len(scripts) == 1
    assert "9 clean, 3 flagged" in scripts[0]


def test_a_quote_in_the_message_cannot_break_the_script(monkeypatch):
    scripts: list[str] = []
    monkeypatch.setattr(notify, "_run_powershell", lambda script: scripts.append(script))

    toast("it's done")

    assert "it''s done" in scripts[0], "single quotes double, PowerShell-style"


def test_a_failing_toast_never_raises(monkeypatch):
    def boom(script):
        raise OSError("no display")

    monkeypatch.setattr(notify, "_run_powershell", boom)

    assert toast("anything") is False


def test_telegram_posts_to_the_bot_api_with_env_credentials(monkeypatch):
    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(notify, "_post_json", lambda url, payload: calls.append((url, payload)))
    env = {ENV_TELEGRAM_TOKEN: "SECRET-TOKEN", ENV_TELEGRAM_CHAT: "12345"}

    assert telegram("scan ready", env) is True

    url, payload = calls[0]
    assert "SECRET-TOKEN" in url
    assert payload == {"chat_id": "12345", "text": "scan ready"}


def test_unconfigured_telegram_is_a_quiet_no_not_an_error():
    assert telegram("anything", env={}) is False


def test_a_network_failure_logs_the_type_never_the_token(monkeypatch, caplog):
    def boom(url, payload):
        raise OSError("connection refused")

    monkeypatch.setattr(notify, "_post_json", boom)
    env = {ENV_TELEGRAM_TOKEN: "SECRET-TOKEN", ENV_TELEGRAM_CHAT: "1"}

    with caplog.at_level("WARNING"):
        assert telegram("x", env) is False

    assert "SECRET-TOKEN" not in caplog.text


def test_notify_all_reports_each_channel(monkeypatch):
    monkeypatch.setattr(notify, "_run_powershell", lambda script: None)

    result = notify_all("message", env={})

    assert result == {"toast": True, "telegram": False}
