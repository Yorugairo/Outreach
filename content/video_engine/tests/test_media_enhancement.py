from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from content.video_engine.src.services.media_enhancement import (
    MANIFEST_VERSION,
    MediaEnhancementError,
    MediaEnhancementService,
    MagnificSettings,
    validate_media_enhancement_plan,
)
from content.video_engine.src.services.magnific_video import (
    MANIFEST_VERSION as VIDEO_MANIFEST_VERSION,
    MagnificVideoError,
    MagnificVideoService,
    MagnificVideoSettings,
    PLAN_VERSION as VIDEO_PLAN_VERSION,
    validate_magnific_video_plan,
)
from content.video_engine.src.services.magnific_image import (
    MANIFEST_VERSION as IMAGE_MANIFEST_VERSION,
    MagnificImageError,
    MagnificImageService,
    MagnificImageSettings,
    PLAN_VERSION as IMAGE_PLAN_VERSION,
    validate_magnific_image_plan,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plan(root: Path, *, count: int = 1) -> dict:
    source = root / "source.png"
    reference = root / "reference.png"
    source.write_bytes(b"source-image")
    reference.write_bytes(b"reference-image")
    return {
        "schema_version": "media_enhancement_plan.v1",
        "provider": "magnific",
        "operation": "image_style_transfer",
        "items": [
            {
                "id": f"candidate-{index}",
                "source_path": source.relative_to(root).as_posix(),
                "source_sha256": _sha(source),
                "reference_path": reference.relative_to(root).as_posix(),
                "reference_sha256": _sha(reference),
                "prompt": "Original non-photorealistic editorial illustration",
                "parameters": {
                    "style_strength": 35,
                    "structure_strength": 85,
                    "engine": "illusio",
                    "flavor": "faithful",
                    "fixed_generation": True,
                },
            }
            for index in range(count)
        ],
    }


class _FakeTransport:
    def __init__(self) -> None:
        self.create_calls = 0
        self.poll_calls = 0
        self.last_payload: dict | None = None

    def create_style_transfer(self, payload):
        self.create_calls += 1
        self.last_payload = dict(payload)
        return {"data": {"task_id": f"task-{self.create_calls}", "status": "CREATED"}}

    def get_style_transfer(self, task_id: str):
        self.poll_calls += 1
        return {
            "data": {
                "task_id": task_id,
                "status": "COMPLETED",
                "generated": [f"https://example.test/{task_id}.png"],
            }
        }

    def create_flux_2_pro(self, payload):
        return self.create_style_transfer(payload)

    def get_flux_2_pro(self, task_id: str):
        return self.get_style_transfer(task_id)

    def download(self, url: str) -> bytes:
        return b"\x89PNG\r\n\x1a\ngenerated-image"


def _settings(**overrides) -> MagnificSettings:
    values = {
        "api_key": "secret-key",
        "max_cost_usd": 1.0,
        "max_calls": 6,
        "paid_calls_allowed": True,
        "poll_interval_s": 0,
    }
    values.update(overrides)
    return MagnificSettings(**values)


def test_settings_fail_closed_without_key_or_paid_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MAGNIFIC_API_KEY", raising=False)
    with pytest.raises(MediaEnhancementError, match="MAGNIFIC_API_KEY"):
        MagnificSettings.from_environment(
            max_cost_usd=1,
            max_calls=1,
            paid_calls_allowed=True,
        )

    monkeypatch.setenv("MAGNIFIC_API_KEY", "configured")
    with pytest.raises(MediaEnhancementError, match="--allow-paid"):
        MagnificSettings.from_environment(
            max_cost_usd=1,
            max_calls=1,
            paid_calls_allowed=False,
        )


def test_plan_rejects_stale_hashes_escape_and_imitation(tmp_path: Path) -> None:
    payload = _plan(tmp_path)
    payload["items"][0]["source_sha256"] = "0" * 64
    with pytest.raises(MediaEnhancementError, match="source hash is stale"):
        validate_media_enhancement_plan(payload, project_root=tmp_path)

    payload = _plan(tmp_path)
    payload["items"][0]["source_path"] = "../escape.png"
    with pytest.raises(MediaEnhancementError, match="escapes"):
        validate_media_enhancement_plan(payload, project_root=tmp_path)

    payload = _plan(tmp_path)
    payload["items"][0]["prompt"] = "in the style of a named creator"
    with pytest.raises(MediaEnhancementError, match="prohibited"):
        validate_media_enhancement_plan(payload, project_root=tmp_path)


def test_execute_enforces_cost_ceiling_before_provider_call(
    tmp_path: Path,
) -> None:
    transport = _FakeTransport()
    service = MediaEnhancementService(
        _settings(max_cost_usd=0.20),
        transport=transport,
    )
    with pytest.raises(MediaEnhancementError, match="projected cost"):
        service.execute(
            _plan(tmp_path, count=2),
            project_root=tmp_path,
            output_dir="outputs",
        )
    assert transport.create_calls == 0


def test_execute_persists_sanitized_manifest_and_uses_cache(
    tmp_path: Path,
) -> None:
    transport = _FakeTransport()
    service = MediaEnhancementService(_settings(), transport=transport)
    payload = _plan(tmp_path)

    first = service.execute(
        payload,
        project_root=tmp_path,
        output_dir="outputs",
    )
    assert first["schema_version"] == MANIFEST_VERSION
    assert first["provider_calls"] == 1
    assert first["cost_ceiling_usd"] == 0.15
    assert first["items"][0]["render_eligible"] is False
    assert first["items"][0]["review_status"] == "pending"
    assert transport.create_calls == 1
    assert (tmp_path / "outputs" / "candidate-0.png").read_bytes() == (
        b"\x89PNG\r\n\x1a\ngenerated-image"
    )

    serialized = (tmp_path / "outputs" / "manifest.json").read_text(
        encoding="utf-8"
    )
    assert "secret-key" not in serialized
    assert "api_key" not in serialized

    second = service.execute(
        payload,
        project_root=tmp_path,
        output_dir="outputs",
    )
    assert second["provider_calls"] == 0
    assert second["cache_hits"] == 1
    assert second["cost_ceiling_usd"] == 0
    assert transport.create_calls == 1


def test_settings_redaction_never_contains_api_key() -> None:
    redacted = _settings().redacted()
    assert "api_key" not in redacted
    assert "secret-key" not in json.dumps(redacted)
    assert os.environ.get("MAGNIFIC_API_KEY") != redacted


def test_flux_2_pro_uses_bounded_dimensions_and_known_cost(
    tmp_path: Path,
) -> None:
    payload = _plan(tmp_path)
    payload["operation"] = "flux_2_pro"
    payload["items"][0]["parameters"] = {
        "width": 1344,
        "height": 768,
        "seed": 1882,
        "prompt_upsampling": True,
    }
    transport = _FakeTransport()
    manifest = MediaEnhancementService(
        _settings(max_cost_usd=0.10),
        transport=transport,
    ).execute(
        payload,
        project_root=tmp_path,
        output_dir="flux-output",
    )

    assert manifest["operation"] == "flux_2_pro"
    assert manifest["cost_ceiling_usd"] == 0.10
    assert transport.last_payload is not None
    assert transport.last_payload["width"] == 1344
    assert transport.last_payload["height"] == 768
    assert transport.last_payload["prompt_upsampling"] is False
    assert "input_image" in transport.last_payload
    assert "input_image_2" in transport.last_payload


def _video_plan(root: Path, *, count: int = 1) -> dict:
    source = root / "learner.png"
    source.write_bytes(b"source-image")
    return {
        "schema_version": VIDEO_PLAN_VERSION,
        "provider": "magnific",
        "model": "kling-v2-5-pro",
        "items": [
            {
                "id": f"motion-{index}",
                "source_path": source.relative_to(root).as_posix(),
                "source_sha256": _sha(source),
                "prompt": "A simple fictional learner nods and points to the timeline",
                "negative_prompt": "no text corruption, no extra characters",
                "duration": "5",
                "cfg_scale": 0.5,
            }
            for index in range(count)
        ],
    }


class _FakeVideoTransport:
    def __init__(self) -> None:
        self.create_calls = 0
        self.poll_calls = 0
        self.last_payload: dict | None = None

    def create_kling_2_5(self, payload):
        self.create_calls += 1
        self.last_payload = dict(payload)
        return {
            "data": {
                "task_id": f"video-task-{self.create_calls}",
                "status": "CREATED",
            }
        }

    def get_kling_2_5(self, task_id: str):
        self.poll_calls += 1
        return {
            "data": {
                "task_id": task_id,
                "status": "COMPLETED",
                "generated": [f"https://example.test/{task_id}.mp4"],
            }
        }

    def download_video(self, url: str) -> bytes:
        return b"....ftypisom....generated-video"


def _video_settings(**overrides) -> MagnificVideoSettings:
    values = {
        "api_key": "secret-key",
        "max_cost_usd": 14.0,
        "max_calls": 1,
        "paid_calls_allowed": True,
        "poll_interval_s": 0,
        "cost_ceiling_usd": 14.0,
    }
    values.update(overrides)
    return MagnificVideoSettings(**values)


def test_video_plan_rejects_stale_hash_and_prohibited_renderer_inputs(
    tmp_path: Path,
) -> None:
    payload = _video_plan(tmp_path)
    payload["items"][0]["source_sha256"] = "0" * 64
    with pytest.raises(MagnificVideoError, match="source hash is stale"):
        validate_magnific_video_plan(payload, project_root=tmp_path)

    payload = _video_plan(tmp_path)
    payload["items"][0]["prompt"] = "in the style of a named creator"
    with pytest.raises(MagnificVideoError, match="prohibited"):
        validate_magnific_video_plan(payload, project_root=tmp_path)


def test_video_service_polls_downloads_and_caches(tmp_path: Path) -> None:
    transport = _FakeVideoTransport()
    service = MagnificVideoService(_video_settings(), transport=transport)
    payload = _video_plan(tmp_path)

    first = service.execute(
        payload,
        project_root=tmp_path,
        output_dir="video-output",
    )
    assert first["schema_version"] == VIDEO_MANIFEST_VERSION
    assert first["provider_calls"] == 1
    assert first["items"][0]["render_eligible"] is False
    assert transport.create_calls == 1
    assert transport.poll_calls == 1
    assert (tmp_path / "video-output" / "motion-0.mp4").is_file()

    second = service.execute(
        payload,
        project_root=tmp_path,
        output_dir="video-output",
    )
    assert second["provider_calls"] == 0
    assert second["cache_hits"] == 1
    assert transport.create_calls == 1


def test_video_service_enforces_ceiling_before_provider_call(tmp_path: Path) -> None:
    transport = _FakeVideoTransport()
    service = MagnificVideoService(
        _video_settings(max_cost_usd=13.99),
        transport=transport,
    )
    with pytest.raises(MagnificVideoError, match="projected cost ceiling"):
        service.execute(
            _video_plan(tmp_path),
            project_root=tmp_path,
            output_dir="video-output",
        )
    assert transport.create_calls == 0


def _image_plan() -> dict:
    return {
        "schema_version": IMAGE_PLAN_VERSION,
        "provider": "magnific",
        "model": "nano-banana-pro-flash",
        "items": [
            {
                "id": "learner-plate",
                "prompt": (
                    "Original flat 2D editorial learner character, filled cream body, "
                    "blue accent, dark background, clear silhouette"
                ),
                "aspect_ratio": "16:9",
                "resolution": "1K",
            }
        ],
    }


class _FakeImageTransport:
    def __init__(self) -> None:
        self.create_calls = 0
        self.poll_calls = 0

    def create_nano_banana_2(self, payload):
        self.create_calls += 1
        return {
            "data": {
                "task_id": f"image-task-{self.create_calls}",
                "status": "CREATED",
            }
        }

    def get_nano_banana_2(self, task_id: str):
        self.poll_calls += 1
        return {
            "data": {
                "task_id": task_id,
                "status": "COMPLETED",
                "generated": [f"https://example.test/{task_id}.png"],
            }
        }

    def download_image(self, url: str) -> bytes:
        return b"\x89PNG\r\n\x1a\ngenerated-image"


def _image_settings(**overrides) -> MagnificImageSettings:
    values = {
        "api_key": "secret-key",
        "max_cost_usd": 14.0,
        "max_calls": 1,
        "paid_calls_allowed": True,
        "poll_interval_s": 0,
        "cost_ceiling_usd": 14.0,
    }
    values.update(overrides)
    return MagnificImageSettings(**values)


def test_image_plan_rejects_prohibited_inputs() -> None:
    payload = _image_plan()
    payload["items"][0]["prompt"] = "in the style of a named creator"
    with pytest.raises(MagnificImageError, match="prohibited"):
        validate_magnific_image_plan(payload)


def test_image_service_polls_downloads_and_caches(tmp_path: Path) -> None:
    transport = _FakeImageTransport()
    service = MagnificImageService(_image_settings(), transport=transport)
    first = service.execute(
        _image_plan(),
        project_root=tmp_path,
        output_dir="image-output",
    )
    assert first["schema_version"] == IMAGE_MANIFEST_VERSION
    assert first["provider_calls"] == 1
    assert first["items"][0]["render_eligible"] is False
    assert transport.create_calls == 1
    assert transport.poll_calls == 1

    second = service.execute(
        _image_plan(),
        project_root=tmp_path,
        output_dir="image-output",
    )
    assert second["provider_calls"] == 0
    assert second["cache_hits"] == 1
    assert transport.create_calls == 1
