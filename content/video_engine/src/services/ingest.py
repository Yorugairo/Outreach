from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


@dataclass(slots=True, frozen=True)
class SourceBundle:
    slug: str
    kind: str
    ref: str
    content_hash: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class IngestService:
    @staticmethod
    def _validate_corpus_record(
        payload: dict[str, Any],
        source_path: Path,
        ctx: StageContext,
        project_root: Path,
    ) -> None:
        schema_path = Path(
            ctx.configs.get(
                "corpus_schema",
                project_root
                / "content"
                / "bjj-registry"
                / "schemas"
                / "technique-corpus.schema.json",
            )
        )
        if not schema_path.is_file():
            raise FileNotFoundError(
                f"canonical corpus schema does not exist: {schema_path}"
            )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = sorted(
            Draft7Validator(schema).iter_errors(payload),
            key=lambda error: [str(part) for part in error.absolute_path],
        )
        if errors:
            details = "; ".join(
                f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: "
                f"{error.message}"
                for error in errors
            )
            raise ValueError(f"corpus record failed canonical validation: {details}")
        if payload["slug"] != source_path.stem:
            raise ValueError(
                "corpus record failed canonical validation: "
                f"slug '{payload['slug']}' must match filename stem "
                f"'{source_path.stem}'"
            )

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        project_root = Path(ctx.configs.get("project_root", Path.cwd())).resolve()
        source_path = Path(job.source_ref)
        if not source_path.is_absolute():
            source_path = project_root / source_path
        source_path = source_path.resolve()
        try:
            relative = source_path.relative_to(project_root)
        except ValueError as exc:
            raise ValueError("source must stay within the project root") from exc
        if not source_path.is_file():
            raise FileNotFoundError(f"source does not exist: {relative.as_posix()}")

        raw = source_path.read_bytes()
        content_hash = hashlib.sha256(raw).hexdigest()
        if source_path.suffix.casefold() == ".json":
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON source must contain an object")
            if payload.get("schema_version") == "history_episode.v1":
                from content.video_engine.src.services.history_contracts import (
                    HistoryContractService,
                )

                payload = HistoryContractService(root=project_root).validate_history_episode(
                    payload
                )
                kind = "history_episode"
                slug = str(payload["id"])
                ctx.job_dir.joinpath("history_episode.json").write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            else:
                if not payload.get("transcript"):
                    raise ValueError(
                        "corpus source must be a JSON object with a transcript"
                    )
                self._validate_corpus_record(payload, source_path, ctx, project_root)
                kind = "corpus_technique"
                slug = str(payload.get("slug") or source_path.stem)
        elif source_path.suffix.casefold() in {".md", ".markdown"}:
            text = raw.decode("utf-8")
            payload = {"markdown": text, "title": source_path.stem.replace("-", " ").title()}
            kind = "essay_markdown"
            slug = source_path.stem
        else:
            raise ValueError("supported source types are .json, .md, and .markdown")

        bundle = SourceBundle(
            slug=slug,
            kind=kind,
            ref=relative.as_posix(),
            content_hash=content_hash,
            payload=payload,
        )
        output_path = ctx.job_dir / "source_bundle.json"
        output_path.write_text(
            json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return StageOutput(
            {
                "artifact_path": "source_bundle.json",
                "source_kind": kind,
                "source_slug": slug,
                "content_hash": content_hash,
                "cost_usd": 0.0,
            }
        )
