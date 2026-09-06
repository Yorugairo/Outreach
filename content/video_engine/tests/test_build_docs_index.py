"""The docs index is a retrieval contract: one record per heading, greppable in one `rg` call.

These pin the record shape on a synthetic docs tree (fenced headings excluded, `docs/research/runs`
excluded, CAPABILITIES / BACKLOG rows indexed), the body-vocabulary `terms` (code spans in,
paths and fenced blocks out, capped), that `--write` is deterministic and `--check` follows the
source, and that the index built over the REAL `docs/` reaches the sections a doctrine query must
land on (42's settle, the E41 ruling, the minimum-jerk chain, Deegan's rim)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_docs_index as BDI  # noqa: E402

DOC_REL = "docs/content-video-engine/42-FAKE-KINETICS.md"
TERMS_REL = "docs/content-video-engine/47-FAKE-VOCABULARY.md"
CAPS_REL = "docs/content-video-engine/CAPABILITIES.md"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
RUNS_REL = "docs/research/runs/2026-01-01/scratch.md"

DOC_42 = (
    "# Fake kinetics\n"                                                             # 1
    "\n"                                                                            # 2
    "The **settle** is closed form, with **three regimes** and **three regimes** again.\n"   # 3
    "\n"                                                                            # 4
    "## 42.1 The stroke — curvature\n"                                              # 5
    "\n"                                                                            # 6
    "| a | b |\n"                                                                   # 7
    "|---|---|\n"                                                                   # 8
    "| one | two |\n"                                                               # 9
    "\n"                                                                            # 10
    "```python\n"                                                                   # 11
    "# not a heading\n"                                                             # 12
    "```\n"                                                                         # 13
    "\n"                                                                            # 14
    "### Deeper still\n"                                                            # 15
)

CAPS = (
    "# Capabilities\n"                                                              # 1
    "\n"                                                                            # 2
    "## Rendering\n"                                                                # 3
    "\n"                                                                            # 4
    "| Capability | Where | State | Proof |\n"                                      # 5
    "|---|---|---|---|\n"                                                           # 6
    "| **Scene player** — the review renderer | `template.html` | LIVE | build F |\n"          # 7
    "| **Ledger page** — a world plate that IS a chart | `ledger_page.py` | LIVE | proof |\n"  # 8
    "| plain row | x | y | z |\n"                                                   # 9
)

BACKLOG = (
    "# Backlog\n"                                                                   # 1
    "\n"                                                                            # 2
    "| # | item | the decision |\n"                                                 # 3
    "|---|---|---|\n"                                                               # 4
    "| **T2** | **Analytic spring evaluator**, three damping regimes | landed |\n"   # 5
    "| ~~G2~~ | ~~Short mode~~ | **CLOSED 2026-09-05** |\n"                          # 6
    "| D1 | **Euler-spiral generator** for procedural curves | open |\n"             # 7
    "| — | T4-T6 (ARAP, the object page) | not yet |\n"                             # 8
)

DOC_47 = (
    "# 47 — Fake vocabulary\n"                                                      # 1
    "\n"                                                                            # 2
    "## 47.1 The stroke clock\n"                                                    # 3
    "\n"                                                                            # 4
    "The clock is `strokeProf`, never `kinetics/stroke.mjs`, and the front is\n"     # 5
    "min-jerk after Flash & Hogan (1985); `springPop` settles it, Deegan 1997\n"     # 6
    "pinned the rim, Kubelka-Munk layered it. Symbols: ζ, ω₀, M_p, coth.\n"          # 7
    "\n"                                                                            # 8
    "```js\n"                                                                       # 9
    'const fencedOut = "never-a-term";\n'                                           # 10
    "```\n"                                                                         # 11
    "\n"                                                                            # 12
    "Overflow: alpha-beta, gamma-delta, epsilon-zeta, eta-theta, iota-kappa.\n"      # 13
)

# The body vocabulary of 47.1, in first-appearance order: a code span, the hyphenated and
# CamelCase tokens, both citation forms, the formula symbols - then the cap bites.
DOC_47_TERMS = [
    "strokeProf", "min-jerk", "Flash & Hogan", "springPop", "Deegan 1997", "Kubelka-Munk",
    "ζ", "ω₀", "M_p", "coth", "alpha-beta", "gamma-delta",
]

RUNS = "# Scratch run\n\nGitignored noise that must never enter the index.\n"


def _write_tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def _tree(tmp_path: Path) -> Path:
    return _write_tree(tmp_path, {DOC_REL: DOC_42, CAPS_REL: CAPS, RUNS_REL: RUNS})


def test_synthetic_tree_yields_exactly_the_expected_records(tmp_path: Path) -> None:
    # Arrange
    root = _tree(tmp_path)

    # Act
    records = BDI.build_index(root)

    # Assert
    assert records == [
        {
            "path": DOC_REL, "line": 1, "level": 1, "doc": "42", "heading": "Fake kinetics",
            "lead": "The settle is closed form, with three regimes and three regimes again.",
            "labels": ["settle", "three regimes"], "terms": [],
        },
        {
            "path": DOC_REL, "line": 5, "level": 2, "doc": "42", "heading": "42.1 The stroke — curvature",
            "lead": "| a | b |", "labels": [], "terms": [],
        },
        {
            "path": DOC_REL, "line": 15, "level": 3, "doc": "42", "heading": "Deeper still",
            "lead": "", "labels": [], "terms": [],
        },
        {
            "path": CAPS_REL, "line": 1, "level": 1, "doc": None, "heading": "Capabilities",
            "lead": "", "labels": [], "terms": [],
        },
        {
            "path": CAPS_REL, "line": 3, "level": 2, "doc": None, "heading": "Rendering",
            "lead": "| Capability | Where | State | Proof |",
            "labels": ["Scene player", "Ledger page"], "terms": [],
        },
        {
            "path": CAPS_REL, "line": 7, "level": 7, "doc": None, "heading": "Scene player",
            "lead": "the review renderer", "labels": [], "terms": [],
        },
        {
            "path": CAPS_REL, "line": 8, "level": 7, "doc": None, "heading": "Ledger page",
            "lead": "a world plate that IS a chart", "labels": [], "terms": [],
        },
    ]


def test_the_fenced_heading_and_the_runs_file_are_excluded(tmp_path: Path) -> None:
    records = BDI.build_index(_tree(tmp_path))

    assert all("not a heading" not in r["heading"] for r in records)
    assert all(not r["path"].startswith("docs/research/runs/") for r in records)


def test_backlog_rows_index_by_id_and_fall_back_to_the_decision_column(tmp_path: Path) -> None:
    root = _write_tree(tmp_path, {BACKLOG_REL: BACKLOG})

    rows = [r for r in BDI.build_index(root) if r["level"] == BDI.ROW_LEVEL]

    assert rows == [
        {
            "path": BACKLOG_REL, "line": 5, "level": 7, "doc": None,
            "heading": "T2 Analytic spring evaluator", "lead": "three damping regimes", "labels": [], "terms": [],
        },
        {
            "path": BACKLOG_REL, "line": 6, "level": 7, "doc": None,
            "heading": "G2 Short mode", "lead": "CLOSED 2026-09-05", "labels": [], "terms": [],
        },
        {
            "path": BACKLOG_REL, "line": 7, "level": 7, "doc": None,
            "heading": "D1 Euler-spiral generator", "lead": "for procedural curves", "labels": [], "terms": [],
        },
    ]


def test_write_is_byte_identical_across_runs_and_lands_lf(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    assert BDI.main(["--write", "--root", str(root)]) == 0
    first = {rel: (root / rel).read_bytes() for rel in (BDI.JSONL_REL, BDI.MD_REL)}
    assert BDI.main(["--write", "--root", str(root)]) == 0
    second = {rel: (root / rel).read_bytes() for rel in (BDI.JSONL_REL, BDI.MD_REL)}

    assert first == second
    assert all(b"\r\n" not in data for data in first.values())


def test_check_passes_after_write_and_fails_when_a_doc_gains_a_heading(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    assert BDI.main(["--write", "--root", str(root)]) == 0

    assert BDI.main(["--check", "--root", str(root)]) == 0
    assert BDI.main(["--root", str(root)]) == 0          # no flag is --check

    doc = root / DOC_REL
    doc.write_text(doc.read_text(encoding="utf-8") + "\n## Appended later\n", encoding="utf-8")

    assert BDI.check(root) != []
    assert BDI.main(["--check", "--root", str(root)]) == 1
    assert BDI.main(["--root", str(root)]) == 1


def test_check_reports_a_missing_artifact(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    problems = BDI.check(root)

    assert problems == [f"{BDI.JSONL_REL} (missing)", f"{BDI.MD_REL} (missing)"]


def test_markdown_render_carries_the_recipe_and_one_line_per_record(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    records = BDI.build_index(root)

    md = BDI.render_md(records)

    assert 'rg -i "<term>" docs/DOCS-INDEX.jsonl' in md
    assert f"## {DOC_REL}" in md
    assert "- L1 [1] Fake kinetics — The settle is closed form" in md
    assert "{settle; three regimes}" in md
    assert "- L15 [3] Deeper still" in md and "- L15 [3] Deeper still —" not in md


def test_real_docs_reach_the_kinetics_settle_and_the_e41_ruling() -> None:
    records = BDI.build_index(BDI.REPO)

    settle = [r for r in records if "The settle" in r["heading"]]
    assert any(r["path"] == "docs/content-video-engine/42-DRAWING-KINETICS.md" and r["doc"] == "42" for r in settle)

    e41 = [r for r in records if r["heading"].startswith("E41")]
    assert any(r["path"] == "docs/portable/OPERATOR-RULINGS.md" for r in e41)

    assert all(not r["path"].startswith("docs/research/runs/") for r in records)
    assert all(r["path"] != BDI.MD_REL for r in records)
    assert all("node_modules" not in r["path"] for r in records)


def test_terms_lift_the_body_vocabulary_in_order_and_stop_at_the_cap(tmp_path: Path) -> None:
    # Arrange
    root = _write_tree(tmp_path, {TERMS_REL: DOC_47})

    # Act
    records = BDI.build_index(root)
    section = next(r for r in records if r["heading"] == "47.1 The stroke clock")

    # Assert
    assert section["terms"] == DOC_47_TERMS
    assert len(section["terms"]) == BDI.TERM_LIMIT
    assert "kinetics/stroke.mjs" not in section["terms"]          # a path is not a term
    assert all("fencedOut" not in t and "never-a-term" not in t   # a fenced block is not body
               for r in records for t in r["terms"])
    assert all(t not in section["terms"] for t in ("epsilon-zeta", "eta-theta", "iota-kappa"))
    assert " <" + "; ".join(DOC_47_TERMS) + ">" in BDI.render_md(records)


def test_real_docs_terms_close_the_minimum_jerk_and_deegan_hops() -> None:
    records = BDI.build_index(BDI.REPO)

    def terms(rel_path: str) -> list[str]:
        return [t.lower() for r in records if r["path"].endswith(rel_path) for t in r["terms"]]

    # 42 never writes "min-jerk" - it writes "minimising squared jerk" and cites the paper, so the
    # term that lands the section is the citation; 48 §48.5, which points at 42 §42.1, carries the
    # hyphenated token itself. One `rg` now reaches both.
    assert "flash & hogan" in terms("42-DRAWING-KINETICS.md")
    assert any("minimum-jerk" in t for t in terms("48-THE-FIGURE-AND-THE-GROUND.md"))
    assert any("deegan" in t for t in terms("44-INK-AND-SURFACE.md"))
