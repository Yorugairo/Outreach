"""Focused contract tests for explicit J13/J14 opening-review evidence."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import opening_review as O  # noqa: E402
import run_script_gates as RG  # noqa: E402


SCRIPT_TEXT = (
    "[stakes] A workshop owner faces a higher renewal bill. `[post-key]` "
    "[promise] By the end you will run one check against the funding price."
)
J13_QUOTE = "A workshop owner faces a higher renewal bill."
J14_QUOTE = "By the end you will run one check against the funding price."


def _script(tmp_path: Path) -> Path:
    path = tmp_path / "SCRIPT-OPENING-VO.txt"
    path.write_text(SCRIPT_TEXT, encoding="utf-8")
    return path


def _payload(*, kind: str = "estimated_draft", basis: str | None = None) -> dict:
    basis = basis or ("estimated" if kind == "estimated_draft" else "actual")
    return {
        "schema": O.SCHEMA,
        "script_hash": RG.script_hash(SCRIPT_TEXT),
        "review_kind": kind,
        "rows": [
            {
                "id": "J13",
                "verdict": "PASS",
                "quote": J13_QUOTE,
                "rationale": "ok",
                "clock": 24.0,
                "clock_basis": basis,
            },
            {
                "id": "J14",
                "verdict": "PASS",
                "quote": J14_QUOTE,
                "rationale": "ok",
                "clock": 40.0,
                "clock_basis": basis,
            },
        ],
    }


def _write_review(path: Path, payload: object, *, allow_nan: bool = False) -> None:
    path.write_text(json.dumps(payload, allow_nan=allow_nan), encoding="utf-8")


def test_missing_sidecar_is_not_ready(tmp_path):
    result = O.validate_opening_review(_script(tmp_path), tmp_path / "missing.json")
    assert not result.ok
    assert result.status == "invalid"
    assert any("missing" in error for error in result.errors)


def test_stale_hash_is_rejected(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    payload["script_hash"] = "0" * 64
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("stale" in error for error in result.errors)


@pytest.mark.parametrize("verdict", ["FAIL", "WARN"])
def test_only_explicit_pass_rows_are_accepted(tmp_path, verdict):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][0]["verdict"] = verdict
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("explicit 'PASS'" in error for error in result.errors)


def test_malformed_shape_and_extra_fields_are_rejected(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    payload.pop("schema")
    payload["rows"][0]["unexpected"] = True
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("top-level" in error for error in result.errors)
    assert any("unexpected field" in error for error in result.errors)


def test_quote_must_be_an_exact_substring_of_current_spoken_script(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][0]["quote"] = "The tag itself is not spoken."
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("exact substring" in error for error in result.errors)


@pytest.mark.parametrize(
    ("row_index", "clock"),
    [(0, 30.01), (1, 45.01)],
)
def test_judge_deadlines_are_hard(tmp_path, row_index, clock):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][row_index]["clock"] = clock
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any(payload["rows"][row_index]["id"] in error and "clock" in error for error in result.errors)


@pytest.mark.parametrize("clock", [True, False])
def test_boolean_clocks_are_not_numbers(tmp_path, clock):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][0]["clock"] = clock
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("not a boolean" in error for error in result.errors)


@pytest.mark.parametrize("clock", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_clocks_are_rejected(tmp_path, clock):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][0]["clock"] = clock
    review = tmp_path / "review.json"
    _write_review(review, payload, allow_nan=True)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("finite" in error for error in result.errors)


def test_duplicate_judge_rows_are_rejected(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][1] = copy.deepcopy(payload["rows"][0])
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("duplicate" in error for error in result.errors)
    assert any("missing review row" in error for error in result.errors)


def test_valid_explicit_estimated_review_is_draft_only(tmp_path):
    script = _script(tmp_path)
    review = tmp_path / "review.json"
    _write_review(review, _payload())
    result = O.validate_opening_review(script, review)
    assert result.ok, result.errors
    assert result.status == "estimated_draft_ready"
    assert result.estimated_draft_ready
    assert not result.recording_ready


def test_valid_shape_measured_review_stays_unavailable_without_clock_binding(tmp_path):
    script = _script(tmp_path)
    review = tmp_path / "review.json"
    _write_review(review, _payload(kind="measured_recording", basis="actual"))
    result = O.validate_opening_review(script, review)
    # An actual-string assertion is not a retained, hash-bound word timeline.
    # The bounded foundation therefore refuses to claim recording readiness.
    assert not result.ok
    assert result.status == "measured_recording_unavailable"
    assert not result.measured_recording_ready
    assert not result.recording_ready
    assert any("hash-bound" in error for error in result.errors)


def test_estimated_kind_cannot_claim_actual_clocks(tmp_path):
    script = _script(tmp_path)
    payload = _payload(kind="estimated_draft", basis="actual")
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("clock_basis" in error for error in result.errors)


def test_j14_before_30_is_allowed_and_g09_owns_early_warning(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    payload["rows"][1]["clock"] = 20.0
    review = tmp_path / "review.json"
    _write_review(review, payload)
    result = O.validate_opening_review(script, review)
    assert result.ok, result.errors
    assert result.estimated_draft_ready


def test_duplicate_json_object_keys_are_rejected(tmp_path):
    script = _script(tmp_path)
    review = tmp_path / "review.json"
    review.write_text(
        '{"schema":"opening_review.v1","script_hash":"%s","script_hash":"%s",'
        '"review_kind":"estimated_draft","rows":[]}'
        % (RG.script_hash(SCRIPT_TEXT), RG.script_hash(SCRIPT_TEXT)),
        encoding="utf-8",
    )
    result = O.validate_opening_review(script, review)
    assert not result.ok
    assert any("duplicate JSON object key" in error for error in result.errors)


def test_hash_and_quote_use_canonical_spoken_text_not_delivery_tags(tmp_path):
    script = _script(tmp_path)
    payload = _payload()
    review = tmp_path / "review.json"
    _write_review(review, payload)
    # Changing a delivery tag changes no spoken words, so the canonical hash
    # and explicit spoken quotes remain valid.
    script.write_text(SCRIPT_TEXT.replace("[stakes]", "[archetype]"), encoding="utf-8")
    result = O.validate_opening_review(script, review)
    assert result.ok, result.errors
