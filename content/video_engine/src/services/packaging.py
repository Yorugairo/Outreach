from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.scenes.title_card import TitleConceptCard
from content.video_engine.src.timing import MeasuredTimeline, load_measured_timeline


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def add_utm(url: str, campaign: str) -> str:
    if not url:
        raise ValueError("a non-empty URL is required for UTM injection")
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"absolute http(s) URL required: {url}")
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update(
        {
            "utm_source": "youtube",
            "utm_medium": "longform",
            "utm_campaign": campaign,
        }
    )
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


def _iso_duration(duration_s: float) -> str:
    seconds = max(0, int(round(duration_s)))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    value = "PT"
    if hours:
        value += f"{hours}H"
    if minutes:
        value += f"{minutes}M"
    if seconds or value == "PT":
        value += f"{seconds}S"
    return value


def _chapters(
    storyboard: dict[str, Any],
    measured_timeline: MeasuredTimeline,
) -> list[dict[str, Any]]:
    chapters: list[dict[str, Any]] = []
    previous_act: str | None = None
    for scene, scene_timing in zip(storyboard["scenes"], measured_timeline):
        act = str(scene["act"])
        if act != previous_act:
            title = str(scene.get("on_screen_text") or act.replace("_", " ").title())
            chapters.append({"start_s": round(scene_timing.start_s, 3), "title": title})
            previous_act = act
    return chapters


class PackagingService:
    def build(
        self,
        storyboard: dict[str, Any],
        source_record: dict[str, Any],
        job_dir: str | Path,
        *,
        article_url: str,
        registry_url: str,
        audio_dir: str | Path | None = None,
    ) -> StageOutput:
        measured_timeline = load_measured_timeline(
            storyboard,
            Path(audio_dir) if audio_dir is not None else Path(job_dir) / "audio",
        )
        package_dir = Path(job_dir) / "package"
        package_dir.mkdir(parents=True, exist_ok=True)
        packaging = storyboard["packaging"]
        source_slug = str(storyboard["source"]["slug"])
        campaign = str(packaging.get("cta", {}).get("utm_campaign") or source_slug)
        description = str(packaging["description_md"])
        description = description.replace("{ARTICLE_URL}", add_utm(article_url, campaign))
        description = description.replace("{REGISTRY_URL}", add_utm(registry_url, campaign))
        if "{ARTICLE_URL}" in description or "{REGISTRY_URL}" in description:
            raise ValueError("description contains unresolved URL placeholders")

        thumbnail = packaging.get("thumbnail") or {}
        variant_texts = list(thumbnail.get("variant_texts") or [""])
        badge_color = str(
            thumbnail.get("badge_color")
            or storyboard.get("global_settings", {})
            .get("theme", {})
            .get("accent_color", "#3B82F6")
        )
        thumbnail_paths: list[str] = []
        theme = dict(storyboard.get("global_settings", {}).get("theme") or {})
        theme["accent_color"] = badge_color
        for index, variant in enumerate(variant_texts, start=1):
            path = package_dir / f"thumbnail_{index}.png"
            TitleConceptCard.render_thumbnail(
                path,
                headline=str(variant),
                concept=str(thumbnail.get("concept") or ""),
                theme=theme,
            )
            thumbnail_paths.append(path.relative_to(Path(job_dir)).as_posix())

        disclosure = dict(packaging["synthetic_content_disclosure"])
        metadata = {
            "titles": list(packaging["titles"]),
            "description": description,
            "tags": list(packaging.get("tags") or []),
            "chapters": _chapters(storyboard, measured_timeline),
            "disclosure": {
                "required": bool(disclosure["required"]),
                "reason": disclosure.get("reason"),
            },
            "upload_checklist": self.upload_checklist(storyboard),
        }
        self._write_json(package_dir / "metadata.json", metadata)

        taught_at = source_record.get("taught_at") or source_record.get("metadata", {}).get(
            "taught_at", []
        )
        target_slugs = [source_slug]
        for academy in taught_at:
            city = _slugify(str((academy or {}).get("city") or ""))
            if city:
                target_slugs.append(city)
        target_slugs = list(dict.fromkeys(target_slugs))

        duration_s = measured_timeline.total_s
        embed_payload = {
            "source_slug": source_slug,
            "target_page_slugs": target_slugs,
            "video_object_jsonld": {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": metadata["titles"][0],
                "description": metadata["description"],
                "thumbnailUrl": ["{THUMBNAIL_URL}"],
                "uploadDate": None,
                "duration": _iso_duration(duration_s),
            },
            "youtube_url": None,
        }
        self._write_json(package_dir / "embed_payload.json", embed_payload)
        return StageOutput(
            {
                "metadata_path": "package/metadata.json",
                "embed_payload_path": "package/embed_payload.json",
                "thumbnail_paths": thumbnail_paths,
                "duration_s": round(duration_s, 3),
                "timing_source": "audio/scene_<id>.words.json",
                "cost_usd": 0.0,
            }
        )

    @staticmethod
    def upload_checklist(storyboard: dict[str, Any]) -> list[str]:
        disclosure = storyboard["packaging"]["synthetic_content_disclosure"]
        checklist = [
            "Choose one approved title variant.",
            "Upload the matching thumbnail variant.",
            "Add the video to the configured series playlist.",
            "Confirm the lane badge matches the series.",
            "Space pilot uploads at least 48 hours apart.",
        ]
        if disclosure["required"]:
            checklist.append("Enable the synthetic-content disclosure before upload.")
        return checklist

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        storyboard_path = ctx.job_dir / "storyboard.json"
        if not storyboard_path.exists():
            raise FileNotFoundError("storyboard.json is required before packaging")
        storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
        source_path = Path(job.source_ref)
        if not source_path.is_absolute():
            source_path = Path(ctx.configs.get("project_root", Path.cwd())) / source_path
        source_record = json.loads(source_path.read_text(encoding="utf-8"))
        article_url = str(ctx.configs.get("article_url") or "")
        if not article_url:
            template = str(ctx.configs.get("article_url_template") or "")
            if template:
                article_url = template.format(
                    slug=storyboard["source"]["slug"],
                    position=source_record.get("position", ""),
                )
        registry_url = str(
            ctx.configs.get("registry_url")
            or storyboard.get("packaging", {}).get("cta", {}).get("url")
            or ""
        )
        if not article_url:
            raise ValueError("article_url config is required before packaging")
        if not registry_url:
            raise ValueError("registry_url config or storyboard CTA URL is required before packaging")
        # Validate both external destinations before loading timing artifacts
        # or creating package files, so configuration errors fail at the
        # stage boundary rather than halfway through assembly.
        add_utm(article_url, str(storyboard["source"]["slug"]))
        add_utm(registry_url, str(storyboard["source"]["slug"]))
        return self.build(
            storyboard,
            source_record,
            ctx.job_dir,
            article_url=article_url,
            registry_url=registry_url,
            audio_dir=ctx.job_dir / "audio",
        )

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(path)
