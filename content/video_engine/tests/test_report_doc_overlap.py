"""The overlap report is the mechanical half of "lift the differences out and dedupe".

A doc marked "superseded by" / "record only" / "partially superseded" was compressed INTO a target,
and the compressed doc still holds detail the target dropped. These tests pin the two halves the
operator's ruling needs: pair DISCOVERY (from an `AGENTS.md` sentence, from a `> **STATUS:` byline,
from `--pair`, and an unresolvable target reported rather than guessed), and section CLASSIFICATION
(DUPLICATE / PARTIAL / DELTA plus the rule lines that get lifted).

The synthetic repo is a whole miniature corpus in `tmp_path` - the discovery walk is a real walk, so
a fixture is a directory, not a monkeypatched list.

The last two tests run over the REAL tree: docs 15 and 16 both pair to 29, and doc 15's motion
discipline / doc 16's motion ownership - the "Motion is authored in this order" ladder that doc 29
does not carry (P45 decision 1) - must NOT come back DUPLICATE, because that ladder is exactly the
lift the ruling is about.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import report_doc_overlap as RDO  # noqa: E402

DOC_15_REL = "docs/content-video-engine/15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md"
DOC_16_REL = "docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md"
DOC_29_REL = "docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md"

CVE = "docs/content-video-engine"

# --- the synthetic corpus -----------------------------------------------------------------

AGENTS = """# AGENTS.md - the fake playbook

Some preamble that names nothing.

- [`docs/content-video-engine/29-FAKE-MOTION.md`](docs/content-video-engine/29-FAKE-MOTION.md)
  — **motion and evidence choreography, the production bar.** Part 3 is the chain.
  Doc 16 (editorial motion) is partially superseded by it and doc 15
  (living-scene language) is record only - where they disagree on motion, 29 wins.
  The renderer is `samples/player.template.html`; do not write another.
"""

DOC_29 = """# 29 - Fake Motion Standards

> **STATUS: DOCTRINE.** The production bar for every channel.

## Timing authority

The `beat_plan.v1` contract owns `duration_ms`. Every shot must declare its duration
in the plan, and the renderer may never invent one.

## 8.1 The shape

A scene is a plate, an evidence card, and a caption. The plate never leaves.
"""

DOC_16 = """# 16 - Fake Editorial Motion

> **STATUS: PARTIALLY SUPERSEDED.** The production pattern is now the scene-evidence lane
> in **29**. Sections 29 does not replace still apply.

## Timing authority

The `beat_plan.v1` contract owns `duration_ms`. Every shot must declare its duration
in the plan, and the renderer may never invent one.

## 2. Plan contract

The `beat_plan.v1` and `shot_table.v1` records carry `duration_ms` per shot; the plan is
the instruction boundary and the renderer must not invent a beat that the plan omits.

## 3. Motion ownership

Motion is authored in this order:

1. Character or prop action.
2. Camera action.

This section records how the decision was reached.
"""

DOC_22 = """# 22 - Fake Audio Runbook

> **STATUS: DEPRECATED.** Kept for the reasoning trail; superseded by **37 §8**,
> Recording Standards v2 (master-take rule; splice-repair banned).

## 1. Splice repair

A splice must never cross a breath.
"""

DOC_37 = """# 37 - Fake TTS Delivery

## 8. Recording standards v2

The master take is the unit. A splice must never cross a breath.
"""

DOC_99 = """# 88 - Fake Orphan

> **STATUS: DEPRECATED.** superseded by **91**, which is not a document in this tree.

## 1. Something

A rule that must survive.
"""


def make_repo(tmp_path: Path) -> Path:
    """A miniature corpus: an AGENTS sentence, three bylines, and the docs they name."""
    (tmp_path / CVE).mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text(AGENTS, encoding="utf-8")
    for name, text in (
        ("29-FAKE-MOTION.md", DOC_29),
        ("16-FAKE-EDITORIAL.md", DOC_16),
        ("15-FAKE-LIVING-SCENE.md", "# 15 - Fake Living Scene\n\n> **STATUS: RECORD.** Not maintained.\n\n## 5. Motion discipline\n\nMotion is authored in this order:\n\n1. Character or prop action.\n2. Camera action.\n\nThis section records how the decision was reached.\n"),
        ("22-FAKE-AUDIO.md", DOC_22),
        ("37-FAKE-TTS.md", DOC_37),
        ("88-FAKE-ORPHAN.md", DOC_99),
    ):
        (tmp_path / CVE / name).write_text(text, encoding="utf-8")
    return tmp_path


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path)


def pair_map(report: RDO.Report) -> dict[str, str]:
    return {RDO.doc_key(p.compressed): RDO.doc_key(p.target) for p in report.pairs}


def sections(report: RDO.Report, compressed_doc: str) -> dict[str, dict]:
    """{heading: record} for one compressed doc, keyed by the record's heading."""
    return {r["heading"]: r for r in report.records
            if RDO.doc_key(r["path"]) == compressed_doc}


# --- discovery ----------------------------------------------------------------------------

def test_pairs_are_discovered_from_the_agents_sentence(repo: Path) -> None:
    report = RDO.build(repo)
    assert pair_map(report)["16"] == "29"
    assert pair_map(report)["15"] == "29"
    named = {RDO.doc_key(p.compressed): p for p in report.pairs}
    assert "record only" in named["15"].sentence
    assert "partially superseded by it" in named["16"].sentence
    assert named["15"].source.startswith("AGENTS.md:")


def test_a_status_byline_names_its_own_pair(repo: Path) -> None:
    report = RDO.build(repo)
    assert pair_map(report)["22"] == "37"
    byline = next(p for p in report.pairs if RDO.doc_key(p.compressed) == "22")
    assert "superseded by" in byline.sentence
    assert byline.source.endswith(":3")          # the byline line, not the title


def test_an_unresolvable_target_is_reported_not_guessed(repo: Path) -> None:
    report = RDO.build(repo)
    assert "88" not in pair_map(report)
    orphan = [u for u in report.unresolved if RDO.doc_key(u.path) == "88"]
    assert len(orphan) == 1
    assert "91" in orphan[0].reason
    assert "superseded by" in orphan[0].sentence


def test_an_explicit_pair_adds_and_overrides(repo: Path) -> None:
    added = RDO.build(repo, pairs=["88=37"])
    assert pair_map(added)["88"] == "37"
    overridden = RDO.build(repo, pairs=["15=37"])
    assert pair_map(overridden)["15"] == "37"          # the AGENTS sentence is replaced, not doubled
    assert sum(1 for p in overridden.pairs if RDO.doc_key(p.compressed) == "15") == 1


# --- classification -----------------------------------------------------------------------

def test_the_three_classes_and_the_rules_that_get_lifted(repo: Path) -> None:
    report = RDO.build(repo)
    rows = sections(report, "16")

    duplicate = rows["Timing authority"]
    assert duplicate["class"] == "DUPLICATE"
    assert duplicate["best_target"]["heading"] == "Timing authority"
    assert duplicate["best_target"]["score_heading"] == 1.0
    assert duplicate["rules"] == []                     # a duplicate is not lifted

    partial = rows["2. Plan contract"]
    assert partial["class"] == "PARTIAL"
    assert partial["best_target"]["path"].endswith("29-FAKE-MOTION.md")
    assert partial["rules"]

    delta = rows["3. Motion ownership"]
    assert delta["class"] == "DELTA"
    texts = [r["text"] for r in delta["rules"]]
    assert "Motion is authored in this order:" in texts          # the lead-in to a ladder is a rule
    assert "1. Character or prop action." in texts
    assert not any("records how the decision was reached" in t for t in texts)
    assert all(r["line"] > delta["line"] for r in delta["rules"])


def test_every_record_carries_its_pair_and_a_class(repo: Path) -> None:
    report = RDO.build(repo)
    assert report.records
    for r in report.records:
        assert r["class"] in {"DUPLICATE", "PARTIAL", "DELTA"}
        assert " -> " in r["pair"]
        assert r["pair"].startswith(r["path"])
        assert r["line"] >= 1


# --- the artifacts ------------------------------------------------------------------------

def test_write_is_deterministic_and_check_is_green_after_it(repo: Path) -> None:
    RDO.write(repo)
    first = (repo / RDO.JSONL_REL).read_bytes(), (repo / RDO.MD_REL).read_bytes()
    RDO.write(repo)
    assert (repo / RDO.JSONL_REL).read_bytes() == first[0]
    assert (repo / RDO.MD_REL).read_bytes() == first[1]
    assert b"\r\n" not in first[0] and b"\r\n" not in first[1]
    assert RDO.check(repo) == []
    assert RDO.main(["--check", "--repo", str(repo)]) == 0


def test_check_is_red_when_a_compressed_doc_moves_on(repo: Path) -> None:
    RDO.write(repo)
    assert RDO.check(repo) == []
    path = repo / CVE / "16-FAKE-EDITORIAL.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n## 9. A new section\n\nIt must be lifted.\n",
                    encoding="utf-8")
    assert RDO.check(repo)
    assert RDO.main(["--check", "--repo", str(repo)]) == 1
    assert RDO.main(["--write", "--repo", str(repo)]) == 0


def test_check_is_red_when_the_report_is_missing(repo: Path) -> None:
    problems = RDO.check(repo)
    assert len(problems) == 2
    assert all("missing" in p for p in problems)


def test_the_markdown_leads_with_delta(repo: Path) -> None:
    text = RDO.render_md(RDO.build(repo))
    assert text.index("### DELTA") < text.index("### PARTIAL") < text.index("### DUPLICATE")
    assert "Motion is authored in this order:" in text
    assert text.endswith("\n")


def test_the_jsonl_is_one_json_object_per_line(repo: Path) -> None:
    lines = RDO.render_jsonl(RDO.build(repo)).splitlines()
    assert lines
    for line in lines:
        record = json.loads(line)
        assert set(record) == {"pair", "path", "line", "heading", "class", "best_target", "rules"}


# --- the real tree ------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real() -> RDO.Report:
    return RDO.build(ROOT)


def test_the_real_corpus_pairs_docs_15_and_16_to_29(real: RDO.Report) -> None:
    found = {(p.compressed, p.target) for p in real.pairs}
    assert (DOC_15_REL, DOC_29_REL) in found
    assert (DOC_16_REL, DOC_29_REL) in found


@pytest.mark.parametrize("path, heading_fragment", [
    (DOC_15_REL, "Motion discipline"),
    (DOC_16_REL, "Motion ownership"),
])
def test_the_motion_authoring_order_is_a_lift_not_a_duplicate(real: RDO.Report, path: str,
                                                              heading_fragment: str) -> None:
    """Doc 29 does not carry the ladder (`rg "authored in this order" 29-...` finds nothing), so the
    section that holds it must classify DELTA or PARTIAL and surface the ladder as a rule."""
    rows = [r for r in real.records if r["path"] == path and heading_fragment in r["heading"]]
    assert len(rows) == 1, f"{path}: {heading_fragment} not found among {len(real.records)} records"
    row = rows[0]
    assert row["class"] in {"DELTA", "PARTIAL"}
    texts = " ".join(r["text"] for r in row["rules"])
    assert "Motion is authored in this order" in texts
    assert "Character or prop action" in texts
