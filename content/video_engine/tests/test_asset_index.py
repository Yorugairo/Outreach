"""The assets layer: a prop manifest and an icon catalog become one findable record per asset.

Pins the record shape over a synthetic tree (two props, two icons, one sourced glyph), that
`--check` follows the source, that an unrecognised catalog shape is refused BY NAME rather than
guessed at, and that an asset whose file is absent reads `on_disk: false`."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_asset_index as BAI  # noqa: E402

PROPS_DIR = "content/video_engine/assets/props"
ICONS_DIR = "content/video_engine/assets/icons"

PROPS = {
    "schema": "finance_props_catalog.v1", "total_assets": 2,
    "props": [
        {"id": "prop-fed-v1", "name": "Federal Reserve", "anchor": [1, 1], "tier": "prop",
         "category": "macro", "tags": ["federal-reserve", "fed"], "context": "Monetary authority.",
         "filename": "prop-fed-v1.png", "path": "assets/props/cutouts/prop-fed-v1.png",
         "width": 20, "height": 10, "sha256": "aa", "source_sheet": "S1"},
        {"id": "prop-oil-v1", "name": "Oil Barrel", "anchor": [1, 1], "tier": "mechanism",
         "category": "energy", "tags": ["crude-oil"], "context": "Energy shock.",
         "filename": "prop-oil-v1.png", "path": "assets/props/cutouts/prop-oil-v1.png",
         "width": 30, "height": 40, "sha256": "bb", "source_sheet": "S2"},
    ],
}
ICONS = {
    "schema_version": "finance_asset_catalog.v1", "project_root": "content/video_engine",
    "resolution_order": ["exact_semantic_match"],
    "assets": [
        {"asset_id": "prop-icon-bull-v1", "path": "assets/icons/cutouts/prop-icon-bull-v1.png",
         "sha256": "cc", "kind": "prop", "visual_worlds": ["story"], "semantic_tags": ["bull-market"],
         "identity_lenses": ["equities"], "resolution_tier": 2, "render_eligible": True},
        {"asset_id": "prop-icon-bear-v1", "path": "assets/icons/cutouts/prop-icon-bear-v1.png",
         "sha256": "dd", "kind": "prop", "visual_worlds": ["mechanism"], "semantic_tags": ["bear-market"],
         "identity_lenses": ["equities"], "resolution_tier": 2, "render_eligible": False},
    ],
}
ICON_CATALOGUE = (
    "# Icons\n\n| Thumbnail / ID | Source Sheet | Dimensions | Context |\n| :--- | :--- | :--- | :--- |\n"
    "| [`prop-icon-bull-v1`](file:///x/prop-icon-bull-v1.png)<br>*Bull Market Rally* | `Icons1.png` "
    "| 293×278 | Equities bull market. |\n"
)
SOURCES = ("# Icon sources\n\n| field | value |\n|---|---|\n| set | **Lucide** |\n"
           "| version | **1.45.0** |\n\n| `coins.svg` | url |\n")
SVG = '<svg viewBox="0 0 24 24"><circle r="1"/></svg>'


def _write(root: Path, rel: str, text: str | bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    _write(tmp_path, f"{PROPS_DIR}/manifest.json", json.dumps(PROPS))
    _write(tmp_path, f"{PROPS_DIR}/CATALOGUE.md", "# Props\n")
    _write(tmp_path, f"{PROPS_DIR}/cutouts/prop-fed-v1.png", b"png")      # prop-oil-v1 is absent
    _write(tmp_path, f"{ICONS_DIR}/finance_icons_catalog.v1.json", json.dumps(ICONS))
    _write(tmp_path, f"{ICONS_DIR}/CATALOGUE.md", ICON_CATALOGUE)
    _write(tmp_path, f"{ICONS_DIR}/SOURCES.md", SOURCES)
    _write(tmp_path, f"{ICONS_DIR}/coins.svg", SVG)
    _write(tmp_path, f"{ICONS_DIR}/cutouts/prop-icon-bull-v1.png", b"png")
    _write(tmp_path, f"{ICONS_DIR}/cutouts/prop-icon-bear-v1.png", b"png")
    return tmp_path


def test_the_prop_manifest_and_icon_catalog_build_the_expected_records(tree: Path) -> None:
    # Act
    records = BAI.build(tree)
    by_id = {r["id"]: r for r in records}

    # Assert
    assert [r["id"] for r in records] == [
        "icon:coins", "prop-icon-bear-v1", "prop-icon-bull-v1", "prop-fed-v1", "prop-oil-v1"]
    assert by_id["prop-fed-v1"] == {
        "library": "props", "id": "prop-fed-v1", "name": "Federal Reserve", "category": "macro",
        "tier": "prop", "kind": "prop", "catalog_kind": None, "form": None,
        "tags": ["federal-reserve", "fed"],
        "context": "Monetary authority.",
        "path": "content/video_engine/assets/props/cutouts/prop-fed-v1.png", "size": "20x10",
        "sha256": "aa", "catalogue": f"{PROPS_DIR}/CATALOGUE.md", "on_disk": True,
        "render_eligible": None,
    }
    bull = by_id["prop-icon-bull-v1"]
    assert (bull["library"], bull["name"], bull["size"], bull["context"]) == (
        "icons", "Bull Market Rally", "293x278", "Equities bull market.")
    assert bull["tags"] == ["bull-market", "equities"] and bull["render_eligible"] is True
    assert bull["path"] == f"{ICONS_DIR}/cutouts/prop-icon-bull-v1.png"
    assert bull["catalogue"] == f"{ICONS_DIR}/CATALOGUE.md"
    assert by_id["prop-icon-bear-v1"]["name"] == "prop-icon-bear-v1"     # no catalogue row: the id
    coins = by_id["icon:coins"]
    assert (coins["kind"], coins["form"], coins["category"], coins["catalogue"], coins["on_disk"]) == (
        "icon", "glyph", "Lucide", f"{ICONS_DIR}/SOURCES.md", True)


def test_kind_says_what_the_asset_is_by_library_and_keeps_the_catalogs_value(tree: Path) -> None:
    # Act
    by_id = {r["id"]: r for r in BAI.build(tree)}

    # Assert: the icon catalog says `prop`; the index says `icon` and keeps `prop` as catalog_kind
    bull = by_id["prop-icon-bull-v1"]
    assert (bull["kind"], bull["catalog_kind"], bull["form"], bull["tier"]) == ("icon", "prop", None, 2)
    coins = by_id["icon:coins"]
    assert (coins["kind"], coins["catalog_kind"], coins["form"]) == ("icon", None, "glyph")
    assert [(by_id[i]["kind"], by_id[i]["tier"]) for i in ("prop-fed-v1", "prop-oil-v1")] == [
        ("prop", "prop"), ("prop", "mechanism")]
    md = BAI.render_md(BAI.build(tree))
    assert "## icons - icon (3)" in md and "## props - prop (2)" in md
    assert "Lucide icon glyph" in md and "equities icon" in md


def test_on_disk_is_false_for_a_catalogued_file_that_is_missing(tree: Path) -> None:
    by_id = {r["id"]: r for r in BAI.build(tree)}

    assert by_id["prop-oil-v1"]["on_disk"] is False
    assert by_id["prop-fed-v1"]["on_disk"] is True


def test_check_passes_after_write_and_fails_after_the_manifest_changes(tree: Path, capsys) -> None:
    # Arrange
    assert BAI.main(["--write", "--repo", str(tree)]) == 0
    assert BAI.main(["--check", "--repo", str(tree)]) == 0

    # Act
    changed = json.loads(json.dumps(PROPS))
    changed["props"][0]["tags"].append("central-bank")
    _write(tree, f"{PROPS_DIR}/manifest.json", json.dumps(changed))

    # Assert
    assert BAI.main(["--check", "--repo", str(tree)]) == 1
    assert "stale" in capsys.readouterr().out


def test_an_unrecognised_catalog_shape_is_refused_by_name(tree: Path, capsys) -> None:
    # Arrange
    _write(tree, "content/video_engine/assets/maps/manifest.json",
           json.dumps({"schema": "maps.v9", "items": []}))

    # Act / Assert
    with pytest.raises(BAI.UnrecognisedCatalog, match="assets/maps/manifest.json"):
        BAI.build(tree)
    assert BAI.main(["--check", "--repo", str(tree)]) == 2
    assert "REFUSED content/video_engine/assets/maps/manifest.json" in capsys.readouterr().out


def test_write_is_deterministic_and_lf(tree: Path) -> None:
    BAI.write(tree)
    first = (tree / BAI.JSONL_REL).read_bytes()
    BAI.write(tree)

    assert (tree / BAI.JSONL_REL).read_bytes() == first
    assert b"\r\n" not in first and b"\r\n" not in (tree / BAI.MD_REL).read_bytes()
