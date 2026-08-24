"""Notification adapters: Windows toast and Telegram, notify-only.

Both are best-effort observers of the loop, never participants: a failed
notification logs and returns — it must never block or fail a scan. The
Telegram half here only *sends*; inbound approval handling lives in the paid
gate (T6) with its own allow-list and ceiling rules.

Secrets come from the environment only and are never logged:

    VIDEO_ENGINE_TELEGRAM_BOT_TOKEN
    VIDEO_ENGINE_TELEGRAM_CHAT_ID

Each transport goes through one module-level boundary tests monkeypatch:
``_run_powershell`` for the toast, ``_post_json`` for Telegram.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import urllib.request
from typing import Any, Mapping

log = logging.getLogger(__name__)

ENV_TELEGRAM_TOKEN = "VIDEO_ENGINE_TELEGRAM_BOT_TOKEN"
ENV_TELEGRAM_CHAT = "VIDEO_ENGINE_TELEGRAM_CHAT_ID"

_TOAST_SCRIPT = """
Add-Type -AssemblyName System.Windows.Forms
$icon = New-Object System.Windows.Forms.NotifyIcon
$icon.Icon = [System.Drawing.SystemIcons]::Information
$icon.Visible = $true
$icon.ShowBalloonTip(10000, 'Video Engine', {message}, 'Info')
Start-Sleep -Seconds 6
$icon.Dispose()
"""


def _run_powershell(script: str) -> None:
    """The toast boundary; tests monkeypatch this."""

    subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, timeout=30,
    )


def _post_json(url: str, payload: Mapping[str, Any]) -> None:
    """The Telegram boundary; tests monkeypatch this."""

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15):
        pass


def _quote_powershell(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def toast(message: str) -> bool:
    """Windows balloon notification. Best-effort; True when dispatched."""

    try:
        _run_powershell(_TOAST_SCRIPT.replace("{message}", _quote_powershell(message)))
        return True
    except Exception as exc:  # any failure: log, never block the scan path
        log.warning("toast failed: %s", exc)
        return False


def telegram(message: str, env: Mapping[str, str] | None = None) -> bool:
    """Send one Telegram message. Best-effort; True when dispatched.

    Unconfigured is a normal state, not an error — the operator may only want
    toasts. The token never appears in logs; only its presence does.
    """

    source = os.environ if env is None else env
    token = source.get(ENV_TELEGRAM_TOKEN)
    chat = source.get(ENV_TELEGRAM_CHAT)
    if not token or not chat:
        log.info("telegram unconfigured (token present: %s)", bool(token))
        return False
    try:
        _post_json(
            f"https://api.telegram.org/bot{token}/sendMessage",
            {"chat_id": chat, "text": message},
        )
        return True
    except Exception as exc:
        log.warning("telegram send failed: %s", type(exc).__name__)
        return False


def notify_all(message: str, env: Mapping[str, str] | None = None) -> dict[str, bool]:
    return {"toast": toast(message), "telegram": telegram(message, env)}
