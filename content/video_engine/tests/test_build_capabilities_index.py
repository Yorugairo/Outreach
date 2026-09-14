"""The capabilities layer: one record per CAPABILITIES.md row, never a silent drop, a page that stays small.

The synthetic tests drive `main` over a temp repo; the real-tree tests pin the count against the doc's
own `| **` rows and the card axes against the effects catalogue.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_capabilities_index as B  # noqa: E402

HEADER = "| Capability | Where | State | Proof |\n|---|---|---|---|\n"
GOOD_ROWS = (
    "| **Widget engine** — draws the widget on its word. Second sentence here. **Use when:** always "
    "| `samples/widget.mjs` (`drawWidget`) | LIVE 2026-09-13 - on the tariff short (E98 s7) "
    "| `tests/test_widget.py`, 3d07ede; the `exit:melt` card, R26-135 |\n"
    "| **Gadget gate, WIRED** — the gadget rule | `scripts/gate_gadget.py` | BUILT, unwired | `test_gadget.py` |\n"
)
DOC = f"# CAPABILITIES\n\n## Rendering\n\n{HEADER}{GOOD_ROWS}\n## Gates\n\n{HEADER}" \
      "| **Pipe prose** — JAPAN | UNITED STATES bars | `p.py` | WIRED | `g.png` |\n"


def repo_with(tmp_path: Path, text: str) -> Path:
    path = tmp_path / B.CAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return tmp_path


def run(capsys, root: Path, *args: str) -> tuple[int, str]:
    code = B.main([*args, "--repo", str(root)])
    return code, capsys.readouterr().out


# --------------------------------------------------------------------------- synthetic

def test_a_four_cell_row_reads_into_every_field(tmp_path):
    # Act
    parsed = B.build(repo_with(tmp_path, DOC))

    # Assert
    widget = parsed.records[0]
    assert parsed.failures == []
    assert widget["id"] == "widget-engine"
    assert widget["name"] == "Widget engine"
    assert widget["section"] == "Rendering"
    assert widget["line"] == 7
    assert widget["what"] == "draws the widget on its word."
    assert widget["where"] == ["samples/widget.mjs", "drawWidget"]
    assert (widget["state"], widget["state_note"]) == ("LIVE", "LIVE 2026-09-13")
    assert widget["proof"] == ["tests/test_widget.py", "exit:melt", "3d07ede"]
    assert widget["cards"] == ["exit:melt"]
    assert widget["rulings"] == ["E98 s7"]
    assert widget["backlog"] == ["R26-135"]
    assert parsed.records[1]["state"] == "BUILT"


def test_an_unescaped_pipe_in_prose_is_rejoined_and_flagged(tmp_path):
    # Act
    parsed = B.build(repo_with(tmp_path, DOC))

    # Assert
    pipe = parsed.records[2]
    assert pipe["what"] == "JAPAN | UNITED STATES bars"
    assert (pipe["where"], pipe["state"], pipe["proof"]) == (["p.py"], "WIRED", ["g.png"])
    assert parsed.flagged == ["line 14: Pipe prose - extra-pipes (5 cells)"]


def test_a_malformed_row_fails_write_by_name_with_its_line(capsys, tmp_path):
    # Arrange: three cells under a four-column header
    root = repo_with(tmp_path, DOC + "| **Broken row** — no state | `b.py` |  proof only |\n")

    # Act
    code, out = run(capsys, root, "--write")

    # Assert: named, lined, and nothing written
    assert code == 1
    assert "FAILURE line 15: Broken row - 3 cells under a 4-column header" in out
    assert not (root / B.JSONL_REL).exists()


def test_a_two_cell_row_reads_its_state_off_the_name_and_strict_fails_it(capsys, tmp_path):
    # Arrange
    root = repo_with(tmp_path, f"## S\n\n{HEADER}| **THE AGENDA (P52 T8), WIRED** (2026-09-12, 3d07ede) - "
                               "`agenda`: numbered rows | `species/agenda.mjs` |\n")

    # Act
    record = B.build(root).records[0]
    strict_code, strict_out = run(capsys, root, "--write", "--strict")
    code, _ = run(capsys, root, "--write")

    # Assert
    assert (record["name"], record["state"], record["form"]) == ("THE AGENDA (P52 T8)", "WIRED", "two-cell")
    assert record["what"] == "agenda: numbered rows"
    assert record["proof"] == ["species/agenda.mjs", "3d07ede"]
    assert strict_code == 1 and "FAILURE line 5: THE AGENDA (P52 T8) - two-cell" in strict_out
    assert code == 0


def test_check_passes_after_write_and_names_the_record_a_one_word_edit_staled(capsys, tmp_path):
    # Arrange
    root = repo_with(tmp_path, DOC)
    assert run(capsys, root, "--write")[0] == 0

    # Act
    fresh = run(capsys, root, "--check")
    (root / B.CAP_REL).write_text(DOC.replace("the gadget rule", "the gizmo rule"), encoding="utf-8")
    stale_code, stale_out = run(capsys, root, "--check")

    # Assert
    assert fresh[0] == 0 and "in sync (3 records" in fresh[1]
    assert stale_code == 1
    assert "docs/CAPABILITIES-INDEX.jsonl differs at record 2 (gadget-gate-wired, CAPABILITIES.md:8)" in stale_out


def test_what_is_capped_at_a_word_never_mid_word(tmp_path):
    # Arrange: one long first sentence of distinct words
    words = [f"word{i}x" for i in range(60)]
    row = f"| **Long** — {' '.join(words)}. | `l.py` | LIVE | `t.py` |\n"

    # Act
    what = B.build(repo_with(tmp_path, HEADER + row)).records[0]["what"]

    # Assert
    assert len(what) <= B.WHAT_MAX
    assert what.endswith(B.ELLIPSIS)
    assert what[:-1].split()[-1] in words


def test_the_page_over_its_byte_budget_is_a_failure(capsys, tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr(B, "MD_MAX_BYTES", 100)

    # Act
    code, out = run(capsys, repo_with(tmp_path, DOC), "--write")

    # Assert
    assert code == 1 and "over MD_MAX_BYTES 100" in out


# --------------------------------------------------------------------------- the real tree

REAL = ROOT / B.CAP_REL
needs_real = pytest.mark.skipif(not REAL.is_file(), reason="CAPABILITIES.md is not in this checkout")


@needs_real
def test_every_capability_row_in_the_doc_is_exactly_one_record():
    # Arrange
    text = REAL.read_text(encoding="utf-8")
    rows = [n for n, line in enumerate(text.split("\n"), 1) if line.startswith(B.ROW_PREFIX)]

    # Act
    parsed = B.build(ROOT)

    # Assert
    assert parsed.failures == []
    assert [r["line"] for r in parsed.records] == rows
    assert len({r["id"] for r in parsed.records}) == len(rows)


@needs_real
def test_every_real_what_is_capped_at_a_word_and_the_page_fits_its_budget():
    # Arrange
    lines = REAL.read_text(encoding="utf-8").replace("\\|", "|").split("\n")
    parsed = B.build(ROOT)

    # Act / Assert
    for record in parsed.records:
        what = record["what"]
        assert len(what) <= B.WHAT_MAX, record["id"]
        if what.endswith(B.ELLIPSIS):
            source = B.plain(lines[record["line"] - 1])
            at = source.find(what[:-1])
            assert at >= 0, record["id"]
            assert not re.match(r"\w", source[at + len(what) - 1:at + len(what)]), record["id"]
    assert len(B.render_md(parsed).encode("utf-8")) <= B.MD_MAX_BYTES


@pytest.mark.skipif(not (ROOT / "docs/EFFECTS-CATALOG.jsonl").is_file(), reason="no effects catalogue")
def test_the_card_axes_cover_every_axis_in_the_effects_catalogue():
    # Arrange
    text = (ROOT / "docs/EFFECTS-CATALOG.jsonl").read_text(encoding="utf-8")

    # Act
    axes = {json.loads(line)["axis"] for line in text.splitlines() if line.strip()}

    # Assert
    assert axes <= set(B.CARD_AXES)
