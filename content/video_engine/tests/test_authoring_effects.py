"""P55 T8: the agent-facing surface - `authoring.effects` resolves a spoken name to the catalogue's cards,
and `effects_card.py` prints one card short enough to read.

Both read only the generated layer `docs/EFFECTS-CATALOG.jsonl`. Ambiguous names resolve to a LIST, never one
card (P55 decision 2), so `card()` refuses them by naming every candidate.

P56 T4: the layer also carries the RECIPES. The pins: "badge ladder" resolves to `recipe:badge-ladder`; an exact
card token still wins ("the test card" is the CHECKLIST CARD, not the recipe whose title contains those words);
"stack" still answers with the three cards; and a recipe prints its members in order inside the 40 lines.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

from authoring import effects as E  # noqa: E402
import effects_card  # noqa: E402

STACK_IDS = {"dock_payload:stack", "dock_option:stack", "overflow:stack"}


def test_load_reads_every_record_of_the_generated_layer():
    lines = (ROOT / "docs/EFFECTS-CATALOG.jsonl").read_text(encoding="utf-8").splitlines()
    cards = E.load()
    assert len(cards) == len([ln for ln in lines if ln.strip()])
    assert all("id" in c and "title" in c for c in cards)


def test_an_operator_alias_resolves_the_evidence_wall_to_the_verdict_stack():
    assert E.card("evidence wall")["id"] == "dock_payload:stack"


def test_the_test_card_resolves_by_its_title():
    assert E.card("test card")["id"] == "chart_dock:checklist"


def test_the_test_card_is_the_card_not_the_recipe_whose_title_contains_it():
    # `recipe:test-card-rows` is "The test card's rows on their words" - the equality tier keeps the CARD first
    assert [c["id"] for c in E.find("the test card")] == ["chart_dock:checklist"]
    assert E.card("the test card")["axis"] == "chart_dock"


def test_a_recipe_resolves_by_its_title_and_is_marked_as_one():
    got = E.card("badge ladder")
    assert got["id"] == "recipe:badge-ladder" and E.is_recipe(got)
    assert [m["card"] for m in got["members"]][0] == "dock_kind:image"
    assert not E.is_recipe(E.card("evidence wall"))


def test_an_exact_recipe_id_wins_over_every_other_tier():
    assert [c["id"] for c in E.find("recipe:badge-ladder")] == ["recipe:badge-ladder"]


def test_an_exact_id_wins_over_every_other_tier():
    assert [c["id"] for c in E.find("dock_option:stack")] == ["dock_option:stack"]


def test_a_token_returns_every_card_carrying_it():
    assert {c["id"] for c in E.find("stack")} == STACK_IDS


def test_an_ambiguous_name_raises_naming_every_candidate():
    with pytest.raises(LookupError) as err:
        E.card("stack")
    for cid in STACK_IDS:
        assert cid in str(err.value)


@pytest.mark.parametrize("spelling", ["blur zoom", "blur-zoom", "blurzoom", "Blur Zoom"])
def test_whitespace_and_hyphens_do_not_change_the_blur_zoom(spelling):
    got = E.card(spelling)
    assert got["id"] == "exit:blurzoom"
    assert (got["axis"], got["token"]) == ("exit", "blurzoom")


def test_an_unknown_name_raises_with_three_suggestions():
    with pytest.raises(LookupError) as err:
        E.card("qqzzx flarp")
    msg = str(err.value)
    assert "unknown" in msg
    assert len(re.findall(r"^\s+- ", msg, flags=re.M)) == 3


def test_find_is_empty_for_an_empty_name():
    assert E.find("   ") == []


def test_the_verdict_stacks_printed_card_lists_its_five_phases(capsys):
    code = effects_card.main(["evidence wall"])
    out = capsys.readouterr().out
    assert code == 0
    assert len(out.splitlines()) <= 40
    phases = [ln for ln in out.splitlines() if re.match(r"^\s+\d+\. ", ln)]
    assert len(phases) == 5
    assert "dock_payload:stack" in out
    assert '("ev-holds-stack-v1",0,701.73,727.63)' in out   # the example, verbatim


def test_a_recipes_printed_card_lists_its_members_in_order_with_the_proof(capsys):
    code = effects_card.main(["badge ladder"])
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert code == 0
    assert len(lines) <= 40
    assert lines[0].endswith("[recipe:badge-ladder]")
    members = [ln for ln in lines if ln.startswith("  +")]
    # the badges moved from `dock_kind:image` to the card `dock_option:badge` when T8 carded the badge rail (2026-09-13)
    assert len(members) == 5 and members[1].startswith("  +2.05s  dock_option:badge (The badge rail)")
    assert "acts: QUOTES, EXPLAINS - window 6s" in out
    assert "FIRST_BADGE_S=2.05" in out and "BADGE_GAP_S=1.3" in out
    assert "proof: steel-and-paper / build-f / 50.4s" in out
    assert "count 41 (a grammar)" in out
    assert "steel-and-paper.timeline.json" in out


def test_several_matches_print_one_line_each_and_exit_2(capsys):
    code = effects_card.main(["stack"])
    out = capsys.readouterr().out
    assert code == 2
    assert "name one id" in out
    for cid in STACK_IDS:
        assert sum(cid in ln for ln in out.splitlines()) == 1


def test_no_match_prints_the_nearest_three_and_exits_1(capsys):
    code = effects_card.main(["qqzzx flarp"])
    out = capsys.readouterr().out
    assert code == 1
    assert len([ln for ln in out.splitlines() if ln.startswith("  ")]) == 3


def test_json_prints_the_record(capsys):
    assert effects_card.main(["evidence wall", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == "dock_payload:stack"


def test_all_prints_every_card_of_an_ambiguous_name(capsys):
    assert effects_card.main(["stack", "--all", "--json"]) == 0
    assert {c["id"] for c in json.loads(capsys.readouterr().out)} == STACK_IDS


def test_every_card_prints_in_forty_lines_or_fewer():
    for c in E.load():
        assert len(effects_card.render(c).splitlines()) <= 40, c["id"]


def test_the_kit_module_names_no_episode():
    names = {p.name for p in (ROOT / "content/video_engine/projects").glob("*/*") if p.is_dir()}
    src = (ROOT / "content/video_engine/scripts/authoring/effects.py").read_text(encoding="utf-8").lower()
    hits = sorted(n for n in names if re.search(rf"(?<![\w-]){re.escape(n.lower())}(?![\w-])", src))
    assert names and hits == []
