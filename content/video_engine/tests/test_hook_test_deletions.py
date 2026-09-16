"""The test-deletion receipt: a commit that removes a test names it, or is refused.

Every case here is the shape of a real event (2026-09-16): a whole-file rewrite sliced to EOF, dropped
the last ten tests of `test_authoring_kit.py`, and hid it behind a count that ROSE 36 -> 45.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("test_deletions", REPO / "scripts/hooks/test_deletions.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

DIFF_ONE = "--- a/tests/t.py\n+++ b/tests/t.py\n-def test_a_plate_may_name_its_use():\n+def test_something_new():\n"


def test_a_commit_that_removes_no_test_passes():
    ok, why = H.check("feat: a thing", "+def test_new():\n", {})
    assert ok and why == "no test removed"


def test_a_test_that_moved_to_another_file_is_not_a_deletion():
    """The gate is about LOSS, not about where a test lives - a move or a rename-in-place passes silently."""
    ok, why = H.check("refactor: split the suite", DIFF_ONE,
                      {"tests/other.py": "def test_a_plate_may_name_its_use():\n    pass\n"})
    assert ok and "moved or renamed" in why


def test_a_test_that_exists_nowhere_afterwards_is_refused_and_named():
    ok, why = H.check("feat: unrelated work", DIFF_ONE, {"tests/t.py": "def test_something_new():\n    pass\n"})
    assert not ok
    assert "test_a_plate_may_name_its_use" in why
    assert "Tests-removed:" in why, "the refusal tells the author how to declare it"


def test_declaring_the_removal_lets_it_through():
    msg = ("feat: retire the plate use option\n\n"
           "Tests-removed: test_a_plate_may_name_its_use - the option it pinned was retired here\n")
    ok, why = H.check(msg, DIFF_ONE, {"tests/t.py": "def test_something_new():\n    pass\n"})
    assert ok and "1 declared" in why


def test_the_real_incident_ten_dropped_behind_a_rising_count_is_refused():
    """36 -> 45 passed as success. The count is not the check; the names are."""
    lost = ["test_a_plate_may_name_its_use", "test_an_unknown_use_refuses_and_names_the_option",
            "test_hold_until_gives_every_held_light_its_sentence", "test_row_line_names_the_world_and_what_fires_on_it",
            "test_the_kit_holds_no_episode_fact", "test_the_kit_is_the_five_modules_the_plan_names",
            "test_tr13_an_estimated_take_keeps_the_gap_rule_and_says_so",
            "test_tr13_the_gap_pin_keeps_m13s_placement_and_the_refusal_holds_under_both_rules",
            "test_tr13_the_onset_rule_is_the_default_and_places_a_cut_three_frames_before_the_word",
            "test_write_shot_table_writes_the_tuple_rows_the_compiler_loads"]
    diff = "".join(f"-def {n}():\n" for n in lost) + "".join(f"+def test_new_{i}():\n" for i in range(19))
    blob = "".join(f"def test_new_{i}():\n    pass\n" for i in range(19))
    ok, why = H.check("feat(vo): the tone chain and its gate", diff, {"tests/t.py": blob})
    assert not ok
    assert all(n in why for n in lost), "every lost name is printed, not a count"
    assert "45" in why and "36" in why, "the refusal carries the incident that earned the gate"


def test_a_partial_declaration_still_refuses_the_rest():
    diff = "-def test_one():\n-def test_two():\n"
    ok, why = H.check("fix: x\n\nTests-removed: test_one - retired\n", diff, {"tests/t.py": "pass\n"})
    assert not ok and "test_two" in why and "test_one" not in why.split("go unnamed")[1]
