"""P54 T1: the operator ledger extractor over small synthetic transcripts (never the real ~/.claude data)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import extract_operator_ledger as L  # noqa: E402


def _dump(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")   # the compact form Claude Code writes


def _user(ts: str, content, **extra) -> dict:
    return {"type": "user", "timestamp": ts, "sessionId": "s1", "cwd": "/repo",
            "message": {"role": "user", "content": content}, **extra}


def _asst(ts: str, blocks: list[dict]) -> dict:
    return {"type": "assistant", "timestamp": ts, "message": {"role": "assistant", "content": blocks}}


def _queued(ts: str, prompt) -> dict:
    return {"type": "attachment", "timestamp": ts, "attachment": {"type": "queued_command", "prompt": prompt}}


def _run(tmp_path: Path, *extra: str) -> int:
    return L.main(["--projects", str(tmp_path / "projects" / "**" / "*.jsonl"),
                   "--out", str(tmp_path / "out"), "--repo-root", str(tmp_path / "repo"), *extra])


def _ledger(tmp_path: Path) -> list[dict]:
    return L.read_jsonl(tmp_path / "out" / "LEDGER.jsonl")


@pytest.fixture
def transcripts(tmp_path: Path) -> Path:
    main = tmp_path / "projects" / "C--Outreach-Program" / "sess.jsonl"
    _dump(main, [
        _user("2026-09-10T10:00:00.000Z", "a one-shot is never a test"),
        _asst("2026-09-10T10:00:01.000Z", [{"type": "text", "text": "Understood."},
                                            {"type": "tool_use", "name": "Read", "input": {}}]),
        _asst("2026-09-10T10:00:02.000Z", [{"type": "text", "text": "second text"},
                                            {"type": "tool_use", "name": "Bash", "input": {}}]),
        _user("2026-09-10T10:00:03.000Z", [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]),
        _user("2026-09-10T10:01:00.000Z", [{"type": "text", "text": "Wash beats the focus rack"}]),
        _user("2026-09-10T10:02:00.000Z", [{"type": "image", "source": {}}, {"type": "image", "source": {}},
                                           {"type": "text", "text": "look at this frame"}]),
        _queued("2026-09-10T10:03:00.000Z", "typed while you were working"),
        _user("2026-09-10T10:04:00.000Z",
              "<command-message>prp-plan</command-message>\n<command-name>/prp-plan</command-name>\n"
              "<command-args>plan the ledger</command-args>"),
        _user("2026-09-10T10:05:00.000Z", "<command-name>/model</command-name>\n<command-args>opus</command-args>"),
        _user("2026-09-10T10:06:00.000Z", "meta words", isMeta=True),
        _user("2026-09-10T10:07:00.000Z", "summary words", isCompactSummary=True),
        _user("2026-09-10T10:08:00.000Z", "sidechain words", isSidechain=True),
        _user("2026-09-10T10:09:00.000Z", '{"packetId": "p1", "brief": "review"}'),
        _user("2026-09-10T10:10:00.000Z", "Stop   doing that"),
        _user("2026-09-10T10:15:00.000Z", "stop doing that"),          # near-duplicate, 300 s later
        _user("2026-09-10T12:10:00.000Z", "Stop doing that"),          # same text 2 h later: kept
    ])
    _dump(tmp_path / "projects" / "C--Outreach-Program" / "sess" / "subagents" / "agent-1.jsonl",
          [_user("2026-09-10T10:20:00.000Z", "subagent prompt words")])
    return tmp_path


def _texts(rows):
    return [r["text"] for r in rows]


def test_full_run_keeps_operator_shapes_and_drops_the_rest(transcripts: Path):
    assert _run(transcripts, "--full") == 0
    rows = _ledger(transcripts)
    assert _texts(rows) == ["a one-shot is never a test", "Wash beats the focus rack", "look at this frame",
                            "typed while you were working", "plan the ledger", "Stop   doing that",
                            "Stop doing that"]
    by = {r["text"]: r for r in rows}
    assert by["a one-shot is never a test"]["via"] == "typed"
    assert by["look at this frame"]["images"] == 2
    assert by["typed while you were working"]["via"] == "mid-turn"
    assert (by["plan the ledger"]["via"], by["plan the ledger"]["slash"]) == ("slash", "/prp-plan")
    for gone in ("opus", "meta words", "summary words", "sidechain words", "subagent prompt words", "ok"):
        assert gone not in _texts(rows)


def test_default_run_writes_no_markdown(transcripts: Path):
    _run(transcripts, "--full")
    assert sorted(p.name for p in (transcripts / "out").iterdir()) == ["LEDGER.jsonl"]


def test_reply_is_first_assistant_text_and_tool_calls_count(transcripts: Path):
    _run(transcripts, "--full")
    first = _ledger(transcripts)[0]
    assert first["reply"] == "Understood."
    assert first["tool_calls"] == 2
    assert "correction" in first["cues"] and "rule" in first["cues"]


def test_row_id_is_sha1_prefix_of_ts_and_text(transcripts: Path):
    _run(transcripts, "--full")
    r = _ledger(transcripts)[0]
    assert r["id"] == L.row_id(r["ts"], r["text"]) and len(r["id"]) == 12


def test_md_on_demand_truncates_pasted_rows(tmp_path: Path):
    long = "Traceback (most recent call last)\n" + "word " * 400
    _dump(tmp_path / "projects" / "p" / "s.jsonl", [_user("2026-09-10T09:00:00.000Z", long)])
    md_path = tmp_path / "view" / "LEDGER.md"
    _run(tmp_path, "--full", "--md", str(md_path))
    row = _ledger(tmp_path)[0]
    md = md_path.read_text(encoding="utf-8")
    assert row["pasted"] and row["text"] == long.strip()
    assert f"### 09:00 `{row['id']}` typed" in md
    assert "[pasted, 405 words - full text in LEDGER.jsonl]" in md
    assert md.count("word") < 100


def test_incremental_run_appends_only_newer_messages(transcripts: Path):
    _run(transcripts, "--full")
    before = _ledger(transcripts)
    _dump(transcripts / "projects" / "C--Outreach-Program" / "sess.jsonl",
          [_user("2026-09-11T08:00:00.000Z", "one newer message")])
    assert _run(transcripts) == 0
    after = _ledger(transcripts)
    assert len(after) == len(before) + 1
    assert after[:-1] == before and after[-1]["text"] == "one newer message"
    assert _run(transcripts) == 0 and len(_ledger(transcripts)) == len(after)


def test_check_exit_codes(transcripts: Path):
    assert _run(transcripts, "--check") == 1                 # no ledger yet: everything is newer
    assert not (transcripts / "out" / "LEDGER.jsonl").exists()
    _run(transcripts, "--full")
    assert _run(transcripts, "--check") == 0
    _dump(transcripts / "projects" / "C--Outreach-Program" / "other.jsonl",
          [_user("2026-09-12T08:00:00.000Z", "later words")])
    assert _run(transcripts, "--check") == 1
    assert len(_ledger(transcripts)) == 7                     # --check wrote nothing


def _triage(tmp_path: Path, rows: list[dict]) -> None:
    path = tmp_path / "out" / "TRIAGE.jsonl"
    path.unlink(missing_ok=True)
    _dump(path, rows)


def _needs_triage(tmp_path: Path) -> list[dict]:
    return [r for r in _ledger(tmp_path) if not r["pasted"] and {"correction", "rule"} & set(r["cues"])]


def _verdict(r: dict, verdict: str = "craft", anchor: str = "") -> dict:
    return {"id": r["id"], "ts": r["ts"], "verdict": verdict, "anchor": anchor, "subject": "", "note": ""}


def test_triage_check_missing_file_fails(transcripts: Path, capsys):
    _run(transcripts, "--full")
    assert _run(transcripts, "--triage-check") == 1
    assert "no triage yet" in capsys.readouterr().out


def test_triage_check_pass(transcripts: Path, capsys):
    _run(transcripts, "--full")
    (transcripts / "repo" / "docs").mkdir(parents=True)
    (transcripts / "repo" / "docs" / "RULINGS.md").write_text("# E1\n", encoding="utf-8")
    need = _needs_triage(transcripts)
    assert len(need) == 3
    _triage(transcripts, [_verdict(need[0], "recorded", "docs/RULINGS.md:E1"),
                          _verdict(need[1], "superseded", need[2]["id"]),
                          _verdict(need[2], "superseded", "E73")])
    assert _run(transcripts, "--triage-check") == 0
    assert "clean - 3" in capsys.readouterr().out


@pytest.mark.parametrize("case", ["missing", "duplicate", "bad-verdict", "missing-anchor-path",
                                  "superseded-missing-row"])
def test_triage_check_failures(transcripts: Path, case: str, capsys):
    _run(transcripts, "--full")
    need = _needs_triage(transcripts)
    good = [_verdict(r) for r in need]
    first = {
        "bad-verdict": _verdict(need[0], "maybe"),
        "missing-anchor-path": _verdict(need[0], "recorded", "docs/NOPE.md:heading"),
        "superseded-missing-row": _verdict(need[0], "superseded", "0123456789ab"),
    }.get(case, good[0])
    rows = {"missing": good[1:], "duplicate": good + [good[0]]}.get(case, [first] + good[1:])
    _triage(transcripts, rows)
    assert _run(transcripts, "--triage-check") == 1
    assert "FAIL" in capsys.readouterr().out


def test_superseded_by_an_older_ruling_or_a_doc_section(tmp_path):
    """P54 T2: `D1` overturned a word-patch procedure, and doc 37 section 21 retired a tag cap - both are real anchors."""
    import extract_operator_ledger as X
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "37.md").write_text("## 21. BREAK TAGS RETIRED", encoding="utf-8")
    ids = {"aaaaaaaaaaaa"}
    assert X.superseded_anchor_ok("D1", ids, tmp_path)
    assert X.superseded_anchor_ok("docs/37.md:21. BREAK TAGS RETIRED", ids, tmp_path)
    assert not X.superseded_anchor_ok("docs/missing.md:21", ids, tmp_path)
    assert not X.superseded_anchor_ok("F9", ids, tmp_path)
