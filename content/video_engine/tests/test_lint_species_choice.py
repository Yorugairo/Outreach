"""Species by sentence (P50 T1): the three places agree (the map's s4 is the compiler's `when`; every kind carries one),
the classifier reads the two shipped takes the way the map does, the lint runs INFO-only on both shorts, and E61's
plate-use check WARNs a long-form plate with no named use."""
from __future__ import annotations

import ast
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


# ---------------------------------------------------------------- --propose (P53 T8): a PROPOSER, never an allocator
BRIDGE = PROJECTS / "normal-for-which-bridge"
BRIDGE_BUILD = "build-short-axes"


def test_every_map_label_is_a_kind_a_chart_to_verb_or_declared_not_a_species():
    """The map may not grow a label the proposer silently drops: it is a species kind, a `chart_to` verb, or it is
    named in NOT_A_SPECIES as the world / dock / page choice it actually is."""
    for act, labels in L.ACT_SPECIES.items():
        for label in labels:
            assert L.proposable(label) or label in L.NOT_A_SPECIES, (act, label)


def test_proposable_reads_the_kinds_and_the_chart_to_verbs():
    assert L.proposable("figure") == ("figure", {})
    assert L.proposable("chart_to:rescale") == ("chart_to", {"to": "rescale"})
    assert L.proposable("bars page") is None          # a PAGE, not a row's species
    assert L.proposable("burst:stop") is None         # the object's `overflow`, not a row's species


def test_anchor_phrase_takes_the_sentences_first_words():
    words = [{"w": w} for w in "Now put that number against the country's whole output.".split()]
    assert L.anchor_phrase("Now put that number against the country's whole output.", words) == ("Now put that number", True)
    assert L.anchor_phrase("Two words", words)[0] == "Two words"
    assert L.anchor_phrase("Not in the take at all", words) == ("Not in the take", False)


def _write_series(project: Path, obj: str, facts: dict) -> None:
    d = project / "evidence/objects"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{obj}.series.json").write_text(json.dumps({"series": [{"pts": [[0, 1]]}], "facts": facts}), encoding="utf-8")


def _propose_project(tmp_path: Path) -> Path:
    project = _write_project(tmp_path, "[(0.0, 6.0, 'ledger:ev-x-v1:line:9:right', (0, 0, 0), [], None, [])]", 6.0)
    _write_series(project, "ev-x-v1", {"latest": 4.83, "last_idx": 9, "idx_aug26": 7})
    return project


def test_proposal_rows_parse_as_dict_literals_anchored_on_a_phrase(tmp_path):
    lines, counts = L.propose(_propose_project(tmp_path))
    assert lines[0] == L.PROPOSE_HEADER
    rows = [l.strip().rstrip(",") for l in lines if l.strip().startswith("{")]
    assert rows, lines
    for row in rows:
        node = ast.parse(row.split("  #")[0].strip().rstrip(","), mode="eval").body
        assert isinstance(node, ast.Dict)
        got = {k.value: v for k, v in zip(node.keys, node.values)}
        assert got["kind"].value in B.SPECIES_KINDS
        assert isinstance(got["at"], ast.Call) and got["at"].func.id == "at"     # a PHRASE call, never a number
        assert isinstance(got["at"].args[0], ast.Constant)
    assert counts["proposed_for"] == 1 and counts["rows"] == len(rows)


def test_every_proposal_names_its_act_and_the_when_that_proposed_it(tmp_path):
    lines, _ = L.propose(_propose_project(tmp_path))
    assert any(l.startswith("PROPOSAL") and "pledged" in l for l in lines)
    for row in [l for l in lines if l.strip().startswith("{")]:
        act, _, when = row.partition("  # ")[2].partition(" · when: ")
        assert act.split(" ")[0] in L.ACTS, row
        assert when.strip() and when.strip() in list(B.SPECIES_WHEN.values()) + list(B.CHART_TO_WHEN.values()), row


def test_target_is_read_off_the_facts_block_by_name(tmp_path):
    lines, _ = L.propose(_propose_project(tmp_path))
    joined = "\n".join(lines)
    assert 'facts("ev-x-v1")["last_idx"]' in joined      # the NAME, never the number
    assert '"index": 9' not in joined
    assert "idx_aug26" in joined                         # the other index keys are offered, not chosen


def test_nothing_is_proposed_where_a_row_fires_or_no_act_exists(tmp_path):
    project = _write_project(tmp_path, "[(0.0, 6.0, 'ledger:ev-x-v1:line:9:right', (0, 0, 0), [], None, "
                                       "[{'kind': 'figure', 'at': 1.0, 'dur': 1.5, 'text': '10T'}])]", 6.0)
    _write_series(project, "ev-x-v1", {"last_idx": 9})
    lines, counts = L.propose(project)
    assert counts["proposed_for"] == 0 and counts["rows"] == 0
    assert not any(l.startswith("PROPOSAL") for l in lines)
    assert any("nothing to propose" in l for l in lines)
    assert "bridge sentence" not in "\n".join(lines)      # no act: never proposed for


def test_propose_leaves_the_report_untouched(tmp_path):
    project = _propose_project(tmp_path)
    before, _ = L.report(project)
    assert L.main([str(project), "--propose"]) == 0
    after, _ = L.report(project)
    assert before == after


def test_a_page_species_is_not_proposed_over_a_plate(tmp_path):
    project = _write_project(tmp_path, "[(0.0, 6.0, 'plate-a;idle=drift', (0, 0, 0), [], None, None)]", 6.0)
    lines, counts = L.propose(project)
    rows = [l for l in lines if l.strip().startswith("{")]
    assert not any('"kind": "figure"' in r for r in rows)          # a page species needs a ledger page
    assert any("not proposable on this world" in l for l in lines)


@pytest.mark.skipif(not (BRIDGE / L.TABLE_NAME).is_file() or not (BRIDGE / BRIDGE_BUILD / "timeline.json").is_file(),
                    reason="the bridge short's axes build is not on disk")
def test_the_bridge_short_is_proposed_for_from_its_own_facts():
    lines, counts = L.propose(BRIDGE, build=BRIDGE_BUILD)
    joined = "\n".join(lines)
    assert lines[0] == L.PROPOSE_HEADER and "count" in lines[0]
    assert counts["rows"] > 0 and counts["proposed_for"] > 0
    assert 'facts("ev-' in joined and '["last_idx"]' in joined
    assert L.main([str(BRIDGE), "--build", BRIDGE_BUILD, "--propose"]) == 0
