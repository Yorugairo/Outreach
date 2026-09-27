"""The paths-written check follows a packet the daemon itself moved (R26-144, found 2026-09-15).

The Gemini lane wrote FINDINGS.md beside its packet in `sent/<id>/` and named that path under PATHS WRITTEN; the
watcher then moved the packet to `replied/`, the form check looked for `sent/<id>/FINDINGS.md`, queued a repair that
restated the same path, and the loop re-queued - two replies waiting that nothing could close. A named path inside a
packet folder now resolves against the packet's CURRENT folder (queue / sent / replied / done) before it is refused.
Every test builds its repo in `tmp_path`; nothing sends, toasts or reads the live IDE.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_daemon as BD  # noqa: E402
import bridge_env as BE  # noqa: E402
import bridge_handlers as BH  # noqa: E402

PACKET = "a1b2c3d4e5f6"
ORDER = {"packetId": PACKET, "lane": "gemini", "replyShape": "paths-written", "title": "outreach fact check"}


@pytest.fixture(autouse=True)
def no_real_toast(monkeypatch):
    monkeypatch.setattr(BD, "toast", lambda title, body: pytest.fail(f"unexpected toast: {title} / {body}"))


def grammar(*paths: str) -> str:
    return ("POSITION: done\nPATHS WRITTEN:\n" + "\n".join(paths) + "\nDISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\n"
            "NOT FOUND WHERE I LOOKED:\n- none\n")


def planted(tmp_path: Path, name: str = "FINDINGS.md") -> tuple[Path, str]:
    """A sent packet with the lane's file written beside it, then moved to replied/ as the watcher moves it."""
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    sent = BE.packet_dir(tmp_path, PACKET, "sent")
    BE.write_json(sent / "order.json", ORDER)
    BE.write_json(sent / "conversation.json", {"packetId": PACKET, "conversationId": "c-9", "lane": "gemini"})
    (sent / name).write_text("# Findings\n", encoding="utf-8")
    named = f"{BE.BRIDGE_ROOT.as_posix()}/sent/{PACKET}/{name}"
    when = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    reply = f"<!-- lane: gemini; conversationId: c-9; landedAt: {when} -->\n\n{grammar(named)}"
    (sent / "reply.md").write_text(reply, encoding="utf-8")
    BE.move_packet(PACKET, "sent", "replied", repo=tmp_path)
    return tmp_path, reply


def test_a_path_named_under_sent_resolves_to_the_packet_now_in_replied(tmp_path):
    repo, reply = planted(tmp_path)

    outcome = BD.tier0_outcome(ORDER, reply, repo)

    assert outcome["pass"], outcome["reason"]
    exists = next(c for c in outcome["checks"] if c["name"].startswith("exists:"))
    assert Path(exists["detail"]) == BE.packet_dir(repo, PACKET, "replied") / "FINDINGS.md"


def test_an_absolute_path_under_sent_is_followed_too(tmp_path):
    repo, _ = planted(tmp_path)
    absolute = (repo / BE.BRIDGE_ROOT / "sent" / PACKET / "FINDINGS.md").as_posix()

    outcome = BD.tier0_outcome(ORDER, grammar(absolute), repo)

    assert outcome["pass"], outcome["reason"]


def test_the_tick_closes_the_moved_packet_and_queues_no_repair(tmp_path):
    repo, _ = planted(tmp_path)

    BD.tick_once(repo, dict(BD.DEFAULTS))

    assert BE.packet_dir(repo, PACKET, "done").is_dir()
    assert not BE.packet_dir(repo, PACKET, "replied").exists()
    assert list((repo / BE.BRIDGE_ROOT / "queue").iterdir()) == []   # no repair re-asks for a path the daemon moved


def test_a_file_that_is_in_no_packet_folder_still_fails(tmp_path):
    repo, _ = planted(tmp_path)
    ghost = f"{BE.BRIDGE_ROOT.as_posix()}/sent/{PACKET}/GHOST.md"

    outcome = BD.tier0_outcome(ORDER, grammar(ghost), repo)

    assert not outcome["pass"]
    assert "GHOST.md" in outcome["reason"]


def test_follow_leaves_a_path_outside_the_bridge_alone(tmp_path):
    assert BH.follow_moved_packet(tmp_path / "docs" / "research" / "tech" / "note.md") is None
