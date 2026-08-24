from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.paid_gate import (
    ENV_CONFIG,
    ENV_JOBS_DIR,
    PaidGateError,
    list_jobs,
    load_config,
    register_job,
    release_job,
)
from content.video_engine.watchdog.notify import ENV_TELEGRAM_CHAT
from content.video_engine.watchdog.telegram_approve import process_updates


def _env(tmp_path: Path, *, ceiling: float | None = None, flow_paused: bool = True) -> dict:
    config = tmp_path / "config.json"
    payload: dict = {"flow_queue_paused": flow_paused}
    if ceiling is not None:
        payload["telegram_ceiling_usd"] = ceiling
    config.write_text(json.dumps(payload), encoding="utf-8")
    return {
        ENV_JOBS_DIR: str(tmp_path / "paid-jobs"),
        ENV_CONFIG: str(config),
        ENV_TELEGRAM_CHAT: "777",
    }


def test_registration_is_never_permission(tmp_path):
    env = _env(tmp_path)

    job = register_job(claim_id="batch-one", lane="audio", description="narration",
                       estimated_cost_usd=3.2, env=env)

    assert job["status"] == "pending"
    assert list_jobs(env)[0]["job_id"] == "batch-one-audio-1"


def test_machine_release_works_at_any_cost(tmp_path):
    env = _env(tmp_path)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=250.0, env=env)

    released = release_job(job["job_id"], channel="machine", env=env)

    assert released["status"] == "released"
    assert released["released_via"] == "machine"


def test_telegram_release_holds_under_the_ceiling_and_all_three_rules(tmp_path):
    env = _env(tmp_path, ceiling=5.0)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=4.0, env=env)

    released = release_job(job["job_id"], channel="telegram", chat_id="777",
                           echoed_job_id=job["job_id"], env=env)

    assert released["status"] == "released"


def test_a_spoofed_chat_id_is_refused(tmp_path):
    env = _env(tmp_path)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=1.0, env=env)

    with pytest.raises(PaidGateError) as excinfo:
        release_job(job["job_id"], channel="telegram", chat_id="999",
                    echoed_job_id=job["job_id"], env=env)

    assert "allow-listed" in " ".join(excinfo.value.errors)


def test_a_wrong_job_id_echo_is_refused(tmp_path):
    env = _env(tmp_path)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=1.0, env=env)

    with pytest.raises(PaidGateError) as excinfo:
        release_job(job["job_id"], channel="telegram", chat_id="777",
                    echoed_job_id="c-audio-999", env=env)

    assert "exact job id" in " ".join(excinfo.value.errors)


def test_an_over_ceiling_telegram_attempt_is_refused_toward_the_machine(tmp_path):
    env = _env(tmp_path, ceiling=5.0)
    job = register_job(claim_id="c", lane="video", description="d",
                       estimated_cost_usd=80.0, env=env)

    with pytest.raises(PaidGateError) as excinfo:
        release_job(job["job_id"], channel="telegram", chat_id="777",
                    echoed_job_id=job["job_id"], env=env)

    assert "release from the machine" in " ".join(excinfo.value.errors)


def test_flow_lane_jobs_refuse_release_through_every_channel_while_paused(tmp_path):
    env = _env(tmp_path, flow_paused=True)
    job = register_job(claim_id="c", lane="flow", description="paid video",
                       estimated_cost_usd=1.0, env=env)

    for kwargs in (
        {"channel": "machine"},
        {"channel": "telegram", "chat_id": "777", "echoed_job_id": job["job_id"]},
    ):
        with pytest.raises(PaidGateError) as excinfo:
            release_job(job["job_id"], **kwargs, env=env)
        assert "Flow queue is paused" in " ".join(excinfo.value.errors)


def test_the_flow_pause_defaults_to_paused_when_config_is_absent(tmp_path):
    env = {ENV_CONFIG: str(tmp_path / "missing.json")}

    assert load_config(env)["flow_queue_paused"] is True


def test_every_decision_lands_in_the_audit_log(tmp_path):
    env = _env(tmp_path)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=1.0, env=env)
    release_job(job["job_id"], channel="machine", env=env)
    with pytest.raises(PaidGateError):
        release_job(job["job_id"], channel="machine", env=env)  # already released

    audit = (tmp_path / "paid-audit.log").read_text(encoding="utf-8")

    assert "RELEASED machine c-audio-1" in audit
    assert "REFUSED machine c-audio-1" in audit


def test_inbound_telegram_approval_releases_only_the_operators_exact_command(tmp_path, monkeypatch):
    from content.video_engine.watchdog import telegram_approve as ta

    sent: list[str] = []
    monkeypatch.setattr(ta, "telegram", lambda message, env=None: sent.append(message))
    env = _env(tmp_path, ceiling=5.0)
    job = register_job(claim_id="c", lane="audio", description="d",
                       estimated_cost_usd=2.0, env=env)

    updates = [
        {"update_id": 1, "message": {"chat": {"id": 999}, "text": f"approve {job['job_id']}"}},
        {"update_id": 2, "message": {"chat": {"id": 777}, "text": "hello there"}},
        {"update_id": 3, "message": {"chat": {"id": 777}, "text": f"approve {job['job_id']}"}},
    ]
    outcomes = process_updates(updates, env)

    assert outcomes == [{"job_id": job["job_id"], "released": True}]
    assert "released c-audio-1" in sent[0]
