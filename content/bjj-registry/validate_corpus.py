"""Validate transcript-grounded BJJ technique records for production readiness."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
DEFAULT_SCHEMA = HERE / "schemas" / "technique-corpus.schema.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from content.video_engine.src.services.script_transform import (  # noqa: E402
    ScriptTransformService,
)


def _error_path(error: Any) -> str:
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _load_schema(schema_path: Path) -> dict[str, Any]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return schema


def _record_paths(corpus_path: Path) -> list[Path]:
    if corpus_path.is_file():
        return [corpus_path]
    if corpus_path.is_dir():
        return sorted(corpus_path.glob("*.json"))
    return []


def _display_path(record_path: Path, corpus_path: Path) -> str:
    if corpus_path.is_dir():
        return record_path.relative_to(corpus_path).as_posix()
    return record_path.name


def _validate_semantics(
    payload: dict[str, Any],
    record_path: Path,
    *,
    enforce_filename: bool,
) -> list[str]:
    errors: list[str] = []
    slug = payload.get("slug")

    if enforce_filename and isinstance(slug, str) and record_path.stem != slug:
        errors.append(
            f"$.slug: must match the filename stem '{record_path.stem}'"
        )

    related = payload.get("related")
    if isinstance(related, list) and isinstance(slug, str):
        seen_related: set[str] = set()
        for index, item in enumerate(related):
            if not isinstance(item, dict):
                continue
            related_slug = item.get("slug")
            if related_slug == slug:
                errors.append(f"$.related[{index}].slug: cannot reference itself")
            if isinstance(related_slug, str):
                if related_slug in seen_related:
                    errors.append(
                        f"$.related[{index}].slug: duplicate related slug "
                        f"'{related_slug}'"
                    )
                seen_related.add(related_slug)

    transcript = payload.get("transcript")
    if isinstance(transcript, str) and transcript.strip():
        try:
            ScriptTransformService().build_corpus(
                {
                    "slug": str(slug or record_path.stem),
                    "payload": payload,
                }
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"$: video engine cannot transform this record: {exc}")

    return errors


def validate_corpus(
    corpus: str | Path,
    *,
    schema: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Return a deterministic readiness report for a corpus file or directory."""
    corpus_path = Path(corpus).resolve()
    schema_path = Path(schema).resolve()
    validator = Draft7Validator(_load_schema(schema_path))
    paths = _record_paths(corpus_path)

    report: dict[str, Any] = {
        "valid": False,
        "corpus": str(corpus_path),
        "schema": str(schema_path),
        "errors": [],
        "summary": {
            "files_checked": len(paths),
            "ready": 0,
            "invalid": 0,
            "error_count": 0,
        },
        "records": [],
    }
    if not paths:
        report["errors"].append("no JSON corpus records found")
        report["summary"]["error_count"] = 1
        return report

    slug_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record_path in paths:
        item: dict[str, Any] = {
            "path": _display_path(record_path, corpus_path),
            "slug": None,
            "valid": False,
            "errors": [],
        }
        try:
            payload = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            item["errors"].append(f"$: malformed or unreadable JSON: {exc}")
            report["records"].append(item)
            continue

        if isinstance(payload, dict):
            item["slug"] = payload.get("slug")
        schema_errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: [str(part) for part in error.absolute_path],
        )
        item["errors"].extend(
            f"{_error_path(error)}: {error.message}" for error in schema_errors
        )
        if isinstance(payload, dict):
            item["errors"].extend(
                _validate_semantics(
                    payload,
                    record_path,
                    enforce_filename=corpus_path.is_dir(),
                )
            )
            slug = payload.get("slug")
            if isinstance(slug, str) and slug:
                slug_records[slug].append(item)
        report["records"].append(item)

    for slug, items in slug_records.items():
        if len(items) <= 1:
            continue
        for item in items:
            item["errors"].append(f"$.slug: duplicate corpus slug '{slug}'")

    for item in report["records"]:
        item["valid"] = not item["errors"]

    ready = sum(1 for item in report["records"] if item["valid"])
    invalid = len(report["records"]) - ready
    error_count = len(report["errors"]) + sum(
        len(item["errors"]) for item in report["records"]
    )
    report["summary"].update(
        {
            "ready": ready,
            "invalid": invalid,
            "error_count": error_count,
        }
    )
    report["valid"] = invalid == 0 and not report["errors"]
    return report


def _print_human(report: dict[str, Any]) -> None:
    summary = report["summary"]
    label = "READY" if report["valid"] else "NOT READY"
    print(
        f"{label}: {summary['ready']}/{summary['files_checked']} records ready; "
        f"{summary['error_count']} error(s)"
    )
    for error in report["errors"]:
        print(f"  [corpus] {error}")
    for item in report["records"]:
        state = "ok" if item["valid"] else "invalid"
        print(f"  [{state}] {item['path']}")
        for error in item["errors"]:
            print(f"    - {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate BJJ technique corpus records for video readiness"
    )
    parser.add_argument("--corpus", required=True, help="JSON record or corpus directory")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help="JSON Schema override (defaults to the canonical corpus schema)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = validate_corpus(args.corpus, schema=args.schema)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        SchemaError,
        ValueError,
    ) as exc:
        report = {
            "valid": False,
            "corpus": str(Path(args.corpus).resolve()),
            "schema": str(Path(args.schema).resolve()),
            "errors": [f"validator setup failed: {exc}"],
            "summary": {
                "files_checked": 0,
                "ready": 0,
                "invalid": 0,
                "error_count": 1,
            },
            "records": [],
        }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_human(report)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
