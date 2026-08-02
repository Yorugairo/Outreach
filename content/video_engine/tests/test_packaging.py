from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from PIL import Image

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)
from content.video_engine.src.services.packaging import PackagingService, add_utm
from content.video_engine.src.services.publish import ManualPublishService


ENGINE_ROOT = Path(__file__).resolve().parents[1]


def _storyboard() -> dict:
    return json.loads(
        ENGINE_ROOT.joinpath("tests/fixtures/armbar_storyboard.json").read_text(
            encoding="utf-8"
        )
    )


def _write_words(audio_dir: Path, storyboard: dict, durations: list[float] | None = None) -> None:
    audio_dir.mkdir(parents=True, exist_ok=True)
    values = durations or [float(scene["timing"]["target_s"]) for scene in storyboard["scenes"]]
    for scene, duration in zip(storyboard["scenes"], values):
        scene_id = int(scene["scene_id"])
        audio_dir.joinpath(f"scene_{scene_id}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene_id,
                    "duration_s": duration,
                    "words": [{"w": "measured", "start_s": 0.0, "end_s": duration}],
                }
            ),
            encoding="utf-8",
        )


def test_add_utm_preserves_existing_query_and_sets_campaign() -> None:
    result = add_utm("https://example.com/article?ref=registry", "armbar")
    query = parse_qs(urlsplit(result).query)

    assert query == {
        "ref": ["registry"],
        "utm_source": ["youtube"],
        "utm_medium": ["longform"],
        "utm_campaign": ["armbar"],
    }


def test_packaging_emits_complete_metadata_embed_payload_and_thumbnails(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    storyboard["packaging"]["thumbnail"]["variant_texts"].append("BREAK THE GRIP")
    source = {
        "slug": "armbar-from-guard",
        "taught_at": [
            {"name": "Example Academy", "city": "Seattle", "state": "WA"},
            {"name": "Second Academy", "city": "Tacoma", "state": "WA"},
        ],
    }
    _write_words(tmp_path / "audio", storyboard)

    output = PackagingService().build(
        storyboard,
        source,
        tmp_path,
        article_url="https://nationalbjjregistry.com/techniques/guard/armbar-from-guard",
        registry_url="https://nationalbjjregistry.com/academies",
    )

    metadata = json.loads(
        tmp_path.joinpath("package/metadata.json").read_text(encoding="utf-8")
    )
    embed = json.loads(
        tmp_path.joinpath("package/embed_payload.json").read_text(encoding="utf-8")
    )
    assert metadata["titles"] == storyboard["packaging"]["titles"]
    assert metadata["chapters"][0]["start_s"] == 0.0
    assert metadata["disclosure"]["required"] is False
    assert "{ARTICLE_URL}" not in metadata["description"]
    urls = [token for token in metadata["description"].split() if token.startswith("http")]
    assert urls
    assert all(
        parse_qs(urlsplit(url).query)["utm_campaign"] == ["armbar-from-guard"]
        for url in urls
    )
    assert embed["source_slug"] == "armbar-from-guard"
    assert embed["target_page_slugs"] == ["armbar-from-guard", "seattle", "tacoma"]
    assert embed["video_object_jsonld"]["@type"] == "VideoObject"
    assert embed["video_object_jsonld"]["duration"].startswith("PT")
    assert embed["youtube_url"] is None
    thumbnail_bytes = []
    for thumbnail in output.summary["thumbnail_paths"]:
        thumbnail_path = tmp_path / thumbnail
        thumbnail_bytes.append(thumbnail_path.read_bytes())
        with Image.open(thumbnail_path) as image:
            assert image.size == (1280, 720)
            assert image.format == "PNG"
    assert thumbnail_bytes[0] != thumbnail_bytes[1]


def test_packaging_uses_measured_duration_for_chapters_and_jsonld(tmp_path: Path) -> None:
    storyboard = _storyboard()
    measured = [float(scene["timing"]["target_s"]) for scene in storyboard["scenes"]]
    measured[0] *= 1.2  # Deliberately diverge from the authoring estimate by 20%.
    _write_words(tmp_path / "audio", storyboard, measured)

    output = PackagingService().build(
        storyboard,
        {"slug": "armbar-from-guard", "taught_at": []},
        tmp_path,
        article_url="https://nationalbjjregistry.com/article",
        registry_url="https://nationalbjjregistry.com/academies",
    )

    expected = sum(
        duration + float(scene["timing"].get("padding_s", 0.0))
        for scene, duration in zip(storyboard["scenes"], measured)
    )
    assert output.summary["duration_s"] == pytest.approx(expected)
    metadata = json.loads(tmp_path.joinpath("package/metadata.json").read_text())
    assert metadata["chapters"][1]["start_s"] == pytest.approx(
        measured[0] + float(storyboard["scenes"][0]["timing"]["padding_s"])
    )
    embed = json.loads(tmp_path.joinpath("package/embed_payload.json").read_text())
    assert embed["video_object_jsonld"]["duration"] == "PT36S"


def test_packaging_fails_closed_when_measured_timing_is_missing(tmp_path: Path) -> None:
    storyboard = _storyboard()
    with pytest.raises(ValueError, match="scene 1.*missing word-timing"):
        PackagingService().build(
            storyboard,
            {"slug": "armbar-from-guard", "taught_at": []},
            tmp_path,
            article_url="https://nationalbjjregistry.com/article",
            registry_url="https://nationalbjjregistry.com/academies",
        )


def test_packaging_stage_rejects_missing_registry_url_before_writes(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    storyboard["packaging"]["cta"]["url"] = ""
    (tmp_path / "storyboard.json").write_text(
        json.dumps(storyboard),
        encoding="utf-8",
    )
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"position": "guard"}), encoding="utf-8")
    run = VideoRun(source_ref=str(source))
    context = StageContext(
        repository=object(),
        configs={"article_url": "https://example.com/article"},
        job_dir=tmp_path,
    )

    with pytest.raises(ValueError, match="registry_url"):
        PackagingService().run_stage(run, context)
    assert not (tmp_path / "package").exists()


def test_disclosure_checklist_is_conditional() -> None:
    storyboard = _storyboard()
    assert not any(
        "disclosure" in item.casefold()
        for item in PackagingService.upload_checklist(storyboard)
    )
    storyboard["packaging"]["synthetic_content_disclosure"] = {
        "required": True,
        "reason": "realistic recreation",
    }
    assert any(
        "disclosure" in item.casefold()
        for item in PackagingService.upload_checklist(storyboard)
    )


def test_manual_publish_requires_gate_b_and_passing_qc(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(source_ref="source.json")
    repository.create_run(run)
    context = StageContext(repository=repository, configs={}, job_dir=repository.job_dir(run.id))
    context.job_dir.joinpath("package/metadata.json").write_text(
        json.dumps({"upload_checklist": ["Choose title"]}),
        encoding="utf-8",
    )
    context.job_dir.joinpath("package/embed_payload.json").write_text(
        json.dumps({"youtube_url": None}),
        encoding="utf-8",
    )
    service = ManualPublishService()

    output = service.run_stage(run, context)
    assert output.summary["status"] == "packaged"
    with pytest.raises(ValueError, match="Gate B"):
        service.approve_publish(run, context)

    run.gate_b_status = "approved"
    context.job_dir.joinpath("qc/report.json").write_text(
        json.dumps({"overall": "pass", "checks": []}),
        encoding="utf-8",
    )
    published = service.approve_publish(run, context)
    assert published.status == "published"
