"""The docs standard is a gate, so these pin what it passes and what it refuses.

A synthetic docs tree carries one instance of each judgement the audit makes: a section with no
lead line, three sections whose lead is exempt because they open on a table / a sub-heading / a
fenced block, an H1 exempt by its italic byline, a generic filing heading, a `Sources` heading that
is structural and must NOT count as generic, and numbering (`42.6`, `3.`, `§`) stripped before the
generic test. The records come from `build_docs_index.file_records` - the audit's real producer -
except in the score test, where they are hand-written so the arithmetic is checkable by eye.

The last test runs over the REAL `docs/DOCS-INDEX.jsonl`: the tree it measures is large (>100
files) and the process docs already hold a median at or above 80, which is what makes the gate
usable rather than aspirational."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import audit_docs_standard as ADS  # noqa: E402
import build_docs_index as BDI  # noqa: E402

A_REL = "docs/synthetic/A.md"
B_REL = "docs/synthetic/B.md"
C_REL = "docs/synthetic/C.md"
D_REL = "docs/synthetic/D.md"

DOC_A = (
    "# Synthetic A - the retrieval standard\n"                                        # 1
    "\n"                                                                              # 2
    "*Pass-1 · 2026-09-05*\n"                                                         # 3
    "\n"                                                                              # 4
    "## 1. Minimum-jerk settle across the plate change\n"                             # 5
    "\n"                                                                              # 6
    "The `settle` is closed form and the **three regimes** follow from one root.\n"    # 7
    "\n"                                                                              # 8
    "## Overview\n"                                                                   # 9
    "\n"                                                                              # 10
    "Short.\n"                                                                        # 11
    "\n"                                                                              # 12
    "## Sources\n"                                                                    # 13
    "\n"                                                                              # 14
    "- one\n"                                                                         # 15
)

DOC_B = (
    "# Synthetic B\n"                                                                 # 1
    "\n"                                                                              # 2
    "## Shot table for the plate change\n"                                            # 3
    "\n"                                                                              # 4
    "| Shot | Cut |\n"                                                                # 5
    "|---|---|\n"                                                                     # 6
    "| one | two |\n"                                                                 # 7
    "\n"                                                                              # 8
    "## Notes\n"                                                                      # 9
    "\n"                                                                              # 10
    "### The deeper cut that names its own concept\n"                                 # 11
    "\n"                                                                              # 12
    "Body text that runs well past the forty character floor for a lead.\n"           # 13
)

DOC_C = (
    "# Synthetic C\n"                                                                 # 1
    "\n"                                                                              # 2
    "```bash\n"                                                                       # 3
    "python content/video_engine/scripts/audit_docs_standard.py\n"                    # 4
    "```\n"                                                                           # 5
)

DOC_D = (
    "# Synthetic D\n"                                                                 # 1
    "\n"                                                                              # 2
    "A first section whose lead line runs past the forty character floor.\n"          # 3
    "\n"                                                                              # 4
    "## Overview\n"                                                                   # 5
    "\n"                                                                              # 6
    "Short.\n"                                                                        # 7
    "\n"                                                                              # 8
    "## The spring pop that names its concept\n"                                      # 9
    "\n"                                                                              # 10
    "Another lead line that comfortably clears the forty character floor.\n"          # 11
    "\n"                                                                              # 12
    "## Ledger\n"                                                                     # 13
    "\n"                                                                              # 14
    "| a | b |\n"                                                                     # 15
    "|---|---|\n"                                                                     # 16
    "| 1 | 2 |\n"                                                                     # 17
)

LONG_LEAD = "A first section whose lead line runs past the forty character floor."

D_RECORDS = [
    {"path": D_REL, "line": 1, "level": 1, "doc": None, "heading": "Synthetic D",
     "lead": LONG_LEAD, "labels": [], "terms": ["known-numbers"]},
    {"path": D_REL, "line": 5, "level": 2, "doc": None, "heading": "Overview",
     "lead": "Short.", "labels": [], "terms": []},
    {"path": D_REL, "line": 9, "level": 2, "doc": None,
     "heading": "The spring pop that names its concept",
     "lead": "Another lead line that comfortably clears the forty character floor.",
     "labels": [], "terms": ["spring"]},
    {"path": D_REL, "line": 13, "level": 2, "doc": None, "heading": "Ledger",
     "lead": "| a | b |", "labels": [], "terms": []},
]


# --- fixtures -----------------------------------------------------------------------------

def write_doc(root: Path, rel: str, text: str) -> list[dict]:
    """Write the synthetic doc and return the records the real index builder makes for it."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return BDI.file_records(rel, text)


@pytest.fixture()
def tree(tmp_path: Path) -> tuple[Path, list[dict]]:
    records: list[dict] = []
    for rel, text in ((A_REL, DOC_A), (B_REL, DOC_B), (C_REL, DOC_C)):
        records += write_doc(tmp_path, rel, text)
    return tmp_path, records


def entries(result: dict, key: str) -> set[tuple[str, int, str]]:
    return {(e["path"], e["line"], e["heading"]) for e in result[key]}


def doc_named(result: dict, rel: str) -> dict:
    return next(d for d in result["docs"] if d["path"] == rel)


# --- lead lines ---------------------------------------------------------------------------

def test_a_section_with_a_short_lead_and_no_exemption_is_reported(tree):
    root, records = tree

    result = ADS.audit(records, root)

    assert (A_REL, 9, "Overview") in entries(result, "missing_leads")
    assert doc_named(result, A_REL)["lead_ok"] == 2


def test_a_section_that_opens_on_a_table_owes_no_lead(tree):
    root, records = tree

    result = ADS.audit(records, root)

    shot_table = next(r for r in records if r["heading"] == "Shot table for the plate change")
    assert len(shot_table["lead"]) < ADS.LEAD_MIN          # the table header is not a lead
    assert (B_REL, 3, "Shot table for the plate change") not in entries(result, "missing_leads")


def test_a_section_that_opens_on_a_sub_heading_owes_no_lead(tree):
    root, records = tree

    result = ADS.audit(records, root)

    notes = next(r for r in records if r["path"] == B_REL and r["heading"] == "Notes")
    assert notes["lead"] == ""                            # nothing between the two headings
    assert (B_REL, 9, "Notes") not in entries(result, "missing_leads")


def test_a_section_that_opens_on_a_fenced_block_owes_no_lead(tree):
    root, records = tree

    result = ADS.audit(records, root)

    assert not [e for e in result["missing_leads"] if e["path"] == C_REL]
    assert doc_named(result, C_REL)["lead_ok"] == 1


def test_an_h1_byline_exempts_the_title_from_the_lead_check(tree):
    root, records = tree

    result = ADS.audit(records, root)

    assert (A_REL, 1, "Synthetic A - the retrieval standard") not in entries(result, "missing_leads")
    assert not ADS.lead_exempt(DOC_A.split("\n"), 1, 2)   # only the H1 gets the byline exemption


def test_a_missing_source_file_fails_the_exemption_closed(tmp_path: Path):
    records = [{"path": "docs/gone.md", "line": 1, "level": 2, "doc": None,
                "heading": "Overview", "lead": "Short.", "labels": [], "terms": []}]

    result = ADS.audit(records, tmp_path)

    assert entries(result, "missing_leads") == {("docs/gone.md", 1, "Overview")}


# --- generic headings ---------------------------------------------------------------------

def test_generic_filing_headings_are_reported(tree):
    root, records = tree

    result = ADS.audit(records, root)

    assert entries(result, "generic_headings") == {(A_REL, 9, "Overview"), (B_REL, 9, "Notes")}


def test_a_structural_sources_heading_is_not_generic(tree):
    root, records = tree

    result = ADS.audit(records, root)

    assert (A_REL, 13, "Sources") not in entries(result, "generic_headings")
    assert not any(ADS.is_generic(h) for h in ("Sources", "Checklist", "Changelog"))


@pytest.mark.parametrize("heading", ["42.6 Overview", "3. Notes", "§ Summary", "§4.2 Next steps",
                                     "5. Rules", "Open Questions:"])
def test_numbering_is_stripped_before_the_generic_check(heading):
    assert ADS.is_generic(heading)


@pytest.mark.parametrize("heading", ["1. Minimum-jerk settle across the plate change",
                                     "3D pipeline", "5 rules for the plate change",
                                     "42.6 The stroke - curvature"])
def test_a_heading_that_names_a_concept_is_not_generic(heading):
    assert not ADS.is_generic(heading)


# --- the score ----------------------------------------------------------------------------

def test_the_score_formula_on_a_doc_with_known_numbers(tmp_path: Path):
    (tmp_path / D_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / D_REL).write_text(DOC_D, encoding="utf-8")

    result = ADS.audit(D_RECORDS, tmp_path)

    doc = doc_named(result, D_REL)
    # 3/4 leads (Ledger is exempt by its table), 2/4 termed, 1/4 generic:
    # 100 * (0.5*0.75 + 0.35*0.5 + 0.15*0.75) = 66.25 -> 66
    assert (doc["headings"], doc["lead_ok"], doc["termed"], doc["generic"]) == (4, 3, 2, 1)
    assert doc["score"] == 66


def test_a_table_row_is_not_a_heading(tmp_path: Path):
    (tmp_path / D_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / D_REL).write_text(DOC_D, encoding="utf-8")
    row = {"path": D_REL, "line": 15, "level": ADS.ROW_LEVEL, "doc": None, "heading": "Overview",
           "lead": "", "labels": [], "terms": []}

    result = ADS.audit([*D_RECORDS, row], tmp_path)

    assert doc_named(result, D_REL)["headings"] == 4
    assert doc_named(result, D_REL)["generic"] == 1


def test_research_and_process_docs_are_summarized_apart(tmp_path: Path):
    research = [dict(r, path="docs/research/motion/R.md") for r in D_RECORDS]
    (tmp_path / "docs/research/motion").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/research/motion/R.md").write_text(DOC_D, encoding="utf-8")
    (tmp_path / D_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / D_REL).write_text(DOC_D, encoding="utf-8")

    result = ADS.audit([*D_RECORDS, *research], tmp_path)

    assert result["groups"]["research"]["files"] == 1
    assert result["groups"]["process"]["files"] == 1
    assert result["groups"]["all"]["headings"] == 8
    assert result["groups"]["process"]["median_score"] == 66.0


# --- the report and the CLI -----------------------------------------------------------------

def index_repo(tmp_path: Path, records: list[dict]) -> Path:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    (tmp_path / ADS.INDEX_REL).write_bytes(text.encode("utf-8"))
    return tmp_path


def test_the_report_is_deterministic_and_written_with_lf(tree):
    root, records = tree
    index_repo(root, records)

    assert ADS.main(["--root", str(root)]) == 0
    first = (root / ADS.REPORT_REL).read_bytes()
    assert ADS.main(["--root", str(root)]) == 0

    assert (root / ADS.REPORT_REL).read_bytes() == first
    assert b"\r" not in first
    assert f"`{A_REL}:9` Overview" in first.decode("utf-8")


def test_min_score_gates_process_docs_and_leaves_research_alone(tmp_path: Path, capsys):
    root, records = tmp_path, write_doc(tmp_path, A_REL, DOC_A)
    records += [dict(r, path="docs/research/motion/R.md") for r in records]
    write_doc(root, "docs/research/motion/R.md", DOC_A)
    index_repo(root, records)

    assert ADS.main(["--root", str(root), "--min-score", "90"]) == 1
    failed = capsys.readouterr().err
    assert A_REL in failed and "docs/research/motion/R.md" not in failed
    assert ADS.main(["--root", str(root), "--min-score", "90", "--only", "docs/research"]) == 0


def test_a_missing_index_is_named_not_guessed(tmp_path: Path, capsys):
    assert ADS.main(["--root", str(tmp_path)]) == 2

    assert "index not found at" in capsys.readouterr().err


# --- the real tree --------------------------------------------------------------------------

def test_the_real_docs_index_clears_the_standard():
    records = ADS.load_records(ROOT / ADS.INDEX_REL)

    result = ADS.audit(records, ROOT)

    assert result["groups"]["all"]["files"] > 100
    assert result["groups"]["process"]["median_score"] >= 80
