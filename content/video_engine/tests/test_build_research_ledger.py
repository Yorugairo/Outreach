"""The research ingestion gate: what makes a run landed, referenced or an orphan.

The ruling under test (the operator, 2026-09-13): research is only ingested when the work names
it. So a BACKLOG row or a plan slice citing the run path is `landed`; a doc alone is only
`referenced`; nothing at all is an `orphan` and the ledger says so first. Each case is built as
a tiny tree in tmp_path - the real runs are gitignored, so a fixture is the only honest fixture.
`--check` is the gate itself: a new run on disk that nobody cites makes it exit 1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_research_ledger as BRL  # noqa: E402


def make_run(root: Path, name: str, files: int = 1) -> Path:
    run = root / BRL.RUNS_REL / name
    run.mkdir(parents=True, exist_ok=True)
    for i in range(files):
        (run / f"findings_{i}.md").write_text(f"# {name} {i}\n", encoding="utf-8")
    return run


def write_doc(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """One run of each status, plus a BACKLOG whose parked row states a trigger."""
    make_run(tmp_path, "landed_run", files=2)
    make_run(tmp_path, "referenced_run")
    make_run(tmp_path, "orphan_run", files=3)

    write_doc(tmp_path, BRL.BACKLOG_REL,
              "# Backlog\n\n"
              "| id | item |\n|---|---|\n"
              "| **R26-200** | the rig, read from `docs/research/runs/landed_run` |\n"
              "| D8 | pseudo-3D head turns | **Deferred with a trigger:** "
              "the first shot that turns a head. -> P45 T11 |\n"
              "| **R26-201** | a row with no trigger at all |\n")
    write_doc(tmp_path, "docs/runbooks/NOTES.md",
              "Read docs/research/runs/referenced_run for the numbers.\n")
    return tmp_path


def record_of(records: list[dict], name: str) -> dict:
    return next(r for r in records if r["name"] == name)


# --- the three statuses ----------------------------------------------------------------------

def test_a_backlog_row_lands_a_run(tree):
    landed = record_of(BRL.build(tree), "landed_run")

    assert landed["status"] == "landed"
    assert [c["path"] for c in landed["cited_by"]] == [BRL.BACKLOG_REL]
    assert landed["cited_by"][0]["line"] == 5
    assert landed["files"] == 2


def test_a_plan_slice_lands_a_run_too(tree):
    write_doc(tree, ".claude/PRPs/plans/P99-THING.plan.md",
              "## T3\nSeed: `docs/research/runs/orphan_run/findings_0.md`.\n")

    record = record_of(BRL.build(tree), "orphan_run")

    assert record["status"] == "landed"
    assert record["cited_by"] == [{"path": ".claude/PRPs/plans/P99-THING.plan.md", "line": 2}]


def test_a_doc_alone_is_only_referenced(tree):
    record = record_of(BRL.build(tree), "referenced_run")

    assert record["status"] == "referenced"
    assert record["cited_by"] == [{"path": "docs/runbooks/NOTES.md", "line": 1}]


def test_a_run_nothing_cites_is_an_orphan_and_the_md_puts_it_first(tree):
    records = BRL.build(tree)
    orphan = record_of(records, "orphan_run")
    assert (orphan["status"], orphan["cited_by"], orphan["files"]) == ("orphan", [], 3)
    assert len(orphan["date"]) == len("2026-09-13")

    md = BRL.render_md(records, BRL.trigger_rows(tree))
    rows = [line for line in md.splitlines() if line.startswith("| `")]
    assert rows[0].startswith("| `orphan_run`")
    assert "**orphan**" in rows[0] and "**nothing cites it**" in rows[0]
    assert "3 runs: 1 landed, 1 referenced, 1 orphan" in md


def test_a_run_citing_itself_is_not_ingestion(tree):
    write_doc(tree, f"{BRL.RUNS_REL}/orphan_run/research_plan.md",
              "Output to docs/research/runs/orphan_run/findings.md\n")

    assert record_of(BRL.build(tree), "orphan_run")["status"] == "orphan"


def test_a_longer_run_name_is_not_a_citation_of_the_shorter_one(tree):
    make_run(tree, "orphan_run_two")
    write_doc(tree, "docs/runbooks/MORE.md", "see docs/research/runs/orphan_run_two\n")

    assert record_of(BRL.build(tree), "orphan_run")["status"] == "orphan"
    assert record_of(BRL.build(tree), "orphan_run_two")["status"] == "referenced"


def test_the_generated_layers_never_count_as_a_citation(tree):
    write_doc(tree, BRL.INDEX_CONFIG_REL,
              json.dumps({"exclude": ["docs/DOCS-MANIFEST.md", "**/node_modules/**"],
                          "output": "docs/DOCS-INDEX"}))
    write_doc(tree, "docs/DOCS-MANIFEST.md", "echoes docs/research/runs/orphan_run\n")
    write_doc(tree, "docs/DOCS-INDEX.md", "echoes docs/research/runs/orphan_run\n")

    assert record_of(BRL.build(tree), "orphan_run")["status"] == "orphan"


# --- the rule, and the artifacts ----------------------------------------------------------------

def test_the_md_states_the_rule_at_the_top(tree):
    md = BRL.render_md(BRL.build(tree), BRL.trigger_rows(tree))
    head = md.splitlines()[:4]

    assert "a run is landed only when a backlog row or a plan slice cites it" in "\n".join(head)
    assert "adds to backlog or exploration" in "\n".join(head)


def test_both_artifacts_are_written_lf_and_the_jsonl_is_one_record_per_run(tree):
    BRL.write(tree)

    raw = (tree / BRL.JSONL_REL).read_bytes()
    assert b"\r\n" not in raw
    assert b"\r\n" not in (tree / BRL.MD_REL).read_bytes()
    names = [json.loads(line)["name"] for line in raw.decode("utf-8").splitlines()]
    assert names == ["landed_run", "orphan_run", "referenced_run"]      # sorted, one each


def test_two_builds_over_the_same_tree_are_byte_identical(tree):
    assert BRL.rendered(tree) == BRL.rendered(tree)


# --- the gate ---------------------------------------------------------------------------------

def test_check_exits_1_when_a_new_run_appears_and_zero_once_written(tree, capsys):
    assert BRL.main(["--check", "--repo", str(tree)]) == 1          # missing artifacts
    assert BRL.main(["--write", "--repo", str(tree)]) == 0

    make_run(tree, "brand_new_run")

    assert BRL.main(["--check", "--repo", str(tree)]) == 1
    out = capsys.readouterr().out
    assert "STALE" in out and "RESEARCH-LEDGER" in out and "--write" in out

    assert BRL.main(["--write", "--repo", str(tree)]) == 0
    assert BRL.main(["--check", "--repo", str(tree)]) == 0


def test_the_write_summary_counts_every_status(tree, capsys):
    assert BRL.main(["--write", "--repo", str(tree)]) == 0

    assert "3 runs (1 orphan, 1 referenced, 1 landed" in capsys.readouterr().out


# --- the parked-row triggers --------------------------------------------------------------------

def test_a_parked_row_with_a_trigger_is_listed_with_its_trigger_text(tree):
    rows = BRL.trigger_rows(tree)

    assert rows == [{"row": "D8", "line": 6, "trigger": "the first shot that turns a head."}]

    md = BRL.render_md(BRL.build(tree), rows)
    assert "## Parked rows with a trigger" in md
    assert "| `D8` | 6 | the first shot that turns a head. |" in md


def test_a_row_without_a_trigger_is_not_listed(tree):
    assert [r["row"] for r in BRL.trigger_rows(tree)] == ["D8"]


def test_a_long_trigger_is_truncated_and_the_backlog_is_never_rewritten(tree):
    backlog = tree / BRL.BACKLOG_REL
    before = backlog.read_text(encoding="utf-8")
    backlog.write_text(before + f"| R26-9 | `trigger:` {'x' * 400} |\n", encoding="utf-8")

    row = BRL.trigger_rows(tree)[-1]

    assert row["row"] == "R26-9"
    assert len(row["trigger"]) == BRL.TRIGGER_MAX + 3 and row["trigger"].endswith("...")
    assert backlog.read_text(encoding="utf-8").startswith(before)   # read-only extraction


# --- the real tree ------------------------------------------------------------------------------

def test_the_committed_ledger_is_in_sync():
    """The gate over this checkout: if a run appeared and nobody ran --write, this is the red."""
    assert BRL.check(ROOT) == []
