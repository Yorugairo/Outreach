"""`docs_find.py` is the query side of the retrieval layers, and its whole value is the OUTPUT SHAPE.

Round 4 of the benchmark (`evals/RETRIEVAL-BENCHMARK-2026-09-05.md`) measured the layers buying accuracy
and hops at a 16 % token premium, because an `rg` on a layer returns whole JSONL records. So these tests
pin the thing the premium comes from: one compact line per hit, the layer order, the per-layer share of the
cap, the `sed -n` window the summary names, a missing layer that reports instead of crashing - and, over the
REAL tree, that a five-hit budget still reaches the doctrine document and no line runs past 220 characters.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import docs_find as DF  # noqa: E402

MAX_LINE = 220

MANIFEST = {
    "path": "docs/alpha.md", "doc": None, "title": "Alpha doc", "kind": "doctrine",
    "purpose": "The widget purpose line.", "sections": 2, "headings": ["Alpha doc", "Widget section"],
    "labels": [], "leads": [], "defines": [], "mentions": [], "key_terms": ["widget"], "byline": None,
}
INDEX = {
    "path": "docs/alpha.md", "line": 30, "level": 2, "doc": None, "heading": "Widget section",
    "lead": "The lead about widgets.", "labels": [], "terms": [],
}
TOPIC = {
    "topic": "widget", "aliases": ["Widget"], "count": 2,
    "sections": [{"path": "content/x.md", "line": 4, "heading": "Other"},
                 {"path": "docs/alpha.md", "line": 30, "heading": "Widget section"}],
}
CITE = {"from": {"path": "docs/alpha.md", "line": 5, "heading": "Widget section"},
        "ref": "widget-42", "to": None}
GATE = {"id": "G99", "tool": "t.py", "family": "widgets", "rule": "the widget rule",
        "levels": ["FAIL"], "cites": [], "tests": [],
        "source": {"path": "content/video_engine/scripts/t.py", "line": 12}}
ANIMATION = {"kind": "formula", "name": "widgetEase", "expr": "w(t) = t^2", "path": "docs/alpha.md",
             "line": 77, "section": "s", "doc": "42", "status": "tracked", "status_evidence": []}
CRAFT = {"device": "the widget beat", "scale": ["L1"], "macro_or_micro": "micro",
         "what": "what the widget does", "defined_in": [{"path": "docs/alpha.md", "line": 9, "heading": "H"}],
         "gates": [], "judge_only": False, "exemplar": {}}

RECORDS = {
    "docs/DOCS-MANIFEST.jsonl": MANIFEST,
    "docs/DOCS-INDEX.jsonl": INDEX,
    "docs/DOCS-TOPICS.jsonl": TOPIC,
    "docs/DOCS-CITATIONS.jsonl": CITE,
    "docs/GATES-REGISTRY.jsonl": GATE,
    "docs/ANIMATION-REGISTRY.jsonl": ANIMATION,
    "docs/CRAFT-MAP.jsonl": CRAFT,
}

EXPECTED = [
    "[manifest] docs/alpha.md — Alpha doc — The widget purpose line.",
    "[index] docs/alpha.md:30 — Widget section — The lead about widgets.",
    "[topics] widget — 2 sections — docs/alpha.md:30, content/x.md:4",
    "[gates] content/video_engine/scripts/t.py:12 — G99 — the widget rule",
    "[animation] docs/alpha.md:77 — widgetEase — w(t) = t^2",
    "[craft] docs/alpha.md:9 — the widget beat — what the widget does",
]
SUMMARY = ("6 hit(s) in manifest, index, topics, gates, animation, craft; "
           "next: sed -n 10,50p docs/alpha.md")


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A synthetic repo: every layer built, one record each, all of them matching "widget"."""
    (tmp_path / "docs").mkdir()
    for rel, record in RECORDS.items():
        (tmp_path / rel).write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    return tmp_path


def run(capsys, tree: Path, *args: str) -> list[str]:
    assert DF.main([*args, "--repo", str(tree)]) == 0
    return capsys.readouterr().out.splitlines()


def test_every_layer_prints_one_compact_line_in_cheapest_first_order(capsys, tree):
    # Arrange / Act
    lines = run(capsys, tree, "widget")

    # Assert
    assert lines == [*EXPECTED, SUMMARY]


def test_the_matched_field_is_shown_when_it_carries_context(capsys, tree):
    # Arrange: the term only appears in the index record's body terms and its lead
    (tree / "docs/DOCS-INDEX.jsonl").write_text(
        json.dumps({**INDEX, "heading": "Settle", "lead": "A settle is a spring.",
                    "terms": ["overshoot"]}) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "spring", "--layer", "index")

    # Assert: the lead is the match, so the lead is the line
    assert lines[0] == "[index] docs/alpha.md:30 — Settle — A settle is a spring."


def test_a_bare_term_match_shows_the_lead_rather_than_echoing_the_query(capsys, tree):
    # Arrange
    (tree / "docs/DOCS-INDEX.jsonl").write_text(
        json.dumps({**INDEX, "heading": "Settle", "lead": "A settle is a spring.",
                    "terms": ["overshoot"]}) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "overshoot", "--layer", "index")

    # Assert
    assert lines[0] == "[index] docs/alpha.md:30 — Settle — A settle is a spring."


def test_the_citation_graph_answers_only_when_it_is_asked_for(capsys, tree):
    # Act
    everywhere = run(capsys, tree, "widget")
    asked = run(capsys, tree, "widget-42", "--layer", "cites")

    # Assert
    assert not [line for line in everywhere if line.startswith("[cites]")]
    assert asked == ["[cites] docs/alpha.md:5 — Widget section — widget-42",
                     "1 hit(s) in cites"]


def test_the_limit_caps_the_total_and_stops_scanning_further_layers(capsys, tree):
    # Act
    lines = run(capsys, tree, "widget", "--limit", "2")

    # Assert: two layers answered, the rest were never opened, and the count says it was cut
    assert lines == [EXPECTED[0], EXPECTED[1],
                     "2+ hit(s) in manifest, index; next: sed -n 10,50p docs/alpha.md"]


def test_a_layer_that_is_not_built_reports_itself_and_never_crashes(capsys, tree):
    # Arrange
    (tree / "docs/GATES-REGISTRY.jsonl").unlink()

    # Act
    lines = run(capsys, tree, "widget")

    # Assert: the note sits in the layer's own place in the order, and is not counted as a hit
    assert lines[3] == "[gates] not built (run build_docs_layers.py --write)"
    assert lines[-1].startswith("5 hit(s) in manifest, index, topics, gates, animation, craft;")


def test_a_corrupt_record_is_skipped_rather_than_raised(capsys, tree):
    # Arrange
    (tree / "docs/DOCS-INDEX.jsonl").write_text(
        "{not json\n" + json.dumps(INDEX) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "widget", "--layer", "index")

    # Assert
    assert lines == [EXPECTED[1], "1 hit(s) in index; next: sed -n 10,50p docs/alpha.md"]


def test_a_term_that_is_not_valid_regex_is_searched_as_a_literal(capsys, tree):
    # Arrange
    (tree / "docs/GATES-REGISTRY.jsonl").write_text(
        json.dumps({**GATE, "id": "G15b", "rule": "doc 42§42.2 (the settle"}) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "(the settle", "--layer", "gates")

    # Assert
    assert lines[0].startswith("[gates] content/video_engine/scripts/t.py:12 — G15b — doc 42§42.2")


def test_no_hits_still_names_the_layers_it_searched(capsys, tree):
    # Act
    lines = run(capsys, tree, "no-such-term-anywhere")

    # Assert
    assert lines == ["0 hit(s) in manifest, index, topics, gates, animation, craft"]


def test_json_carries_the_same_hits_plus_the_window(capsys, tree):
    # Act
    payload = json.loads("\n".join(run(capsys, tree, "widget", "--json")))

    # Assert
    assert payload["query"] == "widget"
    assert payload["count"] == 6
    assert payload["truncated"] is False
    assert payload["missing"] == []
    assert payload["layers_scanned"] == list(DF.ALL_ORDER)
    assert payload["next"] == "sed -n 10,50p docs/alpha.md"
    assert [hit["layer"] for hit in payload["hits"]] == list(DF.ALL_ORDER)
    assert payload["hits"][1] == {
        "layer": "index", "path": "docs/alpha.md", "line": 30, "name": "Widget section",
        "snippet": "The lead about widgets.", "line_text": EXPECTED[1],
    }
    assert payload["hits"][2]["sections"] == [{"path": "docs/alpha.md", "line": 30},
                                              {"path": "content/x.md", "line": 4}]


def test_a_long_record_is_clamped_to_one_readable_line(capsys, tree):
    # Arrange: a deep path, a long heading and a long lead - the shape that blows a line budget
    long_path = "content/video_engine/sources/reference_analyses/" + "a" * 90 + ".md"
    (tree / "docs/DOCS-INDEX.jsonl").write_text(
        json.dumps({**INDEX, "path": long_path, "heading": "widget " + "H" * 200,
                    "lead": "L" * 400}) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "widget", "--layer", "index")

    # Assert
    assert lines[0].startswith(f"[index] {long_path}:30 — widget ")
    assert len(lines[0]) <= MAX_LINE


# --------------------------------------------------------------------------- the real tree

REAL_INDEX = ROOT / "docs/DOCS-INDEX.jsonl"


@pytest.mark.skipif(not REAL_INDEX.is_file(),
                    reason="the layers are not built in this checkout (build_docs_layers.py --write)")
def test_the_real_tree_reaches_the_doctrine_document_inside_a_five_hit_budget(capsys):
    # Act
    assert DF.main(["minimum-jerk", "--limit", "5", "--repo", str(ROOT)]) == 0
    lines = capsys.readouterr().out.splitlines()

    # Assert: the doctrine doc, not the research bundle, and every line stays readable
    index_hits = [line for line in lines if line.startswith("[index] ")]
    assert [line for line in index_hits if "42-DRAWING-KINETICS.md" in line]
    assert all(len(line) <= MAX_LINE for line in lines)
    assert lines[-1].startswith("5+ hit(s) in ")
    assert "; next: sed -n " in lines[-1]
