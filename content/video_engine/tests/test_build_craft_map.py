"""The craft map is a JOIN, so these pin the three joins and the one verification.

On a synthetic seed + gates registry + docs index + script in `tmp_path` they pin: a device
reaching its gate through the declared ALIASES map (`the tell` -> `audit:doc-35-rule-2`,
whose rule text says only "doc 35 rule 2" and could never be reached by its name), a device
reaching its gate by a PHRASE match of its own name, a `defined in` heading resolved exactly
and by prefix and left null when the index cannot reach it, an exemplar found in a wrapped
blockquote (verified, and re-pointed at the line it actually starts on), an exemplar that is
not in the file it cites (verified false, row KEPT), a row that honestly found none, the two
judge-only shapes, that a scale-free device lands in both markdown blocks, determinism, and
`--check`.

The real-repo smoke pins the operator's ask rather than the numbers: at least 30 devices,
`tricolon` reaching a gate, `ring` reaching both `G15b` and `S05`, every row resolving at
least one definition, and every gate id claimed by the map existing in the registry. The
count of unverified exemplars is REPORTED, never asserted to zero - a quote that moved is a
seed edit, not a test failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_craft_map as BCM  # noqa: E402

MINI_SCRIPT_REL = "content/video_engine/projects/mini/SCRIPT-VO.txt"
MINI_DOC_REL = "docs/mini/DOCTRINE.md"

MINI_SCRIPT = (
    "So here's what you're getting: not a rebuttal, not a victory lap, not a panic.\n"
    "\n"
    "The flip: if memory breaks while the buildout holds, the scarcity story is wrong.\n"
)

# Line 4 wraps mid-sentence inside a blockquote: the exemplar for `wrapped device` spans
# lines 4-5 and must resolve to 4.
MINI_DOC = """# Mini doctrine

## 1. Sentence mechanics for the ear

> **Terminal stress:** the ear anchors hardest to the last word
> before a pause, so put the surprising word at the END.

## 2. Delivery - strategic silence

Nothing here but a heading the seed points at by prefix.
"""

MINI_GATES = [
    {"id": "X12", "tool": "gate.py", "family": "opening-long",
     "rule": "Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1",
     "levels": ["FAIL", "PASS"], "cites": [], "tests": [], "source": {"path": "gate.py", "line": 1}},
    {"id": "audit:doc-35-rule-2", "tool": "audit.py", "family": "audit",
     "rule": "doc 35 rule 2", "levels": ["FAIL", "WARN"], "cites": [], "tests": [],
     "source": {"path": "audit.py", "line": 9}},
    {"id": "J02", "tool": "gate.py", "family": "opening-long",
     "rule": "P2: the head-fake is offered STRAIGHT, no wink", "levels": ["JUDGE"],
     "cites": [], "tests": [], "source": {"path": "gate.py", "line": 20}},
]

MINI_INDEX = [
    {"path": MINI_DOC_REL, "line": 1, "level": 1, "doc": None, "heading": "Mini doctrine",
     "lead": "", "labels": [], "terms": []},
    {"path": MINI_DOC_REL, "line": 3, "level": 2, "doc": None,
     "heading": "1. Sentence mechanics for the ear", "lead": "", "labels": [], "terms": []},
    {"path": MINI_DOC_REL, "line": 8, "level": 2, "doc": None,
     "heading": "2. Delivery — strategic silence (the missing voiceover doctrine)",
     "lead": "", "labels": [], "terms": []},
]

MINI_SEED = f"""# CRAFT DEVICES - mini

Prose the parser must ignore, including a decoy table:

| column | rule |
| --- | --- |
| **device** | not a device row |

## The devices

| device | scale | what it does | defined in | exemplar |
| --- | --- | --- | --- | --- |
| tricolon | L0 · L5 | three strokes, the third completes or subverts | {MINI_DOC_REL}#1. Sentence mechanics for the ear | "not a rebuttal, not a victory lap, not a panic." ({MINI_SCRIPT_REL}:1) |
| the tell | L5 | one variable, one threshold, where we sit, what flips us | {MINI_DOC_REL}#2. Delivery | "The flip: if memory breaks while the buildout holds" ({MINI_SCRIPT_REL}:3) |
| head-fake | L2 | the obvious answer offered straight, no wink | {MINI_DOC_REL}#1. Sentence mechanics for the ear | "not a rebuttal, not a victory lap, not a panic." ({MINI_SCRIPT_REL}:1) |
| the never-list | L0 · judge | nothing from the injected voice profile's ban list | {MINI_DOC_REL}#Mini doctrine | "The flip: if memory breaks while the buildout holds" ({MINI_SCRIPT_REL}:3) |
| wrapped device | L1 | a quote that wraps across two blockquote lines | {MINI_DOC_REL}#1. Sentence mechanics for the ear | "the ear anchors hardest to the last word before a pause" ({MINI_DOC_REL}:9) |
| moved device | L0 | its quote is not in the file it cites | {MINI_DOC_REL}#Mini doctrine | "a line nobody ever wrote in this repository" ({MINI_SCRIPT_REL}:1) |
| unsourced device | L6 · judge | a device the sources name but never demonstrate | {MINI_DOC_REL}#A heading the index has never seen | none found (roots searched: docs/mini, content/video_engine/projects/mini) |

## Trailing prose, also ignored.
"""


@pytest.fixture()
def mini_repo(tmp_path: Path) -> Path:
    for rel, text in ((BCM.SEED_REL, MINI_SEED), (MINI_DOC_REL, MINI_DOC),
                      (MINI_SCRIPT_REL, MINI_SCRIPT)):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (tmp_path / BCM.GATES_REL).write_text(
        "".join(json.dumps(g) + "\n" for g in MINI_GATES), encoding="utf-8")
    (tmp_path / BCM.DOCS_INDEX_REL).write_text(
        "".join(json.dumps(r) + "\n" for r in MINI_INDEX), encoding="utf-8")
    return tmp_path


def _by_device(records: list[dict]) -> dict[str, dict]:
    return {r["device"]: r for r in records}


# ---- the seed, parsed -------------------------------------------------------

def test_only_the_device_table_is_parsed_and_order_is_the_seed_s(mini_repo: Path) -> None:
    records = BCM.build(mini_repo)

    assert [r["device"] for r in records] == [
        "tricolon", "the tell", "head-fake", "the never-list",
        "wrapped device", "moved device", "unsourced device"]


def test_a_scale_free_device_is_macro_and_micro_at_once(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["tricolon"]

    assert record["scale"] == ["L0", "L5"]
    assert record["macro_or_micro"] == "both"
    markdown = BCM.render_md(BCM.build(mini_repo))
    assert markdown.count("**tricolon**") == 2      # listed under Macro AND under Micro


# ---- the gate join ----------------------------------------------------------

def test_the_alias_map_reaches_a_rule_the_device_name_cannot(mini_repo: Path) -> None:
    """`audit:doc-35-rule-2`'s whole rule text is "doc 35 rule 2" - only a declared alias
    can reach it from the words "the tell"."""
    record = _by_device(BCM.build(mini_repo))["the tell"]

    assert [g["id"] for g in record["gates"]] == ["audit:doc-35-rule-2"]
    assert record["gates"][0]["rule"] == "doc 35 rule 2"
    assert record["gates"][0]["levels"] == ["FAIL", "WARN"]
    assert record["judge_only"] is False


def test_a_device_name_phrase_matches_the_rule_text_on_its_own(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["tricolon"]

    assert [g["id"] for g in record["gates"]] == ["X12"]
    assert record["gates"][0]["family"] == "opening-long"


def test_a_hyphenated_name_matches_across_the_hyphen(mini_repo: Path) -> None:
    """"head-fake" must reach a rule that writes it the same way; the join normalises both."""
    record = _by_device(BCM.build(mini_repo))["head-fake"]

    assert [g["id"] for g in record["gates"]] == ["J02"]


def test_a_device_with_no_gate_in_the_registry_carries_none(mini_repo: Path) -> None:
    assert _by_device(BCM.build(mini_repo))["wrapped device"]["gates"] == []


# ---- judge_only -------------------------------------------------------------

def test_judge_only_when_only_a_judge_row_joined(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["head-fake"]

    assert record["gates"][0]["levels"] == ["JUDGE"]
    assert record["judge_only"] is True


def test_judge_only_when_the_seed_declares_it_and_no_gate_joins(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["the never-list"]

    assert record["gates"] == []
    assert record["judge_only"] is True


def test_a_gateless_row_that_did_not_declare_judge_is_not_judge_only(mini_repo: Path) -> None:
    assert _by_device(BCM.build(mini_repo))["wrapped device"]["judge_only"] is False


# ---- defined_in -------------------------------------------------------------

def test_an_exact_heading_resolves_to_its_line(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["tricolon"]

    assert record["defined_in"] == [{
        "path": MINI_DOC_REL, "line": 3, "heading": "1. Sentence mechanics for the ear"}]


def test_a_heading_prefix_resolves_and_keeps_the_index_s_full_heading(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["the tell"]

    assert record["defined_in"][0]["line"] == 8
    assert record["defined_in"][0]["heading"].startswith("2. Delivery")


def test_a_heading_the_index_cannot_reach_keeps_a_null_line(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["unsourced device"]

    assert record["defined_in"] == [{
        "path": MINI_DOC_REL, "line": None,
        "heading": "A heading the index has never seen"}]


# ---- the exemplar -----------------------------------------------------------

def test_a_quote_wrapped_across_blockquote_lines_verifies_at_its_first_line(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["wrapped device"]

    assert record["exemplar"]["verified"] is True
    assert record["exemplar"]["line"] == 5          # the seed guessed 9; the file says 5


def test_a_quote_that_is_not_in_the_file_is_flagged_and_the_row_survives(mini_repo: Path) -> None:
    record = _by_device(BCM.build(mini_repo))["moved device"]

    assert record["exemplar"]["verified"] is False
    assert record["exemplar"]["text"] == "a line nobody ever wrote in this repository"
    assert record["exemplar"]["path"] == MINI_SCRIPT_REL
    assert "UNVERIFIED" in BCM.render_md(BCM.build(mini_repo))


def test_a_row_that_found_no_exemplar_says_where_it_looked(mini_repo: Path) -> None:
    exemplar = _by_device(BCM.build(mini_repo))["unsourced device"]["exemplar"]

    assert exemplar["path"] is None and exemplar["line"] is None
    assert exemplar["verified"] is False
    assert exemplar["text"].startswith("none found (roots searched:")


def test_a_verified_quote_reports_the_script_line_it_sits_on(mini_repo: Path) -> None:
    exemplar = _by_device(BCM.build(mini_repo))["the tell"]["exemplar"]

    assert exemplar == {
        "text": "The flip: if memory breaks while the buildout holds",
        "path": MINI_SCRIPT_REL, "line": 3, "verified": True}


# ---- determinism and --check ------------------------------------------------

def test_two_builds_of_the_same_tree_are_byte_identical(mini_repo: Path) -> None:
    first = BCM.rendered(mini_repo)
    second = BCM.rendered(mini_repo)

    assert first == second
    assert first[BCM.JSONL_REL].endswith("\n")
    assert "\r" not in first[BCM.MD_REL]


def test_check_is_clean_after_write_and_stale_after_a_seed_edit(mini_repo: Path) -> None:
    BCM.write(mini_repo)
    assert BCM.check(mini_repo) == []

    seed = mini_repo / BCM.SEED_REL
    seed.write_text(MINI_SEED.replace("| tricolon |", "| anaphora |"), encoding="utf-8")
    stale = BCM.check(mini_repo)

    assert len(stale) == 2
    assert all(rel in " ".join(stale) for rel in (BCM.JSONL_REL, BCM.MD_REL))
    assert all("+" in problem and "/-" in problem for problem in stale)


def test_check_exits_one_when_the_artifacts_are_missing(mini_repo: Path, capsys) -> None:
    assert BCM.main(["--check", "--repo", str(mini_repo)]) == 1
    assert "STALE" in capsys.readouterr().out

    assert BCM.main(["--write", "--repo", str(mini_repo)]) == 0
    assert BCM.main(["--check", "--repo", str(mini_repo)]) == 0


def test_a_seed_with_no_device_table_is_said_so_not_faked(tmp_path: Path) -> None:
    path = tmp_path / BCM.SEED_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# no table here\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no device rows"):
        BCM.build(tmp_path)


# ---- the real seed ----------------------------------------------------------

@pytest.fixture(scope="module")
def real() -> list[dict]:
    return BCM.build(ROOT)


def test_the_map_covers_at_least_thirty_devices(real: list[dict]) -> None:
    assert len(real) >= 30
    assert len({r["device"] for r in real}) == len(real), "a device is listed twice"


def test_tricolon_reaches_at_least_one_gate(real: list[dict]) -> None:
    record = next(r for r in real if r["device"] == "tricolon")

    assert len(record["gates"]) >= 1
    assert all(g["rule"] for g in record["gates"])


def test_ring_reaches_the_long_form_and_the_short_form_gate(real: list[dict]) -> None:
    ids = {g["id"] for g in next(r for r in real if r["device"] == "ring")["gates"]}

    assert {"G15b", "S05"} <= ids


def test_every_device_resolves_at_least_one_definition(real: list[dict]) -> None:
    unresolved = [r["device"] for r in real
                  if not any(d["line"] for d in r["defined_in"])]

    assert unresolved == []


def test_every_gate_the_map_claims_exists_in_the_registry(real: list[dict]) -> None:
    registry = {g["id"] for g in BCM.load_gates(ROOT)}
    claimed = {g["id"] for r in real for g in r["gates"]}

    assert claimed <= registry


def test_every_alias_target_is_a_real_gate_id() -> None:
    registry = {g["id"] for g in BCM.load_gates(ROOT)}
    declared = {gid for ids in BCM.ALIASES.values() for gid in ids}

    assert declared <= registry, f"stale alias target(s): {sorted(declared - registry)}"


def test_the_macro_and_micro_blocks_between_them_hold_every_device(real: list[dict]) -> None:
    macro = [r for r in real if r["macro_or_micro"] in ("macro", "both")]
    micro = [r for r in real if r["macro_or_micro"] in ("micro", "both")]

    assert macro and micro
    assert {r["device"] for r in macro} | {r["device"] for r in micro} == {
        r["device"] for r in real}


def test_unverified_exemplars_are_reported_not_asserted_away(real: list[dict], capsys) -> None:
    """A quote that moved is a seed edit, not a test failure - so this REPORTS the count."""
    unverified = [f'{r["device"]} -> {r["exemplar"]["text"][:60]}'
                  for r in real if not r["exemplar"]["verified"]]

    with capsys.disabled():
        print(f"\ncraft map: {len(unverified)}/{len(real)} exemplars unverified"
              + ("".join(f"\n  - {u}" for u in unverified) if unverified else ""))
    assert isinstance(unverified, list)
