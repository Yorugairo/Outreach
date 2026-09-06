"""The gates registry is generated FROM the checkers, so these pin that it reads the code.

On a synthetic pair of mini-tools in `tmp_path` they pin the record shape exactly: an
`add("X01", "rule (38 B2)", "FAIL" if x else "PASS", msg)` call through a lambda emitter,
an f-string level, a rule given as a module constant, an f-string rule with its threshold
rendered as `{NAME=value}`, an id-less audit-style call collapsing to one slugged record,
and the lint findings whose level is the list they land in. They also pin that a citation
the docs index cannot reach keeps a null path instead of disappearing, that two builds of
the same tree are byte-identical, and that `--check` follows the source.

The real-repo smoke pins that the gates the docs cite by id are actually in the registry
with rule text (`G15b`, `S02`, `M16`, `V01`, `J50`), that `S02` cites land in doc 51, and
that no call site in a checker went unparsed. `M13` is asserted ABSENT: doc 47 s208 lists
it as settled but "the gate lands with the edit pass", so a registry line for it would be
a claim the code does not make - if this flips, M13 shipped and the row is real."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_gates_registry as BGR  # noqa: E402

MINI_OPENING = '''\
"""mini opening gate"""
from dataclasses import dataclass

RING_LEVEL = "FAIL"
SHORT_CYCLE_S = 30.0
SRC_X02 = "51.2 THE SHAPE: the mechanism by 0:10"


@dataclass(frozen=True)
class Gate:
    id: str
    src: str
    level: str
    message: str


def run(text):
    g = []
    add = lambda i, src, lvl, m: g.append(Gate(i, src, lvl, m))
    add("X01", "rule (38 B2)", "FAIL" if text else "PASS", "the message")
    add("X02", SRC_X02, f"{'WARN' if text else 'PASS'}", "the message")
    add("X03", f"a rehook every {SHORT_CYCLE_S:.0f} s", RING_LEVEL, "the message")
    return g


def run_short(text):
    g = []
    add = lambda i, src, lvl, m: g.append(Gate(i, src, lvl, m))
    add("S01", "51.2 HOOK 0:00-0:03: the claim, spoken", "JUDGE", "the message")
    return g
'''

MINI_AUDIT = '''\
"""mini audit"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    level: str
    rule: str
    message: str


def audit(text):
    out = []

    def add(level: str, rule: str, msg: str) -> None:
        out.append(Finding(level, rule, msg))

    add("FAIL", "doc 37 sec 1", "unknown marks would be spoken")
    add("WARN", "doc 37 sec 1", "and a second row on the same rule")
    return out
'''

MINI_LINT = '''\
"""mini lint"""
from dataclasses import dataclass

PASSIVE_RATIO_MAX = 0.15


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _check_passive(sentences):
    return [Finding("PASSIVE_RATIO", f"passive voice over {PASSIVE_RATIO_MAX}")]


def lint_script(text):
    failures = [*_check_passive(text)]
    warnings = [Finding("REHOOK", "no rehook-family construction found")]
    return failures, warnings
'''

MINI_TEST = 'def test_x01_and_passive():\n    assert "X01" and "PASSIVE_RATIO"\n'
INDEX_ROWS = [
    {"path": "docs/content-video-engine/51-THE-SHORTS-FORMAT.md", "line": 1, "level": 1,
     "doc": "51", "heading": "51 - The shorts format", "lead": "", "labels": [], "terms": []},
    {"path": "docs/content-video-engine/51-THE-SHORTS-FORMAT.md", "line": 24, "level": 2,
     "doc": "51", "heading": "51.2 The shape", "lead": "", "labels": [], "terms": []},
]


@pytest.fixture()
def mini_repo(tmp_path: Path) -> Path:
    scripts = tmp_path / BGR.SCRIPTS_REL
    tests = tmp_path / BGR.TESTS_REL
    docs = tmp_path / "docs"
    for folder in (scripts, tests, docs):
        folder.mkdir(parents=True, exist_ok=True)
    (scripts / "gate_opening_structure.py").write_text(MINI_OPENING, encoding="utf-8")
    (scripts / "audit_script_doctrine.py").write_text(MINI_AUDIT, encoding="utf-8")
    (scripts / "lint_script_pattern.py").write_text(MINI_LINT, encoding="utf-8")
    (tests / "test_mini.py").write_text(MINI_TEST, encoding="utf-8")
    (docs / "DOCS-INDEX.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in INDEX_ROWS), encoding="utf-8")
    return tmp_path


def _by_id(records: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in records}


# ---- the record shape, on the mini-tools -----------------------------------

def test_lambda_emitter_call_becomes_an_exact_record(mini_repo: Path) -> None:
    record = _by_id(BGR.build(mini_repo))["X01"]

    assert record == {
        "id": "X01",
        "tool": "gate_opening_structure.py",
        "family": "opening-long",
        "rule": "rule (38 B2)",
        "levels": ["FAIL", "PASS"],
        "cites": [{"ref": "38 B2", "path": None, "line": None}],
        "tests": ["test_mini.py"],
        "source": {"path": "content/video_engine/scripts/gate_opening_structure.py", "line": 20},
    }


def test_constant_rule_and_fstring_level_are_read(mini_repo: Path) -> None:
    record = _by_id(BGR.build(mini_repo))["X02"]

    assert record["rule"] == "51.2 THE SHAPE: the mechanism by 0:10"
    assert record["levels"] == ["WARN", "PASS"]
    assert record["cites"] == [{
        "ref": "51.2", "path": "docs/content-video-engine/51-THE-SHORTS-FORMAT.md", "line": 24}]


def test_fstring_rule_renders_its_threshold_by_name_and_value(mini_repo: Path) -> None:
    record = _by_id(BGR.build(mini_repo))["X03"]

    assert record["rule"] == "a rehook every {SHORT_CYCLE_S=30.0} s"
    assert record["levels"] == ["FAIL"]        # through the RING_LEVEL constant


def test_the_short_branch_is_its_own_family(mini_repo: Path) -> None:
    record = _by_id(BGR.build(mini_repo))["S01"]

    assert record["family"] == "opening-short"
    assert record["levels"] == ["JUDGE"]


def test_id_less_audit_rows_collapse_to_one_slugged_record(mini_repo: Path) -> None:
    record = _by_id(BGR.build(mini_repo))["audit:doc-37-sec-1"]

    assert record["rule"] == "doc 37 sec 1"
    assert record["levels"] == ["FAIL", "WARN"]
    assert record["source"]["line"] == 18      # the FIRST call site, not the last
    assert record["tests"] == []


def test_lint_findings_take_the_level_of_the_list_they_land_in(mini_repo: Path) -> None:
    records = _by_id(BGR.build(mini_repo))

    assert records["lint:passive-ratio"]["levels"] == ["FAIL"]
    assert records["lint:passive-ratio"]["rule"] == "passive voice over {PASSIVE_RATIO_MAX=0.15}"
    assert records["lint:passive-ratio"]["tests"] == ["test_mini.py"]
    assert records["lint:rehook"]["levels"] == ["WARN"]


def test_records_are_sorted_by_family_then_id(mini_repo: Path) -> None:
    records = BGR.build(mini_repo)

    assert [(r["family"], r["id"]) for r in records] == sorted(
        (r["family"], r["id"]) for r in records)


def test_no_call_site_in_the_mini_tools_goes_unparsed(mini_repo: Path) -> None:
    assert BGR.unparsed_calls(mini_repo) == []


# ---- determinism and --check ------------------------------------------------

def test_two_builds_of_the_same_tree_are_byte_identical(mini_repo: Path) -> None:
    first = BGR.rendered(mini_repo)
    second = BGR.rendered(mini_repo)

    assert first == second
    assert first[BGR.JSONL_REL].endswith("\n")
    assert "\r" not in first[BGR.MD_REL]


def test_check_is_clean_after_write_and_stale_after_an_edit(mini_repo: Path) -> None:
    BGR.write(mini_repo)
    assert BGR.check(mini_repo) == []

    target = mini_repo / BGR.SCRIPTS_REL / "gate_opening_structure.py"
    target.write_text(MINI_OPENING.replace('"X03"', '"X04"'), encoding="utf-8")
    stale = BGR.check(mini_repo)

    assert len(stale) == 2
    assert all(rel in " ".join(stale) for rel in (BGR.JSONL_REL, BGR.MD_REL))
    assert all("+" in problem and "/-" in problem for problem in stale)


def test_check_exits_one_when_the_artifacts_are_missing(mini_repo: Path, capsys) -> None:
    assert BGR.main(["--check", "--repo", str(mini_repo)]) == 1
    assert "STALE" in capsys.readouterr().out

    assert BGR.main(["--write", "--repo", str(mini_repo)]) == 0
    assert BGR.main(["--check", "--repo", str(mini_repo)]) == 0


def test_a_missing_runner_is_said_so_not_faked(mini_repo: Path) -> None:
    text = "\n".join(BGR.composition(mini_repo))

    assert "not found in this checkout" in text


# ---- the real checkers ------------------------------------------------------

@pytest.fixture(scope="module")
def real() -> list[dict]:
    return BGR.build(ROOT)


@pytest.mark.parametrize("gate_id", ["G15b", "S02", "M16", "V01", "J50"])
def test_the_gates_the_docs_cite_are_in_the_registry(real: list[dict], gate_id: str) -> None:
    rows = [r for r in real if r["id"] == gate_id]

    assert rows, f"{gate_id} is not in the registry"
    assert all(len(r["rule"]) > 20 for r in rows)
    assert all(r["levels"] for r in rows)


def test_m13_is_not_a_built_gate(real: list[dict]) -> None:
    """47 s208: M13 is settled from the reference but "the gate lands with the edit pass"."""
    assert not [r for r in real if r["id"] == "M13"], (
        "M13 now emits rows - the registry is right and this canary is stale")


def test_s02_cites_the_shorts_format_doc(real: list[dict]) -> None:
    record = next(r for r in real if r["id"] == "S02")

    assert [c["path"] for c in record["cites"]] == [
        "docs/content-video-engine/51-THE-SHORTS-FORMAT.md"]
    assert all(c["line"] for c in record["cites"])


def test_every_checker_contributes_rows(real: list[dict]) -> None:
    families = {r["family"] for r in real}

    assert {"opening-long", "opening-short", "opening-shared", "motion", "audit",
            "lint", "viewer"} <= families
    assert {r["tool"] for r in real} == set(BGR.FAMILY)


def test_the_opening_gate_carries_at_least_sixty_ids(real: list[dict]) -> None:
    ids = {r["id"] for r in real if r["family"].startswith("opening")}

    assert len(ids) >= 60


def test_no_call_site_in_a_real_checker_goes_unparsed() -> None:
    assert BGR.unparsed_calls(ROOT) == []


def test_the_composition_block_quotes_the_runner() -> None:
    text = "\n".join(BGR.composition(ROOT))

    assert "run_all" in text
    assert text.index("lint_script_pattern.py") < text.index("audit_script_doctrine.py")
    assert text.index("audit_script_doctrine.py") < text.index("gate_opening_structure.py")
    assert "--defer-opening" in text
    assert "SHORT_MAX_S" in text          # is_short's own words, not a paraphrase
