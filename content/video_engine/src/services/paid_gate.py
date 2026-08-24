"""The paid gate: the one human gate left in the loop, and it guards money.

Everything upstream is free and automated; nothing here executes spend either.
A *registered* job is a fact ("this claim wants narration TTS, ~$3"); a
*released* job is a permission the paid lane's own tooling may act on. This
service only ever flips pending → released, under rules:

- **Dual-mode release** (operator decision 2026-08-23): Telegram approval is
  valid only for jobs at or under the ceiling (default $5), only from the
  allow-listed chat id, and only with the exact job id echoed back. Anything
  above the ceiling releases from this machine alone — a phone chat message
  is never sufficient for real money.
- **The Flow pause is honoured independently**: a `flow`-lane job refuses
  release through any channel while the pause stands. The pause is a config
  value that defaults to paused — the standing constraint fails closed.
- **Every decision is audited**: who, channel, job, cost, appended to
  ``~/.video-engine/paid-audit.log``.

Registry and config live outside every repo (machine state, like claims):
``~/.video-engine/paid-jobs/`` and ``~/.video-engine/config.json``; env
overrides ``VIDEO_ENGINE_PAID_JOBS_DIR`` / ``VIDEO_ENGINE_CONFIG`` exist for
tests.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.watchdog.notify import ENV_TELEGRAM_CHAT

ENV_JOBS_DIR = "VIDEO_ENGINE_PAID_JOBS_DIR"
ENV_CONFIG = "VIDEO_ENGINE_CONFIG"

DEFAULT_JOBS_DIR = Path.home() / ".video-engine" / "paid-jobs"
DEFAULT_CONFIG = Path.home() / ".video-engine" / "config.json"
DEFAULT_CEILING_USD = 5.0


class PaidGateError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _jobs_dir(env: Mapping[str, str] | None) -> Path:
    source = os.environ if env is None else env
    override = source.get(ENV_JOBS_DIR)
    return Path(override) if override else DEFAULT_JOBS_DIR


def load_config(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Gate config. Absent file means the safest defaults, stated explicitly."""

    source = os.environ if env is None else env
    override = source.get(ENV_CONFIG)
    path = Path(override) if override else DEFAULT_CONFIG
    config: dict[str, Any] = {}
    if path.exists():
        config = json.loads(path.read_text(encoding="utf-8"))
    config.setdefault("telegram_ceiling_usd", DEFAULT_CEILING_USD)
    # The Flow queue pause is a standing constraint; absence of config means
    # PAUSED, never open.
    config.setdefault("flow_queue_paused", True)
    return config


def register_job(
    *,
    claim_id: str,
    lane: str,
    description: str,
    estimated_cost_usd: float,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Record a paid follow-up as pending. Registration is never permission."""

    directory = _jobs_dir(env)
    directory.mkdir(parents=True, exist_ok=True)
    sequence = len(list(directory.glob(f"{claim_id}-*.json"))) + 1
    job_id = f"{claim_id}-{lane}-{sequence}"
    job = {
        "schema_version": "paid_job.v1",
        "job_id": job_id,
        "claim_id": claim_id,
        "lane": lane,
        "description": description,
        "estimated_cost_usd": round(float(estimated_cost_usd), 2),
        "status": "pending",
        "registered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (directory / f"{job_id}.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
    return job


def load_job(job_id: str, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    path = _jobs_dir(env) / f"{job_id}.json"
    if not path.exists():
        raise PaidGateError([f"no paid job {job_id!r}"])
    return json.loads(path.read_text(encoding="utf-8"))


def list_jobs(env: Mapping[str, str] | None = None) -> list[dict[str, Any]]:
    directory = _jobs_dir(env)
    if not directory.is_dir():
        return []
    jobs = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(directory.glob("*.json"))]
    return sorted(jobs, key=lambda j: (j.get("status") != "pending", j.get("registered_at", "")))


def _audit(env: Mapping[str, str] | None, line: str) -> None:
    directory = _jobs_dir(env).parent
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with (directory / "paid-audit.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {line}\n")


def release_job(
    job_id: str,
    *,
    channel: str,
    chat_id: str | None = None,
    echoed_job_id: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Flip pending → released under the channel's rules. Executes no spend."""

    source = os.environ if env is None else env
    job = load_job(job_id, env)
    config = load_config(env)
    errors: list[str] = []

    if job["status"] != "pending":
        errors.append(f"job {job_id!r} is {job['status']}, not pending")
    if job["lane"] == "flow" and config["flow_queue_paused"]:
        errors.append(
            "the Flow queue is paused; flow-lane jobs refuse release through "
            "any channel until the pause is lifted in config"
        )
    if channel == "telegram":
        allowed_chat = source.get(ENV_TELEGRAM_CHAT)
        ceiling = float(config["telegram_ceiling_usd"])
        if not allowed_chat or chat_id != allowed_chat:
            errors.append("telegram release refused: sender is not the allow-listed chat id")
        if echoed_job_id != job_id:
            errors.append("telegram release refused: the exact job id must be echoed")
        if float(job["estimated_cost_usd"]) > ceiling:
            errors.append(
                f"telegram release refused: ${job['estimated_cost_usd']} exceeds the "
                f"${ceiling} ceiling; release from the machine"
            )
    elif channel != "machine":
        errors.append(f"unknown release channel {channel!r}")

    if errors:
        _audit(env, f"REFUSED {channel} {job_id} ${job.get('estimated_cost_usd')}: {'; '.join(errors)}")
        raise PaidGateError(errors)

    job["status"] = "released"
    job["released_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    job["released_via"] = channel
    (_jobs_dir(env) / f"{job_id}.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
    _audit(env, f"RELEASED {channel} {job_id} ${job['estimated_cost_usd']} ({job['lane']})")
    return job
