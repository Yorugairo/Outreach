from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = PROJECT_ROOT / "content" / "bjj-registry" / "validate_corpus.py"


def _record(slug: str = "armbar-from-guard") -> dict:
    return {
        "name": "Armbar from Guard",
        "slug": slug,
        "position": "guard",
        "belt": "white",
        "category": "submission",
        "summary": "A transcript-grounded armbar breakdown.",
        "transcript": (
            "Break posture and control the wrist. "
            "Rotate the hips and keep the elbow aligned."
        ),
        "metadata": {
            "common_errors": ["Releasing the wrist."],
            "key_terms": ["posture", "wrist control"],
        },
        "related": [
            {
                "name": "Triangle Choke",
                "slug": "triangle-choke",
                "position": "guard",
            }
        ],
    }


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _run(corpus: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--corpus",
            str(corpus),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result, json.loads(result.stdout)


def test_valid_record_is_video_ready(tmp_path: Path) -> None:
    _write(tmp_path / "armbar-from-guard.json", _record())

    result, report = _run(tmp_path)

    assert result.returncode == 0
    assert report["valid"] is True
    assert report["summary"] == {
        "files_checked": 1,
        "ready": 1,
        "invalid": 0,
        "error_count": 0,
    }
    assert report["records"][0]["valid"] is True


def test_malformed_json_is_reported(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")

    result, report = _run(tmp_path)

    assert result.returncode == 1
    assert report["summary"]["invalid"] == 1
    assert "malformed or unreadable JSON" in report["records"][0]["errors"][0]


def test_shared_loader_does_not_silently_skip_malformed_json(
    tmp_path: Path,
) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    loader_dir = PROJECT_ROOT / "content" / "bjj-registry" / "src"
    script = (
        "import sys; "
        f"sys.path.insert(0, {str(loader_dir)!r}); "
        "from corpus_loader import load_corpus; "
        f"load_corpus({str(tmp_path)!r})"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "invalid corpus JSON record" in result.stderr


def test_missing_transcript_is_reported(tmp_path: Path) -> None:
    payload = _record()
    del payload["transcript"]
    _write(tmp_path / "armbar-from-guard.json", payload)

    result, report = _run(tmp_path)

    assert result.returncode == 1
    assert any(
        "$: 'transcript' is a required property" in error
        for error in report["records"][0]["errors"]
    )


def test_invalid_slug_and_filename_disagreement_are_reported(tmp_path: Path) -> None:
    _write(tmp_path / "wrong-name.json", _record("Armbar From Guard"))

    result, report = _run(tmp_path)

    assert result.returncode == 1
    errors = report["records"][0]["errors"]
    assert any("$.slug:" in error and "does not match" in error for error in errors)
    assert any("must match the filename stem 'wrong-name'" in error for error in errors)


def test_duplicate_slugs_are_reported_for_every_record(tmp_path: Path) -> None:
    _write(tmp_path / "armbar-from-guard.json", _record())
    _write(tmp_path / "duplicate-file.json", _record())

    result, report = _run(tmp_path)

    assert result.returncode == 1
    assert report["summary"]["files_checked"] == 2
    assert report["summary"]["invalid"] == 2
    assert all(
        any("duplicate corpus slug 'armbar-from-guard'" in error for error in item["errors"])
        for item in report["records"]
    )


def test_self_referencing_related_record_is_rejected(tmp_path: Path) -> None:
    payload = _record()
    payload["related"] = [
        {"name": "Armbar from Guard", "slug": "armbar-from-guard"}
    ]
    _write(tmp_path / "armbar-from-guard.json", payload)

    result, report = _run(tmp_path)

    assert result.returncode == 1
    assert any(
        "$.related[0].slug: cannot reference itself" == error
        for error in report["records"][0]["errors"]
    )


def test_batch_report_counts_ready_and_invalid_records(tmp_path: Path) -> None:
    _write(tmp_path / "armbar-from-guard.json", _record())
    invalid = _record("triangle-choke")
    invalid["metadata"]["key_terms"] = ["guard", 3]
    _write(tmp_path / "triangle-choke.json", invalid)

    result, report = _run(tmp_path)

    assert result.returncode == 1
    assert report["summary"]["files_checked"] == 2
    assert report["summary"]["ready"] == 1
    assert report["summary"]["invalid"] == 1
    assert any(
        "$.metadata.key_terms[1]" in error
        for error in report["records"][1]["errors"]
    )


def test_technique_generator_fails_closed_on_invalid_corpus(tmp_path: Path) -> None:
    invalid = _record()
    del invalid["summary"]
    corpus = tmp_path / "corpus"
    _write(corpus / "armbar-from-guard.json", invalid)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "content" / "bjj-registry" / "src" / "generate.py"),
            "--axis",
            "technique",
            "--corpus",
            str(corpus),
            "--out",
            str(tmp_path / "output"),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "technique corpus is not production-ready" in result.stderr
    assert "'summary' is a required property" in result.stderr


def test_invalid_schema_override_returns_a_report_instead_of_traceback(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "armbar-from-guard.json", _record())
    invalid_schema = tmp_path / "invalid-schema.json"
    _write(invalid_schema, {"type": "not-a-json-schema-type"})

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--corpus",
            str(tmp_path),
            "--schema",
            str(invalid_schema),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert report["valid"] is False
    assert "validator setup failed" in report["errors"][0]
