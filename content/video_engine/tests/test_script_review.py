"""Focused offline tests for script_review.v1 receipt custody/completeness."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

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


def _craft(tmp_path: Path) -> Path:
    path = tmp_path / "craft.jsonl"
    path.write_text("", encoding="utf-8")
    return path


def _receipt(tmp_path: Path, *, stage: str = "text-review") -> dict:
    text = SCRIPT.read_text(encoding="utf-8")
    spoken = C.canonical_spoken(text)
    craft = _craft(tmp_path)
    screens = tmp_path / "screens.md"
    screens.write_text("# STRENGTH SCREENS\n", encoding="utf-8")
    rows = C.obligations(text, "long", craft, screens)
    digest = C.contract_digest(rows)
    map_data = json.loads(MAP.read_text(encoding="utf-8"))
    viewer_windows = tmp_path / "viewer-windows.json"
    VW.write_windows(VW.build_document(SCRIPT, text, no_screens=True), viewer_windows)
    viewer_windows_hash = C.sha256_bytes(viewer_windows.read_bytes())
    windows_doc = json.loads(viewer_windows.read_text(encoding="utf-8"))
    viewer_reports = tmp_path / "viewer-reports.json"
    viewer_reports.write_text(json.dumps({
        "schema_version": "viewer_reports.v1",
        "script_hash": C.spoken_hash(text),
        "annotated_script_hash": C.annotated_hash(text),
        "timeline_hash": windows_doc["timeline_hash"],
        "windows_hash": viewer_windows_hash,
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
    receipt = {
        "schema": R.RECEIPT_SCHEMA,
        "annotated_script_hash": C.annotated_hash(text),
        "spoken_script_hash": C.spoken_hash(text),
        "map_hash": R.map_digest(map_data),
        "contract_digest": digest,
        "form": "long",
        "stage": stage,
        "scope": {"kind": "full", "start_s": 0, "end_s": 240},
        "reviewers": [{"id": "judge-1", "role": "semantic-reviewer", "run_id": "judge-run-1"},
                      {"id": "viewer-1", "role": "blind-viewer", "run_id": "viewer-run-1"},
                      {"id": "independent-1", "role": "independent-reviewer", "run_id": "independent-run-1"}],
        "source": {"viewer_artifact": str(viewer), "viewer_windows": str(viewer_windows),
                   "viewer_reports": str(viewer_reports), "screens": str(screens)},
        "dependencies": {
            "annotated_script_hash": C.annotated_hash(text),
            "spoken_script_hash": C.spoken_hash(text),
            "map_hash": R.map_digest(map_data),
            "contract_digest": digest,
            "viewer_artifact_hash": C.sha256_bytes(viewer.read_bytes()),
            "viewer_windows_hash": viewer_windows_hash,
            "viewer_reports_hash": C.sha256_bytes(viewer_reports.read_bytes()),
            "screens_hash": C.sha256_bytes(screens.read_bytes()),
        },
        "rows": [],
    }
    for index, obligation in enumerate(C.due_by(rows, stage)):
        row = {
            "obligation_id": obligation.id,
            "status": viewer_statuses.get(obligation.id, "PASS"),
            "rationale": f"{obligation.id}: reviewed against the current source and contract ({index}).",
            "evidence": {"finding_id": obligation.id, "source": "offline-fixture"},
        }
        if obligation.owner in {"judge", "blind-viewer", "independent-reviewer"} or obligation.id.startswith(("declared:", "map:")):
            start = (index * 11) % max(1, len(spoken) - 120)
            end = min(len(spoken), start + 120)
            row["quote"] = spoken[start:end]
            row["span"] = {"start": start, "end": end}
            row["reviewer"] = {"judge": "judge-1", "blind-viewer": "viewer-1",
                               "independent-reviewer": "independent-1"}.get(obligation.owner, "judge-1")
        receipt["rows"].append(row)
    return receipt


def test_complete_text_receipt_is_clear(tmp_path):
    receipt = _receipt(tmp_path)
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert result.ok, result.errors
    assert result.status == "CLEAR"
    assert result.missing == ()


def test_blanket_all_pass_boilerplate_cannot_clear(tmp_path):
    receipt = _receipt(tmp_path)
    spoken = C.canonical_spoken(SCRIPT.read_text(encoding="utf-8"))
    for row in receipt["rows"]:
        if "reviewer" in row:
            row.update({"quote": spoken, "span": {"start": 0, "end": len(spoken)},
                        "rationale": "Everything looks good.",
                        "evidence": {"finding_id": row["obligation_id"], "source": "generic-score"}})
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("entire script" in error or "exact obligation ID" in error for error in result.errors)


def test_missing_viewer_judge_and_map_rows_are_incomplete(tmp_path):
    receipt = _receipt(tmp_path)
    receipt["rows"] = [row for row in receipt["rows"] if not row["obligation_id"].startswith("viewer:")]
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert result.status == "INCOMPLETE"
    assert any(row.startswith("viewer:") for row in result.missing)

    # A stale/missing map cannot be laundered by an otherwise complete receipt.
    no_map = R.validate_receipt(SCRIPT, receipt, narrative_map=None, craft_map=_craft(tmp_path))
    assert not no_map.ok
    assert any("narrative_map is required" in error for error in no_map.errors)


@pytest.mark.parametrize("mutation", [
    lambda payload: payload["rows"].append(copy.deepcopy(payload["rows"][0])),
    lambda payload: payload["rows"][0].update({"obligation_id": "not-an-obligation"}),
    lambda payload: payload["rows"][0].update({"status": "WHATEVER"}),
    lambda payload: payload["rows"][0].update({"bogus": True}),
])
def test_invalid_duplicate_or_unexpected_rows_fail_closed(tmp_path, mutation):
    receipt = _receipt(tmp_path)
    mutation(receipt)
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert result.status in {"INCOMPLETE", "FAIL"}


def test_na_requires_basis(tmp_path):
    receipt = _receipt(tmp_path)
    receipt["rows"][0]["status"] = "NA"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("na_basis" in error for error in result.errors)


def test_semantic_rows_require_the_declared_role_and_contract_aware_na(tmp_path):
    receipt = _receipt(tmp_path)
    row = next(row for row in receipt["rows"] if row["obligation_id"].startswith("declared:"))
    row.pop("reviewer")
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("reviewer is required" in error for error in result.errors)

    receipt = _receipt(tmp_path)
    row = next(row for row in receipt["rows"] if row["obligation_id"].startswith("declared:"))
    obligation = next(item for item in C.obligations(SCRIPT.read_text(encoding="utf-8"), "long", _craft(tmp_path))
                      if item.id == row["obligation_id"])
    row.update({"status": "NA", "na_basis": f"Not applicable under {obligation.source}: fixture basis."})
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("NA cannot clear" in error for error in result.errors)


def test_prefix_scope_is_measured_full_form_and_cannot_clear_the_body(tmp_path):
    receipt = _receipt(tmp_path, stage="prefix-preview")
    spoken = C.canonical_spoken(SCRIPT.read_text(encoding="utf-8"))
    words = [{"w": word, "start_s": i * 0.4, "end_s": i * 0.4 + 0.3}
             for i, word in enumerate(spoken.split())]
    timeline = tmp_path / "timeline.json"
    timeline.write_text(json.dumps({"words": words}), encoding="utf-8")
    receipt["timing_source"] = "measured"
    receipt["scope"] = {"kind": "prefix", "start_s": 0, "end_s": words[len(words) // 2]["end_s"]}
    receipt["dependencies"].update({
        "timeline_hash": C.sha256_bytes(timeline.read_bytes()),
        "normalized_timeline_hash": R.word_clock_digest(R.normalize_word_clock(timeline)),
    })
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path), timeline=timeline)
    assert result.ok, result.errors

    receipt["scope"]["kind"] = "full"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path), timeline=timeline)
    assert not result.ok
    assert any("scope.kind must be 'prefix'" in error for error in result.errors)


def test_recording_string_scope_and_stale_map_identity_fail_closed(tmp_path):
    receipt = _receipt(tmp_path)
    receipt["scope"] = "prefix excerpt"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("structured object" in error for error in result.errors)

    receipt = _receipt(tmp_path)
    map_data = json.loads(MAP.read_text(encoding="utf-8"))
    map_data["script_hash"] = "0" * 64
    receipt["map_hash"] = R.map_digest(map_data)
    receipt["dependencies"]["map_hash"] = receipt["map_hash"]
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=map_data, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("narrative map script_hash" in error for error in result.errors)


def test_full_recording_scope_cannot_start_mid_script(tmp_path):
    receipt = _receipt(tmp_path, stage="recording")
    receipt["scope"] = {"kind": "full", "start_s": 120, "end_s": 240}
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("full scope must start at 0" in error for error in result.errors)


def test_viewer_failures_cannot_be_relabeled_pass(tmp_path):
    receipt = _receipt(tmp_path)
    viewer = Path(receipt["source"]["viewer_artifact"])
    windows_hash = receipt["dependencies"]["viewer_windows_hash"]
    viewer.write_text("\n".join([f"script_hash: {receipt['spoken_script_hash']}",
                                  f"annotated_script_hash: {receipt['annotated_script_hash']}",
                                  f"windows_hash: {windows_hash}",
                                  *[f"[FAIL ] V{i:02d} failed" for i in range(1, 6)], ""]), encoding="utf-8")
    receipt["dependencies"]["viewer_artifact_hash"] = C.sha256_bytes(viewer.read_bytes())
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert result.status == "FAIL"
    assert any("does not match" in error for error in result.errors)


def test_info_cannot_launder_applicable_obligations(tmp_path):
    receipt = _receipt(tmp_path)
    for row in receipt["rows"]:
        row["status"] = "INFO"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("INFO is allowed only for viewer:V04 or viewer:V05" in error for error in result.errors)


def test_viewer_summary_without_windows_and_reports_cannot_clear(tmp_path):
    receipt = _receipt(tmp_path)
    receipt["source"].pop("viewer_windows")
    receipt["source"].pop("viewer_reports")
    receipt["dependencies"].pop("viewer_windows_hash")
    receipt["dependencies"].pop("viewer_reports_hash")
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("windows and reports custody files" in error for error in result.errors)


def test_placeholder_viewer_reports_cannot_clear(tmp_path):
    receipt = _receipt(tmp_path)
    reports_path = Path(receipt["source"]["viewer_reports"])
    reports = json.loads(reports_path.read_text(encoding="utf-8"))
    reports["reports"] = [{"i": row["i"]} for row in reports["reports"]]
    reports_path.write_text(json.dumps(reports), encoding="utf-8")
    receipt["dependencies"]["viewer_reports_hash"] = C.sha256_bytes(reports_path.read_bytes())
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("missing answer fields" in error for error in result.errors)


def test_map_without_script_identity_cannot_clear(tmp_path):
    receipt = _receipt(tmp_path)
    map_data = json.loads(MAP.read_text(encoding="utf-8"))
    map_data.pop("script_hash")
    receipt["map_hash"] = R.map_digest(map_data)
    receipt["dependencies"]["map_hash"] = receipt["map_hash"]
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=map_data, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("narrative map script_hash" in error for error in result.errors)


def test_reviewer_identity_requires_run_provenance(tmp_path):
    receipt = _receipt(tmp_path)
    receipt["reviewers"][0].pop("run_id")
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("run_id" in error for error in result.errors)


def test_independent_roles_require_distinct_runs(tmp_path):
    receipt = _receipt(tmp_path)
    for reviewer in receipt["reviewers"]:
        reviewer["run_id"] = "same-self-asserted-run"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("distinct run_id" in error for error in result.errors)


def test_raw_viewer_answers_are_recomputed_not_trusted_from_markdown(tmp_path):
    receipt = _receipt(tmp_path)
    reports_path = Path(receipt["source"]["viewer_reports"])
    reports = json.loads(reports_path.read_text(encoding="utf-8"))
    for row in reports["reports"]:
        row.update({"new_things": [], "held_question": "", "asked_of_me": "", "could_not_follow": []})
    reports_path.write_text(json.dumps(reports), encoding="utf-8")
    receipt["dependencies"]["viewer_reports_hash"] = C.sha256_bytes(reports_path.read_bytes())
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("deterministic score of raw reports" in error for error in result.errors)


def test_duplicate_viewer_ids_cannot_hide_an_earlier_failure(tmp_path):
    receipt = _receipt(tmp_path)
    viewer = Path(receipt["source"]["viewer_artifact"])
    body = viewer.read_text(encoding="utf-8")
    body = body.replace("```text", "```text\n  [FAIL ] V01 injected earlier failure", 1)
    viewer.write_text(body, encoding="utf-8")
    receipt["dependencies"]["viewer_artifact_hash"] = C.sha256_bytes(viewer.read_bytes())
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("duplicate V-row IDs" in error for error in result.errors)


def test_missing_craft_map_cannot_shrink_the_contract(tmp_path):
    receipt = _receipt(tmp_path)
    missing = tmp_path / "missing-craft.jsonl"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=missing)
    assert not result.ok
    assert any("craft map missing" in error for error in result.errors)


def test_deferred_requires_allowed_later_stage_and_target_stage(tmp_path):
    receipt = _receipt(tmp_path, stage="recording")
    target = next(row for row in receipt["rows"] if row["obligation_id"] == "map:narrative-map")
    target["status"] = "DEFERRED"
    target["deferred_to"] = "prefix-preview"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert result.status == "INCOMPLETE"

    target["deferred_to"] = "diagnostic"
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("later stage" in error for error in result.errors)


def test_stale_spoken_and_tag_only_hashes_are_distinct(tmp_path):
    receipt = _receipt(tmp_path)
    tagged = SCRIPT.read_text(encoding="utf-8").replace("[archetype]", "[rehook]")
    tagged_path = tmp_path / "tagged.txt"
    tagged_path.write_text(tagged, encoding="utf-8")
    result = R.validate_receipt(tagged_path, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("annotated_script_hash" in error for error in result.errors)
    assert C.spoken_hash(tagged) == receipt["spoken_script_hash"]


def test_exact_quote_and_span_are_checked(tmp_path):
    receipt = _receipt(tmp_path)
    row = next(row for row in receipt["rows"] if row["obligation_id"].startswith("declared:"))
    row["quote"] = "A sentence that is not in the script."
    result = R.validate_receipt(SCRIPT, receipt, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert not result.ok
    assert any("exact substring" in error for error in result.errors)


def test_receipt_and_map_markdown_and_path_custody(tmp_path):
    receipt = _receipt(tmp_path)
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    result = R.validate_receipt(SCRIPT, path, narrative_map=MAP, craft_map=_craft(tmp_path))
    assert result.receipt_path == path
    assert "Review rows" in R.render_receipt_markdown(result.receipt or {}, result)
