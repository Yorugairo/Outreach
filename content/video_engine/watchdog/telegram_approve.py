"""Inbound Telegram approvals — the phone half of the dual-mode paid gate.

Polls the bot's updates and acts on exactly one message shape from exactly one
sender: ``approve <job-id>`` from the allow-listed chat id. Everything else is
ignored (not answered — an unknown sender learns nothing, not even that the
bot gates anything). Every accepted command still passes the full
``paid_gate.release_job`` rules: ceiling, exact id echo, Flow pause.

Run ``--once`` from a scheduled task or the watchdog host; the offset file
keeps polls incremental. Network sits behind ``_get_updates`` for tests.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.src.services.paid_gate import PaidGateError, release_job
from content.video_engine.watchdog.notify import (
    ENV_TELEGRAM_CHAT,
    ENV_TELEGRAM_TOKEN,
    telegram,
)

OFFSET_FILE = Path.home() / ".video-engine" / "telegram-offset.json"

_APPROVE = re.compile(r"^\s*approve\s+([A-Za-z0-9-]+)\s*$", re.I)


def _get_updates(token: str, offset: int) -> list[dict[str, Any]]:
    """The Telegram polling boundary; tests monkeypatch this."""

    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=0&offset={offset}"
    with urllib.request.urlopen(url, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("result", [])


def process_updates(
    updates: list[dict[str, Any]], env: Mapping[str, str] | None = None
) -> list[dict[str, Any]]:
    """Act on approve commands from the allow-listed chat; report outcomes."""

    source = os.environ if env is None else env
    allowed = source.get(ENV_TELEGRAM_CHAT)
    outcomes: list[dict[str, Any]] = []
    for update in updates:
        message = update.get("message") or {}
        chat_id = str((message.get("chat") or {}).get("id") or "")
        text = str(message.get("text") or "")
        match = _APPROVE.match(text)
        if not match or not allowed or chat_id != allowed:
            continue  # silence toward everyone but the operator
        job_id = match.group(1)
        try:
            job = release_job(
                job_id, channel="telegram", chat_id=chat_id,
                echoed_job_id=job_id, env=env,
            )
            outcomes.append({"job_id": job_id, "released": True})
            telegram(f"released {job_id} (${job['estimated_cost_usd']}, {job['lane']})", env)
        except PaidGateError as exc:
            outcomes.append({"job_id": job_id, "released": False, "errors": exc.errors})
            telegram(f"refused {job_id}: {'; '.join(exc.errors)}", env)
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", required=True,
                        help="poll once and exit (the only supported mode)")
    parser.parse_args(argv)

    token = os.environ.get(ENV_TELEGRAM_TOKEN)
    if not token:
        print("telegram unconfigured; nothing to poll")
        return 0
    offset = 0
    if OFFSET_FILE.exists():
        offset = int(json.loads(OFFSET_FILE.read_text(encoding="utf-8")).get("offset", 0))
    updates = _get_updates(token, offset)
    outcomes = process_updates(updates)
    if updates:
        OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
        OFFSET_FILE.write_text(
            json.dumps({"offset": max(u["update_id"] for u in updates) + 1}),
            encoding="utf-8",
        )
    for outcome in outcomes:
        print(json.dumps(outcome))
    return 0


if __name__ == "__main__":
    sys.exit(main())
