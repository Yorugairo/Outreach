"""P46 T7 - tier 0 as the contract both sides run: the failure classes, the order's roots and verify command, the fill-in
block, the check CLI, and the daemon's repair round (one form repair at zero Claude tokens before tier 1; substance never).
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
import bridge_handlers as H  # noqa: E402
import bridge_send as BS  # noqa: E402

GRAMMAR = "POSITION: done\nPATHS WRITTEN:\n{paths}\nDISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- none\n"


# ---- the classes, the roots, the verify command, the block -------------------------------------


def test_the_first_failing_check_names_the_class():
    assert H.failure_class([{"name": "paths-named", "ok": False, "detail": ""}]) == "form"
    assert H.failure_class([{"name": "exists:C:/x.md", "ok": False, "detail": ""}]) == "form"
    assert H.failure_class([{"name": "not-found-block", "ok": False, "detail": ""}]) == "form"
    assert H.failure_class([{"name": "marker:x.md", "ok": False, "detail": ""}]) == "substance"
    assert H.failure_class([{"name": "proof-line", "ok": False, "detail": ""}]) == "substance"
    assert H.failure_class([{"name": "verdict-verified", "ok": False, "detail": ""}]) == "substance"
    assert H.failure_class([{"name": "verify-cmd", "ok": False, "detail": ""}]) == "substance"
    assert H.failure_class([{"name": "exists:x", "ok": True, "detail": ""}]) is None
    # the FIRST failure decides: a mangled path list before a missing marker is form
    assert H.failure_class([{"name": "exists:a", "ok": False, "detail": ""}, {"name": "marker:b", "ok": False, "detail": ""}]) == "form"


def test_a_relative_path_resolves_under_a_root_the_order_named(tmp_path: Path):
    other = tmp_path / "other-repo" / ".agents" / "agents"
    other.mkdir(parents=True)
    (other / "video-researcher.md").write_text("model: flash\n", encoding="utf-8")
    repo = tmp_path / "repo"; repo.mkdir()
    reply = GRAMMAR.format(paths=".agents/agents/video-researcher.md")
    without = H.classify({"replyShape": "paths-written"}, reply, repo)
    assert not without["pass"] and without["class"] == "form"
    with_root = H.classify({"replyShape": "paths-written", "roots": [str(tmp_path / "other-repo")]}, reply, repo)
    assert with_root["pass"], with_root
    assert H.order_roots({"roots": [str(tmp_path / "nowhere")]}, repo) == [], "a root that does not exist is ignored, never an error"


def test_the_orders_own_verify_command_is_a_substance_check_run_after_the_form_passes(tmp_path: Path, monkeypatch):
    f = tmp_path / "a.md"; f.write_text("x", encoding="utf-8")
    reply = GRAMMAR.format(paths=str(f))
    ran: list = []
    monkeypatch.setattr(H, "run_command", lambda cmd, repo: (ran.append(cmd) or (0, "ok")))
    ok = H.classify({"replyShape": "paths-written", "verify": "python check.py --strict"}, reply, tmp_path)
    assert ok["pass"] and ran == [["python", "check.py", "--strict"]] and ok["checks"][-1]["name"] == "verify-cmd"
    monkeypatch.setattr(H, "run_command", lambda cmd, repo: (2, "3 rows disagree"))
    bad = H.classify({"replyShape": "paths-written", "verify": ["python", "check.py"]}, reply, tmp_path)
    assert not bad["pass"] and bad["class"] == "substance" and "3 rows disagree" in bad["reason"]
    ran.clear()
    H.classify({"replyShape": "paths-written", "verify": "python check.py"}, "no grammar here", tmp_path)
    assert ran == [], "the verify never runs on a reply that failed on form"


def test_the_block_carries_the_five_heads_and_says_one_bare_path_per_line():
    for shape in ("paths-written", "report-landed", "contract-block", "review", "test-run"):
        t = H.template(shape)
        for head in ("POSITION:", "PATHS WRITTEN:", "DISAGREEMENTS:", "PREREQUISITES:", "NOT FOUND WHERE I LOOKED:"):
            assert head in t, (shape, head)
    assert "no links, no backticks, no bullets" in H.template("paths-written")
    assert "## Verdict up front" in H.template("report-landed")
    assert H.template("nonsense") == H.template("paths-written")


# ---- the CLI ---------------------------------------------------------------------------------------


def test_the_cli_passes_a_good_reply_order_less_and_prints_the_block_on_a_bad_one(tmp_path: Path, capsys):
    f = tmp_path / "a.md"; f.write_text("x", encoding="utf-8")
    good = tmp_path / "good.md"; good.write_text(GRAMMAR.format(paths=str(f)), encoding="utf-8")
    assert BC.main(["--shape", "paths-written", "--reply", str(good), "--repo", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("PASS paths-written") and f"exists:{f}" in out.replace("\\", "/") or "ok  " in out
    bad = tmp_path / "bad.md"; bad.write_text("I did the thing. See [`zzz.md`](zzz.md).\n", encoding="utf-8")
    assert BC.main(["--shape", "paths-written", "--reply", str(bad), "--repo", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert out.startswith("FAIL form:") and "fill this block" in out and "PATHS WRITTEN:" in out


def test_the_cli_reads_the_order_by_packet_and_prints_a_template(tmp_path: Path, capsys):
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    f = tmp_path / "marked.md"; f.write_text("BLOCK-7 here", encoding="utf-8")
    folder = BE.packet_dir(tmp_path, "abc123", "replied")
    BE.write_json(folder / "order.json", {"packetId": "abc123", "replyShape": "paths-written", "marker": "BLOCK-7"})
    reply = tmp_path / "r.md"; reply.write_text(GRAMMAR.format(paths=str(f)), encoding="utf-8")
    assert BC.main(["--packet", "abc123", "--reply", str(reply), "--repo", str(tmp_path)]) == 0
    assert "marker:" in capsys.readouterr().out
    f.write_text("no block", encoding="utf-8")
    assert BC.main(["--packet", "abc123", "--reply", str(reply), "--repo", str(tmp_path)]) == 1
    assert "FAIL substance:" in capsys.readouterr().out and "the block alone will not close it" not in ""  # substance is named
    assert BC.main(["--template", "review"]) == 0
    assert "DISAGREEMENTS:" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        BC.main(["--packet", "nope", "--reply", str(reply), "--repo", str(tmp_path)])


def test_bridge_send_appends_the_block_and_carries_roots_and_verify(tmp_path: Path):
    brief = "# Order\n\nDo the thing.\n"
    out = BS.with_template(brief, "report-landed")
    assert "## Reply block" in out and "bridge_check.py --shape report-landed" in out and "## Verdict up front" in out
    assert BS.with_template(out, "report-landed") == out, "never appended twice"
    assert BS.with_template(brief, "free") == brief
    parser = BS.build_parser()
    args = parser.parse_args(["--lane", "gemini", "--brief-file", "x.md", "--root", "C:/a", "--root", "C:/b", "--verify", "python v.py"])
    order = BS.build_order(args, brief)
    assert order["roots"] == [str(Path("C:/a").expanduser()), str(Path("C:/b").expanduser())] and order["verify"] == "python v.py"
    plain = BS.build_order(parser.parse_args(["--lane", "gemini", "--brief-file", "x.md"]), brief)
    assert "roots" not in plain and "verify" not in plain, "an order without them compiles exactly as before"


# ---- the daemon's repair round ---------------------------------------------------------------------


def _repo(tmp_path: Path) -> Path:
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    return tmp_path


def _landed(minutes_ago: float) -> str:
    when = (dt.datetime.now().astimezone() - dt.timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    return f"<!-- lane: gemini; conversationId: c-9; landedAt: {when} -->\n\n"


def _replied(repo: Path, packet: str, order: dict, reply: str, minutes_ago: float = 0.0, conversation: str | None = "c-9") -> Path:
    folder = BE.packet_dir(repo, packet, "replied")
    BE.write_json(folder / "order.json", {"packetId": packet, "lane": "gemini", **order})
    if conversation:
        BE.write_json(folder / "conversation.json", {"packetId": packet, "conversationId": conversation})
    (folder / "reply.md").write_text(_landed(minutes_ago) + reply, encoding="utf-8")
    return folder


def _rows(repo: Path) -> list[dict]:
    p = repo / BE.LEDGER
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def _tick(repo: Path, **cfg):
    return BD.Tick(repo=repo, config={**BD.load_config(None), **cfg}, dry_run=False)


@pytest.fixture(autouse=True)
def quiet(monkeypatch):
    monkeypatch.setattr(BD, "toast", lambda title, body: pytest.fail(f"unexpected toast: {title} / {body}"))


def test_a_form_failure_queues_one_repair_and_tier_one_waits(tmp_path: Path, monkeypatch):
    repo = _repo(tmp_path)
    calls: list = []
    monkeypatch.setattr(BD, "run_tier1", lambda r, f: (calls.append(f) or {"exit": 0, "payload": {}}))
    original = _replied(repo, "orig1", {"replyShape": "paths-written", "title": "the order", "roots": ["C:/elsewhere"]},
                        "I wrote the files, see the links: [`a.md`](a.md)\n", minutes_ago=30)
    tick = _tick(repo, grace_min=1)
    BD.step_tier0(tick)
    t0 = json.loads((original / "tier0.json").read_text(encoding="utf-8"))
    assert not t0["pass"] and t0["class"] == "form"
    assert (original / BD.REPAIR_MARKER).exists(), "the repair is marked on the original"
    queued = [p for p in BD.packets(repo, "queue")]
    assert len(queued) == 1
    ro = json.loads((queued[0] / "order.json").read_text(encoding="utf-8"))
    assert ro["repairs"] == "orig1" and ro["conversationId"] == "c-9" and ro["replyShape"] == "paths-written" and ro["roots"] == ["C:/elsewhere"]
    assert "add nothing new" in ro["brief"] and "PATHS WRITTEN:" in ro["brief"] and "bridge_check.py" in ro["brief"]
    assert [r["event"] for r in _rows(repo)] == ["repair"]
    BD.step_tier0(tick)   # a second tick queues nothing more
    assert len(BD.packets(repo, "queue")) == 1
    BD.step_tier1(tick)   # past the grace window, the original still waits for its repair
    assert calls == [] and original.exists()


def test_a_substance_failure_goes_to_tier_one_with_its_reason_and_never_a_repair(tmp_path: Path, monkeypatch):
    repo = _repo(tmp_path)
    f = tmp_path / "block.md"; f.write_text("no block here", encoding="utf-8")
    calls: list = []

    def runner(r, folder):
        calls.append(folder); (folder / "result.md").write_text("DECISION: done\n", encoding="utf-8")
        return {"exit": 0, "payload": {"usage": {"input_tokens": 1, "output_tokens": 1}, "total_cost_usd": 0.01}}
    monkeypatch.setattr(BD, "run_tier1", runner)
    _replied(repo, "orig2", {"replyShape": "paths-written", "marker": "BLOCK-7"}, GRAMMAR.format(paths=str(f)), minutes_ago=30)
    tick = _tick(repo, grace_min=1)
    BD.step_tier0(tick)
    assert BD.packets(repo, "queue") == [] and [r["event"] for r in _rows(repo)] == []
    BD.step_tier1(tick)
    assert len(calls) == 1
    row = [r for r in _rows(repo) if r["event"] == "tier1"][0]
    assert row["reason"].startswith("substance:") and "BLOCK-7" in row["reason"]


def test_a_passing_repair_closes_the_original_with_it(tmp_path: Path):
    repo = _repo(tmp_path)
    original = _replied(repo, "orig3", {"replyShape": "paths-written"}, "links only: [`a.md`](a.md)\n", minutes_ago=40)
    BE.write_json(original / "tier0.json", {"pass": False, "class": "form", "reason": "not found", "checks": []})
    BE.write_json(original / BD.REPAIR_MARKER, {"repairPacket": "rep3"})
    f = tmp_path / "a.md"; f.write_text("x", encoding="utf-8")
    _replied(repo, "rep3", {"replyShape": "paths-written", "repairs": "orig3", "conversationId": "c-9"}, GRAMMAR.format(paths=str(f)), minutes_ago=1)
    tick = _tick(repo, grace_min=1)
    BD.step_tier0(tick)
    assert not original.exists() and BE.packet_dir(repo, "orig3", "done").exists(), "the original moved to done"
    assert BE.packet_dir(repo, "rep3", "done").exists()
    closed = json.loads((BE.packet_dir(repo, "orig3", "done") / "tier0.json").read_text(encoding="utf-8"))
    assert closed["pass"] and closed["repairedBy"] == "rep3"
    events = [r["event"] for r in _rows(repo)]
    assert "tier0" in events and "repaired" in events


def test_a_failing_repair_is_never_repaired_again_and_reaches_tier_one(tmp_path: Path, monkeypatch):
    repo = _repo(tmp_path)
    calls: list = []

    def runner(r, folder):
        calls.append(folder); (folder / "result.md").write_text("DECISION: done\n", encoding="utf-8")
        return {"exit": 0, "payload": {}}
    monkeypatch.setattr(BD, "run_tier1", runner)
    _replied(repo, "rep4", {"replyShape": "paths-written", "repairs": "orig4", "conversationId": "c-9"}, "still links: [`a.md`](a.md)\n", minutes_ago=30)
    tick = _tick(repo, grace_min=1)
    BD.step_tier0(tick)
    assert BD.packets(repo, "queue") == [], "a repair packet's failure never queues a second repair"
    BD.step_tier1(tick)
    assert len(calls) == 1
    row = [r for r in _rows(repo) if r["event"] == "tier1"][0]
    assert row["repairs"] == "orig4" and row["reason"].startswith("form:")


def test_a_form_failure_with_no_conversation_queues_nothing(tmp_path: Path):
    repo = _repo(tmp_path)
    _replied(repo, "orig5", {"replyShape": "paths-written"}, "no grammar", minutes_ago=5, conversation=None)
    BD.step_tier0(_tick(repo, grace_min=1))
    assert BD.packets(repo, "queue") == [] and _rows(repo) == []


def test_a_packet_landed_twice_supersedes_the_older_copy_instead_of_crashing_the_loop(tmp_path: Path):
    repo = _repo(tmp_path)
    f = tmp_path / "a.md"; f.write_text("x", encoding="utf-8")
    stale = BE.packet_dir(repo, "twice", "done"); stale.mkdir(parents=True)
    (stale / "reply.md").write_text("the older landing", encoding="utf-8")
    _replied(repo, "twice", {"replyShape": "paths-written"}, GRAMMAR.format(paths=str(f)), minutes_ago=1)
    BD.step_tier0(_tick(repo, grace_min=1))
    assert (BE.packet_dir(repo, "twice", "done") / "reply.md").read_text(encoding="utf-8") != "the older landing", "the newer landing is the one in done/"
    kept = [p for p in (repo / BE.BRIDGE_ROOT / "done").iterdir() if p.name.startswith("twice.superseded-")]
    assert len(kept) == 1 and (kept[0] / "reply.md").read_text(encoding="utf-8") == "the older landing", "the older copy is kept beside it, never deleted"
