from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.martial_editorial_adapter import (
    MartialEditorialAdapterError,
    _artifact_hash,
    _validate_source_contracts,
    compile_martial_editorial,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EPISODE_ROOT = (
    PROJECT_ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "martial-matters"
    / "pilots"
    / "marshall-monday-001"
)
EDIT_PACKAGE = EPISODE_ROOT / "edit" / "revisions" / "r1" / "marshall-monday-001-edit-package.v1.json"
CUE_SHEET = EPISODE_ROOT / "continuity" / "revisions" / "r1" / "word-timed-visual-cues-r1.v1.json"
AUDIO_MANIFEST = EPISODE_ROOT / "audio" / "revisions" / "r1" / "marshall-monday-001-canonical-audio-r1.v1.json"
WORD_TIMINGS = EPISODE_ROOT / "audio" / "revisions" / "r1" / "marshall-monday-001-master-r1.words.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _authorization(package: dict, cues: dict, audio: dict) -> dict:
    core = {
        "schema_version": "editorial_review_authorization.v1",
        "authorization_id": "marshall-monday-001-r1-internal-review",
        "episode_id": package["episode_id"],
        "scope": "internal_revision_render_only",
        "reviewer": "operator-fixture",
        "reviewed_at": "2026-08-07T00:00:00Z",
        "reason": "Test exact immutable r1 authorization.",
        "base_edit_package_hash": package["artifact_hash"],
        "canonical_audio_manifest_hash": audio["artifact_hash"],
        "canonical_audio_hash": audio["audio_sha256"],
        "word_timing_sha256": _sha256(WORD_TIMINGS),
        "cue_sheet_hash": cues["artifact_hash"],
        "selected_assets": [
            {
                "cue_id": entry["cue_id"],
                "candidate_path": entry["candidate"]["candidate_path"],
                "sha256": entry["candidate"]["sha256"],
            }
            for entry in package["timeline"]
        ],
        "publication_authorized": False,
        "catalog_promotion_authorized": False,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def test_real_r1_contract_resolves_exact_192_hash_bound_cues() -> None:
    package = _load(EDIT_PACKAGE)
    cues = _load(CUE_SHEET)
    audio = _load(AUDIO_MANIFEST)
    words = _load(WORD_TIMINGS)
    authorization = _authorization(package, cues, audio)

    normalized, sources = _validate_source_contracts(
        package=package,
        cues_payload=cues,
        audio=audio,
        words_payload=words,
        authorization=authorization,
        package_hash=_artifact_hash(package, "edit package"),
        cue_hash=_artifact_hash(cues, "cue sheet"),
        audio_manifest_hash=_artifact_hash(audio, "audio manifest"),
        word_sha=_sha256(WORD_TIMINGS),
        episode_root=EPISODE_ROOT,
        project_root=PROJECT_ROOT,
    )

    assert len(normalized) == len(sources) == 192
    assert normalized[0]["start_word_index"] == 0
    assert normalized[0]["timeline_start_s"] == 0.0
    assert normalized[-1]["end_word_index"] == 1527
    assert normalized[-1]["timeline_end_s"] == 567.804
    assert all(source.is_file() for source in sources)
    assert all(
        block["micro_events"]
        for block in normalized
        if block["duration_s"] > 3.35
    )


def test_real_r1_contract_rejects_rehashed_authorization_with_changed_plate() -> None:
    package = _load(EDIT_PACKAGE)
    cues = _load(CUE_SHEET)
    audio = _load(AUDIO_MANIFEST)
    words = _load(WORD_TIMINGS)
    authorization = _authorization(package, cues, audio)
    core = {key: value for key, value in authorization.items() if key != "artifact_hash"}
    core["selected_assets"][0]["sha256"] = "0" * 64
    authorization = {**core, "artifact_hash": canonical_sha256(core)}

    with pytest.raises(MartialEditorialAdapterError, match="candidate hash differs"):
        _validate_source_contracts(
            package=package,
            cues_payload=cues,
            audio=audio,
            words_payload=words,
            authorization=authorization,
            package_hash=package["artifact_hash"],
            cue_hash=cues["artifact_hash"],
            audio_manifest_hash=audio["artifact_hash"],
            word_sha=_sha256(WORD_TIMINGS),
            episode_root=EPISODE_ROOT,
            project_root=PROJECT_ROOT,
        )


def test_adapter_fails_before_compilation_without_authorization(tmp_path: Path) -> None:
    with pytest.raises(MartialEditorialAdapterError, match="authorization is required"):
        compile_martial_editorial(
            edit_package=EDIT_PACKAGE,
            cue_sheet=CUE_SHEET,
            audio_manifest=AUDIO_MANIFEST,
            word_timings=WORD_TIMINGS,
            caption_plan=EPISODE_ROOT / "edit" / "revisions" / "r1" / "captions" / "marshall-monday-001-dynamic-captions.v1.json",
            caption_output=EPISODE_ROOT / "edit" / "revisions" / "r1" / "captions" / "marshall-monday-001-anchor.en-US.srt",
            authorization=None,  # type: ignore[arg-type]
            pacing_recipe={},
            job_root=tmp_path / "job",
            revision_id="fixture",
            allow_external_job_root=True,
        )


def test_adapter_rejects_output_outside_runtime_jobs(tmp_path: Path) -> None:
    with pytest.raises(MartialEditorialAdapterError, match="job_root must remain under"):
        compile_martial_editorial(
            edit_package={},
            cue_sheet={},
            audio_manifest={},
            word_timings={},
            caption_plan={},
            caption_output={},
            authorization={},
            pacing_recipe={},
            job_root=tmp_path / "escaped-job",
            revision_id="fixture",
        )
