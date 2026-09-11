"""Species by sentence (P50 T1): the three places agree (the map's s4 is the compiler's `when`; every kind carries one),
the classifier reads the two shipped takes the way the map does, the lint runs INFO-only on both shorts, and E61's
plate-use check WARNs a long-form plate with no named use."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import lint_species_choice as L  # noqa: E402

PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"
TOKYO, TARIFF = PROJECTS / "tokyo-tea-break", PROJECTS / "japan-tariff-trick"


def _has_build(project: Path) -> bool:
    return (project / L.TABLE_NAME).is_file() and (project / L.DEFAULT_BUILD / "timeline.json").is_file()


# ---------------------------------------------------------------- the three places agree
def test_every_kind_and_verb_carries_a_when():
    assert set(B.SPECIES_WHEN) == set(B.SPECIES_KINDS)
    assert set(B.CHART_TO_WHEN) == set(B.CHART_TO_KINDS)
    for text in list(B.SPECIES_WHEN.values()) + list(B.CHART_TO_WHEN.values()):
        assert "\n" not in text and 30 <= len(text) <= 260, text


def test_map_carries_the_compiler_when_and_the_ten_acts():
    doc = L.MAP_DOC.read_text(encoding="utf-8")
    a, b = L.doc_block(doc)
    assert doc[a:b] == "\n" + L.render_when_md(), "SPECIES-BY-SENTENCE.md s4 is stale: lint_species_choice.py --write-doc"
    assert L.sync_doc(write=False)
    for act in L.ACTS:
        assert f"**{act}" in doc, act
    for kind in B.SPECIES_KINDS:
        assert f"`{kind}`" in doc, kind


def test_every_act_names_built_species_the_map_lists():
    for act in L.ACTS:
        assert L.ACT_SPECIES[act], act


# ---------------------------------------------------------------- the classifier (crude on purpose)
@pytest.mark.parametrize("text, acts", [
    ("Tokyo has pledged ten trillion yen to chips, and if that works, it beats our bonds.", {"QUOTES", "TURNS", "BREAKS"}),
    ("Since February, Japan has sold a hundred and twenty-two billion dollars of it, a tenth of the pile.", {"COMPARES", "DIVIDES", "TURNS"}),
    ("The opponent isn't the Fed; it's a Japanese balance sheet.", {"RETRACTS"}),
    ("Two numbers show where the money went: a Treasury page, and your phone.", {"SETS"}),
    ("When you buy an American truck, its parts cross the border six separate times.", {"NAMES", "EXPLAINS"}),   # "six" is not a figure to the crude table; "percent" and "billion" are
    ("Tokyo is still on its tea break.", set()),   # `breaks` the verb, never the noun
    ("Tokyo took a tea break.", set()),
])
def test_classify_reads_the_shipped_sentences(text, acts):
    assert acts <= set(L.classify(text)), (text, L.classify(text))


def test_classify_keeps_the_map_order():
    acts = L.classify("Since February the biggest lender said it beats bonds, a tenth of the pile, because of the border.")
    assert acts == [a for a in L.ACTS if a in acts]


# ---------------------------------------------------------------- the report on the shipped shorts
@pytest.mark.skipif(not _has_build(TOKYO), reason="the Tokyo build-short is not on disk")
def test_tokyo_report_reads_the_burst_and_the_record():
    lines, counts = L.report(TOKYO)
    joined = "\n".join(lines)
    pledge = next(l for l in lines if "pledged ten trillion yen" in l)
    assert "QUOTES" in pledge and "BREAKS" in pledge
    assert "record" in pledge and "read->park" in pledge, pledge        # the record dock pops centred and parks
    assert "chart_to:recast" in pledge and "(burst)" in pledge, pledge  # the recast into the overflow state
    two = next(l for l in lines if "Two numbers show" in l)
    assert "SETS" in two and "chart_to:park" in two, two
    assert "un-park" in joined
    assert counts["sentences"] >= 15 and counts["with_row"] >= 8
    assert all(l.startswith(("INFO", "species by sentence")) for l in lines)   # a short: no E61 plate rows, no WARN
    assert L.main([str(TOKYO)]) == 0


@pytest.mark.skipif(not _has_build(TARIFF), reason="the tariff build-short is not on disk")
def test_tariff_report_is_info_only():
    lines, counts = L.report(TARIFF)
    border = next(l for l in lines if "cross the border" in l)
    assert "NAMES" in border and "trace" in border, border
    assert counts["sentences"] >= 20
    assert not any(l.startswith("WARN") for l in lines)
    assert L.main([str(TARIFF)]) == 0


# ---------------------------------------------------------------- E61: a long-form plate names its use
def _write_project(tmp_path: Path, rows: str, runtime: float) -> Path:
    project = tmp_path / "long-form"
    (project / L.DEFAULT_BUILD).mkdir(parents=True)
    (project / L.TABLE_NAME).write_text('"""test table"""\nW = ' + rows + "\n", encoding="utf-8")
    (project / L.DEFAULT_BUILD / "timeline.json").write_text(json.dumps({
        "runtime_s": runtime,
        "sentences": [{"text": "Tokyo has pledged ten trillion yen to chips.", "start": 0.0, "end": 3.0, "part": 1},
                      {"text": "And here is a bridge sentence with nothing in it.", "start": 3.0, "end": 6.0, "part": 1}],
    }), encoding="utf-8")
    return project


def test_long_form_plate_without_a_use_warns(tmp_path):
    project = _write_project(tmp_path, "[(0.0, 100.0, 'plate-a;idle=drift', (0, 0, 0), [], None, None), "
                                       "(100.0, 200.0, 'plate-b;idle=drift;use=bridge', (0, 0, 0), [], None, None), "
                                       "(200.0, 210.0, 'ledger:ev-x-v1:line:0:right', (0, 0, 0), [], 'cut', [])]", 210.0)
    lines, counts = L.report(project)
    warns = [l for l in lines if l.startswith("WARN")]
    assert len(warns) == 1 and "plate-a" in warns[0] and "E61" in warns[0]
    assert any("plate-b" in l and "use=bridge" in l and l.startswith("INFO") for l in lines)
    assert counts["plates"] == 2 and counts["plates_unnamed"] == 1
    assert L.main([str(project)]) == 0          # a WARN never blocks


def test_short_skips_the_plate_check_unless_asked(tmp_path):
    project = _write_project(tmp_path, "[(0.0, 60.0, 'plate-a;idle=drift', (0, 0, 0), [], None, None)]", 60.0)
    lines, _ = L.report(project)
    assert not any(l.startswith("WARN") for l in lines)
    lines, _ = L.report(project, long=True)
    assert any(l.startswith("WARN") for l in lines)


def test_no_row_marks_the_sentence(tmp_path):
    project = _write_project(tmp_path, "[(0.0, 6.0, 'plate-a;idle=drift', (0, 0, 0), [], None, None)]", 6.0)
    lines, counts = L.report(project)
    pledge = next(l for l in lines if "pledged" in l)
    assert pledge.endswith("· no row") and "row has: world plate:plate-a" in pledge   # a world starting is context, not a row
    bridge = next(l for l in lines if "bridge sentence" in l)
    assert "· bridge ·" in bridge and "no row" not in bridge
    assert counts["no_row"] == 1


def test_usage_errors_exit_2(tmp_path):
    assert L.main([]) == 2
    assert L.main([str(tmp_path)]) == 2
