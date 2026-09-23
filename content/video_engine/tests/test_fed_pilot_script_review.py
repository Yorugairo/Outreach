"""Focused tests for the episode-local pilot script-gate exception."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVIEW = _load("fed_liquidity_pilot_script_review_test", EPISODE / "pilot_script_review.py")
BUILDER = _load("fed_liquidity_builder_script_review_test", EPISODE / "build_fed_liquidity.py")
GATES = _load("fed_run_script_gates_pilot_script_review_test", ROOT / "content/video_engine/scripts/run_script_gates.py")


def _write(path: Path, value: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value, encoding="utf-8", newline="")
    return path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _script_hash(path: Path) -> str:
    return GATES.script_hash(path.read_text(encoding="utf-8"))


def _script(root: Path) -> Path:
    return _write(
        root / "SCRIPT-VO.txt",
        "Your machine still works. Banks avoid that cash drain because another account shrinks instead.\n",
    )


def _opening_review(root: Path, script: Path) -> Path:
    script_hash = _script_hash(script)
    return _write(
        root / "SCRIPT-OPENING-REVIEW.json",
        json.dumps(
            {
                "schema": "opening_review.v1",
                "script_hash": script_hash,
                "review_kind": "estimated_draft",
                "rows": [
                    {
                        "id": "J13",
                        "verdict": "PASS",
                        "quote": "Your machine still works.",
                        "rationale": "A concrete human consequence is stated.",
                        "clock": 10.0,
                        "clock_basis": "estimated",
                    },
                    {
                        "id": "J14",
                        "verdict": "PASS",
                        "quote": "Banks avoid that cash drain because another account shrinks instead.",
                        "rationale": "The viewer receives a testable accounting promise.",
                        "clock": 20.0,
                        "clock_basis": "estimated",
                    },
                ],
            },
            indent=2,
        ),
    )


def _gate_report(root: Path, script: Path, *, crlf: bool = False, extra_failure: bool = False, dual_verdict: bool = False) -> Path:
    script_hash = _script_hash(script)
    opening_id = "G31" if extra_failure else "G15b"
    text = f"""script_hash: {script_hash}
timing_source: estimated
opening_review: SCRIPT-OPENING-REVIEW.json

## lint_script_pattern.py
FAIL RING: no opening token recurs in the close
RESULT: 1 failure(s)

## audit_script_doctrine.py
  [FAIL] doc 35 rule 2: no falsifiable tell — an answer video must name one variable
RESULT: 1 FAIL, 0 WARN

## gate_opening_structure.py
  [FAIL ] {opening_id} one opening pattern is not satisfied
  [FAIL ] G21 1 [loop] in P2
  [FAIL ] G27 'machine' 0x in P2
RESULT: 3 FAIL / 0 WARN / 0 PASS / 0 JUDGE

## enumerate_strength_screens.py
SCRIPT-SCREENS.md: X1=1 deixis=1 junctions=1 anchors=1 declared=1

VERDICT: FAIL (3 failing tools)
"""
    if dual_verdict:
        text += "VERDICT: PASS\n"
    if crlf:
        text = text.replace("\n", "\r\n")
        return _write(root / "SCRIPT-GATES.md", text.encode("utf-8"))
    return _write(root / "SCRIPT-GATES.md", text)


def _review_artifact(root: Path, script: Path, gates: Path, opening: Path) -> Path:
    script_hash = _script_hash(script)
    return _write(
        root / REVIEW.REVIEW_PATH,
        json.dumps(
            {
                "schema": REVIEW.SCHEMA,
                "episode_id": REVIEW.EPISODE_ID,
                "accepted_for": "pilot_only",
                "script_hash": script_hash,
                "script_gates_sha256": _digest(gates),
                "operator_authorization": {
                    "quote": "YES — preserve the approved prose for this pilot-only manual review.",
                    "reference": "operator question and reply recorded in the production ledger",
                },
                "opening_review": {
                    "path": "SCRIPT-OPENING-REVIEW.json",
                    "sha256": _digest(opening),
                },
                "failures": [
                    {
                        "id": row_id,
                        "report": REVIEW.FAILURE_REPORTS[row_id],
                        "verdict": "MANUALLY_REVIEWED" if row_id.endswith(("G21", "G27")) else "DEFERRED_TO_FULL_EPISODE",
                        "quote": "Your machine still works.",
                        "rationale": "Parent-authored bounded evidence; timing, captions, visual and source gates remain mandatory.",
                    }
                    for row_id in REVIEW.FAILURE_IDS
                ],
            },
            indent=2,
        ),
    )


def _fixture(tmp_path: Path, *, artifact: bool = True, crlf: bool = False) -> Path:
    root = tmp_path / "episode"
    script = _script(root)
    opening = _opening_review(root, script)
    gates = _gate_report(root, script, crlf=crlf)
    if artifact:
        _review_artifact(root, script, gates, opening)
    return root


def test_known_failure_set_and_operator_sidecar_accept_for_pilot(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    result = REVIEW.validate(root)
    assert result.ok, result.errors
    assert result.failure_ids == REVIEW.FAILURE_IDS

    preflight = BUILDER.PreflightResult(segment="pilot")
    BUILDER._validate_script_and_reports(root, preflight, "pilot")
    assert not any("report contains FAIL" in blocker for blocker in preflight.blockers)
    assert preflight.facts["script_gate_exception"].endswith("accepted_for=pilot_only")


def test_minute_segment_consumes_the_same_hash_bound_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    preflight = BUILDER.PreflightResult(segment="minute")
    BUILDER._validate_script_and_reports(root, preflight, "minute")
    assert not any("report contains FAIL" in blocker for blocker in preflight.blockers)
    assert preflight.facts["script_gate_exception"].endswith("accepted_for=pilot_only")


def test_missing_sidecar_keeps_raw_gate_fail_blocking(tmp_path: Path) -> None:
    root = _fixture(tmp_path, artifact=False)
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("pilot script review: missing" in error for error in result.errors)

    preflight = BUILDER.PreflightResult(segment="pilot")
    BUILDER._validate_script_and_reports(root, preflight, "pilot")
    assert "script gates: report contains FAIL" in preflight.blockers


def test_stale_sidecar_hash_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["script_hash"] = "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("script_hash is stale" in error for error in result.errors)


def test_unknown_new_failure_row_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    script = root / "SCRIPT-VO.txt"
    _gate_report(root, script, extra_failure=True)
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("unknown failure row" in error for error in result.errors)


def test_episode_segment_cannot_consume_valid_pilot_exception(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    preflight = BUILDER.PreflightResult(segment="episode")
    BUILDER._validate_script_and_reports(root, preflight, "episode")
    assert "script gates: exactly one explicit PASS verdict is required" in preflight.blockers
    assert "script gates: report contains FAIL" in preflight.blockers
    assert "script_gate_exception" not in preflight.facts


def test_empty_review_and_dual_verdict_fail_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / REVIEW.REVIEW_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["operator_authorization"]["quote"] = ""
    payload["failures"][0]["quote"] = ""
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert not REVIEW.validate(root).ok

    root = _fixture(tmp_path / "dual")
    script = root / "SCRIPT-VO.txt"
    gates = _gate_report(root, script, dual_verdict=True)
    _review_artifact(root, script, gates, root / "SCRIPT-OPENING-REVIEW.json")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("exactly one VERDICT: FAIL" in error for error in result.errors)


def test_raw_gate_digest_is_bytes_bound_across_crlf(tmp_path: Path) -> None:
    root = _fixture(tmp_path, crlf=True)
    result = REVIEW.validate(root)
    assert result.ok, result.errors
    assert result.script_gates_sha256 == _digest(root / "SCRIPT-GATES.md")


def test_unrecognized_opening_failure_cannot_hide_behind_known_counts(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    gates = root / "SCRIPT-GATES.md"
    raw = gates.read_text(encoding="utf-8")
    raw = raw.replace("## gate_opening_structure.py", "## gate_opening_structure.py\n[FAIL ] J99 unexpected new failure", 1)
    gates.write_text(raw, encoding="utf-8")
    _review_artifact(root, root / "SCRIPT-VO.txt", gates, root / "SCRIPT-OPENING-REVIEW.json")
    result = REVIEW.validate(root)
    assert not result.ok
    assert any("unknown failure row" in error for error in result.errors)
