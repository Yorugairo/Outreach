"""The assets layer: every prop, icon and glyph under `content/video_engine/assets/`, findable.

The operator, 2026-09-15: "our icon and props should also be" indexed the same as docs - an asset
that exists and cannot be found is treated as not existing. The catalogues already carry the
names, tags and context; nothing read them into the retrieval stack, so `docs_find "federal
reserve"` never reached the Federal Reserve prop. This reads them and writes one record per asset:

    docs/ASSETS-INDEX.jsonl   one JSON object per line - the layer `docs_find --layer assets` scans
    docs/ASSETS-INDEX.md      the same, readable, grouped by library

    python content/video_engine/scripts/build_asset_index.py --write   # regenerate both
    python content/video_engine/scripts/build_asset_index.py --check   # exit 1 when stale (the default)

A record: `{library, id, name, category, tier, kind, catalog_kind, form, tags, context, path
(repo-relative), size, sha256, catalogue, on_disk, render_eligible}`. `kind` says what the asset IS
to a reader, by library (the operator, 2026-09-15: "the icon kind should be icon ... and the props get
the prop"): everything in `icons` is `icon`, everything in `props` is `prop`; any other library keeps
its catalog's value. `catalog_kind` is the source catalog's own `kind`, unchanged - kept so a catalog
that disagrees with its library shows it (the icon catalog was relabelled `prop` -> `icon` on 2026-09-15). `form` is `glyph`
for a sourced `*.svg`, else null. The sources, per library folder
`content/video_engine/assets/<library>/`:

  * `manifest.json` or any `*catalog*.json` in a shape this tool recognises - today
    `finance_props_catalog.v1` (`props[]`) and `finance_asset_catalog.v1` (`assets[]`). A file
    that matches the name but not a known shape is REFUSED by name (exit 2), never guessed at;
  * the library's `CATALOGUE.md` table fills what the JSON leaves out (an icon's display name,
    dimensions and context);
  * a root-level `*.svg` is a sourced glyph (the chip's `icon:<name>`), catalogued in `SOURCES.md`.

`on_disk` says whether the asset's file exists in THIS checkout: cutouts are gitignored, so a
clone without them reads `on_disk: false` and the layer is stale against the author's tree -
a known limit, stated rather than worked around. Standard library only; deterministic output
(sorted, no timestamps), written LF.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

ASSETS_REL = "content/video_engine/assets"
JSONL_REL = "docs/ASSETS-INDEX.jsonl"
MD_REL = "docs/ASSETS-INDEX.md"
CATALOGUE_NAME = "CATALOGUE.md"
SOURCES_NAME = "SOURCES.md"
CATALOG_GLOBS = ("manifest.json", "*catalog*.json")
LIBRARY_KIND = {"icons": "icon", "props": "prop"}   # what an asset IS, by the library it lives in

PROPS_SCHEMA = "finance_props_catalog.v1"
ICONS_SCHEMA = "finance_asset_catalog.v1"

ROW_ID = re.compile(r"\[`([^`]+)`\]\([^)]*\)(?:<br>\*([^*]+)\*)?")
DIMS = re.compile(r"(\d+)\s*[×x]\s*(\d+)")
SET_ROW = re.compile(r"^\|\s*set\s*\|\s*\**([^|*]+?)\**\s*\|", re.M)
VERSION_ROW = re.compile(r"^\|\s*version\s*\|\s*\**([^|*]+?)\**\s*\|", re.M)


class UnrecognisedCatalog(ValueError):
    """A catalog-named file whose shape this tool does not know."""


# --------------------------------------------------------------------------- sources

def catalog_files(repo: Path) -> list[Path]:
    """Every `manifest.json` / `*catalog*.json` directly inside a library folder, sorted."""
    base = Path(repo) / ASSETS_REL
    found: set[Path] = set()
    for pattern in CATALOG_GLOBS:
        found.update(p for p in base.glob(f"*/{pattern}") if p.is_file())
    return sorted(found, key=lambda p: p.as_posix())


def shape_of(data: object) -> str | None:
    """The adapter name for a known catalog shape, else None."""
    if not isinstance(data, dict):
        return None
    if data.get("schema") == PROPS_SCHEMA and isinstance(data.get("props"), list):
        return "props"
    if data.get("schema_version") == ICONS_SCHEMA and isinstance(data.get("assets"), list):
        return "assets"
    return None


def catalogue_rows(md_path: Path) -> dict[str, dict]:
    """`id -> {name, size, context}` from a CATALOGUE.md registry table; empty when absent."""
    if not md_path.is_file():
        return {}
    rows: dict[str, dict] = {}
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        m = ROW_ID.search(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        dims = next((DIMS.fullmatch(c) for c in cells[1:] if DIMS.fullmatch(c)), None)
        rows[m.group(1)] = {
            "name": (m.group(2) or "").strip(),
            "size": f"{dims.group(1)}x{dims.group(2)}" if dims else None,
            "context": cells[-1] if len(cells) > 1 else "",
        }
    return rows


def repo_rel(repo: Path, path: Path) -> str:
    return path.relative_to(repo).as_posix()


def resolve_asset(repo: Path, library_dir: Path, data: dict, raw_path: str) -> Path:
    """The asset's file: under the catalog's `project_root` when named, else the folder that
    holds `assets/` (the catalogs write `assets/<library>/...`), else beside the catalog."""
    raw = str(raw_path or "").replace("\\", "/")
    root = data.get("project_root")
    if isinstance(root, str) and root.strip():
        return Path(repo) / root.strip("/") / raw
    if raw.startswith("assets/"):
        return library_dir.parent.parent / raw
    return library_dir / raw


def asset_record(repo: Path, library_dir: Path, catalogue: str | None, fields: dict,
                 file_path: Path) -> dict:
    """The record, keys in the contract's order."""
    catalog_kind = fields.get("kind")
    return {
        "library": library_dir.name,
        "id": fields["id"],
        "name": fields.get("name") or fields["id"],
        "category": fields.get("category"),
        "tier": fields.get("tier"),
        "kind": LIBRARY_KIND.get(library_dir.name, catalog_kind),
        "catalog_kind": catalog_kind,
        "form": fields.get("form"),
        "tags": list(fields.get("tags") or []),
        "context": fields.get("context") or "",
        "path": repo_rel(repo, file_path),
        "size": fields.get("size"),
        "sha256": fields.get("sha256"),
        "catalogue": catalogue,
        "on_disk": file_path.is_file(),
        "render_eligible": fields.get("render_eligible"),
    }


def props_records(repo: Path, library_dir: Path, data: dict, catalogue: str | None) -> list[dict]:
    out = []
    for prop in data["props"]:
        width, height = prop.get("width"), prop.get("height")
        fields = {
            "id": prop["id"], "name": prop.get("name"), "category": prop.get("category"),
            "tier": prop.get("tier"), "kind": prop.get("kind"), "tags": prop.get("tags"),
            "context": prop.get("context"), "sha256": prop.get("sha256"),
            "size": f"{width}x{height}" if width and height else None,
            "render_eligible": prop.get("render_eligible"),
        }
        out.append(asset_record(repo, library_dir, catalogue, fields,
                                resolve_asset(repo, library_dir, data, prop.get("path", ""))))
    return out


def icons_records(repo: Path, library_dir: Path, data: dict, catalogue: str | None) -> list[dict]:
    rows = catalogue_rows(library_dir / CATALOGUE_NAME)
    out = []
    for asset in data["assets"]:
        ident = asset["asset_id"]
        row = rows.get(ident, {})
        lenses = list(asset.get("identity_lenses") or [])
        fields = {
            "id": ident, "name": row.get("name"), "category": lenses[0] if lenses else None,
            "tier": asset.get("resolution_tier"), "kind": asset.get("kind"),
            "tags": [*(asset.get("semantic_tags") or []), *lenses],
            "context": row.get("context") or ", ".join(asset.get("visual_worlds") or []),
            "sha256": asset.get("sha256"), "size": row.get("size"),
            "render_eligible": asset.get("render_eligible"),
        }
        out.append(asset_record(repo, library_dir, catalogue, fields,
                                resolve_asset(repo, library_dir, data, asset.get("path", ""))))
    return out


ADAPTERS = {"props": props_records, "assets": icons_records}


def first_group(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def glyph_records(repo: Path, library_dir: Path) -> list[dict]:
    """A root-level `*.svg` is a sourced glyph the chip embeds as `icon:<name>`."""
    svgs = sorted(library_dir.glob("*.svg"))
    if not svgs:
        return []
    sources = library_dir / SOURCES_NAME
    text = sources.read_text(encoding="utf-8") if sources.is_file() else ""
    icon_set, version = first_group(SET_ROW, text), first_group(VERSION_ROW, text)
    catalogue = repo_rel(repo, sources) if sources.is_file() else None
    origin = " ".join(x for x in (icon_set, version) if x) or "unsourced"
    out = []
    for svg in svgs:
        listed = f"`{svg.name}`" in text
        fields = {
            "id": f"icon:{svg.stem}", "name": svg.stem, "category": icon_set, "form": "glyph",
            "tags": [svg.stem], "sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
            "context": f"{origin} glyph, the chip's icon:{svg.stem}"
                       + ("" if listed else f" (not listed in {SOURCES_NAME})"),
        }
        out.append(asset_record(repo, library_dir, catalogue, fields, svg))
    return out


def build(repo: Path = REPO) -> list[dict]:
    """Every asset record, sorted by (library, id). Raises UnrecognisedCatalog by name."""
    repo = Path(repo)
    records: list[dict] = []
    for catalog in catalog_files(repo):
        data = json.loads(catalog.read_text(encoding="utf-8"))
        shape = shape_of(data)
        if shape is None:
            keys = ", ".join(sorted(data)) if isinstance(data, dict) else type(data).__name__
            raise UnrecognisedCatalog(f"{repo_rel(repo, catalog)}: unrecognised catalog shape ({keys})")
        library_dir = catalog.parent
        md = library_dir / CATALOGUE_NAME
        catalogue = repo_rel(repo, md) if md.is_file() else None
        records += ADAPTERS[shape](repo, library_dir, data, catalogue)
    base = repo / ASSETS_REL
    if base.is_dir():
        for library_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            records += glyph_records(repo, library_dir)
    return sorted(records, key=lambda r: (r["library"], r["id"]))


# --------------------------------------------------------------------------- render / write / check

def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def md_line(record: dict) -> str:
    state = "" if record["on_disk"] else " (NOT ON DISK)"
    kind = " ".join(str(x) for x in (record["kind"], record["form"]) if x) or record["tier"] or ""
    head = f"- `{record['id']}` - {record['name']} - {record['category'] or ''} {kind}".rstrip()
    return f"{head} - `{record['path']}`{state} - catalogue `{record['catalogue']}`"


def render_md(records: list[dict]) -> str:
    lines = ["# Assets index", "",
             "Generated by `content/video_engine/scripts/build_asset_index.py` - do not edit. "
             "One line per asset; search it with",
             '`python content/video_engine/scripts/docs_find.py "<term>" --layer assets`.']
    libraries = sorted({r["library"] for r in records})
    for library in libraries:
        rows = [r for r in records if r["library"] == library]
        kinds = ", ".join(sorted({str(r["kind"]) for r in rows if r["kind"]}))
        label = f"{library} - {kinds}" if kinds else library
        lines += ["", f"## {label} ({len(rows)})", ""]
        lines += [md_line(r) for r in rows]
    return "\n".join(lines) + "\n"


def rendered(repo: Path = REPO) -> dict[str, str]:
    records = build(repo)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}


def write(repo: Path = REPO) -> int:
    artifacts = rendered(repo)
    for rel, text in artifacts.items():
        path = Path(repo) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return artifacts[JSONL_REL].count("\n")


def check(repo: Path = REPO) -> list[str]:
    """The stale artifacts, each with the first differing lines; empty when in sync."""
    stale: list[str] = []
    for rel, expected in rendered(repo).items():
        path = Path(repo) / rel
        if not path.is_file():
            stale.append(f"{rel} is missing")
            continue
        actual = path.read_bytes().decode("utf-8")
        if actual != expected:
            diff = list(difflib.unified_diff(actual.splitlines(), expected.splitlines(),
                                             rel, "expected", lineterm="", n=0))[:8]
            stale.append(f"{rel} is stale\n" + "\n".join(diff))
    return stale


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--check", action="store_true", help="exit 1 when stale (default)")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    try:
        if a.write:
            count = write(repo)
            print(f"build_asset_index: wrote {count} assets to {JSONL_REL} + {MD_REL}")
            return 0
        stale = check(repo)
        total = len(build(repo))
    except UnrecognisedCatalog as exc:
        print(f"build_asset_index: REFUSED {exc}")
        return 2
    if stale:
        for entry in stale:
            print(entry)
        print("build_asset_index: stale - run build_asset_index.py --write")
        return 1
    print(f"build_asset_index: in sync ({total} assets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
