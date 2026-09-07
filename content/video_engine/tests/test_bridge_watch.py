"""The watcher, pinned on the real transcripts of 2026-09-06 and on synthetic copies of their shape.

What is worth pinning is what the hand-driven watch had to judge by eye: whether a turn is finished or the
model is still working, which record is the reply, that the operator's second message is in there at all,
that a deadline is a state and not a hang, and that nothing private (a `thinking` field, a CSRF token) can
reach a file we write.

Every test reads a COPY in `tmp_path`; nothing here starts a process, opens a socket, touches the real
`evals/BRIDGE-LOG.jsonl` or writes into the operator's stores. The two real transcripts are read at test
time and skipped with a reason when this machine does not have them - the synthetic transcript covers the
same rules so the core never silently disappears.
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_env as BE  # noqa: E402
import bridge_watch as BW  # noqa: E402

GEMINI_EXAMPLE = (
    Path.home()
    / ".gemini/antigravity/brain/7aaa9146-88f1-4f03-b004-d5bdf18a5492/.system_generated/logs/transcript.jsonl"
)
CLAUDE_EXAMPLE = (
    Path.home()
    / ".claude/projects/C--Users-Snipe-AppData-Local-Temp-agent-bridge-run-0HB8Hg"
    / "715d091c-96c9-43ba-9380-748ad4fbbce7.jsonl"
)
COMPLETION_HEAD = "I have successfully completed the order"
TOKEN = "9c1e77b0a4d34f118e2b6c0d5a7f3e21"
THINKING = "PRIVATE-REASONING-MARKER"


# --------------------------------------------------------------------------- fixtures


def _copy(example: Path, tmp_path: Path, name: str, keep: int | None = None) -> Path:
    """A copy of a real transcript (optionally truncated to its first ``keep`` records)."""

    if not example.exists():
        pytest.skip(f"transcript not found where I looked: {example}")
    target = tmp_path / name
    if keep is None:
        shutil.copyfile(example, target)
        return target
    lines = [line for line in example.read_text(encoding="utf-8").splitlines() if line.strip()]
    target.write_text("\n".join(lines[:keep]) + "\n", encoding="utf-8")
    return target


def _record(step: int, rtype: str, content: str = "", **extra) -> dict:
    record = {
        "step_index": step,
        "source": extra.pop("source", "MODEL"),
        "type": rtype,
        "status": extra.pop("status", "DONE"),
        "created_at": f"2026-09-06T06:4{step % 10}:00Z",
        "content": content,
        "thinking": f"{THINKING} - the model's private reasoning, never copied anywhere",
        "tool_calls": extra.pop("tool_calls", None),
        "truncated_fields": None,
    }
    record.update(extra)
    return record


def _write_jsonl(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    return path


def synthetic_gemini(path: Path, *, finished: bool = True) -> Path:
    """The worked example's shape in six records: an order, a tool round, an abstention, a correction."""

    records = [
        _record(0, "USER_INPUT", "<USER_REQUEST>\nApply the work order.\n</USER_REQUEST>", source="USER_EXPLICIT"),
        _record(1, "PLANNER_RESPONSE", "", tool_calls=[{"name": "view_file", "args": {"AbsolutePath": "x"}}]),
        _record(2, "GENERIC", f"The command exited with code 0. token={TOKEN}"),
        _record(3, "PLANNER_RESPONSE", "**Not found where I looked.** Roots: C:\\Users\\Snipe"),
        _record(4, "SYSTEM_MESSAGE", "[Message] sender=system content=The source is the other folder.", source="SYSTEM"),
        _record(5, "PLANNER_RESPONSE", "", tool_calls=[{"name": "run_command", "args": {}}]),
        _record(6, "GENERIC", "The command exited with code 0."),
    ]
    if finished:
        records.append(_record(7, "PLANNER_RESPONSE", f"{COMPLETION_HEAD} and synced the changes."))
    return _write_jsonl(path, records)


def _packet(repo: Path, transcript: Path, *, deadline: dt.datetime, sent_at: dt.datetime | None = None) -> str:
    """A packet sitting in `sent/`, as `bridge_send.py` leaves one."""

    packet_id = BE.packet_id(f"synthetic order for {transcript.name}")
    folder = BE.packet_dir(repo, packet_id, "sent")
    BE.write_json(
        folder / "order.json",
        {
            "packetId": packet_id,
            "lane": "gemini",
            "title": "synthetic",
            "replyShape": "paths-written",
            "deadline": deadline.isoformat(timespec="seconds"),
            "brief": "apply the work order",
            "createdAt": (sent_at or deadline).isoformat(timespec="seconds"),
        },
    )
    if sent_at:
        BE.write_json(
            folder / "conversation.json",
            {"packetId": packet_id, "conversationId": "synthetic", "sentAt": sent_at.isoformat(timespec="seconds")},
        )
    return packet_id


def _ledger_lines(repo: Path) -> list[dict]:
    path = repo / BE.LEDGER
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------- the reply rule


def test_synthetic_transcript_lands_the_completion_report(tmp_path):
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl")

    reply = BW.gemini_reply(BW.read_records(transcript))

    assert reply["status"] == "done"
    assert reply["text"].startswith(COMPLETION_HEAD), "the reply is the last clean PLANNER_RESPONSE"


def test_an_unfinished_turn_reads_as_working(tmp_path):
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl", finished=False)

    reply = BW.gemini_reply(BW.read_records(transcript))

    assert reply["status"] == "working", "a tool call after the last text means the model is still going"
    assert reply["text"] == ""


def test_an_abstention_that_ends_the_turn_is_a_reply(tmp_path):
    records = BW.read_records(synthetic_gemini(tmp_path / "t.jsonl", finished=False))[:4]

    reply = BW.gemini_reply(records)

    assert reply["status"] == "done"
    assert "Not found where I looked" in reply["text"]


def test_the_operators_second_message_is_a_system_message_not_a_user_input(tmp_path):
    records = BW.read_records(synthetic_gemini(tmp_path / "t.jsonl"))

    steps = BW.gemini_steps(records)
    user_steps = [s for s in steps if s.get("user")]

    assert [s["type"] for s in user_steps] == ["USER_INPUT", "SYSTEM_MESSAGE"], (
        "the correction goes in by send-message and lands as a SYSTEM_MESSAGE with sender=system"
    )
    tool_results = [s for s in steps if s["type"] == "SYSTEM_MESSAGE" and not s.get("user")]
    assert all("sender=system" not in s["head"] for s in tool_results)


# --------------------------------------------------------------------------- the real gemini transcript


def test_replay_of_the_worked_example(tmp_path):
    transcript = _copy(GEMINI_EXAMPLE, tmp_path, "transcript.jsonl")
    records = BW.read_records(transcript)
    out = tmp_path / "out"

    code = BW.main(["--lane", "gemini", "--id", str(transcript), "--replay", "--out", str(out)])

    assert code == 0, "the 2026-09-06 order is finished, so a replay is done"
    reply = (out / "reply.md").read_text(encoding="utf-8")
    assert reply.splitlines()[0].startswith("<!-- lane: gemini;")
    assert reply.rstrip().endswith(records[-1]["content"].strip()), "reply.md ends with the completion report"
    steps = (out / "steps.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(steps) == len(records) == 101
    watch = json.loads((out / "watch.json").read_text(encoding="utf-8"))
    assert watch["status"] == "done" and watch["steps"] == 101
    assert watch["secondsToReply"] is None, "no packet, no clock"
    assert watch["positionLine"] is None, "the gemini report does not open with POSITION:"


def test_the_worked_example_carries_two_operator_turns_and_the_abstention(tmp_path):
    transcript = _copy(GEMINI_EXAMPLE, tmp_path, "transcript.jsonl")
    steps = BW.gemini_steps(BW.read_records(transcript))

    user_steps = [s for s in steps if s.get("user")]
    abstention = [r for r in BW.read_records(transcript) if r["step_index"] == 80]

    assert [s["type"] for s in user_steps] == ["USER_INPUT", "SYSTEM_MESSAGE"], (
        "one USER_INPUT at step 0; the correction arrives as a SYSTEM_MESSAGE with sender=system"
    )
    assert [s["step_index"] for s in user_steps] == [0, 82]
    assert len(abstention) == 1 and abstention[0]["type"] == "PLANNER_RESPONSE"
    assert "Not found where I looked" in abstention[0]["content"], "step 80 is the abstention"
    assert [s for s in steps if s["step_index"] == 80][0]["head"].startswith("I attempted to locate")


def test_a_transcript_cut_before_the_completion_record_is_still_working(tmp_path):
    transcript = _copy(GEMINI_EXAMPLE, tmp_path, "partial.jsonl", keep=100)
    out = tmp_path / "out"

    code = BW.main(["--lane", "gemini", "--id", str(transcript), "--replay", "--out", str(out)])

    watch = json.loads((out / "watch.json").read_text(encoding="utf-8"))
    assert watch["status"] == "working" and code == 3
    assert not (out / "reply.md").exists(), "no reply is written while the model is still going"


# --------------------------------------------------------------------------- the claude lane


def test_the_claude_lane_yields_astras_position_line(tmp_path):
    transcript = _copy(CLAUDE_EXAMPLE, tmp_path, "session.jsonl")
    out = tmp_path / "out"

    code = BW.main(["--lane", "claude", "--id", str(transcript), "--replay", "--out", str(out)])

    watch = json.loads((out / "watch.json").read_text(encoding="utf-8"))
    assert code == 0 and watch["status"] == "done"
    assert watch["positionLine"] == "POSITION: conditional"
    reply = (out / "reply.md").read_text(encoding="utf-8")
    assert "DISAGREEMENTS:" in reply
    steps = [json.loads(line) for line in (out / "steps.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(steps) == len(BW.read_records(transcript))
    assert [s["type"] for s in steps].count("assistant") == 2


def test_the_claude_reader_skips_a_thinking_only_record(tmp_path):
    transcript = tmp_path / "session.jsonl"
    _write_jsonl(
        transcript,
        [
            {"type": "user", "timestamp": "2026-09-06T02:13:01Z", "message": {"role": "user", "content": "brief"}},
            {
                "type": "assistant",
                "timestamp": "2026-09-06T02:13:23Z",
                "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "secret reasoning"}]},
            },
            {
                "type": "assistant",
                "timestamp": "2026-09-06T02:13:39Z",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "POSITION: conditional\n\nDISAGREEMENTS:\n- one"}],
                    "usage": {"input_tokens": 2, "output_tokens": 2484},
                },
            },
        ],
    )

    reply = BW.claude_reply(BW.read_records(transcript))

    assert reply["text"].startswith("POSITION: conditional")
    assert "secret reasoning" not in reply["text"]
    assert BW.claude_usage(reply["record"]) == {"inputTokens": 2, "outputTokens": 2484}


# --------------------------------------------------------------------------- packets, deadlines, the ledger


def test_a_packet_past_its_deadline_times_out_and_stays_in_sent(tmp_path):
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl", finished=False)
    past = dt.datetime.now().astimezone() - dt.timedelta(minutes=5)
    packet = _packet(tmp_path, transcript, deadline=past)

    code = BW.main(["--lane", "gemini", "--id", str(transcript), "--packet", packet, "--repo", str(tmp_path)])

    assert code == 2
    assert BE.packet_dir(tmp_path, packet, "sent").exists()
    assert not BE.packet_dir(tmp_path, packet, "replied").exists()
    watch = json.loads((BE.packet_dir(tmp_path, packet, "sent") / "watch.json").read_text(encoding="utf-8"))
    assert watch["status"] == "timeout"
    lines = _ledger_lines(tmp_path)
    assert len(lines) == 1 and lines[0]["event"] == "timeout"
    assert lines[0]["packetId"] == packet


def test_a_completed_transcript_lands_the_packet_in_replied_and_ledgers_it(tmp_path):
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl")
    now = dt.datetime.now().astimezone()
    packet = _packet(tmp_path, transcript, deadline=now + dt.timedelta(minutes=30), sent_at=now - dt.timedelta(seconds=90))

    code = BW.main(["--lane", "gemini", "--id", str(transcript), "--packet", packet, "--repo", str(tmp_path)])

    replied = BE.packet_dir(tmp_path, packet, "replied")
    assert code == 0
    assert replied.exists() and not BE.packet_dir(tmp_path, packet, "sent").exists()
    assert COMPLETION_HEAD in (replied / "reply.md").read_text(encoding="utf-8")
    assert (replied / "order.json").exists(), "the order travels with the packet"
    lines = _ledger_lines(tmp_path)
    assert len(lines) == 1 and lines[0]["event"] == "replied"
    assert isinstance(lines[0]["secondsToReply"], (int, float)) and lines[0]["secondsToReply"] >= 89
    assert lines[0]["replyShape"] == "paths-written"


def test_a_replay_without_a_packet_ledgers_nothing(tmp_path):
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl")

    BW.main(["--lane", "gemini", "--id", str(transcript), "--replay", "--repo", str(tmp_path), "--out", str(tmp_path / "out")])

    assert _ledger_lines(tmp_path) == []


def test_timeout_min_overrides_the_orders_deadline(tmp_path):
    order = {"deadline": (dt.datetime.now().astimezone() + dt.timedelta(hours=2)).isoformat(timespec="seconds")}
    started = dt.datetime.now().astimezone()

    assert BW.resolve_deadline(0, order, started) == started
    assert BW.resolve_deadline(None, order, started) == BW.parse_time(order["deadline"])
    assert BW.resolve_deadline(None, {}, started) is None, "no order, no deadline - poll until told otherwise"


# --------------------------------------------------------------------------- nothing private reaches a file


def test_no_thinking_and_no_secret_reaches_any_output(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTIGRAVITY_CSRF_TOKEN", TOKEN)
    transcript = synthetic_gemini(tmp_path / "transcript.jsonl")
    out = tmp_path / "out"

    BW.main(["--lane", "gemini", "--id", str(transcript), "--replay", "--out", str(out), "--repo", str(tmp_path)])

    steps = (out / "steps.jsonl").read_text(encoding="utf-8")
    assert TOKEN not in steps and "<masked>" in steps, "a csrf value in the environment is masked out of a head"
    for name in ("steps.jsonl", "watch.json", "reply.md"):
        body = (out / name).read_text(encoding="utf-8")
        assert THINKING not in body and '"thinking"' not in body, "no thinking, not even the field"
        assert TOKEN not in body


def test_environment_secrets_reads_csrf_and_host_bridge_only():
    environ = {
        "ANTIGRAVITY_CSRF_TOKEN": TOKEN,
        "HOST_BRIDGE_TOKEN": "b" * 12,
        "PATH": "C:/Windows",
        "SHORT_CSRF": "abc",
    }

    assert sorted(BW.environment_secrets(environ)) == sorted([TOKEN, "b" * 12])


def test_a_head_is_bounded_and_collapsed():
    head = BW.head_text("line one\n\n  line two   " + "x" * 400, secrets=[])

    assert len(head) == BW.HEAD_CHARS
    assert head.startswith("line one line two ")


# --------------------------------------------------------------------------- paths


def test_transcript_path_resolves_an_id_or_a_path(tmp_path):
    brain = tmp_path / "brain"
    resolved = BW.transcript_path("gemini", "7aaa9146", brain=brain)

    assert resolved == brain / "7aaa9146/.system_generated/logs/transcript.jsonl"
    assert BW.transcript_path("claude", str(tmp_path / "s.jsonl")) == tmp_path / "s.jsonl"


def test_a_missing_packet_says_where_it_looked(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        BW.locate_packet(tmp_path, "deadbeef")

    assert "not found where I looked" in str(excinfo.value)


def test_a_wait_for_task_placeholder_is_working_not_a_reply():
    """2026-09-07 03:00: the sourcing-repair turn ended on "Waiting for task-289." with status DONE while a background task ran;
    the watcher landed it, tier 0 failed it on form, the daemon repaired it - all on a reply that never was."""
    import bridge_watch as BW
    planner = lambda text, **kw: {"type": "PLANNER_RESPONSE", "content": text, "status": "DONE", **kw}
    generic = lambda text: {"type": "GENERIC", "content": text, "status": "DONE"}
    waiting = [planner("Wait for task-289 to complete.", tool_calls=[{"name": "schedule"}]),
               generic("Tool is running as a background task with task id: c/task-326"),
               planner("Waiting for task-289.")]
    assert BW.gemini_reply(waiting)["status"] == "working"
    assert BW.gemini_reply(waiting + [planner("Waiting for task-335 to finish.")])["status"] == "working"
    done = waiting + [planner("POSITION: done\nPATHS WRITTEN:\nC:/x/report.md\n")]
    out = BW.gemini_reply(done)
    assert out["status"] == "done" and out["text"].startswith("POSITION: done")
    assert BW.gemini_reply([planner("POSITION: done")])["status"] == "done", "a real reply is still a reply"
