"""The topic index is the context layer over the docs index: "everything we hold about X" and
"what cites 42 §42.2", both derived, never hand-written.

These pin the topic key (casefold, `_`/`-`/space collapse, singular-only-when-it-occurs), that the
merge is surface normalisation and not synonymy (`minimum-jerk` is its own word), the
single-section drop and its citation / formula-symbol exception, one citation edge of every
reference form the spec lists resolving to the right heading, an unresolved reference staying
`to: null`, fenced code contributing nothing, `--write` being byte-identical twice, and `--check`
going red when a doc gains a reference.

The last test runs over the REAL index: a `spring` topic reaches three files, `42§42.2` resolves to
doc 42's settle, and `E38` resolves to the rulings ledger."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_docs_index as BDI  # noqa: E402
import build_topic_index as BTI  # noqa: E402

DOC_42_REL = "docs/content-video-engine/42-FAKE-KINETICS.md"
DOC_47_REL = "docs/content-video-engine/47-FAKE-CHECKS.md"
DOC_29_REL = "docs/content-video-engine/29-FAKE-MOTION.md"
DOC_38_REL = "docs/content-video-engine/38-FAKE-ARCHITECTURE.md"
DOC_48_REL = "docs/content-video-engine/48-FAKE-CITER.md"
RULINGS_REL = "docs/portable/OPERATOR-RULINGS.md"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
CAPS_REL = "docs/content-video-engine/CAPABILITIES.md"
VOICE_REL = "docs/portable/VOICE-FAKE.md"

DOC_42 = (
    "# 42 — Fake kinetics\n"                                                        # 1
    "\n"                                                                            # 2
    "The **min-jerk** front, `min_jerk` in code, is not **minimum-jerk**.\n"         # 3
    "\n"                                                                            # 4
    "## 42.2 The settle — closed form\n"                                            # 5
    "\n"                                                                            # 6
    "Min-jerk again, and the rim is Deegan 1997.\n"                                 # 7
)

DOC_47 = (
    "# 47 — Fake checks\n"                                                          # 1
    "\n"                                                                            # 2
    "## M13 No still over six seconds\n"                                            # 3
    "\n"                                                                            # 4
    "The motion gate.\n"                                                            # 5
)

DOC_29 = (
    "# 29 — Fake motion\n"                                                          # 1
    "\n"                                                                            # 2
    "## Part 3 — Linked-evidence choreography\n"                                    # 3
    "\n"                                                                            # 4
    "The chain is the transition.\n"                                                # 5
    "\n"                                                                            # 6
    "### 9.31 The cross-reveal wipe\n"                                              # 7
    "\n"                                                                            # 8
    "The wipe.\n"                                                                   # 9
)

DOC_38 = (
    "# 38 — Fake architecture\n"                                                    # 1
    "\n"                                                                            # 2
    "## B2 The promise\n"                                                           # 3
    "\n"                                                                            # 4
    "Stated by 0:30.\n"                                                             # 5
)

DOC_48 = (
    "# 48 — Fake citer\n"                                                           # 1
    "\n"                                                                            # 2
    "## 48.1 The chain\n"                                                           # 3
    "\n"                                                                            # 4
    "The settle is 42 §42.2, the gate 47 §M13, the choreography 29 Part 3.\n"        # 5
    "The promise is 38 B2; see doc 47 and §9.31; the ruling is E38, the row T2.\n"   # 6
    "Nothing in the index defines S02.\n"                                           # 7
    "\n"                                                                            # 8
    "```text\n"                                                                     # 9
    "42 §42.2 and E38 inside a fence are not references.\n"                         # 10
    "```\n"                                                                         # 11
)

RULINGS = (
    "# OPERATOR RULINGS\n"                                                          # 1
    "\n"                                                                            # 2
    "## E38 — Thresholds are measured on the reference (2026-09-04)\n"               # 3
    "\n"                                                                            # 4
    "Measure the reference first.\n"                                                # 5
)

BACKLOG = (
    "# Backlog\n"                                                                   # 1
    "\n"                                                                            # 2
    "| # | item | the decision |\n"                                                 # 3
    "|---|---|---|\n"                                                               # 4
    "| **T2** | **Analytic spring evaluator** | landed |\n"                          # 5
)

CAPS = (
    "# Capabilities\n"                                                              # 1
    "\n"                                                                            # 2
    "| Capability | Where | State |\n"                                              # 3
    "|---|---|---|\n"                                                               # 4
    "| **G15b ring mechanism** — the close returns the stems | `gate.py` | LIVE |\n"  # 5
)

VOICE = (
    "# Voice\n"                                                                     # 1
    "\n"                                                                            # 2
    "Flash & Hogan (1985) fixed it; ω₀ is the frequency; a **Solitary label**.\n"    # 3
)

TREE = {
    DOC_42_REL: DOC_42, DOC_47_REL: DOC_47, DOC_29_REL: DOC_29, DOC_38_REL: DOC_38,
    DOC_48_REL: DOC_48, RULINGS_REL: RULINGS, BACKLOG_REL: BACKLOG, CAPS_REL: CAPS,
    VOICE_REL: VOICE,
}

CITER_SECTION = {"path": DOC_48_REL, "line": 3, "heading": "48.1 The chain"}


def _tree(tmp_path: Path) -> Path:
    for rel, text in TREE.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def _built(tmp_path: Path) -> tuple[dict[str, dict], list[dict]]:
    """(topics by key, edges) over the synthetic tree, through the real index builder."""
    root = _tree(tmp_path)
    topics, edges = BTI.build(BDI.build_index(root), root)
    return {t["topic"]: t for t in topics}, edges


def _refs(edges: list[dict], section: dict) -> dict[str, dict | None]:
    return {e["ref"]: e["to"] for e in edges if e["from"] == section}


# --- topics -------------------------------------------------------------------------------

def test_surface_forms_merge_into_one_key_but_a_different_word_stays_a_different_topic(tmp_path: Path) -> None:
    # Arrange / Act
    topics, _ = _built(tmp_path)

    # Assert - case and `_`/`-` are surface; "minimum-jerk" is a different word, held once, dropped
    assert topics["min-jerk"]["aliases"] == ["Min-jerk", "min-jerk", "min_jerk"]
    assert topics["min-jerk"]["count"] == 2
    assert topics["min-jerk"]["sections"] == [
        {"path": DOC_42_REL, "line": 1, "heading": "42 — Fake kinetics", "doc": "42"},
        {"path": DOC_42_REL, "line": 5, "heading": "42.2 The settle — closed form", "doc": "42"},
    ]
    assert "minimum-jerk" not in topics


def test_a_single_section_key_is_dropped_unless_it_is_a_citation_or_a_symbol(tmp_path: Path) -> None:
    topics, _ = _built(tmp_path)

    assert "solitary-label" not in topics                     # ordinary prose, held once
    assert topics["flash-hogan"]["count"] == 1                # a citation is a topic on its own
    assert topics["ω₀"]["count"] == 1                         # so is a formula symbol
    assert topics["ω₀"]["sections"] == [
        {"path": VOICE_REL, "line": 1, "heading": "Voice", "doc": None}]


def test_topic_keys_normalise_and_sort_by_count_then_key(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    topics, _ = BTI.build(BDI.build_index(root), root)

    assert all(topic["topic"] == topic["topic"].casefold() for topic in topics)
    assert all(" " not in topic["topic"] and "_" not in topic["topic"] for topic in topics)
    assert [(-t["count"], t["topic"]) for t in topics] == sorted((-t["count"], t["topic"]) for t in topics)


def test_singularisation_folds_a_plural_only_when_the_singular_also_occurs() -> None:
    records = [
        {"path": "docs/a.md", "line": 1, "level": 1, "doc": None, "heading": "A", "lead": "",
         "labels": ["Springs", "Wipes"], "terms": []},
        {"path": "docs/b.md", "line": 1, "level": 1, "doc": None, "heading": "B", "lead": "",
         "labels": ["spring", "Wipes"], "terms": []},
    ]

    topics = {t["topic"]: t for t in BTI.build_topics(records)}

    assert topics["spring"]["aliases"] == ["spring", "Springs"]     # the singular occurs: folded
    assert topics["spring"]["count"] == 2
    assert topics["wipes"]["count"] == 2 and "wipe" not in topics    # no singular anywhere: kept


# --- the citation graph -------------------------------------------------------------------

def test_every_reference_form_resolves_to_the_heading_it_names(tmp_path: Path) -> None:
    _, edges = _built(tmp_path)

    assert _refs(edges, CITER_SECTION) == {
        "42§42.2": {"path": DOC_42_REL, "line": 5, "heading": "42.2 The settle — closed form"},
        "47§M13": {"path": DOC_47_REL, "line": 3, "heading": "M13 No still over six seconds"},
        "29§Part3": {"path": DOC_29_REL, "line": 3, "heading": "Part 3 — Linked-evidence choreography"},
        "38§B2": {"path": DOC_38_REL, "line": 3, "heading": "B2 The promise"},
        "doc47": {"path": DOC_47_REL, "line": 1, "heading": "47 — Fake checks"},
        "29§9.31": {"path": DOC_29_REL, "line": 7, "heading": "9.31 The cross-reveal wipe"},
        "E38": {"path": RULINGS_REL, "line": 3,
                "heading": "E38 — Thresholds are measured on the reference (2026-09-04)"},
        "T2": {"path": BACKLOG_REL, "line": 5, "heading": "T2 Analytic spring evaluator"},
        "S02": None,                       # nothing in the index defines it: null, never a guess
    }


def test_a_fenced_reference_is_not_a_citation(tmp_path: Path) -> None:
    _, edges = _built(tmp_path)

    fenced = [e for e in edges if e["from"]["path"] == DOC_48_REL and e["ref"] in ("42§42.2", "E38")]
    assert len(fenced) == 2                      # the two prose occurrences, not the fenced pair


def test_edges_sort_by_source_then_ref_and_carry_the_enclosing_section(tmp_path: Path) -> None:
    _, edges = _built(tmp_path)

    keys = [(e["from"]["path"], e["from"]["line"], e["ref"]) for e in edges]
    assert keys == sorted(keys, key=lambda k: (k[0].lower(), k[0], k[1], k[2]))
    assert all(e["from"]["line"] > 0 for e in edges if e["from"]["path"] == DOC_48_REL)


def test_a_capabilities_row_answers_a_bare_gate_id(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    (root / DOC_48_REL).write_text(DOC_48 + "\nThe ring is G15b.\n", encoding="utf-8")

    _, edges = BTI.build(BDI.build_index(root), root)

    assert {"path": CAPS_REL, "line": 5, "heading": "G15b ring mechanism"} in [
        e["to"] for e in edges if e["ref"] == "G15b"]


# --- the artifacts ------------------------------------------------------------------------

def _index(root: Path) -> None:
    assert BDI.main(["--write", "--repo", str(root)]) == 0


def test_write_is_byte_identical_across_runs_and_lands_lf(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _index(root)
    rels = (BTI.TOPICS_REL, BTI.CITATIONS_REL, BTI.HUBS_REL)

    assert BTI.main(["--write", "--repo", str(root)]) == 0
    first = {rel: (root / rel).read_bytes() for rel in rels}
    assert BTI.main(["--write", "--repo", str(root)]) == 0
    second = {rel: (root / rel).read_bytes() for rel in rels}

    assert first == second
    assert all(b"\r\n" not in data for data in first.values())


def test_check_is_red_before_the_first_write_and_after_a_doc_gains_a_reference(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _index(root)

    assert BTI.main(["--check", "--repo", str(root)]) == 1          # nothing written yet
    assert BTI.main(["--write", "--repo", str(root)]) == 0
    assert BTI.main(["--repo", str(root)]) == 0                     # no flag is --check

    (root / DOC_38_REL).write_text(DOC_38 + "\nSee 42 §42.2.\n", encoding="utf-8")
    assert BTI.main(["--repo", str(root)]) == 1                     # the docs moved under it
    assert BTI.check(root) == [f"{BTI.CITATIONS_REL} (+1/-0 lines)",
                               f"{BTI.HUBS_REL} (+3/-3 lines)"]     # the new edge, and its hub line


def test_the_hubs_carry_the_recipe_the_top_n_and_who_cites_the_section(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _index(root)

    assert BTI.main(["--write", "--repo", str(root), "--top", "1"]) == 0
    hubs = (root / BTI.HUBS_REL).read_text(encoding="utf-8")

    assert 'rg -i \'"topic": "settle' in hubs
    assert 'rg \'"ref": "42§42.2"\'' in hubs
    assert hubs.count("\n## ") == 1                                  # --top 1
    assert f"cited by: {DOC_48_REL}:3" in hubs


def test_a_missing_index_is_an_error_not_staleness(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    assert BTI.main(["--write", "--repo", str(root)]) == 2


# --- the real corpus ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def real() -> tuple[list[dict], list[dict]]:
    return BTI.build(BTI.load_records(ROOT), ROOT)


def test_the_real_corpus_holds_a_spring_topic_that_spans_at_least_three_files(real) -> None:
    topics, _ = real

    spread = {t["topic"]: len({s["path"] for s in t["sections"]}) for t in topics if "spring" in t["topic"]}
    assert spread, "not found: no topic key contains 'spring' in the real index"
    assert max(spread.values()) >= 3, spread


def test_the_real_graph_resolves_42_section_42_2_and_the_E38_ruling(real) -> None:
    _, edges = real

    settle = [e["to"] for e in edges if e["ref"] == "42§42.2"]
    assert settle and all(to and to["path"] == "docs/content-video-engine/42-DRAWING-KINETICS.md"
                          for to in settle), settle
    rulings = [e["to"] for e in edges if e["ref"] == "E38"]
    assert rulings and all(to and to["path"] == "docs/portable/OPERATOR-RULINGS.md"
                           for to in rulings), rulings


def test_the_real_index_is_the_only_input_the_records_need(real) -> None:
    topics, edges = real

    assert json.loads(json.dumps(topics[0], ensure_ascii=False)).keys() == {
        "topic", "aliases", "sections", "count"}
    assert json.loads(json.dumps(edges[0], ensure_ascii=False)).keys() == {"from", "ref", "to"}
