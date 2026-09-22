"""Recording clearance refuses incomplete/stale review before provider work."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures/script_review"
sys.path.insert(0, str(SCRIPTS))

import record_master_take as RM  # noqa: E402
import run_script_gates as RG  # noqa: E402
import script_review as R  # noqa: E402
import script_review_contract as C  # noqa: E402
import viewer_score as VS  # noqa: E402
import viewer_windows as VW  # noqa: E402


def recording_package(tmp_path: Path) -> tuple[Path, ...]:
    script = tmp_path / "TEST-VO.txt"
    script.write_text((FIXTURES / "v14-opening-vo.txt").read_text(encoding="utf-8"), encoding="utf-8")
    narrative_map = tmp_path / "map.json"
    narrative_map.write_bytes((FIXTURES / "sustained-tension-map.json").read_bytes())
    spoken = C.canonical_spoken(script.read_text(encoding="utf-8"))
    words = []
    tokens = spoken.split()
    step = 240.0 / len(tokens)
    for index, word in enumerate(tokens):
        words.append({"w": word, "start_s": index * step,
                      "end_s": 240.0 if index == len(tokens) - 1 else (index + 1) * step})
    timeline = tmp_path / "words.json"
    timeline.write_text(json.dumps({"words": words}), encoding="utf-8")
    scratch = tmp_path / "scratch.mp3"
    scratch.write_bytes(b"offline-scratch-fixture")
    viewer_windows = tmp_path / "TEST-VIEWER-WINDOWS.json"
    VW.write_windows(VW.build_document(script, script.read_text(encoding="utf-8"), timeline,
                                        no_screens=True, require_measured=True), viewer_windows)
    viewer_windows_hash = C.sha256_bytes(viewer_windows.read_bytes())
    windows_doc = json.loads(viewer_windows.read_text(encoding="utf-8"))
    viewer_reports = tmp_path / "TEST-VIEWER-REPORTS.json"
    viewer_reports.write_text(json.dumps({
        "schema_version": "viewer_reports.v1",
        "script_hash": C.spoken_hash(script.read_text(encoding="utf-8")),
        "annotated_script_hash": C.annotated_hash(script.read_text(encoding="utf-8")),
        "timeline_hash": windows_doc["timeline_hash"], "windows_hash": viewer_windows_hash,
        "expected_windows": len(windows_doc["windows"]),
        "reports": [{"i": window["i"], "new_things": [window["text"]],
                     "held_question": "fixture question", "asked_of_me": "fixture ask",
                     "could_not_follow": []} for window in windows_doc["windows"]],
    }), encoding="utf-8")
    reports_doc = json.loads(viewer_reports.read_text(encoding="utf-8"))
    viewer_score = VS.score(windows_doc, reports_doc, script.read_text(encoding="utf-8"))
    viewer_score.update({"script_hash": C.spoken_hash(script.read_text(encoding="utf-8")),
                         "annotated_script_hash": C.annotated_hash(script.read_text(encoding="utf-8")),
                         "windows_hash": viewer_windows_hash})
    viewer_statuses = {f"viewer:{row['id']}": row["level"] for row in viewer_score["rows"]}
    viewer = tmp_path / "viewer.md"
    viewer.write_text(VS.render(viewer_score, script.name), encoding="utf-8")
    screens = tmp_path / "TEST-SCREENS.md"
    screens.write_text("# STRENGTH SCREENS\n", encoding="utf-8")

    map_data = json.loads(narrative_map.read_text(encoding="utf-8"))
    rows = C.obligations(script.read_text(encoding="utf-8"), "long", screens=screens)
    dependencies = {
        "annotated_script_hash": C.annotated_hash(script.read_text(encoding="utf-8")),
        "spoken_script_hash": C.spoken_hash(script.read_text(encoding="utf-8")),
        "map_hash": R.map_digest(map_data),
        "contract_digest": C.contract_digest(rows),
        "timeline_hash": C.sha256_bytes(timeline.read_bytes()),
        "normalized_timeline_hash": R.word_clock_digest(R.normalize_word_clock(timeline)),
        "scratch_take_hash": C.sha256_bytes(scratch.read_bytes()),
        "viewer_artifact_hash": C.sha256_bytes(viewer.read_bytes()),
        "viewer_windows_hash": viewer_windows_hash,
        "viewer_reports_hash": C.sha256_bytes(viewer_reports.read_bytes()),
        "screens_hash": C.sha256_bytes(screens.read_bytes()),
    }
    receipt = {
        "schema": "script_review.v1", **{key: dependencies[key] for key in (
            "annotated_script_hash", "spoken_script_hash", "map_hash", "contract_digest")},
        "form": "long", "stage": "recording", "timing_source": "measured",
        "scope": {"kind": "full", "start_s": 0, "end_s": words[-1]["end_s"]},
        "reviewers": [{"id": "judge", "role": "semantic-reviewer", "run_id": "judge-run"},
                      {"id": "viewer", "role": "blind-viewer", "run_id": "viewer-run"},
                      {"id": "independent", "role": "independent-reviewer", "run_id": "independent-run"}],
        "source": {"viewer_artifact": str(viewer), "viewer_windows": str(viewer_windows),
                   "viewer_reports": str(viewer_reports), "screens": str(screens)},
        "dependencies": dependencies, "rows": [],
    }
    for index, obligation in enumerate(C.due_by(rows, "recording")):
        row = {"obligation_id": obligation.id, "status": viewer_statuses.get(obligation.id, "PASS"),
               "rationale": f"{obligation.id}: offline source-bound regression fixture ({index}).",
               "evidence": {"finding_id": obligation.id, "source": "fixture"}}
        if obligation.owner in {"judge", "blind-viewer", "independent-reviewer"} or obligation.id.startswith(("declared:", "map:")):
            start = (index * 11) % max(1, len(spoken) - 120)
            end = min(len(spoken), start + 120)
            row.update({"quote": spoken[start:end], "span": {"start": start, "end": end},
                        "reviewer": {"judge": "judge", "blind-viewer": "viewer",
                                     "independent-reviewer": "independent"}.get(obligation.owner, "judge")})
        receipt["rows"].append(row)
    receipt_path = tmp_path / "review.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    return script, receipt_path, narrative_map, timeline, scratch, viewer, viewer_windows, viewer_reports, screens


def write_clear_report(script: Path, receipt: Path, narrative_map: Path,
                       timeline: Path, scratch: Path, viewer: Path, viewer_windows: Path,
                       viewer_reports: Path, screens: Path) -> None:
    review = RG.review_result(script, receipt, narrative_map, "recording", "long",
                              timeline=timeline, scratch_take=scratch, viewer_artifact=viewer,
                              screens=screens, viewer_windows=viewer_windows, viewer_reports=viewer_reports)
    assert review and review.ok, review.errors if review else "missing review"
    tools = [RG.ToolResult("x", 0, "", {"fail": 0}, "x")] * 4
    RG.write_report(script, tools, form="long", stage="recording", review=review,
                    receipt=receipt, narrative_map=narrative_map, timeline=timeline,
                    scratch_take=scratch, viewer_artifact=viewer, viewer_windows=viewer_windows,
                    viewer_reports=viewer_reports, screens=screens)


def test_complete_recording_receipt_clears_and_changed_clock_invalidates(tmp_path):
    package = recording_package(tmp_path)
    write_clear_report(*package)
    script, _receipt, _map, timeline, _scratch, _viewer, _windows, _reports, _screens = package
    assert RG.check_report(script) == ("ok", str(RG.report_path(script)))
    timeline.write_text(timeline.read_text(encoding="utf-8").replace('"end_s":', '"end_s": 0.001, "old_end_s":', 1), encoding="utf-8")
    assert RG.check_report(script)[0] == "incomplete"


def test_free_text_force_cannot_override_mechanical_failure(tmp_path, capsys):
    package = recording_package(tmp_path)
    (script, receipt, narrative_map, timeline, scratch, viewer,
     viewer_windows, viewer_reports, screens) = package
    review = RG.review_result(script, receipt, narrative_map, "recording", "long",
                              timeline=timeline, scratch_take=scratch, viewer_artifact=viewer,
                              screens=screens, viewer_windows=viewer_windows, viewer_reports=viewer_reports)
    assert review and review.ok, review.errors if review else "missing review"
    tools = [RG.ToolResult("broken", 1, "", {"fail": 1}, "broken")] + [
        RG.ToolResult("ok", 0, "", {"fail": 0}, "ok") for _ in range(3)]
    RG.write_report(script, tools, form="long", stage="recording", review=review,
                    receipt=receipt, narrative_map=narrative_map, timeline=timeline,
                    scratch_take=scratch, viewer_artifact=viewer, viewer_windows=viewer_windows,
                    viewer_reports=viewer_reports, screens=screens)
    failures: list[str] = []
    assert RG.recording_preflight(script, ["--force", "agent-authored reason"], failures) is None
    assert failures
    assert "cannot authorize recording" in capsys.readouterr().out


def test_force_cannot_bypass_missing_receipt_before_provider_lookup(tmp_path, monkeypatch):
    script = tmp_path / "MISSING-VO.txt"
    script.write_text("A complete spoken idea.", encoding="utf-8")
    env = tmp_path / "local.env"
    env.write_text("ELEVENLABS_API_KEY=test\nELEVENLABS_VOICE_ID=test\n", encoding="utf-8")
    provider_touched = {"value": False}

    def provider_probe(_key):
        provider_touched["value"] = True
        return (0, 1000)

    monkeypatch.setattr(RM, "VO_TEXT", script)
    monkeypatch.setattr(RM, "ENV_FILE", env)
    monkeypatch.setattr(RM, "credits_remaining", provider_probe)
    monkeypatch.setattr(sys, "argv", ["record_master_take.py", "--go", "--force", "diagnostic"])
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)
    assert RM.main() == 1
    assert not provider_touched["value"]
