"""The animation registry: every formula, dial and kinetics symbol, and the status column that says
whether it is implemented, tracked, retired, or orphaned.

The synthetic tree pins the mechanics - a module's flag and citation read out of its header comment,
the object keys lifted as code surface AND as dials, the template's inlined `KINETICS:BEGIN..END`
copy not counting as a use site, the enclosing section taken from the docs index, and one record of
each status with the evidence that produced it. `closed-form` is not `closed`.

The last block runs over the REAL repository and asserts today's findings, which is the reason the
tool exists: the two-thirds power law is implemented in `stroke.mjs` and nobody calls it by name;
zero-slip is tracked and unbuilt; the secondary-motion 0.22 ratio is retired as an invented number;
and the three citation orphans the 2026-09-05 triage found (07 §1.2, the damping regimes, the LTX
`8n+1` frame law) read implemented through the chain that reaches them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import animation_registry_render as ARR  # noqa: E402  (the Markdown face, split out 2026-09-05)
import build_animation_registry as BAR  # noqa: E402
import build_docs_index as BDI  # noqa: E402
import build_topic_index as BTI  # noqa: E402

MODULE_REL = "content/video_engine/scripts/kinetics/fake.mjs"
TEMPLATE_REL = BAR.TEMPLATE_REL
DOC_42_REL = "docs/content-video-engine/42-FAKE-KINETICS.md"
DOC_48_REL = "docs/content-video-engine/48-FAKE-FIGURE.md"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
CHECKS_REL = "docs/content-video-engine/47-FINDINGS-TO-CHECKS.md"
TEST_REL = "content/video_engine/tests/test_fake_kinetics.py"
RESEARCH_REL = f"{BAR.SOURCES_DIR}/07_academic_literature_fake.md"
RESEARCH_INDEX_REL = BAR.RESEARCH_INDEX_REL

MODULE = (
    "/* kinetics/fake.mjs - the fake stroke (42 s42.1; FINDING-the-fake-math s1). Inlined into\n"  # 1
    "   the scene-evidence player by sync_kinetics.py. Behind kinetics.curvature_stroke. */\n"     # 2
    "\n"                                                                                       # 3
    "export const FAKE = Object.freeze({ ALPHA: 0.5, BETA: 2 });   /* the dials (42 s42.5) */\n"  # 4
    "\n"                                                                                       # 5
    "/* the fake draw */\n"                                                                    # 6
    "export const fakeDraw = (u) => FAKE.ALPHA * u;\n"                                         # 7
)

TEMPLATE = (
    "<script>\n"                                                                # 1
    "  const KINETICS_DEFAULTS = Object.freeze({\n"                             # 2
    "    curvature_stroke: false,   // 42.1 the fake stroke\n"                  # 3
    "    arap_morph:       false,   // 43.5B ARAP morph - declared, never read\n"  # 4
    "  });\n"                                                                   # 5
    "  const kin = (name) => KIN[name] === true;\n"                             # 6
    "  /* KINETICS:BEGIN fake */\n"                                             # 7
    "  const FAKE = Object.freeze({ ALPHA: 0.5, BETA: 2 });\n"                  # 8
    "  const fakeDraw = (u) => FAKE.ALPHA * u;\n"                               # 9
    "  /* KINETICS:END */\n"                                                    # 10
    "  const MARK = { RED: 3, POP: 1.10 };\n"                                   # 11
    "  const WIPE = 0.62, DISSOLVE_S = 0.8, MOUNT_STEPS = 5;\n"                 # 12
    "  const draw = (u) => kin(\"curvature_stroke\") ? fakeDraw(u) : u;\n"      # 13
    "</script>\n"                                                               # 14
)

DOC_42 = (
    "# 42 — Fake kinetics\n"                                                    # 1
    "\n"                                                                        # 2
    "## 42.1 The stroke — curvature-reparameterised drawing\n"                  # 3
    "\n"                                                                        # 4
    "The law is the two-thirds power law of Viviani, out of `07` §1.2.\n"       # 5
    "\n"                                                                        # 6
    "$$v = \\gamma (\\kappa + \\kappa_0)^{-1/3}$$\n"                            # 7
    "\n"                                                                        # 8
    "The width couples: w = 1 + λ_w (v_max / v)^α.\n"                           # 9
    "\n"                                                                        # 10
    "## 42.5 What is ours to tune\n"                                            # 11
    "\n"                                                                        # 12
    "The smoothing window is a dial, not a finding.\n"                          # 13
    "\n"                                                                        # 14
    "The morph is ARAP, never a vertex lerp.\n"                                 # 15
)

DOC_48 = (
    "# 48 — Fake figure\n"                                                      # 1
    "\n"                                                                        # 2
    "## 48.7 Grounding\n"                                                       # 3
    "\n"                                                                        # 4
    "Zero-slip requires `v_contact = v_surface` during contact.\n"              # 5
    "\n"                                                                        # 6
    "The penumbra widens: σ(y) = σ₀ + k (y_base + y).\n"                        # 7
    "\n"                                                                        # 8
    "## 48.9 Cadence\n"                                                         # 9
    "\n"                                                                        # 10
    "On-1s above 250 px/s, On-2s below it.\n"                                   # 11
    "\n"                                                                        # 12
    "### A6: The Secondary-Motion Budget\n"                                     # 13
    "\n"                                                                        # 14
    "$$E_{secondary} \\le 0.22 · E_{primary}$$\n"                               # 15
    "\n"                                                                        # 16
    "### 3.7 Two-Handed Closed Kinematic Chains\n"                              # 17
    "\n"                                                                        # 18
    "Both wrists lock to the prop: p = M_prop · s^socket.\n"                    # 19
    "\n"                                                                        # 20
    "### 4.2 Grasp aperture\n"                                                  # 21
    "\n"                                                                        # 22
    "The aperture peaks: a = 0.68 · τ^2.\n"                                     # 23
)

BACKLOG = (
    "# Backlog\n"                                                               # 1
    "\n"                                                                        # 2
    "| id | item | why |\n"                                                     # 3
    "|---|---|---|\n"                                                           # 4
    "| **G-j** | **zero-slip anchoring** — sprites bind to floor velocity (48 s48.7) | foot slide |\n"  # 5
    "| D9 | **Two-Handed Closed Kinematic Chains** — the prop is the master | **Deferred with a trigger:** the first two-handed prop. |\n"  # 6
)

CHECKS = (
    "# 47 — Fake findings\n"                                                    # 1
    "\n"                                                                        # 2
    "| finding | verdict |\n"                                                   # 3
    "|---|---|\n"                                                               # 4
    "| **A6 secondary-motion ratio (0.22)** | An invented number. |\n"          # 5
    "| **42.2 closed-form springs** | shipped 2026-09-05 |\n"                   # 6
    "| **42.3 squash** | `det(A) = 1` for all α, by construction | the tolerance test |\n"  # 7
    "| **4.2 Grasp aperture** | ~~open~~ **CLOSED 2026-09-04** by doc 48 |\n"   # 8
)

# one numbered research file, the way the bundle numbers them: the module cites OUR doc, our doc
# cites `07` §1.2, and the RESEARCH-INDEX row carries §3.1 the other way. §9.9 is reached by neither.
RESEARCH = (
    "# 07 — Fake academic literature\n"                                         # 1
    "\n"                                                                        # 2
    "## 1.2 Fake Arc-Length Reparameterisation\n"                               # 3
    "\n"                                                                        # 4
    "$$v(s) = \\gamma (|\\kappa| + \\kappa_0)^{-1/3}$$\n"                       # 5
    "\n"                                                                        # 6
    "### The regulariser\n"                                                     # 7
    "\n"                                                                        # 8
    "$$\\kappa_0 = (v_{max} / \\gamma)^{-3}$$\n"                                # 9
    "\n"                                                                        # 10
    "## 3.1 Fake Damping Regimes\n"                                             # 11
    "\n"                                                                        # 12
    "$$x(t) = 1 - e^{-\\zeta \\omega t}$$\n"                                    # 13
    "\n"                                                                        # 14
    "## 9.9 Reached by nobody\n"                                                # 15
    "\n"                                                                        # 16
    "$$q = p^2$$\n"                                                             # 17
)

RESEARCH_INDEX = (
    "# Research index\n"                                                        # 1
    "\n"                                                                        # 2
    "### `07_academic_literature_fake.md` — 4 headings\n"                       # 3
    "\n"                                                                        # 4
    "| heading | disposition |\n"                                               # 5
    "|---|---|\n"                                                               # 6
    "| 3.1 Fake Damping Regimes | EXTRACTED -> 42 SS42.1 |\n"                   # 7
    "| 9.9 Reached by nobody | RECORD - nothing took it |\n"                    # 8
)

FINDING_REL = "docs/content-video-engine/FINDING-the-fake-math-and-what-it-changes.md"
FINDING = (
    "# The fake math, and what each piece changes\n"                            # 1
    "\n"                                                                        # 2
    "## 1. The stroke is wrong in one fixable way\n"                            # 3
    "\n"                                                                        # 4
    "The pen is not a sliding mask.\n"                                          # 5
)

FILES = {MODULE_REL: MODULE, TEMPLATE_REL: TEMPLATE, DOC_42_REL: DOC_42, DOC_48_REL: DOC_48,
         BACKLOG_REL: BACKLOG, CHECKS_REL: CHECKS, FINDING_REL: FINDING,
         RESEARCH_REL: RESEARCH, RESEARCH_INDEX_REL: RESEARCH_INDEX,
         TEST_REL: "def test_fake_draw():\n    assert fakeDraw(1) == 0.5\n"}


def _tree(tmp_path: Path) -> Path:
    """The synthetic repository, with the real docs index and citation graph built over it."""
    for rel, text in FILES.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    BDI.write(tmp_path)
    _, edges = BTI.build(BDI.build_index(tmp_path), tmp_path)
    (tmp_path / BAR.CITATIONS_REL).write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def records(tmp_path: Path) -> list[dict]:
    return BAR.build(_tree(tmp_path))


def _one(records: list[dict], kind: str, name: str, line: int | None = None) -> dict:
    hits = [r for r in records if r["kind"] == kind and r["name"] == name
            and (line is None or r["line"] == line)]
    assert len(hits) == 1, f"not found (or ambiguous): {kind} {name!r} line={line} in {len(records)} records"
    return hits[0]


# --- code ---------------------------------------------------------------------------------

def test_an_export_carries_its_flag_its_citation_its_tests_and_only_the_declared_fields(records) -> None:
    # Arrange / Act
    rec = _one(records, "code", "fakeDraw")

    # Assert - the flag and the section come out of the module header; `42 s42.1` normalises like
    # the citation graph and resolves to the heading the index holds
    assert rec["flag"] == "curvature_stroke"
    assert rec["module"] == MODULE_REL and rec["line"] == 7
    assert rec["signature"] == "export const fakeDraw = (u) => FAKE.ALPHA * u;"
    # `FINDING-<slug> s1` has no document number, so the citation graph cannot carry it; the
    # registry parses it and resolves it to the finding's own section 1
    assert rec["cites"] == [{"ref": "42§42.1", "to": f"{DOC_42_REL}:3"},
                            {"ref": "FINDING-the-fake-math§1", "to": f"{FINDING_REL}:3"}]
    assert rec["tests"] == [TEST_REL]
    assert set(rec) == {"kind", "name", "module", "line", "signature", "flag", "template_sites",
                        "tests", "cites", "status", "status_evidence"}


def test_the_templates_inlined_copy_of_a_module_is_not_a_use_site(records) -> None:
    rec = _one(records, "code", "fakeDraw")

    # the template names fakeDraw twice: once inside KINETICS:BEGIN..END (the generated copy, line
    # 9) and once in the player's own code (line 13). Only the second is a site.
    assert rec["template_sites"] == 1
    assert f"{TEMPLATE_REL}:13" in rec["status_evidence"]
    assert rec["status"] == "implemented"


def test_every_key_of_an_exported_constant_object_is_code_surface_and_a_dial(records) -> None:
    code = _one(records, "code", "FAKE.ALPHA")
    dial = _one(records, "dial", "FAKE.ALPHA")

    assert code["signature"] == "FAKE.ALPHA = 0.5" and code["flag"] == "curvature_stroke"
    assert (dial["value"], dial["path"], dial["line"]) == ("0.5", MODULE_REL, 4)
    # the note beside the dial first ("the dials (42 s42.5)"), then what the module itself cites
    assert dial["cites"] == [{"ref": "42§42.5", "to": f"{DOC_42_REL}:11"},
                             {"ref": "42§42.1", "to": f"{DOC_42_REL}:3"},
                             {"ref": "FINDING-the-fake-math§1", "to": f"{FINDING_REL}:3"}]
    assert {r["name"] for r in records if r["kind"] == "dial"} >= {
        "FAKE.ALPHA", "FAKE.BETA", "MARK.RED", "MARK.POP", "DISSOLVE_S", "MOUNT_STEPS"}


def test_a_template_dial_is_recorded_where_the_template_declares_it(records) -> None:
    assert _one(records, "dial", "MOUNT_STEPS") == {
        "kind": "dial", "name": "MOUNT_STEPS", "value": "5", "path": TEMPLATE_REL, "line": 12,
        "cites": []}


# --- formulas and status ------------------------------------------------------------------

def test_a_display_block_a_symbol_line_and_a_law_line_are_all_formulas_of_their_section(records) -> None:
    formulas = {(r["path"], r["line"]): r for r in records if r["kind"] == "formula"}

    law = formulas[(DOC_42_REL, 5)]
    assert law["name"] == "two-thirds power law"          # the law names the record, not the heading
    assert law["section"] == "42.1 The stroke — curvature-reparameterised drawing"
    assert law["doc"] == "42"
    assert formulas[(DOC_42_REL, 7)]["expr"] == "v = \\gamma (\\kappa + \\kappa_0)^{-1/3}"
    assert formulas[(DOC_42_REL, 9)]["name"] == "42.1 The stroke — curvature-reparameterised drawing"
    assert (DOC_42_REL, 13) not in formulas               # prose with no symbol and no law


def test_a_law_a_module_cites_is_implemented_with_the_module_as_evidence(records) -> None:
    rec = _one(records, "formula", "two-thirds power law")

    assert rec["status"] == "implemented"
    # the two code records whose module header cites 42 §42.1 - the object and the function
    assert rec["status_evidence"] == [f"{MODULE_REL}:4", f"{MODULE_REL}:7"]


def test_a_law_only_a_backlog_row_names_is_tracked(records) -> None:
    rec = _one(records, "formula", "zero-slip")

    assert rec["status"] == "tracked"
    # the row itself, and the same row as a citation edge - the graph's `from` is the section
    assert rec["status_evidence"] == [f"{BACKLOG_REL}:1", f"{BACKLOG_REL}:5"]


def test_a_section_a_backlog_row_cites_is_tracked_through_the_citation_graph(records) -> None:
    rec = _one(records, "formula", "48.7 Grounding", line=7)

    assert rec["status"] == "tracked"                      # nothing names "48.7 Grounding"...
    assert rec["status_evidence"] == [f"{BACKLOG_REL}:1"]  # ...but G-j cites 48 s48.7


def test_a_finding_a_47_row_calls_invented_is_retired(records) -> None:
    rec = _one(records, "formula", "A6: The Secondary-Motion Budget")

    assert rec["status"] == "retired"
    assert rec["status_evidence"] == [f"{CHECKS_REL}:5"]


def test_a_formula_that_is_itself_a_47_row_is_tracked_by_that_row(records) -> None:
    rec = _one(records, "formula", "47 — Fake findings", line=7)

    # nothing outside the row names it, and no token can see a row naming itself
    assert (rec["status"], rec["status_evidence"]) == ("tracked", [f"{CHECKS_REL}:7"])


def test_a_kinetics_flag_nothing_reads_does_not_implement_the_law_it_names(records) -> None:
    rec = _one(records, "formula", "ARAP / polar decomposition")

    # the template declares `arap_morph` and names ARAP beside it, but never passes it to kin():
    # a placeholder flag is not an implementation
    assert (rec["status"], rec["status_evidence"]) == ("orphaned", [])


def test_a_law_with_no_code_and_no_row_is_orphaned(records) -> None:
    rec = _one(records, "formula", "On-1s / On-2s")

    assert (rec["status"], rec["status_evidence"]) == ("orphaned", [])


def test_the_section_falls_back_to_the_file_when_the_docs_index_is_missing(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    (root / BAR.INDEX_REL).unlink()

    rec = _one(BAR.build(root), "formula", "two-thirds power law")

    # the section still resolves, off the file's own headings; the citation does not - a reference
    # resolves through the index, so a missing index costs the status, never the record
    assert rec["section"] == "42.1 The stroke — curvature-reparameterised drawing"
    assert rec["status"] == "orphaned"
    assert _one(BAR.build(root), "code", "fakeDraw")["cites"] == [
        {"ref": "42§42.1", "to": None}, {"ref": "FINDING-the-fake-math§1", "to": None}]


def test_closed_form_is_not_closed() -> None:
    assert BAR.RETIRED_WORD.search("**42.2 closed-form springs** | shipped") is None
    assert BAR.RETIRED_WORD.search("CLOSED 2026-09-04 by doc 48")
    assert BAR.RETIRED_WORD.search("An invented number.")


# --- the citation chain -------------------------------------------------------------------

def test_a_research_section_our_doc_cites_inherits_the_modules_status_with_the_chain(records) -> None:
    # Arrange / Act - fake.mjs cites 42 §42.1, and 42 §42.1's body cites `07` §1.2
    rec = _one(records, "formula", "1.2 Fake Arc-Length Reparameterisation", line=5)

    # Assert - the research section is not an orphan: it is what the module implements, and the
    # evidence is the whole chain, starting at the header line the citation is written on
    assert rec["status"] == "implemented"
    assert rec["status_evidence"] == [f"{MODULE_REL}:1 → 42§42.1 → 07§1.2"]


def test_the_chain_covers_the_subsections_of_the_section_it_reaches(records) -> None:
    rec = _one(records, "formula", "The regulariser")

    # `07 §1.2` reaches §1.2 and everything stated under it - the regulariser is inside that span
    assert rec["status"] == "implemented"
    assert all("42§42.1 → 07§1.2" in e for e in rec["status_evidence"])


def test_a_research_index_row_carries_the_chain_where_the_doc_body_does_not(records) -> None:
    rec = _one(records, "formula", "3.1 Fake Damping Regimes")

    # nothing in doc 42 cites `07` §3.1; RESEARCH-INDEX's `| 3.1 … | EXTRACTED -> 42 SS42.1 |` does,
    # and `SS` is the spelling the citation graph cannot see
    assert rec["status"] == "implemented"
    assert all(e.endswith("→ 42§42.1 → 07§3.1") for e in rec["status_evidence"])


def test_a_research_section_no_chain_reaches_is_still_an_orphan(records) -> None:
    rec = _one(records, "formula", "9.9 Reached by nobody")

    # its RESEARCH-INDEX row is a RECORD disposition with no doc reference: nothing took it
    assert (rec["status"], rec["status_evidence"]) == ("orphaned", [])


# --- retirement is a verdict, not a word --------------------------------------------------

def test_the_word_closed_inside_a_title_does_not_retire_the_row_it_names(records) -> None:
    rec = _one(records, "formula", "3.7 Two-Handed Closed Kinematic Chains")

    # D9's verdict is "Deferred with a trigger"; `closed` sits in the bolded item title
    assert rec["status"] == "tracked"
    assert rec["status_evidence"] == [f"{BACKLOG_REL}:6"]


def test_closed_by_a_doc_is_a_graduation_and_carries_the_doc_it_graduated_to(records) -> None:
    rec = _one(records, "formula", "4.2 Grasp aperture")

    # "**CLOSED 2026-09-04** by doc 48" retires nothing - the question became a written standard
    assert rec["status"] == "tracked"
    assert rec["status_evidence"] == [f"{CHECKS_REL}:8", f"{DOC_48_REL}:1"]


def test_a_row_is_read_for_the_verdict_it_states_not_for_a_word_in_its_title() -> None:
    assert BAR.retirement("| D9 | **Two-Handed Closed Kinematic Chains** | deferred |") is None
    assert BAR.retirement("| A6 | An invented number. |") == "retired"
    assert BAR.retirement("| ~~X10~~ | **CLOSED 2026-09-04** by [48-X](48-X.md) |") == "graduated"
    assert BAR.retirement("| 42.2 spring | **shipped** | the closed form is stateless |") is None


# --- provenance ----------------------------------------------------------------------------

def test_a_row_calling_a_figure_invented_makes_it_derived(records) -> None:
    assert _one(records, "formula", "A6: The Secondary-Motion Budget")["provenance"] == "derived"


def _records_with(root_dir: Path, rel: str, text: str) -> list[dict]:
    """The synthetic tree with one file rewritten, the index and the citation graph rebuilt over it."""
    root = _tree(root_dir)
    (root / rel).write_text(text, encoding="utf-8")
    BDI.write(root)
    _, edges = BTI.build(BDI.build_index(root), root)
    (root / BAR.CITATIONS_REL).write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    return BAR.build(root)


CADENCE_LINE = "On-1s above 250 px/s, On-2s below it.\n"
DERIVED_TAG_LINE = ("Chosen, not measured [DERIVED: from Williams 2001 cadence practice "
                    "(sources: not on file), a picked threshold].\n")


def test_a_derived_tag_anywhere_in_the_section_makes_that_sections_figure_derived(tmp_path: Path) -> None:
    """E42 / P45 T5: the tag is read over the record's whole section, not only its own line."""
    # Arrange / Act - the same doc without the tag, and with it two lines below the figure
    plain = _records_with(tmp_path / "plain", DOC_48_REL, DOC_48)
    tagged = _records_with(tmp_path / "tagged", DOC_48_REL,
                           DOC_48.replace(CADENCE_LINE, CADENCE_LINE + "\n" + DERIVED_TAG_LINE))

    # Assert - the tag is two lines below the figure, so only a section-wide read finds it
    rec = _one(tagged, "formula", "On-1s / On-2s")
    assert _one(plain, "formula", "On-1s / On-2s")["provenance"] == "unsourced"
    assert rec["provenance"] == "derived"
    assert DERIVED_TAG_LINE.strip() not in DOC_48.split("\n")[rec["line"] - 1]


def test_a_section_that_reaches_a_research_file_is_sourced(records) -> None:
    # the research file itself, and our own section whose body cites it
    assert _one(records, "formula", "3.1 Fake Damping Regimes")["provenance"] == "sourced"
    assert _one(records, "formula", "two-thirds power law")["provenance"] == "sourced"


def test_a_figure_with_nothing_behind_it_is_unsourced(records) -> None:
    assert _one(records, "formula", "On-1s / On-2s")["provenance"] == "unsourced"
    assert _one(records, "formula", "zero-slip")["provenance"] == "unsourced"


# --- artifacts ----------------------------------------------------------------------------

def test_the_build_is_deterministic_and_write_is_byte_identical_twice(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    first = BAR.render_jsonl(BAR.build(root))
    BAR.write(root)
    once = (root / BAR.JSONL_REL).read_bytes(), (root / BAR.MD_REL).read_bytes()
    BAR.write(root)

    assert BAR.render_jsonl(BAR.build(root)) == first
    assert ((root / BAR.JSONL_REL).read_bytes(), (root / BAR.MD_REL).read_bytes()) == once
    assert b"\r\n" not in once[0] and b"\r\n" not in once[1]


def test_check_is_green_after_write_and_red_when_a_doc_gains_a_law(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    BAR.write(root)
    assert BAR.check(root) == []
    assert BAR.main(["--check", "--repo", str(root)]) == 0

    (root / DOC_48_REL).write_text(DOC_48 + "\nFitts' law bounds the reach.\n", encoding="utf-8")

    problems = BAR.check(root)
    assert len(problems) == 2 and all("+1/-" in p or "+" in p for p in problems), problems
    assert BAR.main(["--check", "--repo", str(root)]) == 1


def test_the_markdown_groups_by_module_by_status_and_ends_on_the_orphan_list(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    text = BAR.render_md(BAR.build(root))

    assert text.index("## Code (kinetics)") < text.index("## Dials") < text.index("## Formulas and laws")
    assert f"### `{MODULE_REL}`" in text and f"### `{TEMPLATE_REL}`" in text
    assert all(f"### {status} (" in text for status in BAR.STATUS_ORDER)
    orphans = text[text.index("## Orphaned"):]
    assert "**On-1s / On-2s**" in orphans and "**zero-slip**" not in orphans


# --- the real repository ------------------------------------------------------------------

@pytest.fixture(scope="module")
def real() -> list[dict]:
    return BAR.build(ROOT)


def _named(records: list[dict], kind: str, name: str) -> list[dict]:
    hits = [r for r in records if r["kind"] == kind and r["name"] == name]
    assert hits, f"not found in the real registry: {kind} {name!r}"
    return hits


def test_the_two_thirds_power_law_is_implemented_and_stroke_mjs_is_the_evidence(real) -> None:
    hits = _named(real, "formula", "two-thirds power law")

    assert {r["status"] for r in hits} == {"implemented"}
    assert any(e.endswith(".mjs:" + e.rsplit(":", 1)[1]) and "stroke.mjs" in e
               for r in hits for e in r["status_evidence"]), [r["status_evidence"] for r in hits]


def test_zero_slip_is_tracked_and_the_cadence_rule_is_implemented(real) -> None:
    # zero-slip: G-j tracks it, a gate checks a proxy, and nothing binds the ground - the gate's
    # citation of 48 §48.7 is not an implementation, so the row's verdict stands
    assert {r["status"] for r in _named(real, "formula", "zero-slip")} == {"tracked"}
    # On-1s / On-2s was the orphan of 2026-09-05; P47 T1 (2026-09-06) built it as kinetics/stopaction.mjs - the cadence
    # rule stepped on the integer frame index - so the registry now reads the module that names it: implemented
    cadence = _named(real, "formula", "On-1s / On-2s")
    assert {r["status"] for r in cadence} == {"implemented"}
    assert any(e.startswith("content/video_engine/scripts/kinetics/stopaction.mjs")
               for r in cadence for e in r["status_evidence"]), "the cadence rule is stopaction.mjs (P47 T1)"


def test_the_secondary_motion_ratio_is_retired_by_the_doc_47_row(real) -> None:
    hits = [r for r in real if r["kind"] == "formula" and "Secondary-Motion" in r["name"]
            and "0.22" in r["expr"]]

    assert hits, "not found in the real registry: a Secondary-Motion formula carrying 0.22"
    assert {r["status"] for r in hits} == {"retired"}
    assert any("47-FINDINGS-TO-CHECKS.md" in e for r in hits for e in r["status_evidence"])


def _at(records: list[dict], name_part: str, heading_part: str) -> list[dict]:
    hits = [r for r in records if r["kind"] == "formula" and name_part in r["path"]
            and heading_part in (r["section"] or "")]
    assert hits, f"not found in the real registry: {heading_part!r} in a path holding {name_part!r}"
    return hits


def test_the_three_citation_orphans_the_triage_found_are_implemented_through_their_chain(real) -> None:
    # TRIAGE-2026-09-05 §1b, rows S1 / S4 / S8: shipped verbatim, orphaned only because the module
    # cites our doc and the doc's research section was never linked back
    arc = _at(real, "ACADEMIC_LITERATURE", "1.2 Kinematic Arc-Length")
    damping = _at(real, "ACADEMIC_LITERATURE", "Derivation of Damped Harmonic Oscillator")
    frames = _at(real, "UNIFIED_LEDGER", "4.1 Mechanics Under the Hood")

    assert {r["status"] for r in arc} == {"implemented"}
    # the evidence is the implementing MODULE, never the engine's inlined copy of it (the recipe's rule).
    # Which module wins is an artifact of the three-entry cap and its sort: stroke.mjs keeps the stroke's own
    # arclength table and clothoid.mjs the fitter's Fresnel series, and both implement this law (2026-09-12).
    assert all("/kinetics/" in e for r in arc for e in r["status_evidence"])
    assert {r["status"] for r in damping} == {"implemented"}
    assert any("spring.mjs" in e for r in damping for e in r["status_evidence"])
    assert {r["status"] for r in frames} == {"implemented"}
    assert any("gate_comfy_config.py" in e for r in frames for e in r["status_evidence"])


def test_the_two_handed_chains_row_tracks_it_and_the_word_closed_in_its_title_does_not_retire_it(real) -> None:
    hits = _at(real, "09_2d", "Closed Kinematic Chains")

    # TRIAGE T12: `BACKLOG.md` defers D9 with a trigger; the retire keyword was reading the title
    assert {r["status"] for r in hits} == {"tracked"}


def test_every_formula_record_carries_one_of_the_three_provenances(real) -> None:
    formulas = [r for r in real if r["kind"] == "formula"]

    assert {r["provenance"] for r in formulas} <= set(ARR.PROVENANCE_ORDER)
    assert all(r.get("provenance") for r in formulas)
    # a research-side record is never unsourced - it IS the source. It can still be derived: doc 47
    # calls the 0.22 an invented number, and that verdict reaches the bundled copy of the brief too
    assert "unsourced" not in {r["provenance"] for r in formulas
                               if r["path"].startswith(BAR.SOURCES_DIR)}
    assert {r["provenance"] for r in formulas if "0.22" in r["expr"]
            and "Secondary-Motion" in r["name"]} == {"derived"}


def test_the_chain_cut_the_research_side_orphans(real) -> None:
    orphans = [r for r in real if r["kind"] == "formula" and r["status"] == "orphaned"]

    # 107 formula records were orphaned before the chain read the research layer (2026-09-05), and the
    # guard used to be that the chain had not claimed them ALL. P52 gave the last 45 a row instead
    # (BACKLOG R26-61 the rig's bibliography, R26-62 the ground and the transform chain, R26-63 the
    # research the triage dropped, R26-64 two dials nothing reads), so the bucket is empty on purpose.
    # What still catches an over-reaching chain: every record carries a status WITH its evidence, and an
    # orphan carries none - so nothing can sit in the bucket unaccounted, and nothing can leave it silently.
    assert len(orphans) < 107, len(orphans)
    assert all(r["status_evidence"] for r in real if r["kind"] in ("formula", "code")), \
        [r["name"] for r in real if r["kind"] in ("formula", "code") and not r["status_evidence"]][:5]
    assert not [r for r in orphans if r["status_evidence"]]
    assert all(BAR.CHAIN_ARROW not in e for r in real if r["kind"] == "formula"
               and r["status"] != "implemented" for e in r["status_evidence"])


def test_the_shipped_kinetics_symbols_carry_their_flag_and_their_tests(real) -> None:
    min_jerk = _named(real, "code", "minJerk")[0]
    spring_pop = _named(real, "code", "springPop")[0]

    assert min_jerk["flag"] == "min_jerk" and len(min_jerk["tests"]) >= 1
    assert spring_pop["flag"] == "analytic_spring"
    assert min_jerk["status"] == spring_pop["status"] == "implemented"
