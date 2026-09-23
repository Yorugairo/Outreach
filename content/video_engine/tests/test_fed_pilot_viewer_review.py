"""Focused tests for the current, episode-local pilot viewer-recall exception."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
sys.path.insert(0, str(ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVIEW = _load("fed_liquidity_pilot_viewer_review_test", EPISODE / "pilot_viewer_review.py")
BUILDER = _load("fed_liquidity_builder_viewer_review_test", EPISODE / "build_fed_liquidity.py")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_raw(root: Path) -> None:
    for name in (
        REVIEW.SCRIPT_NAME,
        REVIEW.VIEWER_NAME,
        REVIEW.HISTORICAL_VIEWER_NAME,
        REVIEW.WINDOWS_NAME,
        REVIEW.REPORTS_NAME,
    ):
        shutil.copyfile(EPISODE / name, root / name)


def _artifact(root: Path) -> None:
    gates, scorer, _ = REVIEW._load_tools()
    script = root / REVIEW.SCRIPT_NAME
    viewer = root / REVIEW.VIEWER_NAME
    windows = root / REVIEW.WINDOWS_NAME
    reports = root / REVIEW.REPORTS_NAME
    script_text = script.read_text(encoding="utf-8")
    windows_doc = json.loads(windows.read_text(encoding="utf-8"))
    reports_doc = json.loads(reports.read_text(encoding="utf-8"))
    score = scorer.score(windows_doc, reports_doc, script_text)
    missed = {(row["tag"], row["window"]): row for row in score["recall"] if not row["perceived"]}
    expected_pairs = {(tag, window) for _, tag, window in REVIEW.EXPECTED_MISSES}
    assert set(missed) == expected_pairs
    reader_by_window = {
        1: "Replacing a 2% loan with a 7% loan would more than triple the interest cost.",
        2: "The higher interest cost leaves less money for wages, materials, and hiring.",
    }
    payload = {
        "schema": REVIEW.SCHEMA,
        "episode_id": REVIEW.EPISODE_ID,
        "accepted_for": "pilot_only",
        "script_hash": gates.script_hash(script_text),
        "artifacts": {
            "viewer": {"path": REVIEW.VIEWER_NAME, "sha256": _digest(viewer)},
            "windows": {"path": REVIEW.WINDOWS_NAME, "sha256": _digest(windows)},
            "reports": {"path": REVIEW.REPORTS_NAME, "sha256": _digest(reports)},
        },
        "operator_authorization": {
            "quote": "YES — synthetic test authorization only; not operator approval.",
            "reference": "tests/test_fed_pilot_viewer_review.py::_artifact",
        },
        "misses": [
            {
                "tag": tag,
                "window": window,
                "script_quote": missed[(tag, window)]["sentence"],
                "reader_quote": reader_by_window[window],
                "rationale": "Bounded manual evidence; raw FAIL and full-episode gates remain required.",
                "verdict": "MANUALLY_REVIEWED",
            }
            for _, tag, window in REVIEW.EXPECTED_MISSES
        ],
    }
    review_path = root / REVIEW.REVIEW_PATH
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _fixture(tmp_path: Path, *, artifact: bool = True) -> Path:
    root = tmp_path / "episode"
    root.mkdir()
    _copy_raw(root)
    if artifact:
        _artifact(root)
    return root


def test_current_two_misses_accept_only_with_synthetic_pilot_approval(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    result = REVIEW.validate(root)
    assert result.ok, result.errors
    assert result.score["rows"][0]["id"] == "V01"
    missed = [(row["tag"], row["window"]) for row in result.score["recall"] if not row["perceived"]]
    assert missed == [("archetype", 1), ("ring", 2)]


def test_current_recheck_requires_operator_sidecar() -> None:
    result = REVIEW.validate(EPISODE)
    assert not result.ok
    assert result.score is not None
    missed = [(row["tag"], row["window"]) for row in result.score["recall"] if not row["perceived"]]
    assert missed == [("archetype", 1), ("ring", 2)]
    assert not any(error.startswith("viewer markdown:") for error in result.errors)
    assert any("missing (review/PILOT-VIEWER-REVIEW.json)" in error for error in result.errors)
    historical = (EPISODE / REVIEW.HISTORICAL_VIEWER_NAME).read_text(encoding="utf-8")
    recheck = (EPISODE / REVIEW.VIEWER_NAME).read_text(encoding="utf-8")
    assert "60/63 declared beats perceived" in historical
    assert "61/63 declared beats perceived" in recheck
    assert "DIAGNOSTIC ONLY" in recheck


def test_missing_sidecar_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path, artifact=False)
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("missing" in error for error in result.errors)


def test_stale_nested_artifact_hash_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifacts"]["viewer"]["sha256"] = "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("artifacts.viewer.sha256 is stale" in error for error in result.errors)


def test_historical_viewer_sidecar_path_and_hash_are_rejected(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifacts"]["viewer"]["sha256"] = _digest(root / REVIEW.HISTORICAL_VIEWER_NAME)
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("artifacts.viewer.sha256 is stale" in error for error in result.errors)

    payload["artifacts"]["viewer"]["path"] = REVIEW.HISTORICAL_VIEWER_NAME
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("artifacts.viewer.path must be" in error for error in result.errors)


def test_new_viewer_failure_is_not_covered_by_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    viewer = root / REVIEW.VIEWER_NAME
    viewer.write_text(
        viewer.read_text(encoding="utf-8").replace("[PASS ] V02", "[FAIL ] V02", 1),
        encoding="utf-8",
    )
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifacts"]["viewer"]["sha256"] = _digest(viewer)
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("only V01 may remain FAIL" in error for error in result.errors)


def test_empty_manual_evidence_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["misses"][0]["reader_quote"] = ""
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("reader_quote must be non-empty" in error for error in result.errors)


def test_malformed_report_index_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    reports = root / REVIEW.REPORTS_NAME
    report_doc = json.loads(reports.read_text(encoding="utf-8"))
    report_doc["reports"][0]["i"] = "zero"
    reports.write_text(json.dumps(report_doc), encoding="utf-8")
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifacts"]["reports"]["sha256"] = _digest(reports)
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("report indices must be integers" in error for error in result.errors)


def test_duplicate_result_line_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    viewer = root / REVIEW.VIEWER_NAME
    raw = viewer.read_text(encoding="utf-8")
    viewer.write_text(raw + "\nRESULT: 1 FAIL / 0 WARN / 2 PASS / 2 INFO\n", encoding="utf-8")
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifacts"]["viewer"]["sha256"] = _digest(viewer)
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("RESULT row is missing or malformed" in error for error in result.errors)


def test_episode_segment_cannot_consume_valid_pilot_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    script_hash = REVIEW._load_tools()[0].script_hash((root / REVIEW.SCRIPT_NAME).read_text(encoding="utf-8"))
    (root / "SCRIPT-GATES.md").write_text(
        f"script_hash: {script_hash}\nVERDICT: PASS\n", encoding="utf-8"
    )
    preflight = BUILDER.PreflightResult(segment="episode")
    BUILDER._validate_script_and_reports(root, preflight, "episode")
    assert "script viewer: report contains FAIL" in preflight.blockers
    assert "viewer_gate_exception" not in preflight.facts


def test_pilot_segment_consumes_only_valid_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    script_hash = REVIEW._load_tools()[0].script_hash((root / REVIEW.SCRIPT_NAME).read_text(encoding="utf-8"))
    (root / "SCRIPT-GATES.md").write_text(
        f"script_hash: {script_hash}\nVERDICT: PASS\n", encoding="utf-8"
    )
    preflight = BUILDER.PreflightResult(segment="pilot")
    BUILDER._validate_script_and_reports(root, preflight, "pilot")
    assert "script viewer: report contains FAIL" not in preflight.blockers
    assert preflight.facts["viewer_gate_exception"].endswith("accepted_for=pilot_only")


def test_minute_segment_consumes_the_same_hash_bound_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    script_hash = REVIEW._load_tools()[0].script_hash((root / REVIEW.SCRIPT_NAME).read_text(encoding="utf-8"))
    (root / "SCRIPT-GATES.md").write_text(
        f"script_hash: {script_hash}\nVERDICT: PASS\n", encoding="utf-8"
    )
    preflight = BUILDER.PreflightResult(segment="minute")
    BUILDER._validate_script_and_reports(root, preflight, "minute")
    assert "script viewer: report contains FAIL" not in preflight.blockers
    assert preflight.facts["viewer_gate_exception"].endswith("accepted_for=pilot_only")
