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
EFFECT = {"id": "dock_payload:widget", "axis": "dock_payload", "token": "widget", "title": "The widget card",
          "aliases": [{"name": "widget wall", "source": "operator 2026-09-13"}], "does": "The widget lands on its beat.",
          "lives": {"form": "inline", "path": "docs/alpha.mjs", "symbol": "drawWidget"}}

CAPABILITY = {"id": "widget-engine", "name": "Widget engine", "section": "Rendering", "line": 12,
              "what": "draws the widget on its word.", "where": ["docs/alpha.mjs"], "state": "LIVE",
              "state_note": "LIVE", "proof": [], "cards": ["dock_payload:widget"], "rulings": [],
              "backlog": [], "form": "four", "terms": ["widget", "draws"]}
CAP_DOC = "docs/content-video-engine/CAPABILITIES.md"
ASSET = {"library": "props", "id": "prop-gadget-v1", "name": "Gadget prop", "category": "macro",
         "tier": "prop", "kind": "prop", "catalog_kind": None, "form": None, "tags": ["gadget"],
         "context": "a gadget on the desk",
         "path": "content/video_engine/assets/props/cutouts/prop-gadget-v1.png", "size": "2x2",
         "sha256": "aa", "catalogue": "content/video_engine/assets/props/CATALOGUE.md",
         "on_disk": True, "render_eligible": None}

RECORDS = {
    "docs/CAPABILITIES-INDEX.jsonl": CAPABILITY,
    "docs/ASSETS-INDEX.jsonl": ASSET,
    "docs/EFFECTS-CATALOG.jsonl": EFFECT,
    "docs/DOCS-MANIFEST.jsonl": MANIFEST,
    "docs/DOCS-INDEX.jsonl": INDEX,
    "docs/DOCS-TOPICS.jsonl": TOPIC,
    "docs/DOCS-CITATIONS.jsonl": CITE,
    "docs/GATES-REGISTRY.jsonl": GATE,
    "docs/ANIMATION-REGISTRY.jsonl": ANIMATION,
    "docs/CRAFT-MAP.jsonl": CRAFT,
}

EXPECTED = [
    f"[capabilities] {CAP_DOC}:12 — Widget engine — LIVE - draws the widget on its word.",
    "[effects] docs/alpha.mjs — The widget card — dock_payload:widget - The widget lands on its beat.",
    "[manifest] docs/alpha.md — Alpha doc — The widget purpose line.",
    "[index] docs/alpha.md:30 — Widget section — The lead about widgets.",
    "[topics] widget — 2 sections — docs/alpha.md:30, content/x.md:4",
    "[gates] content/video_engine/scripts/t.py:12 — G99 — the widget rule",
    "[animation] docs/alpha.md:77 — widgetEase — w(t) = t^2",
    "[craft] docs/alpha.md:9 — the widget beat — what the widget does",
]
SUMMARY = ("8 hit(s) in capabilities, assets, effects, manifest, index, topics, gates, animation, craft; "
           f"next: sed -n 12p {CAP_DOC}")


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
                     "1 hit(s) in cites; next: sed -n 1,25p docs/alpha.md"]


def test_the_limit_caps_the_total_and_stops_scanning_further_layers(capsys, tree):
    # Arrange: no capabilities layer, so the first two built layers carry no line
    (tree / "docs/CAPABILITIES-INDEX.jsonl").unlink()

    # Act
    lines = run(capsys, tree, "widget", "--limit", "2")

    # Assert: two layers answered, the rest were never opened, and the count says it was cut;
    # neither hit has a line, so the effect's card is the window
    assert lines == ["[capabilities] not built (run build_docs_layers.py --write)",
                     EXPECTED[1], EXPECTED[2], "2+ hit(s) in capabilities, assets, effects, manifest; "
                     'next: python content/video_engine/scripts/effects_card.py "dock_payload:widget"']


def test_an_effects_hit_first_never_suppresses_the_window_of_a_lined_hit(capsys, tree):
    # Arrange: no capabilities, manifest or index, so the first lined hit under the cap is a gate
    (tree / "docs/CAPABILITIES-INDEX.jsonl").unlink()
    (tree / "docs/DOCS-MANIFEST.jsonl").unlink()
    (tree / "docs/DOCS-INDEX.jsonl").unlink()

    # Act
    lines = run(capsys, tree, "widget", "--limit", "3")

    # Assert
    assert lines[1] == EXPECTED[1]
    assert lines[-1] == ("3+ hit(s) in capabilities, assets, effects, manifest, index, topics, gates; "
                         "next: sed -n 1,32p content/video_engine/scripts/t.py")


def test_a_capabilities_hit_leads_and_its_window_is_its_one_row(capsys, tree):
    # Act
    lines = run(capsys, tree, "widget", "--limit", "1")

    # Assert
    assert lines == [EXPECTED[0], f"1+ hit(s) in capabilities; next: sed -n 12p {CAP_DOC}"]


def test_a_capability_named_for_the_term_ranks_before_one_that_only_says_it(capsys, tree):
    # Arrange: the first record says "gizmo" only in its prose terms, the second names it
    prose = {**CAPABILITY, "id": "a", "name": "Alpha", "line": 5, "terms": ["gizmo"]}
    named = {**CAPABILITY, "id": "b", "name": "The gizmo gate", "line": 9}
    (tree / "docs/CAPABILITIES-INDEX.jsonl").write_text(
        json.dumps(prose) + "\n" + json.dumps(named) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "gizmo", "--layer", "capabilities")

    # Assert
    assert [line.split(" — ")[1] for line in lines[:2]] == ["The gizmo gate", "Alpha"]


def test_the_capabilities_list_prints_the_page_lines_filtered_by_state_and_section(capsys, tree):
    # Arrange
    wired = {**CAPABILITY, "id": "w", "name": "Wired thing", "section": "Gates", "line": 40,
             "state": "WIRED", "what": ""}
    (tree / "docs/CAPABILITIES-INDEX.jsonl").write_text(
        json.dumps(CAPABILITY) + "\n" + json.dumps(wired) + "\n", encoding="utf-8")

    # Act
    everything = run(capsys, tree, "--capabilities")
    live = run(capsys, tree, "--capabilities", "--state", "live")
    gates = run(capsys, tree, "--capabilities", "--section", "gate")

    # Assert
    assert everything[:4] == ["## Rendering",
                              "- Widget engine - LIVE - draws the widget on its word. (CAPABILITIES.md:12)",
                              "## Gates", "- Wired thing - WIRED (CAPABILITIES.md:40)"]
    assert everything[-1].startswith("2 of 2 capabilities; open a row: sed -n <line>p ")
    assert live[:2] == everything[:2] and live[-1].startswith("1 of 2 capabilities (state live)")
    assert gates[:2] == everything[2:4]


def test_the_capabilities_list_without_the_layer_prints_one_line(capsys, tree):
    # Arrange
    (tree / "docs/CAPABILITIES-INDEX.jsonl").unlink()

    # Act / Assert
    assert run(capsys, tree, "--capabilities") == [
        "[capabilities] not built (run build_capabilities_index.py --write)"]


def test_an_effects_only_answer_names_the_card_as_the_window(capsys, tree):
    # Act
    lines = run(capsys, tree, "widget", "--layer", "effects")
    payload = json.loads("\n".join(run(capsys, tree, "widget", "--layer", "effects", "--json")))

    # Assert: the text line and the JSON field name the same window
    card = 'python content/video_engine/scripts/effects_card.py "dock_payload:widget"'
    assert lines == [EXPECTED[1], f"1 hit(s) in effects; next: {card}"]
    assert payload["next"] == card


def test_a_layer_that_is_not_built_reports_itself_and_never_crashes(capsys, tree):
    # Arrange
    (tree / "docs/GATES-REGISTRY.jsonl").unlink()

    # Act
    lines = run(capsys, tree, "widget")

    # Assert: the note sits in the layer's own place in the order, and is not counted as a hit
    assert lines[5] == "[gates] not built (run build_docs_layers.py --write)"
    assert lines[-1].startswith(
        "7 hit(s) in capabilities, assets, effects, manifest, index, topics, gates, animation, craft;")


def test_a_corrupt_record_is_skipped_rather_than_raised(capsys, tree):
    # Arrange
    (tree / "docs/DOCS-INDEX.jsonl").write_text(
        "{not json\n" + json.dumps(INDEX) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "widget", "--layer", "index")

    # Assert
    assert lines == [EXPECTED[3], "1 hit(s) in index; next: sed -n 10,50p docs/alpha.md"]


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
    assert lines == ["0 hit(s) in capabilities, assets, effects, manifest, index, topics, gates, animation, craft"]


def test_json_carries_the_same_hits_plus_the_window(capsys, tree):
    # Act
    payload = json.loads("\n".join(run(capsys, tree, "widget", "--json")))

    # Assert
    assert payload["query"] == "widget"
    assert payload["count"] == 8
    assert payload["truncated"] is False
    assert payload["missing"] == []
    assert payload["layers_scanned"] == list(DF.ALL_ORDER)
    assert payload["next"] == f"sed -n 12p {CAP_DOC}"
    assert [hit["layer"] for hit in payload["hits"]] == [n for n in DF.ALL_ORDER if n != "assets"]
    assert payload["hits"][3] == {
        "layer": "index", "path": "docs/alpha.md", "line": 30, "name": "Widget section",
        "snippet": "The lead about widgets.", "line_text": EXPECTED[3],
    }
    assert payload["hits"][4]["sections"] == [{"path": "docs/alpha.md", "line": 30},
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
REAL_CAPABILITIES = ROOT / "docs/CAPABILITIES-INDEX.jsonl"
CAPABILITY_LINE_MAX = 240
needs_capabilities = pytest.mark.skipif(
    not REAL_CAPABILITIES.is_file(), reason="build_capabilities_index.py --write has not run here")


@needs_capabilities
@pytest.mark.parametrize("term", ["suck", "ledger page", "melt", "plate library", "one-shot floor"])
def test_the_real_tree_answers_a_capability_term_from_the_capabilities_layer_first(capsys, term):
    # Arrange: does a capability row carry the term in a searched field?
    pattern = DF.build_pattern(term)
    layer = DF.BY_NAME["capabilities"]
    has_row = any(DF.matched_field(r, layer, pattern) for r in DF.read_records(REAL_CAPABILITIES))

    # Act
    assert DF.main([term, "--repo", str(ROOT)]) == 0
    lines = capsys.readouterr().out.splitlines()

    # Assert
    assert has_row, term
    assert lines[0].startswith("[capabilities] docs/content-video-engine/CAPABILITIES.md:")
    assert all(len(line) < CAPABILITY_LINE_MAX for line in lines if line.startswith("[capabilities]"))


@needs_capabilities
def test_the_real_capabilities_list_is_the_index_page_line_for_line(capsys):
    # Arrange
    page = (ROOT / "docs/CAPABILITIES-INDEX.md").read_text(encoding="utf-8")
    body = page.split("\n## Rows the doc should fix", 1)[0]
    want = [line for line in body.splitlines() if line.startswith(("- ", "## "))]

    # Act
    assert DF.main(["--capabilities", "--repo", str(ROOT)]) == 0
    lines = capsys.readouterr().out.splitlines()

    # Assert
    assert lines[:-1] == want


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


def test_the_assets_layer_is_searched_right_after_capabilities(capsys, tree):
    # Arrange / Act
    lines = run(capsys, tree, "gadget prop", "--limit", "5")

    # Assert
    assert DF.ALL_ORDER[:2] == ("capabilities", "assets")
    assert lines[0].startswith("[assets] content/video_engine/assets/props/cutouts/prop-gadget-v1.png")
    assert "catalogue content/video_engine/assets/props/CATALOGUE.md" in lines[0]


TAGGED_ASSET = {**ASSET, "id": "prop-fed-v1", "name": "Fed building", "tags": ["federal-reserve"],
                "context": "the central bank"}


def test_a_plain_spaced_query_matches_a_hyphenated_tag(capsys, tree):
    # Arrange
    (tree / "docs/ASSETS-INDEX.jsonl").write_text(json.dumps(TAGGED_ASSET) + "\n", encoding="utf-8")

    # Act
    lines = run(capsys, tree, "federal reserve", "--layer", "assets")

    # Assert
    assert lines[0].startswith("[assets] content/video_engine/assets/props/cutouts/prop-gadget-v1.png — Fed building")
    assert lines[-1] == "1 hit(s) in assets"


def test_a_regex_query_compiles_exactly_as_before(capsys, tree):
    # Arrange / Act
    pattern = DF.build_pattern(r"\bG99\b")
    lines = run(capsys, tree, r"\bG99\b", "--layer", "gates")

    # Assert
    assert pattern.pattern == r"\bG99\b"
    assert DF.build_pattern("federal-reserve").pattern == "federal-reserve"     # a hyphen is not plain
    assert lines == [EXPECTED[5], "1 hit(s) in gates; next: sed -n 1,32p content/video_engine/scripts/t.py"]


def test_all_words_answers_only_when_the_phrase_hits_nothing(capsys, tree):
    # Arrange / Act: no record says "gadget catalogue", but the asset carries both words
    lines = run(capsys, tree, "gadget catalogue", "--layer", "assets")

    # Assert
    assert lines[0].startswith("[assets] content/video_engine/assets/props/cutouts/prop-gadget-v1.png")
    assert lines[-1] == "1 hit(s) in assets (all words)"


def test_a_phrase_that_hits_never_falls_back(capsys, tree):
    # Arrange / Act
    lines = run(capsys, tree, "gadget prop", "--layer", "assets")
    payload = json.loads("\n".join(run(capsys, tree, "gadget prop", "--layer", "assets", "--json")))

    # Assert
    assert lines[-1] == "1 hit(s) in assets"
    assert "(all words)" not in "\n".join(lines)
    assert payload["all_words"] is False


PROPS_RECORD = {**ASSET, "id": "prop-desk-v1", "name": "Desk", "tags": ["furniture"], "context": "an office desk",
                "path": "content/video_engine/assets/props/cutouts/prop-desk-v1.png"}
ICON_RECORD = {**ASSET, "library": "icons", "id": "prop-icon-desk-v1", "name": "Desk badge", "tier": 2,
               "kind": "icon", "catalog_kind": "prop", "tags": ["furniture"], "context": "a desk badge",
               "path": "content/video_engine/assets/icons/cutouts/prop-icon-desk-v1.png",
               "catalogue": "content/video_engine/assets/icons/CATALOGUE.md"}


@pytest.mark.parametrize("term", ["prop", "prop catalogue"])
def test_what_an_asset_is_ranks_before_a_word_inside_another_assets_id(capsys, tree, term):
    # Arrange: the icon comes first in file order and its id starts `prop-`
    rows = [ICON_RECORD, PROPS_RECORD]
    (tree / "docs/ASSETS-INDEX.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    # Act
    lines = run(capsys, tree, term, "--layer", "assets")

    # Assert
    assert lines[0].startswith("[assets] content/video_engine/assets/props/cutouts/prop-desk-v1.png — Desk — props prop")
    assert lines[1].startswith("[assets] content/video_engine/assets/icons/cutouts/prop-icon-desk-v1.png — Desk badge — icons icon")
    assert lines[-1].startswith("2 hit(s) in assets")
