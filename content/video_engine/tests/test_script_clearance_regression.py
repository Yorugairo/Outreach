"""Regression fixtures for the old fail-open script-review clearance.

These tests are deliberately provider-free.  The historical V14 shape had a
mechanical PASS while its viewer, declared-judge, and narrative-map rows were
missing.  The new receipt adapter must report that state as INCOMPLETE; the
green fixture proves that the same adapter can clear a complete named stage.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures/script_review"
sys.path.insert(0, str(SCRIPTS))

import script_review as R  # noqa: E402
import script_review_contract as C  # noqa: E402
import viewer_score as VS  # noqa: E402
import viewer_windows as VW  # noqa: E402


SCRIPT = FIXTURES / "v14-opening-vo.txt"
MAP = FIXTURES / "sustained-tension-map.json"


def _empty_craft(tmp_path: Path) -> Path:
    craft = tmp_path / "craft.jsonl"
    craft.write_text("", encoding="utf-8")
    return craft


def _complete_receipt(tmp_path: Path, stage: str = "text-review") -> dict:
    text = SCRIPT.read_text(encoding="utf-8")
    map_data = json.loads(MAP.read_text(encoding="utf-8"))
    craft = _empty_craft(tmp_path)
    screens = tmp_path / "screens.md"
    screens.write_text("# STRENGTH SCREENS\n", encoding="utf-8")
    rows = C.obligations(text, "long", craft, screens)
    digest = C.contract_digest(rows)
    spoken = C.canonical_spoken(text)
    viewer_windows = tmp_path / "viewer-windows.json"
    VW.write_windows(VW.build_document(SCRIPT, text, no_screens=True), viewer_windows)
    viewer_windows_hash = C.sha256_bytes(viewer_windows.read_bytes())
    windows_doc = json.loads(viewer_windows.read_text(encoding="utf-8"))
    viewer_reports = tmp_path / "viewer-reports.json"
    viewer_reports.write_text(json.dumps({
        "schema_version": "viewer_reports.v1",
        "script_hash": C.spoken_hash(text), "annotated_script_hash": C.annotated_hash(text),
        "timeline_hash": windows_doc["timeline_hash"], "windows_hash": viewer_windows_hash,
        "expected_windows": len(windows_doc["windows"]),
        "reports": [{"i": window["i"], "new_things": [window["text"]],
                     "held_question": "fixture question", "asked_of_me": "fixture ask",
                     "could_not_follow": []} for window in windows_doc["windows"]],
    }), encoding="utf-8")
    reports_doc = json.loads(viewer_reports.read_text(encoding="utf-8"))
    viewer_score = VS.score(windows_doc, reports_doc, text)
    viewer_score.update({"script_hash": C.spoken_hash(text),
                         "annotated_script_hash": C.annotated_hash(text),
                         "windows_hash": viewer_windows_hash})
    viewer_statuses = {f"viewer:{row['id']}": row["level"] for row in viewer_score["rows"]}
    viewer = tmp_path / "viewer.md"
    viewer.write_text(VS.render(viewer_score, SCRIPT.name), encoding="utf-8")
    hashes = {
        "annotated_script_hash": C.annotated_hash(text),
        "spoken_script_hash": C.spoken_hash(text),
        "map_hash": R.map_digest(map_data),
        "contract_digest": digest,
    }
    result = {
        "schema": "script_review.v1",
        **hashes,
        "form": "long",
        "stage": stage,
        "scope": {"kind": "full", "start_s": 0, "end_s": 240},
        "reviewers": [{"id": "judge-1", "role": "semantic-reviewer", "run_id": "judge-run-1"},
                      {"id": "viewer-1", "role": "blind-viewer", "run_id": "viewer-run-1"},
                      {"id": "independent-1", "role": "independent-reviewer", "run_id": "independent-run-1"}],
        "source": {"viewer_artifact": str(viewer), "viewer_windows": str(viewer_windows),
                   "viewer_reports": str(viewer_reports), "screens": str(screens)},
        "dependencies": {**hashes, "viewer_artifact_hash": C.sha256_bytes(viewer.read_bytes()),
                         "viewer_windows_hash": viewer_windows_hash,
                         "viewer_reports_hash": C.sha256_bytes(viewer_reports.read_bytes()),
                         "screens_hash": C.sha256_bytes(screens.read_bytes())},
        "rows": [],
    }
    for index, obligation in enumerate(C.due_by(rows, stage)):
        row = {"obligation_id": obligation.id, "status": viewer_statuses.get(obligation.id, "PASS"),
               "rationale": f"{obligation.id}: reviewed in offline fixture ({index}).",
               "evidence": {"finding_id": obligation.id, "source": "fixture"}}
        if obligation.owner in {"judge", "blind-viewer", "independent-reviewer"} or obligation.id.startswith(("declared:", "map:")):
            start = (index * 11) % max(1, len(spoken) - 120)
            end = min(len(spoken), start + 120)
            row.update({"quote": spoken[start:end], "span": {"start": start, "end": end},
                        "reviewer": {"judge": "judge-1", "blind-viewer": "viewer-1",
                                     "independent-reviewer": "independent-1"}.get(obligation.owner, "judge-1")})
        result["rows"].append(row)
    return result


def test_v14_missing_viewer_and_map_review_is_incomplete(tmp_path):
    receipt = _complete_receipt(tmp_path)
    receipt["rows"] = [row for row in receipt["rows"] if not row["obligation_id"].startswith("viewer:")]
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_empty_craft(tmp_path))
    assert not result.ok
    assert result.status == "INCOMPLETE"
    assert any(item.startswith("viewer:") for item in result.missing)


def test_green_complete_fixture_clears_named_text_review_stage(tmp_path):
    receipt = _complete_receipt(tmp_path)
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_empty_craft(tmp_path))
    assert result.ok, result.errors
    assert result.status == "CLEAR"


def test_sustained_tension_diagnostic_is_not_tag_spacing():
    result = R.validate_narrative_map(MAP)
    assert result.ok, result.errors
    assert all(result.diagnostics["coverage"]["windows"][str(window)]["ok"] for window in (90, 180, 300))


def test_historical_empty_rows_fixture_is_fail_closed(tmp_path):
    incomplete = json.loads((FIXTURES / "v14-incomplete-receipt.json").read_text(encoding="utf-8"))
    result = R.validate_receipt(SCRIPT, incomplete, narrative_map=MAP, craft_map=_empty_craft(tmp_path))
    assert not result.ok
    assert result.status == "INCOMPLETE"
    assert result.missing
