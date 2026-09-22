from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import script_review_contract as C  # noqa: E402


def _craft(tmp_path: Path) -> Path:
    path = tmp_path / "craft.jsonl"
    path.write_text("\n".join((
        json.dumps({"device": "the loop"}),
        json.dumps({"device": "the callback ledger"}),
    )) + "\n", encoding="utf-8")
    return path


def test_inventory_keeps_mechanical_and_clearance_obligations_separate(tmp_path):
    text = "[promise] One test. [rehook] But the real question remains."
    rows = C.obligations(text, "long", _craft(tmp_path))
    ids = {row.id for row in rows}
    assert {"tool:lint", "mechanical:G36-broad-beat-activity"} <= ids
    assert {"map:narrative-map", "map:first-180-continuity", "viewer:V01"} <= ids
    assert {"declared:promise:1", "declared:rehook:1"} <= ids
    assert {"craft:the-loop", "craft:the-callback-ledger"} <= ids


def test_declared_occurrences_are_individually_identified(tmp_path):
    rows = C.obligations("[rehook] First. [rehook] Second.", "long", _craft(tmp_path))
    ids = [row.id for row in rows]
    assert "declared:rehook:1" in ids and "declared:rehook:2" in ids


def test_short_and_long_judge_contracts_do_not_cross(tmp_path):
    craft = _craft(tmp_path)
    long_ids = {row.id for row in C.obligations("Words.", "long", craft)}
    short_ids = {row.id for row in C.obligations("Words.", "short", craft)}
    assert "opening:J14" in long_ids and "opening:J50" not in long_ids
    assert "opening:J50" in short_ids and "opening:J14" not in short_ids
    assert "map:macro-phases" not in short_ids


def test_tag_only_change_invalidates_annotation_without_invalidating_audio():
    plain = "The lender wants a higher price."
    tagged = "[rehook] The lender wants a higher price."
    assert C.spoken_hash(plain) == C.spoken_hash(tagged)
    assert C.annotated_hash(plain) != C.annotated_hash(tagged)


def test_stage_due_set_grows_and_scratch_does_not_require_measured_clearance(tmp_path):
    rows = C.obligations("[promise] One test.", "long", _craft(tmp_path))
    diagnostic = {row.id for row in C.due_by(rows, "diagnostic")}
    scratch = {row.id for row in C.due_by(rows, "scratch")}
    text_review = {row.id for row in C.due_by(rows, "text-review")}
    recording = {row.id for row in C.due_by(rows, "recording")}
    assert diagnostic == scratch
    assert diagnostic < text_review < recording
    assert "timing:measured-word-clock" not in scratch
    assert "timing:measured-word-clock" in recording


def test_every_current_craft_row_enters_the_manifest():
    lines = [line for line in C.CRAFT_MAP.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = C.coverage_manifest("Words.")
    craft = [row for row in manifest["obligations"] if row["id"].startswith("craft:")]
    assert len(craft) == len(lines)
    assert manifest["counts"]["total"] == len(manifest["obligations"])
    assert len(manifest["contract_digest"]) == 64


def test_duplicate_craft_devices_fail_closed(tmp_path):
    path = tmp_path / "craft.jsonl"
    path.write_text('{"device":"same"}\n{"device":"same"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate obligation"):
        C.obligations("Words.", craft_map=path)


def test_every_emitted_strength_screen_candidate_becomes_an_obligation(tmp_path):
    screens = tmp_path / "S-SCREENS.md"
    screens.write_text("""# STRENGTH SCREENS
## X1 — antecedent pairs (1)
- [15] prior -> sentence
## P6 — deixis openers (1)
- [27] This is the line.
## P4C — cadence runs
- ¶1: [8, 20]
""", encoding="utf-8")
    ids = {row.id for row in C.obligations("Words.", craft_map=_craft(tmp_path), screens=screens)}
    assert {"screen:x1:15", "screen:deixis:27", "screen:cadence:1"} <= ids


def test_missing_craft_or_screen_source_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError, match="craft map missing"):
        C.obligations("Words.", craft_map=tmp_path / "missing.jsonl")
    with pytest.raises(FileNotFoundError, match="strength screens missing"):
        C.obligations("Words.", craft_map=_craft(tmp_path), screens=tmp_path / "missing.md")
