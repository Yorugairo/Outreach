"""Migrate a video-engine project tree into the durability-class layout.

Dry-run by default: prints every planned move and the catalogue rewrite, and
touches nothing. ``--execute`` performs the migration in an order that never
leaves the live catalogue naming a missing path:

    1. copy every file to its class destination,
    2. re-verify each catalogue-recorded sha256 against the bytes at the
       destination,
    3. write the rewritten catalogue to a temp file and atomically swap it in,
    4. only then delete the originals.

Idempotent: paths already under a class root are left alone, a re-run is a
no-op, and an interrupted run resumes safely because copies are verified
before anything is deleted.

Mapping (video engine only, per P18):

    catalogue-referenced paths        -> canonical/<unchanged relative path>
    assets/generated/review/**        -> review/**
    everything else                   -> untouched
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

CATALOG_FILENAME = "asset-catalog.v1.json"
LEGACY_REVIEW_PREFIX = ("assets", "generated", "review")
CLASS_ROOTS = ("canonical", "review", "runtime")


class MigrationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class Move:
    source: str  # project-relative, posix
    destination: str  # project-relative, posix
    sha256: str | None  # catalogue-recorded digest to verify, when known


@dataclass
class Plan:
    project_root: Path
    moves: list[Move] = field(default_factory=list)
    catalog_rewrites: dict[str, str] = field(default_factory=dict)  # old path -> new path

    @property
    def is_noop(self) -> bool:
        return not self.moves and not self.catalog_rewrites


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _already_classed(rel: str) -> bool:
    return rel.split("/", 1)[0] in CLASS_ROOTS


def _catalogue_path_fields(catalog: dict) -> list[tuple[dict, str]]:
    """Every (mapping, key) in the catalogue whose value is an asset path."""

    fields: list[tuple[dict, str]] = []
    for asset in catalog.get("assets", []):
        if asset.get("path"):
            fields.append((asset, "path"))
        for layer in asset.get("layers") or []:
            if layer.get("path"):
                fields.append((layer, "path"))
    return fields


def build_plan(project_root: str | Path) -> Plan:
    """Read the tree and the catalogue; compute moves. Touches nothing."""

    root = Path(project_root).resolve()
    if not root.is_dir():
        raise MigrationError([f"project root {root} is not a directory"])
    plan = Plan(project_root=root)
    planned: set[str] = set()

    catalog_file = root / CATALOG_FILENAME
    if catalog_file.exists():
        catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
        for holder, key in _catalogue_path_fields(catalog):
            rel = str(holder[key]).replace("\\", "/")
            if _already_classed(rel):
                continue
            destination = f"canonical/{rel}"
            plan.catalog_rewrites[rel] = destination
            if rel not in planned and (root / rel).exists():
                plan.moves.append(Move(rel, destination, holder.get("sha256")))
                planned.add(rel)

    legacy_review = root.joinpath(*LEGACY_REVIEW_PREFIX)
    if legacy_review.is_dir():
        for file in sorted(p for p in legacy_review.rglob("*") if p.is_file()):
            rel = file.relative_to(root).as_posix()
            if rel in planned:
                continue
            tail = file.relative_to(legacy_review).as_posix()
            plan.moves.append(Move(rel, f"review/{tail}", None))
            planned.add(rel)

    return plan


def render_plan(plan: Plan) -> str:
    lines = [f"# migration plan for {plan.project_root}"]
    if plan.is_noop:
        lines.append("nothing to do — tree already conforms to the class layout")
    for move in plan.moves:
        lines.append(f"move  {move.source}  ->  {move.destination}")
    for old, new in sorted(plan.catalog_rewrites.items()):
        lines.append(f"catalogue  {old}  ->  {new}")
    return "\n".join(lines)


def _copy_and_verify(plan: Plan) -> list[str]:
    errors: list[str] = []
    for move in plan.moves:
        source = plan.project_root / move.source
        destination = plan.project_root / move.destination
        if destination.exists():
            pass  # resumed run: verify below rather than re-copy
        elif not source.exists():
            errors.append(f"{move.source} missing and {move.destination} not yet copied")
            continue
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if move.sha256 and _sha256(destination) != move.sha256:
            errors.append(
                f"{move.destination} does not match the catalogue sha256 {move.sha256}"
            )
        elif move.sha256 is None and source.exists() and _sha256(destination) != _sha256(source):
            errors.append(f"{move.destination} does not match the bytes of {move.source}")
    return errors


def _swap_catalogue(plan: Plan) -> None:
    if not plan.catalog_rewrites:
        return
    catalog_file = plan.project_root / CATALOG_FILENAME
    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
    for holder, key in _catalogue_path_fields(catalog):
        rel = str(holder[key]).replace("\\", "/")
        if rel in plan.catalog_rewrites:
            holder[key] = plan.catalog_rewrites[rel]
    temp = catalog_file.with_suffix(".migrating.json")
    temp.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    os.replace(temp, catalog_file)


def execute(plan: Plan) -> list[str]:
    """Copy → verify → swap catalogue → delete originals. Returns actions taken."""

    errors = _copy_and_verify(plan)
    if errors:
        raise MigrationError(errors)
    _swap_catalogue(plan)
    actions: list[str] = []
    for move in plan.moves:
        source = plan.project_root / move.source
        if source.exists():
            source.unlink()
            actions.append(f"moved {move.source} -> {move.destination}")
    _prune_empty_dirs(plan.project_root / "assets")
    return actions


def _prune_empty_dirs(base: Path) -> None:
    if not base.is_dir():
        return
    for directory in sorted((p for p in base.rglob("*") if p.is_dir()), reverse=True):
        try:
            directory.rmdir()  # only succeeds when empty
        except OSError:
            pass
    try:
        base.rmdir()
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", help="video-engine project root to migrate")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="perform the migration; without this flag only the plan is printed",
    )
    args = parser.parse_args(argv)

    try:
        plan = build_plan(args.project_root)
        print(render_plan(plan))
        if not args.execute:
            print("\ndry-run: nothing was changed. Re-run with --execute to migrate.")
            return 0
        for action in execute(plan):
            print(action)
        return 0
    except MigrationError as exc:
        for error in exc.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
