"""Tier 0: the deterministic close, pinned on synthetic packets and on the two real replies of 2026-09-06.

What is worth pinning is the thing a model would otherwise be paid to do: read the reply, look at the disk,
and say whether they agree. Every test builds its own repo root in `tmp_path`; nothing here starts a model,
opens a socket, touches the real `evals/BRIDGE-LOG.jsonl` or moves a real packet. The two real artefacts -
Gemini's completion report (`7aaa9146`) and Astra's `POSITION: conditional` review - are read where this
machine has them and skipped with a reason where it does not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_env as BE  # noqa: E402
import bridge_handlers as BH  # noqa: E402

REPLAY_REPLY = ROOT / "docs/research/runs/bridge/replay/7aaa9146-88f1-4f03-b004-d5bdf18a5492/reply.md"
PROFILES = ROOT / ".agents/agents"

# Astra's real reply of 2026-09-06, first lines verbatim (the bullets are cut at the first sentence).
ASTRA_REPLY = """POSITION: conditional

DISAGREEMENTS:
- Tool isolation is asserted, not demonstrated.
- Exclusive claim lacks lease/expiry semantics.

PREREQUISITES:
- Env sanitization and post-call verification of the actual auth/model in response metadata.
"""


def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs/research/tech").mkdir(parents=True, exist_ok=True)
    return tmp_path


def write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# --------------------------------------------------------------------------- the grammar


def test_the_grammar_parses_astras_real_review():
    grammar = BH.parse_reply(ASTRA_REPLY)

    assert grammar.position == "conditional"
    assert len(grammar.disagreements) == 2
    assert grammar.disagreements[0].startswith("Tool isolation is asserted")
    assert len(grammar.prerequisites) == 1
    assert grammar.paths_written is None, "an absent header is None, not an empty list"


def test_a_missing_header_is_none_and_a_none_value_is_empty():
    grammar = BH.parse_reply("POSITION: done\nPATHS WRITTEN: none\nDISAGREEMENTS: none\n")

    assert grammar.position == "done"
    assert grammar.paths_written == [] and grammar.disagreements == []
    assert grammar.not_found is None


def test_the_watchers_header_comment_is_not_part_of_the_grammar():
    text = "<!-- lane: gemini; conversationId: x; landedAt: 2026-09-06T00:32:03-07:00 -->\n\nPOSITION: done\n"

    assert BH.parse_reply(text).position == "done"


def test_backticked_paths_are_the_fallback_and_a_command_is_not_a_path():
    text = "Ran `build_docs_layers.py --write` and wrote `docs/a.md` into `C:\\dev\\one network\\.agents\\`."

    found = BH.extract_paths(text)

    assert found == ["docs/a.md", "C:\\dev\\one network\\.agents"]


# --------------------------------------------------------------------------- paths-written


def test_paths_written_passes_when_every_named_path_exists(tmp_path):
    root = repo(tmp_path)
    write(root / "docs/research/tech/note.md", "body\n")
    order = {"replyShape": "paths-written"}

    outcome = BH.classify(order, "PATHS WRITTEN: docs/research/tech/note.md\n", root)

    assert outcome["pass"] and outcome["shape"] == "paths-written"


def test_paths_written_fails_on_a_missing_path_and_names_where_it_looked(tmp_path):
    root = repo(tmp_path)
    order = {"replyShape": "paths-written"}

    outcome = BH.classify(order, "PATHS WRITTEN: docs/research/tech/ghost.md\n", root)

    assert not outcome["pass"]
    assert "not found where I looked" in outcome["reason"]


def test_paths_written_fails_when_the_orders_marker_is_absent(tmp_path):
    root = repo(tmp_path)
    write(root / "docs/research/tech/note.md", "body without the contract\n")
    order = {"replyShape": "paths-written", "marker": "P46 T6 contract"}

    outcome = BH.classify(order, "PATHS WRITTEN: docs/research/tech/note.md\n", root)

    assert not outcome["pass"] and "absent from" in outcome["reason"]


def test_a_reply_that_names_no_path_fails_rather_than_passing_vacuously(tmp_path):
    outcome = BH.classify({"replyShape": "paths-written"}, "All done, boss.\n", repo(tmp_path))

    assert not outcome["pass"] and outcome["reason"] == "no paths named"


# --------------------------------------------------------------------------- contract-block


def test_contract_block_passes_when_source_and_every_copy_carry_it(tmp_path):
    root = repo(tmp_path)
    block = "## This repository's contract"
    for name in ("source.md", "copy-a.md", "copy-b.md"):
        write(root / name, f"head\n{block}\nrules\n")
    order = {"replyShape": "contract-block", "block": block, "source": "source.md", "copies": ["copy-a.md", "copy-b.md"]}

    assert BH.classify(order, "POSITION: done\n", root)["pass"]


def test_contract_block_fails_when_one_copy_lacks_the_block(tmp_path):
    root = repo(tmp_path)
    block = "## This repository's contract"
    write(root / "source.md", f"{block}\n")
    write(root / "copy-a.md", f"{block}\n")
    write(root / "copy-b.md", "head only\n")
    order = {"replyShape": "contract-block", "block": block, "source": "source.md", "copies": ["copy-a.md", "copy-b.md"]}

    outcome = BH.classify(order, "POSITION: done\n", root)

    assert not outcome["pass"] and "copy-b.md" in outcome["reason"]


def test_contract_block_fails_when_the_source_itself_lacks_the_block(tmp_path):
    root = repo(tmp_path)
    block = "## This repository's contract"
    write(root / "source.md", "head only\n")
    write(root / "copy-a.md", f"{block}\n")
    order = {"replyShape": "contract-block", "block": block, "source": "source.md", "copies": ["copy-a.md"]}

    outcome = BH.classify(order, "POSITION: done\n", root)

    assert not outcome["pass"] and outcome["reason"] == "block missing at source"


# --------------------------------------------------------------------------- report-landed


REPORT = """# A report

[Adoption | 41% | Acme | URL: https://example.com/x | Verified 2026-09-06]

## NOT FOUND WHERE I LOOKED
- the roots I searched
"""


def test_report_landed_passes_with_a_proof_line_a_not_found_block_and_green_layers(tmp_path, monkeypatch):
    root = repo(tmp_path)
    write(root / "docs/research/tech/report.md", REPORT)
    calls = []
    monkeypatch.setattr(BH, "run_layers", lambda r: (calls.append(r), (True, "--write then --check exit 0"))[1])

    outcome = BH.classify({"replyShape": "report-landed"}, "Wrote `docs/research/tech/report.md`.\n", root)

    assert outcome["pass"] and len(calls) == 1, "the layers are rebuilt exactly once"


def test_report_landed_fails_without_the_not_found_block_and_never_rebuilds(tmp_path, monkeypatch):
    root = repo(tmp_path)
    write(root / "docs/research/tech/report.md", REPORT.split("## NOT FOUND")[0])
    monkeypatch.setattr(BH, "run_layers", lambda r: pytest.fail("the layers must not be rebuilt for a broken report"))

    outcome = BH.classify({"replyShape": "report-landed"}, "Wrote `docs/research/tech/report.md`.\n", root)

    assert not outcome["pass"] and "NOT FOUND WHERE I LOOKED" in outcome["reason"]


def test_report_landed_fails_when_the_layers_do_not_rebuild(tmp_path, monkeypatch):
    root = repo(tmp_path)
    write(root / "docs/research/tech/report.md", REPORT)
    monkeypatch.setattr(BH, "run_layers", lambda r: (False, "build_docs_layers.py --check exit 1: drift"))

    outcome = BH.classify({"replyShape": "report-landed"}, "Wrote `docs/research/tech/report.md`.\n", root)

    assert not outcome["pass"] and "exit 1" in outcome["reason"]


# --------------------------------------------------------------------------- review


def test_review_passes_on_done_with_nothing_outstanding(tmp_path):
    text = "POSITION: done\nDISAGREEMENTS: none\nPREREQUISITES: none\n"

    assert BH.classify({"replyShape": "review"}, text, repo(tmp_path))["pass"]


def test_review_sends_astras_conditional_review_to_tier_one_by_name(tmp_path):
    outcome = BH.classify({"replyShape": "review"}, ASTRA_REPLY, repo(tmp_path))

    assert not outcome["pass"] and outcome["reason"] == "disagreements"


def test_review_names_prerequisites_and_a_bare_conditional_apart(tmp_path):
    prereq = "POSITION: done\nDISAGREEMENTS: none\nPREREQUISITES:\n- the token store must exist first\n"
    conditional = "POSITION: conditional\nDISAGREEMENTS: none\nPREREQUISITES: none\n"

    assert BH.classify({"replyShape": "review"}, prereq, repo(tmp_path))["reason"] == "prerequisites"
    assert BH.classify({"replyShape": "review"}, conditional, repo(tmp_path))["reason"] == "conditional"


def test_a_review_without_a_position_line_cannot_be_closed(tmp_path):
    outcome = BH.classify({"replyShape": "review"}, "Looks fine to me.\n", repo(tmp_path))

    assert not outcome["pass"] and outcome["reason"] == "no POSITION line"


# --------------------------------------------------------------------------- test-run and free


def test_test_run_passes_on_exit_zero_and_fails_on_exit_one(tmp_path):
    root = repo(tmp_path)
    green = {"replyShape": "test-run", "command": [sys.executable, "-c", "print('ok')"]}
    red = {"replyShape": "test-run", "command": [sys.executable, "-c", "raise SystemExit(1)"]}

    assert BH.classify(green, "POSITION: done\n", root)["pass"]
    assert BH.classify(red, "POSITION: done\n", root)["reason"] == "command exit 1"


def test_a_test_run_order_without_a_command_is_a_refusal_not_a_pass(tmp_path):
    outcome = BH.classify({"replyShape": "test-run"}, "POSITION: done\n", repo(tmp_path))

    assert not outcome["pass"] and outcome["reason"] == "order names no command"


def test_every_free_reply_reaches_tier_one(tmp_path):
    outcome = BH.classify({"replyShape": "free"}, "POSITION: done\nPATHS WRITTEN: none\n", repo(tmp_path))

    assert not outcome["pass"] and outcome["reason"].startswith("free shape")


def test_an_unknown_shape_is_never_silently_closed(tmp_path):
    outcome = BH.classify({"replyShape": "vibes"}, "POSITION: done\n", repo(tmp_path))

    assert not outcome["pass"] and "unknown replyShape" in outcome["reason"]


# --------------------------------------------------------------------------- the real reply of 2026-09-06


@pytest.mark.skipif(not REPLAY_REPLY.exists(), reason=f"no replayed reply on this machine: {REPLAY_REPLY}")
@pytest.mark.skipif(not (PROFILES / "video-researcher.md").exists(), reason=f"the synced profiles are not in {PROFILES}")
def test_geminis_real_completion_report_closes_at_tier_zero_with_no_model():
    text = REPLAY_REPLY.read_text(encoding="utf-8")

    outcome = BH.classify({"replyShape": "paths-written"}, text, ROOT)

    assert outcome["pass"], outcome["reason"]
    assert len([c for c in outcome["checks"] if c["ok"]]) >= 14, "the 11 synced folders and the three profiles"


@pytest.mark.skipif(not REPLAY_REPLY.exists(), reason=f"no replayed reply on this machine: {REPLAY_REPLY}")
def test_the_cli_replays_the_worked_example_and_exits_zero(capsys):
    code = BH.main(["--replay", "7aaa9146-88f1-4f03-b004-d5bdf18a5492", "--repo", str(ROOT)])

    assert code == 0
    assert json.loads(capsys.readouterr().out)["pass"] is True


def test_the_cli_refuses_a_packet_that_is_not_there(tmp_path):
    with pytest.raises(SystemExit) as refusal:
        BH.main(["--packet", "deadbeef", "--repo", str(tmp_path)])

    assert "not found where I looked" in str(refusal.value)


def test_the_cli_reads_a_packet_in_place_and_moves_nothing(tmp_path, capsys):
    root = repo(tmp_path)
    folder = BE.packet_dir(root, "abc123", "replied")
    BE.write_json(folder / "order.json", {"packetId": "abc123", "replyShape": "review"})
    write(folder / "reply.md", "POSITION: done\n")

    code = BH.main(["--packet", "abc123", "--repo", str(root)])

    assert code == 0 and json.loads(capsys.readouterr().out)["pass"] is True
    assert folder.exists() and not BE.packet_dir(root, "abc123", "done").exists()


# ---- an honest abstention is not a pass: tier 0 sends an [UNVERIFIED] verdict on to tier 1 ----
def test_report_landed_fails_when_the_verdict_is_an_abstention(tmp_path, monkeypatch):
    import bridge_handlers as H
    rep = tmp_path / "docs" / "research" / "motion" / "X_RESEARCH_BLUEPRINT.md"
    rep.parent.mkdir(parents=True)
    rep.write_text(
        "# X\n\n[Metric | 99 | source | URL: https://example.org | Verified 2026-09-06]\n\n"
        "## Verdict up front\n[UNVERIFIED] - could not be resolved from the keyframes.\n\n"
        "## NOT FOUND WHERE I LOOKED\nthe boundaries\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(H, "run_layers", lambda repo: (True, "ok"))
    order = {"replyShape": "report-landed", "brief": ""}
    text = "POSITION: done\nPATHS WRITTEN:\n- " + str(rep) + "\n"
    res = H.check_report_landed(order, text, tmp_path)
    assert res["pass"] is False
    assert "abstention" in res["reason"]
    names = {c["name"]: c["ok"] for c in res["checks"]}
    assert names["verdict-verified"] is False and names["proof-line"] is True and names["not-found-block"] is True


# ---- a PATHS WRITTEN item may be a markdown link with a backticked path and a note - the path alone is checked ----
def test_paths_written_items_in_markdown_link_form_yield_the_path_alone():
    import bridge_handlers as H
    item = "[`C:/x/y/video-researcher.md`](file:///C:/x/y/video-researcher.md) (Source)"
    assert H._path_from_item(item) == "C:/x/y/video-researcher.md"
    assert H._path_from_item("[link](file:///C:/a%20b/c.md)") == "C:/a b/c.md"
    assert H._path_from_item("C:/plain/path.md (synced copy)") == "C:/plain/path.md"
    assert H._path_from_item("C:/plain/path.md") == "C:/plain/path.md"


# ---- a reply the transcript cut in half is verified for what survived and failed on the cut itself ----
def test_paths_written_on_a_truncated_reply_verifies_the_whole_items_and_fails_on_the_cut(tmp_path):
    import bridge_handlers as H
    a = tmp_path / "a.md"; a.write_text("x", encoding="utf-8")
    text = ("POSITION: done\nPATHS WRITTEN:\n- `" + str(a) + "`\n- [`C:/half/pa\n<truncated 3478 bytes>\n"
            ".md`](file:///C:/half/other.md)\nDISAGREEMENTS: None.\n")
    res = H.check_paths_written({"replyShape": "paths-written"}, text, tmp_path)
    names = [c["name"] for c in res["checks"]]
    assert res["pass"] is False and "truncated" in res["reason"]
    assert names[0] == "reply-whole"
    assert any(n == f"exists:{a}" and c["ok"] for n, c in zip(names, res["checks"]))
    assert not any("half/pa" in n for n in names)
