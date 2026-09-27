"""R26-340: the bridge's restart burst and the packets it lost (2026-09-25, "the bridge is freaking out").

The daemon came back after days down, fired 10 toasts in 15 minutes and spent the day's six tier-1 runs. Each test
here pins one of the seven defects the triage found, on a repo built in `tmp_path`: no test calls `claude -p`,
raises a real toast, reads the live IDE or touches the real `evals/BRIDGE-LOG.jsonl`.

  1. toasts grouped per tick; the budget toast once a day
  2. the conversation id read from agentapi's stdout, and recovered from a sent packet's stored stdout on a restart
  3. a follow-up's reply must post-date the follow-up (no echo of the original's text)
  4. no repair for a failure a repair cannot fix (a cut outside a whole paths block; an order defect)
  5. an original is closed whenever its repair closes, by any route
  6. a lane with no watcher (now any lane but gemini / claude / astra) or no sender (astra) is skipped / refused once,
     never argparse-failed every tick
  7. a reply path outside the order's roots fails tier 0 with its own class; the order names the output root
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_check as BC  # noqa: E402
import bridge_daemon as BD  # noqa: E402
import bridge_env as BE  # noqa: E402
import bridge_reply as BR  # noqa: E402
import bridge_send as BS  # noqa: E402
import bridge_watch as BW  # noqa: E402

CONFIG = dict(BD.DEFAULTS)
CONV = "7c7d69bb-e1ee-4fac-84b4-87d3ae15788f"


# --------------------------------------------------------------------------- fixtures


@pytest.fixture(autouse=True)
def no_real_toast(monkeypatch):
    monkeypatch.setattr(BD, "toast", lambda title, body: pytest.fail(f"unexpected toast: {title} / {body}"))


def toasts(monkeypatch) -> list[tuple[str, str]]:
    seen: list[tuple[str, str]] = []
    monkeypatch.setattr(BD, "toast", lambda title, body: bool(seen.append((title, body))))
    return seen


def make_repo(tmp_path: Path) -> Path:
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    return tmp_path


def landed(minutes_ago: float) -> str:
    when = (dt.datetime.now().astimezone() - dt.timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    return f"<!-- lane: gemini; conversationId: c-9; landedAt: {when} -->\n\n"


def replied(repo: Path, packet: str, order: dict, reply: str, minutes_ago: float = 0.0, conversation: str | None = "c-9") -> Path:
    folder = BE.packet_dir(repo, packet, "replied")
    BE.write_json(folder / "order.json", {"packetId": packet, "lane": "gemini", **order})
    if conversation:
        BE.write_json(folder / "conversation.json", {"packetId": packet, "conversationId": conversation})
    (folder / "reply.md").write_text(landed(minutes_ago) + reply, encoding="utf-8")
    return folder


def rows(repo: Path) -> list[dict]:
    path = repo / BE.LEDGER
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def tick(repo: Path, dry_run: bool = False) -> BD.Tick:
    return BD.Tick(repo=repo, config=dict(CONFIG), dry_run=dry_run)


def grammar(*paths: str, tail: str = "") -> str:
    return ("POSITION: done\nPATHS WRITTEN:\n" + "\n".join(paths) + "\nDISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\n"
            "NOT FOUND WHERE I LOOKED:\n- none\n" + tail)


def spend_budget(repo: Path) -> None:
    for _ in range(int(CONFIG["residue_runs_per_day"])):
        BE.ledger_append(repo, {"event": "tier1", "tier": 1, "packetId": "earlier", "inputTokens": 10, "outputTokens": 5})


# --------------------------------------------------------------------------- 1. toasts per tick


def test_fix1_a_tick_with_many_escalations_fires_one_summary_toast(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BD, "run_tier1", lambda *a: pytest.fail("no tier 1 on a spent budget"))
    for n in range(5):
        replied(repo, f"p-sla{n}", {"replyShape": "free"}, "whatever\n", minutes_ago=90)
        BE.write_json(BE.packet_dir(repo, f"p-sla{n}", "replied") / "tier1.json", {"exit": 0})   # tier 1 already looked
        BE.write_json(BE.packet_dir(repo, f"p-sla{n}", "replied") / "tier0.json", {"pass": False, "class": "substance", "checks": []})

    BD.tick_once(repo, CONFIG)

    assert len(seen) == 1, f"one summary toast, not {len(seen)}: {seen}"
    title, body = seen[0]
    assert "5" in title and "5 sla" in body
    assert "p-sla0" in body and "p-sla2" in body and "p-sla3" not in body, "the first three ids, no more"
    escalated = [r for r in rows(repo) if r["event"] == "escalated"]
    assert len(escalated) == 5, "every packet keeps its own ledger line"
    for n in range(5):
        assert (BE.packet_dir(repo, f"p-sla{n}", "replied") / "escalated.json").exists(), "and its own marker"


def test_fix1_two_escalations_in_a_tick_still_toast_singly(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    for n in range(2):
        replied(repo, f"p-two{n}", {"replyShape": "free"}, "whatever\n", minutes_ago=90)
        BE.write_json(BE.packet_dir(repo, f"p-two{n}", "replied") / "tier1.json", {"exit": 0})
        BE.write_json(BE.packet_dir(repo, f"p-two{n}", "replied") / "tier0.json", {"pass": False, "class": "substance", "checks": []})

    BD.tick_once(repo, CONFIG)

    assert len(seen) == 2 and all("sla" in t for t, _ in seen)


def test_fix1_the_budget_toast_fires_once_a_day_across_packets_and_ticks(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    spend_budget(repo)
    for n in range(3):
        replied(repo, f"p-broke{n}", {"replyShape": "paths-written"}, "PATHS WRITTEN: docs/ghost.md\n", minutes_ago=30,
                conversation=None)
    BD.tick_once(repo, CONFIG)
    replied(repo, "p-broke-later", {"replyShape": "paths-written"}, "PATHS WRITTEN: docs/ghost.md\n", minutes_ago=30,
            conversation=None)
    BD.tick_once(repo, CONFIG)

    budget = [t for t in seen if "budget" in t[0]]
    assert len(budget) == 1, f"the budget is told once a day, not per packet: {seen}"
    budget_rows = [r for r in rows(repo) if r["event"] == "escalated" and r["reason"] == "budget"]
    assert len(budget_rows) == 4, "each packet still ledgers its own budget escalation"


def test_fix1_a_dry_run_prints_one_summary_toast_line(tmp_path):
    repo = make_repo(tmp_path)
    for n in range(4):
        replied(repo, f"p-dry{n}", {"replyShape": "free"}, "whatever\n", minutes_ago=90)
        BE.write_json(BE.packet_dir(repo, f"p-dry{n}", "replied") / "tier1.json", {"exit": 0})
        BE.write_json(BE.packet_dir(repo, f"p-dry{n}", "replied") / "tier0.json", {"pass": False, "class": "substance", "checks": []})

    lines = BD.tick_once(repo, CONFIG, dry_run=True).lines

    assert len([l for l in lines if l.startswith("TOAST")]) == 1, lines


# --------------------------------------------------------------------------- 2. the conversation id


AGENTAPI_STDOUT = json.dumps({"response": {"newConversation": {"prompt": "a long prompt " * 400, "conversationId": CONV}}},
                             indent=2)


def test_fix2_the_conversation_id_is_read_from_agentapis_stdout():
    assert BS.conversation_from_stdout(AGENTAPI_STDOUT) == CONV
    assert BS.conversation_from_stdout("prompt echoed") is None
    # a stdout stored cut at 4000 characters still yields the id when its tail survives; a half id never does
    cut = AGENTAPI_STDOUT[:4000]
    assert BS.conversation_from_stdout(cut) is None
    assert BS.conversation_from_stdout(AGENTAPI_STDOUT[:-30]) is None, "an id cut short is no id"


def test_fix2_send_gemini_takes_the_stdout_id_over_the_file_time_guess(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(BE, "discover_gemini_env", lambda **k: {"ANTIGRAVITY_LS_ADDRESS": "127.0.0.1:1", "ANTIGRAVITY_CSRF_TOKEN": "t" * 16})
    monkeypatch.setattr(BE, "ensure_registered", lambda repo: {"projects_added": False, "trusted_added": False})
    monkeypatch.setattr(BE, "agentapi_command", lambda env, args: ["agy.exe", "agentapi", *args])
    monkeypatch.setattr(BE, "newest_conversation", lambda **k: "the-file-time-guess")

    class Proc:
        returncode, stdout, stderr = 0, AGENTAPI_STDOUT, ""

    monkeypatch.setattr(BS.subprocess, "run", lambda *a, **k: Proc())
    order = {"packetId": "p-id", "title": "t", "brief": "b", "replyShape": "free"}
    folder = BE.packet_dir(repo, "p-id", "queue")
    BE.write_json(folder / "order.json", order)
    args = BD.SimpleNamespace(lane="gemini", repo=repo, dry_run=False, model=None, profile=None)

    result = BS.send_gemini(args, order, folder, [])

    assert result["conversationId"] == CONV
    record = json.loads((BE.packet_dir(repo, "p-id", "sent") / "conversation.json").read_text(encoding="utf-8"))
    assert record["conversationId"] == CONV and record.get("conversationIdSource") == "stdout"


def test_fix2_a_restart_recovers_a_null_id_from_the_packets_own_stdout(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    watched: list[str] = []
    monkeypatch.setattr(BD, "watch_packet", lambda t, packet, lane, ident, once=True: watched.append(ident) or {"watch": {"status": "working"}})
    folder = BE.packet_dir(repo, "p-null", "sent")
    BE.write_json(folder / "order.json", {"packetId": "p-null", "lane": "gemini", "replyShape": "free"})
    BE.write_json(folder / "conversation.json", {"packetId": "p-null", "conversationId": None, "stdout": AGENTAPI_STDOUT[-3000:]})

    BD.tick_once(repo, CONFIG)

    record = json.loads((folder / "conversation.json").read_text(encoding="utf-8"))
    assert record["conversationId"] == CONV
    assert "stdout" in record["conversationIdRecoveredFrom"]
    assert watched == [CONV], "the recovered id is watched on the same tick"


# --------------------------------------------------------------------------- 3. the echo guard


def _planner(content: str, at: str) -> dict:
    return {"type": "PLANNER_RESPONSE", "status": "DONE", "content": content, "tool_calls": None, "created_at": at}


def test_fix3_a_reply_older_than_the_follow_up_is_not_its_reply():
    records = [
        {"type": "USER_INPUT", "status": "DONE", "content": "the order", "created_at": "2026-09-22T18:00:00Z"},
        _planner("POSITION: done\nthe original's text", "2026-09-22T18:05:00Z"),
    ]
    after = dt.datetime(2026, 9, 25, 9, 17, 28, tzinfo=dt.timezone.utc)

    assert BW.gemini_reply(records, after=after)["status"] == "working", "an echo of the original is not the repair's reply"
    later = records + [{"type": "SYSTEM_MESSAGE", "status": "DONE", "content": "[Message] sender=system content=repair",
                        "created_at": "2026-09-25T09:17:29Z"}, _planner("POSITION: done\nthe repair", "2026-09-25T09:22:00Z")]
    reply = BW.gemini_reply(later, after=after)
    assert reply["status"] == "done" and reply["text"].endswith("the repair")


def test_fix3_the_watcher_holds_a_repair_packet_until_its_own_reply_lands(tmp_path):
    repo = make_repo(tmp_path)
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(json.dumps(r) for r in [
        {"type": "USER_INPUT", "status": "DONE", "content": "the order", "created_at": "2026-09-22T18:00:00Z"},
        _planner("POSITION: done\nthe original's text", "2026-09-22T18:05:00Z"),
    ]) + "\n", encoding="utf-8")
    now = dt.datetime.now().astimezone()
    folder = BE.packet_dir(repo, "p-repair", "sent")
    BE.write_json(folder / "order.json", {"packetId": "p-repair", "lane": "gemini", "from": "claude", "conversationId": "c-9",
                                          "repairs": "p-orig", "replyShape": "paths-written",
                                          "deadline": (now + dt.timedelta(minutes=60)).isoformat(timespec="seconds"),
                                          "lastFollowupAt": now.isoformat(timespec="seconds")})
    BE.write_json(folder / "conversation.json", {"packetId": "p-repair", "conversationId": "c-9", "followup": 1,
                                                 "sentAt": now.isoformat(timespec="seconds")})

    code = BW.main(["--lane", "gemini", "--id", str(transcript), "--packet", "p-repair", "--repo", str(repo), "--once"])

    assert code == 3, "still working: the only completed reply predates the follow-up"
    assert folder.is_dir() and not BE.packet_dir(repo, "p-repair", "replied").exists()


# --------------------------------------------------------------------------- 4. repairs that cannot work


def test_fix4_a_cut_outside_a_whole_paths_block_passes_tier_zero_and_queues_no_repair(tmp_path):
    repo = make_repo(tmp_path)
    a, b = tmp_path / "findings.md", tmp_path / "audit.md"
    a.write_text("x", encoding="utf-8")
    b.write_text("y", encoding="utf-8")
    replied(repo, "p-cut", {"replyShape": "paths-written"},
            grammar(str(a), str(b), tail="\nPASS paths-written (2 checks)\n\n---\nprose prose\n<truncated 3787 bytes>\n"))

    BD.step_tier0(tick(repo))

    assert BE.packet_dir(repo, "p-cut", "done").is_dir(), "the paths block is whole and every path exists: tier 0 closes it"
    assert BD.packets(repo, "queue") == [], "no repair: restating the block would hit the same transcript cut"


def test_fix4_a_cut_outside_a_whole_block_with_a_missing_path_is_one_order_escalation(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BD, "run_tier1", lambda *a: pytest.fail("an order failure never reaches tier 1"))
    a = tmp_path / "findings.md"
    a.write_text("x", encoding="utf-8")
    replied(repo, "p-cut2", {"replyShape": "paths-written"},
            grammar(str(a), str(tmp_path / "ghost.md"), tail="\nprose\n<truncated 900 bytes>\n"), minutes_ago=30)

    BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    folder = BE.packet_dir(repo, "p-cut2", "replied")
    assert json.loads((folder / "tier0.json").read_text(encoding="utf-8"))["class"] == "order"
    assert BD.packets(repo, "queue") == [], "no repair is queued"
    assert [r["reason"] for r in rows(repo) if r["event"] == "escalated"] == ["order"]
    assert len(seen) == 1


def test_fix4_an_order_defect_is_classed_order_and_never_repaired(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BD, "run_tier1", lambda *a: pytest.fail("an order failure never reaches tier 1"))
    replied(repo, "p-nofetch", {"replyShape": "fetch"}, grammar(str(tmp_path / "MANIFEST.json")), minutes_ago=30)

    BD.tick_once(repo, CONFIG)

    folder = BE.packet_dir(repo, "p-nofetch", "replied")
    assert json.loads((folder / "tier0.json").read_text(encoding="utf-8"))["class"] == "order"
    assert BD.packets(repo, "queue") == [] and not (folder / BD.REPAIR_MARKER).exists()
    assert len(seen) == 1 and "order" in seen[0][0]


def test_fix4_a_cut_inside_the_paths_block_is_still_repaired(tmp_path):
    repo = make_repo(tmp_path)
    a = tmp_path / "findings.md"
    a.write_text("x", encoding="utf-8")
    replied(repo, "p-cutin", {"replyShape": "paths-written"},
            "POSITION: done\nPATHS WRITTEN:\n" + str(a) + "\nC:/some/half-pa\n<truncated 676 bytes>\nth/file.md\nDISAGREEMENTS:\n- none\n")

    BD.step_tier0(tick(repo))

    assert len(BD.packets(repo, "queue")) == 1, "a cut inside the block may still be restated"


def test_fix4_the_repair_order_carries_the_originals_fetch_dir(tmp_path):
    repo = make_repo(tmp_path)
    fetch_dir = tmp_path / "fetch"
    replied(repo, "p-fetch", {"replyShape": "fetch", "fetch_dir": str(fetch_dir)}, "the files are in the folder\n")

    BD.step_tier0(tick(repo))

    queued = BD.packets(repo, "queue")
    assert len(queued) == 1
    order = json.loads((queued[0] / "order.json").read_text(encoding="utf-8"))
    assert order["fetch_dir"] == str(fetch_dir), "without it the repair can never pass"


# --------------------------------------------------------------------------- 5. stranded originals


def test_fix5_an_original_whose_repair_closed_elsewhere_is_closed_on_the_next_tick(tmp_path):
    repo = make_repo(tmp_path)
    original = replied(repo, "p-orig", {"replyShape": "paths-written"}, "PATHS WRITTEN: docs/ghost.md\n", minutes_ago=30)
    BE.write_json(original / "tier0.json", {"pass": False, "class": "form", "reason": "x", "checks": []})
    BE.write_json(original / BD.REPAIR_MARKER, {"repairPacket": "p-rep"})
    done = BE.packet_dir(repo, "p-rep", "done")   # the parent closed the repair by hand, or its tier 1 said follow-up
    BE.write_json(done / "order.json", {"packetId": "p-rep", "repairs": "p-orig"})

    BD.tick_once(repo, CONFIG)

    closed = BE.packet_dir(repo, "p-orig", "done")
    assert closed.is_dir() and not original.exists()
    assert json.loads((closed / "tier0.json").read_text(encoding="utf-8"))["repairedBy"] == "p-rep"
    assert [r for r in rows(repo) if r["event"] == "repaired"]


def test_fix5_a_repair_whose_tier_one_says_follow_up_closes_its_original(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)

    def runner(repo_, folder):
        (folder / "result.md").write_text("DECISION: follow-up\n", encoding="utf-8")
        return {"exit": 0, "payload": {}}

    monkeypatch.setattr(BD, "run_tier1", runner)
    original = replied(repo, "p-orig2", {"replyShape": "paths-written"}, "PATHS WRITTEN: docs/ghost.md\n", minutes_ago=30)
    BE.write_json(original / "tier0.json", {"pass": False, "class": "form", "reason": "x", "checks": []})
    BE.write_json(original / BD.REPAIR_MARKER, {"repairPacket": "p-rep2"})
    rep = replied(repo, "p-rep2", {"replyShape": "paths-written", "repairs": "p-orig2"}, "PATHS WRITTEN: docs/ghost2.md\n", minutes_ago=30)
    BE.write_json(rep / "tier0.json", {"pass": False, "class": "form", "reason": "x", "checks": []})

    BD.tick_once(repo, CONFIG)

    assert BE.packet_dir(repo, "p-rep2", "done").is_dir()
    assert BE.packet_dir(repo, "p-orig2", "done").is_dir(), "the original is not stranded in replied/"


def test_fix5_a_prior_passing_verdict_on_a_repair_closes_its_original(tmp_path):
    repo = make_repo(tmp_path)
    original = replied(repo, "p-orig3", {"replyShape": "paths-written"}, "x\n")
    BE.write_json(original / BD.REPAIR_MARKER, {"repairPacket": "p-rep3"})
    rep = replied(repo, "p-rep3", {"replyShape": "paths-written", "repairs": "p-orig3"}, "x\n")
    BE.write_json(rep / "tier0.json", {"pass": True, "by": "parent-triage", "checks": []})

    BD.step_tier0(tick(repo))

    assert BE.packet_dir(repo, "p-orig3", "done").is_dir()


# --------------------------------------------------------------------------- 6. lanes with no watcher or sender


def test_fix6_a_sent_packet_on_a_lane_with_no_watcher_is_skipped_and_logged_once(tmp_path, monkeypatch, capsys):
    repo = make_repo(tmp_path)
    # R26-355 gave astra a file watcher (test_bridge_daemon); a lane with NEITHER a transcript nor a file watcher still skips
    folder = BE.packet_dir(repo, "p-astra", "sent")
    BE.write_json(folder / "order.json", {"packetId": "p-astra", "lane": "hermes", "replyShape": "paths-written"})
    BE.write_json(folder / "conversation.json", {"packetId": "p-astra", "conversationId": "c-1", "lane": "hermes"})

    first = BD.tick_once(repo, CONFIG)
    second = BD.tick_once(repo, CONFIG)

    err = capsys.readouterr().err
    assert "usage:" not in err and "invalid choice" not in err, "no argparse error"
    assert not any("WATCH-FAILED" in l for l in first.lines + second.lines)
    assert any("WATCH-SKIP" in l for l in first.lines) and not any("p-astra" in l for l in second.lines)
    assert (folder / "watch-skip.json").exists()
    assert [r["event"] for r in rows(repo)] == ["watch-skip"]


def test_fix6_a_queued_order_on_a_lane_with_no_sender_is_refused_and_escalated_once(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    seen = toasts(monkeypatch)
    monkeypatch.setattr(BS, "send_gemini", lambda *a: pytest.fail("an astra order must never go through the gemini send"))
    monkeypatch.setattr(BS, "send_claude", lambda *a: pytest.fail("an astra order must never go through the claude send"))
    monkeypatch.setattr(BR, "send", lambda *a: pytest.fail("an astra follow-up must never be sent"))
    BE.write_json(BE.packet_dir(repo, "p-astra-new", "queue") / "order.json",
                  {"packetId": "p-astra-new", "lane": "astra", "brief": "x"})
    BE.write_json(BE.packet_dir(repo, "p-astra-fu", "queue") / "order.json",
                  {"packetId": "p-astra-fu", "lane": "astra", "conversationId": "c-1", "brief": "y"})

    BD.tick_once(repo, CONFIG)
    BD.tick_once(repo, CONFIG)

    assert BE.packet_dir(repo, "p-astra-new", "queue").is_dir() and BE.packet_dir(repo, "p-astra-fu", "queue").is_dir()
    assert sorted(r["packetId"] for r in rows(repo) if r["event"] == "escalated") == ["p-astra-fu", "p-astra-new"]
    assert len(seen) == 2


def test_fix6_bridge_reply_refuses_a_lane_with_no_sender(tmp_path):
    with pytest.raises(BR.BridgeReplyError, match="astra"):
        BR.resolve("astra", "c-1", "hello", tmp_path)


# --------------------------------------------------------------------------- 7. paths outside the repo root


def test_fix7_a_reply_path_outside_the_repo_root_fails_tier_zero_with_its_own_class(tmp_path):
    repo = make_repo(tmp_path / "main")
    stray = tmp_path / "astra-worktree" / "GEMINI-REVIEW.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("a review in the wrong checkout", encoding="utf-8")

    outcome = BC.classify({"replyShape": "paths-written"}, grammar(str(stray)), repo)

    assert outcome["pass"] is False and outcome["class"] == BC.CLASS_OUTSIDE_ROOT
    assert str(stray) in outcome["reason"]
    inside = repo / "docs" / "ok.md"
    inside.parent.mkdir(parents=True, exist_ok=True)
    inside.write_text("x", encoding="utf-8")
    assert BC.classify({"replyShape": "paths-written"}, grammar(str(inside)), repo)["pass"] is True
    declared = BC.classify({"replyShape": "paths-written", "roots": [str(stray.parent)]}, grammar(str(stray)), repo)
    assert declared["pass"] is True, "a root the order declared is inside"


def test_fix7_the_daemons_tier_zero_fails_a_stray_path_and_queues_no_repair(tmp_path):
    repo = make_repo(tmp_path / "main")
    stray = tmp_path / "elsewhere" / "review.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("x", encoding="utf-8")
    replied(repo, "p-stray", {"replyShape": "paths-written"}, grammar(str(stray)))

    BD.step_tier0(tick(repo))

    folder = BE.packet_dir(repo, "p-stray", "replied")
    assert json.loads((folder / "tier0.json").read_text(encoding="utf-8"))["class"] == BC.CLASS_OUTSIDE_ROOT
    assert BD.packets(repo, "queue") == []


def test_fix7_the_order_template_names_the_main_checkout_as_the_output_root(tmp_path):
    main = tmp_path / "main"
    (main / ".git" / "worktrees" / "wt").mkdir(parents=True)
    worktree = tmp_path / "main" / ".claude" / "worktrees" / "wt"
    worktree.mkdir(parents=True)
    (worktree / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / 'wt'}\n", encoding="utf-8")

    assert BS.main_checkout(worktree) == main
    assert BS.main_checkout(main) == main
    brief = BS.with_template("do the work", "paths-written", worktree)
    assert str(main) in brief and "absolute" in brief.lower()
