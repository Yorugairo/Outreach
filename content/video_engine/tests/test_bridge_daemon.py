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
    assert summary == {"sent": 1, "watched": 1, "tier0_done": 0, "tier1_runs": 0, "escalated": 0, "skipped_budget": 0, "repairs": 0}


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


# ---- a replied packet with a passing prior verdict moves to done on the next tick, with no re-check ----
def test_a_replied_packet_with_a_passing_prior_verdict_is_moved_not_rechecked(tmp_path, monkeypatch):
    import json
    import bridge_daemon as D
    import bridge_env as E
    pid = "p-prior"
    folder = E.packet_dir(tmp_path, pid, "replied"); folder.mkdir(parents=True)
    (folder / "order.json").write_text(json.dumps({"packetId": pid, "lane": "gemini", "replyShape": "paths-written"}), encoding="utf-8")
    (folder / "reply.md").write_text("POSITION: done\nPATHS WRITTEN: none\n", encoding="utf-8")
    (folder / "tier0.json").write_text(json.dumps({"pass": True, "shape": "paths-written", "reason": "", "checks": []}), encoding="utf-8")
    called = []
    monkeypatch.setattr(D.handlers, "classify", lambda *a, **k: called.append(1))
    tick = D.Tick(repo=tmp_path, config=D.load_config(None), dry_run=False)
    D.step_tier0(tick)
    assert not called
    assert not folder.exists() and E.packet_dir(tmp_path, pid, "done").exists()


# --------------------------------------------------------------------------- R26-354: a report with no verdict up front, one repair


def test_a_report_with_no_verdict_up_front_queues_one_form_repair_and_only_one(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/report.md").write_text(
        "# R\n\n[Adoption | 41% | Acme | URL: https://example.com/x | Verified 2026-09-06]\n\n## NOT FOUND WHERE I LOOKED\n- roots\n",
        encoding="utf-8")
    monkeypatch.setattr(BD.handlers, "run_layers", lambda r: pytest.fail("no layer regen for a report with no verdict"))
    folder = replied_packet(repo, "p-noverdict", shape="report-landed", reply="PATHS WRITTEN:\ndocs/research/tech/report.md\n")
    BE.write_json(folder / "conversation.json", {"packetId": "p-noverdict", "conversationId": "c-1", "lane": "gemini"})

    BD.step_tier0(BD.Tick(repo, dict(CONFIG)))
    (folder / "tier0.json").unlink()   # re-checked on a later tick: the repair marker still stops a second repair
    BD.step_tier0(BD.Tick(repo, dict(CONFIG)))

    tier0 = json.loads((folder / "tier0.json").read_text(encoding="utf-8"))
    assert not tier0["pass"] and tier0["class"] == "form" and "Verdict up front" in tier0["reason"]
    assert (folder / BD.REPAIR_MARKER).exists() and len(BD.packets(repo, "queue")) == 1
    assert [r["event"] for r in ledger_rows(repo)] == ["repair"]


# --------------------------------------------------------------------------- R26-355: the astra lane reads its own reply.md


BRIEF = "# ORDER - from the parent to Astra\n\nDo the thing, then write reply.md in this folder.\n"


def _iso(when: dt.datetime) -> str:
    return when.isoformat(timespec="seconds")


def days_ago(days: float) -> dt.datetime:
    return dt.datetime.now().astimezone() - dt.timedelta(days=days)


def astra_sent(repo: Path, packet: str, *, reply: str | None, replied_at: dt.datetime, created_at: dt.datetime,
               followups: tuple = ()) -> Path:
    """An astra packet as the live ones sit: the order handed over by hand, the lane's reply.md written into the folder."""
    folder = BE.packet_dir(repo, packet, "sent")
    order = {"packetId": packet, "lane": "astra", "from": "claude", "replyShape": "paths-written", "brief": BRIEF,
             "createdAt": _iso(created_at), "deadline": _iso(created_at + dt.timedelta(days=1))}
    conversation = {"packetId": packet, "conversationId": "01a0c089-9991-7f51-84ed-a709555b08fa", "lane": "astra"}
    for number, (sent_at, body) in enumerate(followups, start=1):
        path = folder / "followups" / f"{number:02d}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"<!-- sentAt: {_iso(sent_at)}; lane: astra; conversationId: {conversation['conversationId']} -->\n{body}",
                        encoding="utf-8")
        order.update(followups=number, lastFollowupAt=_iso(sent_at))
        conversation.update(sentAt=_iso(sent_at), followup=number)
    BE.write_json(folder / "order.json", order)
    BE.write_json(folder / "conversation.json", conversation)
    (folder / "brief.md").write_text(BRIEF, encoding="utf-8")
    os.utime(folder / "brief.md", (created_at.timestamp(), created_at.timestamp()))
    if reply is not None:
        (folder / "reply.md").write_text(reply, encoding="utf-8")
        os.utime(folder / "reply.md", (replied_at.timestamp(), replied_at.timestamp()))
    return folder


def astra_reply(repo: Path, packet: str, written: str = "docs/research/tech/note.md") -> str:
    own = (repo / BE.BRIDGE_ROOT / "queue" / packet / "EXECUTION.md").as_posix()
    return f"POSITION: done\nPATHS WRITTEN:\n{(repo / written).as_posix()}\n{own}\nDISAGREEMENTS:\n- none\n"


def test_an_astra_packet_lands_from_its_own_reply_md_and_tier_zero_runs_on_the_same_tick(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/note.md").write_text("body\n", encoding="utf-8")
    text = astra_reply(repo, "a1b2c3d4e5f6")
    folder = astra_sent(repo, "a1b2c3d4e5f6", reply=text, replied_at=days_ago(3), created_at=days_ago(3.1))
    (folder / "EXECUTION.md").write_text("what I did\n", encoding="utf-8")

    tick = BD.tick_once(repo, CONFIG)

    done = BE.packet_dir(repo, "a1b2c3d4e5f6", "done")
    assert done.is_dir() and not folder.exists(), tick.lines
    assert (done / "reply.md").read_text(encoding="utf-8") == text, "the lane's own file is never rewritten"
    watch = json.loads((done / "watch.json").read_text(encoding="utf-8"))
    assert watch["lane"] == "astra" and watch["status"] == "done" and watch["source"] == "reply.md"
    assert watch["provenance"] and all(c["ok"] for c in watch["provenance"])
    assert json.loads((done / "tier0.json").read_text(encoding="utf-8"))["pass"] is True
    assert [(r["event"], r["lane"]) for r in ledger_rows(repo)] == [("replied", "astra"), ("tier0", "astra")]
    assert tick.summary["watched"] == 1 and tick.summary["tier0_done"] == 1


def test_a_resend_of_the_orders_own_brief_is_not_a_new_ask(tmp_path):
    """The live case: at 02:17 on 09-25 the old daemon re-sent three 09-22 astra orders through the Gemini send (R26-340 F6) -
    `followups/01.md` is the order's brief verbatim, so a reply written before it still answers the order."""
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/note.md").write_text("body\n", encoding="utf-8")
    folder = astra_sent(repo, "b1b2c3d4e5f6", reply=astra_reply(repo, "b1b2c3d4e5f6"), replied_at=days_ago(3),
                        created_at=days_ago(3.1), followups=((days_ago(0.4), BRIEF),))
    (folder / "EXECUTION.md").write_text("what I did\n", encoding="utf-8")

    tick = BD.tick_once(repo, CONFIG)

    assert BE.packet_dir(repo, "b1b2c3d4e5f6", "done").is_dir() and not folder.exists(), tick.lines


def test_an_astra_reply_older_than_a_new_follow_up_is_stale_and_reported_once(tmp_path, monkeypatch):
    seen = toasts(monkeypatch)
    repo = make_repo(tmp_path)
    folder = astra_sent(repo, "c1b2c3d4e5f6", reply=astra_reply(repo, "c1b2c3d4e5f6"), replied_at=days_ago(3),
                        created_at=days_ago(3.1), followups=((days_ago(1), "A NEW ASK: also fix the gate.\n"),))

    first = BD.tick_once(repo, CONFIG)
    second = BD.tick_once(repo, CONFIG)

    assert folder.is_dir() and not BE.packet_dir(repo, "c1b2c3d4e5f6", "replied").exists(), "never landed"
    assert any("REPLY-REFUSED" in l and "predates" in l for l in first.lines), first.lines
    assert not any("REPLY-REFUSED" in l for l in second.lines), "reported once"
    assert [r["reason"] for r in ledger_rows(repo) if r["event"] == "escalated"] == ["unproven-reply"]
    assert len(seen) == 1 and "c1b2c3d4e5f6" in seen[0][1]
    assert json.loads((folder / "provenance.json").read_text(encoding="utf-8"))["status"] == "refused"


def test_an_astra_reply_that_predates_its_order_is_stale(tmp_path, monkeypatch):
    toasts(monkeypatch)
    repo = make_repo(tmp_path)
    folder = astra_sent(repo, "d1b2c3d4e5f6", reply=astra_reply(repo, "d1b2c3d4e5f6"), replied_at=days_ago(4),
                        created_at=days_ago(3))

    tick = BD.tick_once(repo, CONFIG)

    assert folder.is_dir(), tick.lines
    assert any("REPLY-REFUSED" in l and "predates" in l for l in tick.lines), tick.lines


def test_an_astra_reply_written_by_another_lanes_watcher_is_refused(tmp_path, monkeypatch):
    toasts(monkeypatch)
    repo = make_repo(tmp_path)
    header = f"<!-- lane: gemini; conversationId: c-1; landedAt: {_iso(days_ago(3))} -->\n\n"
    folder = astra_sent(repo, "e1b2c3d4e5f6", reply=header + astra_reply(repo, "e1b2c3d4e5f6"), replied_at=days_ago(3),
                        created_at=days_ago(3.1))

    tick = BD.tick_once(repo, CONFIG)

    assert folder.is_dir()
    assert any("REPLY-REFUSED" in l and "gemini" in l for l in tick.lines), tick.lines


def test_an_astra_reply_that_never_names_its_packet_is_refused(tmp_path, monkeypatch):
    toasts(monkeypatch)
    repo = make_repo(tmp_path)
    folder = astra_sent(repo, "f1b2c3d4e5f6", reply="POSITION: done\nPATHS WRITTEN:\n- none\n", replied_at=days_ago(3),
                        created_at=days_ago(3.1))

    tick = BD.tick_once(repo, CONFIG)

    assert folder.is_dir()
    assert any("REPLY-REFUSED" in l and "never names" in l for l in tick.lines), tick.lines


def test_an_astra_reply_that_wrote_into_another_packets_folder_is_refused(tmp_path, monkeypatch):
    toasts(monkeypatch)
    repo = make_repo(tmp_path)
    other = (repo / BE.BRIDGE_ROOT / "queue" / "999999999999" / "reply.md").as_posix()
    reply = astra_reply(repo, "a2b2c3d4e5f6").replace("DISAGREEMENTS", f"{other}\nDISAGREEMENTS")
    folder = astra_sent(repo, "a2b2c3d4e5f6", reply=reply, replied_at=days_ago(3), created_at=days_ago(3.1))

    tick = BD.tick_once(repo, CONFIG)

    assert folder.is_dir()
    assert any("REPLY-REFUSED" in l and "999999999999" in l for l in tick.lines), tick.lines


def test_an_astra_packet_with_no_reply_yet_waits_and_times_out_once(tmp_path, monkeypatch):
    seen = toasts(monkeypatch)
    repo = make_repo(tmp_path)
    waiting = astra_sent(repo, "a3b2c3d4e5f6", reply=None, replied_at=days_ago(0), created_at=days_ago(0.01))
    late = astra_sent(repo, "a4b2c3d4e5f6", reply=None, replied_at=days_ago(0), created_at=days_ago(3))

    first = BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert waiting.is_dir() and late.is_dir()
    assert any("WAIT a3b2c3d4e5f6" in l for l in first.lines), first.lines
    assert [(r["packetId"], r.get("reason")) for r in ledger_rows(repo)] == [("a4b2c3d4e5f6", "timeout")]
    assert len(seen) == 1 and not (waiting / "watch-skip.json").exists()


def test_three_astra_landings_toast_nothing_and_their_sla_is_one_summary(tmp_path, monkeypatch):
    """R26-340's rule holds: the three replies of 09-22 land today, so the SLA counts from the landing (no toast at once),
    and when it passes the three escalations are ONE summary toast."""
    seen = toasts(monkeypatch)
    repo = make_repo(tmp_path)
    ids = ["b5b2c3d4e5f6", "b6b2c3d4e5f6", "b7b2c3d4e5f6"]
    for packet in ids:   # each names a file that is not there: tier 0 fails, the packet waits in replied/
        astra_sent(repo, packet, reply=astra_reply(repo, packet, "docs/research/tech/missing.md"), replied_at=days_ago(3),
                   created_at=days_ago(3.1))
    config = {**CONFIG, "grace_min": 10_000}

    first = BD.tick_once(repo, config)
    assert [BE.packet_dir(repo, p, "replied").is_dir() for p in ids] == [True] * 3, first.lines
    assert seen == [], "the landing itself toasts nothing"

    later = dt.datetime.now().astimezone() + dt.timedelta(hours=2)
    monkeypatch.setattr(BD, "now", lambda: later)
    BD.tick_once(repo, config)

    assert len(seen) == 1 and seen[0][0] == "Bridge: 3 escalations" and "3 sla" in seen[0][1], seen


def test_a_form_failure_on_a_lane_with_no_sender_queues_no_repair(tmp_path):
    repo = make_repo(tmp_path)
    folder = BE.packet_dir(repo, "a8b2c3d4e5f6", "replied")
    BE.write_json(folder / "order.json", {"packetId": "a8b2c3d4e5f6", "lane": "astra", "replyShape": "paths-written"})
    BE.write_json(folder / "conversation.json", {"packetId": "a8b2c3d4e5f6", "conversationId": "c-1", "lane": "astra"})
    (folder / "reply.md").write_text("I did it, see the links: [`a.md`](a.md)\n", encoding="utf-8")

    tick = BD.Tick(repo, dict(CONFIG))
    BD.step_tier0(tick)

    assert json.loads((folder / "tier0.json").read_text(encoding="utf-8"))["class"] == "form"
    assert not (folder / BD.REPAIR_MARKER).exists() and BD.packets(repo, "queue") == []
    assert any("REPAIR-SKIP" in l and "no sender" in l for l in tick.lines), tick.lines


def test_a_dry_run_proves_an_astra_reply_and_moves_nothing(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "docs/research/tech/note.md").write_text("body\n", encoding="utf-8")
    astra_sent(repo, "a9b2c3d4e5f6", reply=astra_reply(repo, "a9b2c3d4e5f6"), replied_at=days_ago(3), created_at=days_ago(3.1))
    before = snapshot(repo)

    tick = BD.tick_once(repo, CONFIG, dry_run=True)

    assert snapshot(repo) == before
    assert any("LAND a9b2c3d4e5f6" in l and "dry-run" in l for l in tick.lines), tick.lines
