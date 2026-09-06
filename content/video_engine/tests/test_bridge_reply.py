"""The follow-up path: answering a landed reply on the SAME conversation, and what that must cost.

The 2026-09-06 order needed a second message ("your PATHS WRITTEN names a file not on disk") before Gemini
could finish. `bridge_reply.py` is that message as a command, so what is pinned here is what a hand-driven
follow-up got wrong: sending on a new conversation instead of resuming one, sending twice, sending a packet
that never went out, and leaving no trace of the correction in the packet folder or the ledger.

Every test runs against a temp repository root with the `docs/research/runs/bridge/<state>/<packetId>/`
layout; the CLI is monkeypatched, so no process starts, no IDE is read and no network is touched. The CSRF
token is a synthetic fixture and every test asserts it never reaches stdout, the ledger or a packet file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_env as BE  # noqa: E402
import bridge_reply as BR  # noqa: E402

TOKEN = "5df9d4a1c0b34e2fa1d47c2b8e6a09f3"
BRIEF = "# order\n\nDo the thing.\n"
PID = BE.packet_id(BRIEF)
CONVERSATION = "7aaa9146-88f1-4f03-b004-d5bdf18a5492"
TEXT = "PATHS WRITTEN names docs/absent.md, which is not on disk. The source is docs/research/profiles.md."


class _Proc:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _packet(repo: Path, *, state: str = "replied", lane: str = "gemini", conversation: str | None = CONVERSATION) -> Path:
    """One packet folder in ``state`` with the order `bridge_send.py` would have written."""

    order = {
        "packetId": PID,
        "lane": lane,
        "title": "profiles",
        "replyShape": "review",
        "deadline": "2026-09-06T02:00:00+09:00",
        "brief": BRIEF,
        "createdAt": "2026-09-06T01:00:00+09:00",
    }
    if conversation is not None:
        order["conversationId"] = conversation
    folder = BE.packet_dir(repo, PID, state)
    BE.write_json(folder / "order.json", order)
    return folder


@pytest.fixture()
def calls(monkeypatch) -> list[dict]:
    """Capture every CLI invocation instead of making one."""

    seen: list[dict] = []

    def _fake_run(argv, **kwargs):
        seen.append({"argv": list(argv), "kwargs": kwargs})
        return _Proc(stdout='{"result": "ok"}')

    monkeypatch.setattr(BR.subprocess, "run", _fake_run)
    return seen


@pytest.fixture()
def fake_gemini_env(monkeypatch, tmp_path):
    """The resolved IDE environment, with a synthetic token that must never be rendered."""

    env = {
        "ANTIGRAVITY_LS_ADDRESS": "127.0.0.1:49635",
        "ANTIGRAVITY_CSRF_TOKEN": TOKEN,
        "ANTIGRAVITY_PROJECT_ID": str(tmp_path),
        "AGENTAPI": str(tmp_path / "agentapi.bat"),
    }
    monkeypatch.setattr(BE, "discover_gemini_env", lambda pid=None, repo_root=None: dict(env))
    return env


def _ledger(repo: Path) -> list[dict]:
    path = repo / "evals/BRIDGE-LOG.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------- the happy path


def test_a_replied_packet_is_answered_on_the_same_conversation(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path)

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])
    out = capsys.readouterr().out

    sent = BE.packet_dir(tmp_path, PID, "sent")
    followup = sent / "followups" / "01.md"
    order = json.loads((sent / "order.json").read_text(encoding="utf-8"))
    body = followup.read_text(encoding="utf-8")
    ledger = _ledger(tmp_path)

    assert code == 0
    assert len(calls) == 1, "exactly one send per invocation"
    argv = calls[0]["argv"]
    assert argv[-3:] == ["send-message", CONVERSATION, TEXT], "resumed, not a new conversation"
    assert calls[0]["kwargs"]["env"]["ANTIGRAVITY_CSRF_TOKEN"] == TOKEN, "the token reaches the child by env only"

    assert not BE.packet_dir(tmp_path, PID, "replied").exists(), "a new round starts: replied -> sent"
    assert body.startswith(f"<!-- sentAt: "), "the header records when, which lane, which conversation"
    assert f"conversationId: {CONVERSATION} -->" in body.splitlines()[0]
    assert TEXT in body, "the follow-up text is recorded verbatim"
    assert order["followups"] == 1 and order["lastFollowupAt"]
    assert order["brief"] == BRIEF and order["replyShape"] == "review", "every other order field survives"

    assert len(ledger) == 1
    assert ledger[0]["event"] == "followup" and ledger[0]["lane"] == "gemini"
    assert ledger[0]["packetId"] == PID and ledger[0]["conversationId"] == CONVERSATION
    assert ledger[0]["followup"] == 1 and ledger[0]["chars"] == len(TEXT)
    assert ledger[0]["inputTokens"] is None and ledger[0]["outputTokens"] is None, "null, never zero"

    assert TOKEN not in out
    assert TOKEN not in (tmp_path / "evals/BRIDGE-LOG.jsonl").read_text(encoding="utf-8")
    assert TOKEN not in body


def test_a_second_followup_numbers_itself_02(tmp_path, calls, fake_gemini_env):
    _packet(tmp_path)
    BR.main(["--packet", PID, "--text", "first", "--repo", str(tmp_path)])

    code = BR.main(["--packet", PID, "--text", "second", "--repo", str(tmp_path)])

    sent = BE.packet_dir(tmp_path, PID, "sent")
    order = json.loads((sent / "order.json").read_text(encoding="utf-8"))

    assert code == 0
    assert (sent / "followups" / "01.md").exists() and (sent / "followups" / "02.md").exists()
    assert "second" in (sent / "followups" / "02.md").read_text(encoding="utf-8")
    assert order["followups"] == 2
    assert len(calls) == 2, "one send each, and the packet stayed in sent/"
    assert [row["followup"] for row in _ledger(tmp_path)] == [1, 2]


def test_the_text_can_come_from_a_file(tmp_path, calls, fake_gemini_env):
    _packet(tmp_path)
    body_file = tmp_path / "correction.md"
    body_file.write_text(TEXT, encoding="utf-8")

    BR.main(["--packet", PID, "--text-file", str(body_file), "--repo", str(tmp_path)])

    assert calls[0]["argv"][-1] == TEXT


def test_json_output_names_the_conversation_and_the_followup(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path)

    BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out.strip())

    assert payload == {
        "packetId": PID,
        "lane": "gemini",
        "conversationId": CONVERSATION,
        "followup": 1,
        "path": str(BE.packet_dir(tmp_path, PID, "sent") / "followups" / "01.md"),
        "sent": True,
    }


# --------------------------------------------------------------------------- the dry run


def test_a_dry_run_calls_nothing_moves_nothing_and_ledgers_nothing(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path)

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out.strip()

    assert code == 0
    assert calls == [], "a dry run never calls the CLI"
    assert BE.packet_dir(tmp_path, PID, "replied").exists(), "and never moves the packet"
    assert not BE.packet_dir(tmp_path, PID, "sent").exists()
    assert not (tmp_path / "evals/BRIDGE-LOG.jsonl").exists(), "and never touches the ledger"
    assert not (BE.packet_dir(tmp_path, PID, "replied") / "followups").exists(), "and writes no follow-up"
    assert "send-message" in out and "01.md" in out, "it prints the command and the path it would write"
    assert TOKEN not in out, "the command is printed masked or not at all"
    assert out.endswith("next: send for real (drop --dry-run)")


# --------------------------------------------------------------------------- the refusals


def test_a_queued_packet_is_refused_and_the_state_is_named(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path, state="queue")

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])
    err = capsys.readouterr().err

    assert code != 0
    assert "queue" in err and "bridge_send" in err, "a packet that never went out is sent, not replied to"
    assert calls == []


def test_a_finished_packet_is_refused(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path, state="done")

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])

    assert code != 0 and "done" in capsys.readouterr().err
    assert calls == []


def test_an_absent_packet_names_the_four_state_dirs(tmp_path, calls, fake_gemini_env, capsys):
    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])
    err = capsys.readouterr().err

    assert code != 0
    assert "not found where I looked" in err
    assert all(state in err for state in BE.STATES)


def test_a_packet_without_a_conversation_id_cannot_be_replied_to(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path, conversation=None)

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])

    assert code != 0 and "conversationId" in capsys.readouterr().err
    assert calls == []


def test_an_empty_follow_up_is_refused(tmp_path, calls, fake_gemini_env, capsys):
    _packet(tmp_path)

    code = BR.main(["--packet", PID, "--text", "   ", "--repo", str(tmp_path)])

    assert code != 0 and calls == []


def test_a_failed_send_writes_no_followup_and_no_ledger_line(tmp_path, monkeypatch, fake_gemini_env, capsys):
    _packet(tmp_path)
    monkeypatch.setattr(BR.subprocess, "run", lambda argv, **kw: _Proc(returncode=1, stderr="connection forcibly closed"))

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])
    err = capsys.readouterr().err

    assert code != 0 and "connection forcibly closed" in err
    assert BE.packet_dir(tmp_path, PID, "replied").exists(), "an undelivered follow-up leaves the packet alone"
    assert not (BE.packet_dir(tmp_path, PID, "replied") / "followups").exists()
    assert _ledger(tmp_path) == []


# --------------------------------------------------------------------------- the claude lane


def test_the_claude_lane_resumes_the_session(tmp_path, calls, capsys):
    _packet(tmp_path, lane="claude", conversation="abc-123")

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])

    argv = calls[0]["argv"]
    ledger = _ledger(tmp_path)

    assert code == 0
    assert argv[:4] == ["claude", "-p", "--resume", "abc-123"]
    assert argv[-1] == TEXT
    assert calls[0]["kwargs"]["cwd"] == str(tmp_path), "the claude CLI runs from the repo root"
    assert ledger[0]["lane"] == "claude" and ledger[0]["conversationId"] == "abc-123"
    assert (BE.packet_dir(tmp_path, PID, "sent") / "followups" / "01.md").exists()


def test_the_conversation_id_is_read_from_the_send_record_when_the_order_lacks_it(tmp_path, calls, fake_gemini_env):
    """`bridge_send.py` records the gemini conversation in `conversation.json`, not in the order."""

    folder = _packet(tmp_path, conversation=None)
    BE.write_json(folder / "conversation.json", {"packetId": PID, "conversationId": CONVERSATION, "sentAt": "x"})

    code = BR.main(["--packet", PID, "--text", TEXT, "--repo", str(tmp_path)])

    assert code == 0
    assert calls[0]["argv"][-2] == CONVERSATION


# --------------------------------------------------------------------------- the ledger contract


def test_the_ledger_accepts_every_declared_event(tmp_path):
    for event in BE.LEDGER_EVENTS:
        BE.ledger_append(tmp_path, {"lane": "gemini", "packetId": PID, "event": event})

    assert [row["event"] for row in _ledger(tmp_path)] == list(BE.LEDGER_EVENTS)


def test_the_ledger_refuses_an_unknown_or_missing_event(tmp_path):
    with pytest.raises(ValueError) as unknown:
        BE.ledger_append(tmp_path, {"lane": "gemini", "packetId": PID, "event": "gossip"})
    with pytest.raises(ValueError):
        BE.ledger_append(tmp_path, {"lane": "gemini", "packetId": PID})

    assert "gossip" in str(unknown.value) and "followup" in str(unknown.value)
    assert not (tmp_path / "evals/BRIDGE-LOG.jsonl").exists(), "a rejected record writes no line"
