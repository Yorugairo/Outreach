"""The unattended tick, pinned on the promises the operator is asked to trust it with (P46 T6).

Those promises are: a reply Python can close never costs a token; one that cannot is looked at once, after
the grace window, and only inside the day's budget; nothing is ever announced twice; a restart does not
double-send; and `--dry-run` is a read. Every test builds a repo root in `tmp_path`; nothing here calls
`claude -p`, raises a real toast, reads the live IDE or touches the real `evals/BRIDGE-LOG.jsonl`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_daemon as BD  # noqa: E402
import bridge_env as BE  # noqa: E402

CONFIG = dict(BD.DEFAULTS)


# --------------------------------------------------------------------------- fixtures the tests build on


@pytest.fixture(autouse=True)
def no_real_toast(monkeypatch):
    """Nothing in this file may raise a desktop notification; every test that cares counts the calls."""

    monkeypatch.setattr(BD, "toast", lambda title, body: pytest.fail(f"unexpected toast: {title} / {body}"))


def toasts(monkeypatch) -> list[tuple[str, str]]:
    seen: list[tuple[str, str]] = []
    monkeypatch.setattr(BD, "toast", lambda title, body: bool(seen.append((title, body))))
    return seen


def make_repo(tmp_path: Path) -> Path:
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/research/tech").mkdir(parents=True, exist_ok=True)
    return tmp_path


def landed_header(minutes_ago: float) -> str:
    when = (dt.datetime.now().astimezone() - dt.timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    return f"<!-- lane: gemini; conversationId: c-1; landedAt: {when} -->\n\n"


def replied_packet(repo: Path, packet: str, *, shape: str, reply: str, minutes_ago: float = 0.0) -> Path:
    folder = BE.packet_dir(repo, packet, "replied")
    BE.write_json(folder / "order.json", {"packetId": packet, "lane": "gemini", "replyShape": shape})
    (folder / "reply.md").write_text(landed_header(minutes_ago) + reply, encoding="utf-8")
    return folder


def ledger_rows(repo: Path) -> list[dict]:
    path = repo / BE.LEDGER
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def fake_tier1(calls: list, *, result: str | None = "DECISION: done\nEVIDENCE:\n- docs/x.md:1\n", exit_code: int = 0):
    def runner(repo: Path, folder: Path) -> dict:
        calls.append(folder)
        if result is not None:
            (folder / "result.md").write_text(result, encoding="utf-8")
        return {
            "exit": exit_code,
            "payload": {"usage": {"input_tokens": 1234, "output_tokens": 567}, "total_cost_usd": 0.42},
        }

    return runner


# --------------------------------------------------------------------------- tier 0 closes for free


def test_a_passing_reply_is_closed_to_done_and_ledgered_at_tier_zero(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/note.md").write_text("body\n", encoding="utf-8")
    replied_packet(repo, "p-pass", shape="paths-written", reply="PATHS WRITTEN: docs/research/tech/note.md\n")

    tick = BD.tick_once(repo, CONFIG)

    assert BE.packet_dir(repo, "p-pass", "done").is_dir()
    assert not BE.packet_dir(repo, "p-pass", "replied").exists()
    assert json.loads((BE.packet_dir(repo, "p-pass", "done") / "tier0.json").read_text(encoding="utf-8"))["pass"] is True
    row = ledger_rows(repo)[0]
    assert (row["event"], row["tier"], row["packetId"]) == ("tier0", 0, "p-pass")
    assert tick.summary["tier0_done"] == 1 and tick.summary["tier1_runs"] == 0


def test_a_failing_reply_inside_the_grace_window_is_left_alone(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    calls: list = []
    monkeypatch.setattr(BD, "run_tier1", fake_tier1(calls))
    folder = replied_packet(repo, "p-young", shape="paths-written", reply="PATHS WRITTEN: docs/ghost.md\n", minutes_ago=1)

    tick = BD.tick_once(repo, CONFIG)

    assert calls == [], "nothing is dispatched before the grace window closes"
    assert json.loads((folder / "tier0.json").read_text(encoding="utf-8"))["pass"] is False
    assert not (folder / "tier1.json").exists() and folder.is_dir()
    assert ledger_rows(repo) == [] and tick.summary["tier1_runs"] == 0


# --------------------------------------------------------------------------- tier 1, exactly once


def test_a_failure_past_the_grace_window_is_dispatched_once_and_lands_in_done(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    calls: list = []
    monkeypatch.setattr(BD, "run_tier1", fake_tier1(calls))
    replied_packet(repo, "p-residue", shape="paths-written", reply="PATHS WRITTEN: docs/ghost.md\n", minutes_ago=45)

    BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert len(calls) == 1, "the residue is looked at once, never on every tick"
    done = BE.packet_dir(repo, "p-residue", "done")
    tier1 = json.loads((done / "tier1.json").read_text(encoding="utf-8"))
    assert tier1["exit"] == 0 and tier1["usage"] == {"input_tokens": 1234, "output_tokens": 567, "total_cost_usd": 0.42}
    assert tier1["resultPath"].endswith("result.md") and tier1["startedAt"] and tier1["finishedAt"]
    rows = [r for r in ledger_rows(repo) if r["event"] == "tier1"]
    assert len(rows) == 1
    assert (rows[0]["tier"], rows[0]["inputTokens"], rows[0]["outputTokens"]) == (1, 1234, 567)
    assert rows[0]["decision"] == "done" and rows[0]["costUsd"] == 0.42


def test_usage_the_run_did_not_report_is_null_and_never_zero(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(BD, "run_tier1", lambda repo_, folder: {"exit": 0, "payload": {}})
    replied_packet(repo, "p-nousage", shape="free", reply="whatever\n", minutes_ago=45)

    BD.tick_once(repo, CONFIG)

    folder = BE.packet_dir(repo, "p-nousage", "replied")
    assert json.loads((folder / "tier1.json").read_text(encoding="utf-8"))["usage"] is None
    row = [r for r in ledger_rows(repo) if r["event"] == "tier1"][0]
    assert row["inputTokens"] is None and row["outputTokens"] is None


def test_the_handlers_own_escalation_raises_exactly_one_toast(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BD, "run_tier1", fake_tier1([], result="DECISION: escalate\nQUESTION: ship or not?\n"))
    replied_packet(repo, "p-escalate", shape="free", reply="whatever\n", minutes_ago=45)

    BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert len(seen) == 1, "one toast per packet per condition"
    rows = [r for r in ledger_rows(repo) if r["event"] == "escalated"]
    assert len(rows) == 1 and rows[0]["reason"] == "handler-escalate"


# --------------------------------------------------------------------------- the budget


def test_a_spent_residue_budget_stops_the_dispatch_and_says_so_once(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    for _ in range(int(CONFIG["residue_runs_per_day"])):
        BE.ledger_append(repo, {"event": "tier1", "tier": 1, "packetId": "earlier", "inputTokens": 10, "outputTokens": 5})
    calls: list = []
    monkeypatch.setattr(BD, "run_tier1", fake_tier1(calls))
    replied_packet(repo, "p-broke", shape="paths-written", reply="PATHS WRITTEN: docs/ghost.md\n", minutes_ago=45)

    tick = BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert calls == [], "the budget is spent, so no model is called"
    assert tick.summary["skipped_budget"] == 1
    assert len(seen) == 1 and "residue runs used today" in seen[0][1]
    rows = [r for r in ledger_rows(repo) if r["event"] == "escalated"]
    assert len(rows) == 1 and rows[0]["reason"] == "budget"


def test_the_token_cap_binds_as_well_as_the_run_count(tmp_path):
    repo = make_repo(tmp_path)
    BE.ledger_append(repo, {"event": "tier1", "tier": 1, "packetId": "big", "inputTokens": 199_000, "outputTokens": 2_000})

    assert "residue tokens used today" in (BD.budget_spent(repo, CONFIG) or "")


def test_yesterdays_runs_do_not_count_against_today(tmp_path):
    repo = make_repo(tmp_path)
    path = repo / BE.LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    old = {"ts": "2020-01-01T00:00:00", "event": "tier1", "inputTokens": 999_999, "outputTokens": 1}
    path.write_text(json.dumps(old) + "\n", encoding="utf-8")

    assert BD.budget_spent(repo, CONFIG) is None
    assert BD.todays_tier1(repo) == {"runs": 0, "tokens": 0}


# --------------------------------------------------------------------------- the SLA


def test_a_reply_open_past_the_sla_toasts_once_and_not_again(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BD, "run_tier1", fake_tier1([], result=None))  # the handler writes nothing back
    replied_packet(repo, "p-stale", shape="free", reply="whatever\n", minutes_ago=90)

    BD.tick_once(repo, CONFIG)
    second = BD.tick_once(repo, CONFIG)

    assert len(seen) == 1 and "SLA" in seen[0][1]
    assert second.summary["escalated"] == 0, "the marker file stops the repeat"
    marker = json.loads((BE.packet_dir(repo, "p-stale", "replied") / "escalated.json").read_text(encoding="utf-8"))
    assert list(marker["reasons"]) == ["sla"]


# --------------------------------------------------------------------------- the lock


def test_a_lock_held_by_a_dead_pid_is_reclaimed(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    BE.write_json(repo / BD.LOCK_PATH, {"pid": 999_999_999, "startedAt": "2020-01-01T00:00:00"})
    monkeypatch.setattr(BD, "pid_alive", lambda pid: False)

    assert BD.main(["--once", "--repo", str(repo)]) == 0
    assert not (repo / BD.LOCK_PATH).exists(), "the tick releases what it took"


def test_a_lock_held_by_a_live_pid_refuses_the_tick(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    BE.write_json(repo / BD.LOCK_PATH, {"pid": 4242, "startedAt": "2026-09-06T00:00:00"})
    monkeypatch.setattr(BD, "pid_alive", lambda pid: True)

    assert BD.main(["--once", "--repo", str(repo)]) == 1


def test_this_very_process_is_alive_and_a_nonsense_pid_is_not():
    assert BD.pid_alive(os.getpid()) is True
    assert BD.pid_alive(0) is False


# --------------------------------------------------------------------------- a dry run is a read


def test_a_dry_run_changes_not_one_byte(tmp_path, capsys):
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/note.md").write_text("body\n", encoding="utf-8")
    BE.write_json(
        BE.packet_dir(repo, "p-queued", "queue") / "order.json",
        {"packetId": "p-queued", "lane": "gemini", "replyShape": "free", "brief": "x"},
    )
    sent = BE.packet_dir(repo, "p-sent", "sent")
    BE.write_json(sent / "order.json", {"packetId": "p-sent", "lane": "gemini", "replyShape": "free"})
    BE.write_json(sent / "conversation.json", {"conversationId": "c-1", "lane": "gemini"})
    replied_packet(repo, "p-pass", shape="paths-written", reply="PATHS WRITTEN: docs/research/tech/note.md\n")
    before = snapshot(repo)

    assert BD.main(["--once", "--dry-run", "--json", "--repo", str(repo)]) == 0

    assert snapshot(repo) == before, "a dry run sends, moves, dispatches, toasts and ledgers nothing"
    assert not (repo / BD.LOCK_PATH).exists(), "not even the lock"
    summary = json.loads(capsys.readouterr().out)
    assert summary == {"sent": 1, "watched": 1, "tier0_done": 0, "tier1_runs": 0, "escalated": 0, "skipped_budget": 0}


def test_a_dry_run_prints_the_toast_instead_of_raising_one(tmp_path):
    repo = make_repo(tmp_path)
    folder = replied_packet(repo, "p-stale", shape="free", reply="whatever\n", minutes_ago=90)
    before = snapshot(repo)

    tick = BD.tick_once(repo, CONFIG, dry_run=True)

    assert any(line.startswith("TOAST: bridge sla") for line in tick.lines)
    assert tick.summary["escalated"] == 1
    assert snapshot(repo) == before and not (folder / "escalated.json").exists()


def test_a_dry_run_says_what_it_would_send_and_check(tmp_path):
    repo = make_repo(tmp_path)
    BE.write_json(
        BE.packet_dir(repo, "p-queued", "queue") / "order.json",
        {"packetId": "p-queued", "lane": "gemini", "replyShape": "review", "brief": "x"},
    )
    replied_packet(repo, "p-open", shape="review", reply="POSITION: conditional\n")

    lines = BD.tick_once(repo, CONFIG, dry_run=True).lines

    assert any(line.startswith("SEND p-queued") and "dry-run" in line for line in lines)
    assert any(line.startswith("TIER0 p-open") for line in lines)


# --------------------------------------------------------------------------- sending and watching


def test_a_queued_order_is_sent_and_a_follow_up_continues_its_conversation(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    sends: list = []
    monkeypatch.setattr(BD, "send_packet", lambda tick, folder, order: sends.append(order) or {"status": "sent"})
    BE.write_json(
        BE.packet_dir(repo, "p-new", "queue") / "order.json",
        {"packetId": "p-new", "lane": "gemini", "replyShape": "review", "brief": "x"},
    )
    BE.write_json(
        BE.packet_dir(repo, "p-follow", "queue") / "order.json",
        {"packetId": "p-follow", "lane": "gemini", "from": "claude", "conversationId": "c-1", "brief": "y"},
    )

    tick = BD.tick_once(repo, CONFIG)

    assert tick.summary["sent"] == 2
    assert [o["packetId"] for o in sends] == ["p-follow", "p-new"]


def test_a_packet_already_sent_is_never_sent_twice(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(BD, "send_packet", lambda tick, folder, order: pytest.fail("re-sent a packet that went out"))
    folder = BE.packet_dir(repo, "p-again", "queue")
    BE.write_json(folder / "order.json", {"packetId": "p-again", "lane": "gemini", "brief": "x"})
    BE.write_json(folder / "conversation.json", {"conversationId": "c-9"})

    assert BD.tick_once(repo, CONFIG).summary["sent"] == 0


def test_a_watched_timeout_escalates_once_then_the_packet_is_read_as_a_replay(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    modes: list[bool] = []

    def fake_watch(tick, packet, lane, ident, once=True):
        modes.append(once)
        return {"watch": {"status": "timeout" if once else "working"}}

    monkeypatch.setattr(BD, "watch_packet", fake_watch)
    folder = BE.packet_dir(repo, "p-late", "sent")
    BE.write_json(folder / "order.json", {"packetId": "p-late", "lane": "gemini", "replyShape": "free"})
    BE.write_json(folder / "conversation.json", {"conversationId": "c-1", "lane": "gemini"})

    BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert modes == [True, False], "once the timeout is recorded the watcher stops re-recording it"
    assert len(seen) == 1
    assert [r["reason"] for r in ledger_rows(repo) if r["event"] == "escalated"] == ["timeout"]


def test_a_sent_packet_with_no_conversation_id_is_reported_not_crashed(tmp_path):
    repo = make_repo(tmp_path)
    BE.write_json(BE.packet_dir(repo, "p-orphan", "sent") / "order.json", {"packetId": "p-orphan", "lane": "gemini"})

    tick = BD.tick_once(repo, CONFIG)

    assert tick.summary["watched"] == 0
    assert any("WATCH-SKIP" in line for line in tick.lines)


# --------------------------------------------------------------------------- config and results


def test_the_config_file_overrides_only_the_keys_it_names(tmp_path):
    path = tmp_path / "bridge-config.json"
    path.write_text(json.dumps({"grace_min": 3, "unknown": 1}), encoding="utf-8")

    config = BD.load_config(path)

    assert config["grace_min"] == 3 and config["sla_min"] == BD.DEFAULTS["sla_min"]
    assert "unknown" not in config


def test_an_absent_config_file_is_not_an_error(tmp_path):
    assert BD.load_config(tmp_path / "nothing.json") == BD.DEFAULTS


def test_a_result_written_straight_into_done_is_merged_not_lost(tmp_path):
    repo = make_repo(tmp_path)
    folder = replied_packet(repo, "p-merge", shape="free", reply="whatever\n")
    done = BE.packet_dir(repo, "p-merge", "done")
    done.mkdir(parents=True, exist_ok=True)
    (done / "result.md").write_text("DECISION: follow-up\n", encoding="utf-8")

    result_path, landed = BD.land_result(repo, "p-merge", folder)

    assert landed == done and not folder.exists()
    assert (done / "order.json").exists() and (done / "reply.md").exists()
    assert BD.decision_of(result_path) == "follow-up"
