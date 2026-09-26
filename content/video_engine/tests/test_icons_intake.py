"""P73 T4: THE SUPPLY-CHAIN ICONS - the sourced glyph intake a flow node or a chip can name.

A flow node's and a chip's glyph is a SOURCED SVG (`build_scene_timeline_f.icon_file` -> assets/icons/<name>.svg;
A2a: sourced with provenance, never generated). Five shipped with P50; T4 adds the ones any supply chain needs
(a maker, a distributor, a reseller, the carriers, the licence, the law, a price, a flag, a buyer). Pinned here:

* every glyph in the folder is drawn to the five's conventions (24x24 viewBox, fill none, stroke currentColor,
  stroke-width 2, round caps and joins) and survives the compiler's own geometry filter (`icon_geometry`);
* the intake record (assets/icons/SOURCES.md) names every file's upstream URL pinned to the set's tag, the set,
  the version and the ISC licence, whose text is committed beside the files - and names no file that is absent;
* every glyph RENDERS, through the geometry the compiler embeds, at the chip's size (CHIP.GLYPH) and at the
  smallest a flow node is ever drawn (CHIP.GLYPH x FLOW.MIN_K): ink on the canvas that spans its box.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ICONS = B.ICONS_DIR
SOURCES_MD = ICONS / "SOURCES.md"
LICENSE = ICONS / "LICENSE.lucide.txt"
SPECIES = ROOT / "content/video_engine/scripts/species"

# the five P50 shipped, and the supply chain P73 T4 adds (the slice's list; container beside the ship, both the
# antenna and the radio, building and user as the company and the buyer, users for a crowd of them)
FIRST_FIVE = ("coins", "cpu", "factory", "landmark", "ship")
SUPPLY_CHAIN = ("warehouse", "store", "truck", "container", "plane", "shield", "radar", "antenna", "radio", "tag",
                "scale", "flag", "globe", "building", "user", "users")
# the five's root attributes, exactly (Lucide's own drawing conventions)
CONVENTIONS = {"width": "24", "height": "24", "viewBox": "0 0 24 24", "fill": "none", "stroke": "currentColor",
               "stroke-width": "2", "stroke-linecap": "round", "stroke-linejoin": "round"}
MIN_INK = 0.03     # the share of the glyph's box a rendered glyph inks, at least (a blank or a speck fails)
MIN_SPAN = 0.6     # ... and the share of the box its ink spans on the longer axis (Lucide draws to ~20 of 24 units)


def _svgs() -> list[str]:
    return sorted(p.stem for p in ICONS.glob("*.svg"))


def _mjs_const(path: Path, name: str) -> float:
    """One numeric dial from a species module's frozen table (`NAME: 92,`) - the test reads the engine's own size."""
    m = re.search(rf"^\s*{name}:\s*([0-9.]+),", path.read_text(encoding="utf-8"), re.M)
    assert m, f"{name} not found in {path.name}"
    return float(m.group(1))


def _record() -> tuple[dict[str, str], dict[str, str]]:
    """(the Set table's fields, {file: upstream URL}) from the intake record."""
    text = SOURCES_MD.read_text(encoding="utf-8")
    fields = {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^\|\s*(\w+)\s*\|\s*(.+?)\s*\|\s*$", text, re.M)}
    files = {m.group(1): m.group(2) for m in re.finditer(r"^\|\s*`([a-z0-9-]+\.svg)`\s*\|\s*(\S+)\s*\|", text, re.M)}
    return fields, files


def test_the_supply_chain_glyphs_are_in_the_folder() -> None:
    missing = [n for n in (*FIRST_FIVE, *SUPPLY_CHAIN) if not B.icon_file(n).is_file()]
    assert not missing, f"no sourced SVG for {missing} - fetch them per assets/icons/SOURCES.md"


@pytest.mark.parametrize("name", SUPPLY_CHAIN + FIRST_FIVE)
def test_every_glyph_keeps_the_five_s_conventions_and_survives_the_compiler(name: str) -> None:
    root = ET.fromstring(B.icon_file(name).read_text(encoding="utf-8"))
    assert root.tag.split("}")[-1] == "svg"
    assert {k: root.get(k) for k in CONVENTIONS} == CONVENTIONS, f"{name}.svg departs from the five's drawing conventions"
    geo = json.loads(B.icon_geometry(name))
    assert geo["vb"] == [0, 0, 24, 24] and geo["el"], f"{name}: nothing survives the compiler's geometry filter"
    assert all(e["t"] in B.ICON_TAGS for e in geo["el"])


def test_the_intake_record_names_every_file_its_source_and_licence() -> None:
    fields, files = _record()
    assert fields.get("set", "").strip("*") == "Lucide"
    version = fields.get("version", "").split()[0].strip("*")
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), f"the record pins no version: {fields.get('version')!r}"
    assert "ISC" in fields.get("license", "") and "LICENSE.lucide.txt" in fields.get("license", "")
    assert LICENSE.read_text(encoding="utf-8").startswith("ISC License"), "the licence text is not committed beside the files"
    on_disk = {f"{n}.svg" for n in _svgs()}
    assert set(files) == on_disk, f"unrecorded: {sorted(on_disk - set(files))}; recorded but absent: {sorted(set(files) - on_disk)}"
    wrong = {f: u for f, u in files.items()
             if u != f"https://raw.githubusercontent.com/lucide-icons/lucide/{version}/icons/{f}"}
    assert not wrong, f"not pinned to the tag {version}: {wrong}"


PAGE = """<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff"><script>
window.inkOf = async (geo, size) => {
  const ns = "http://www.w3.org/2000/svg", svg = document.createElementNS(ns, "svg");
  svg.setAttribute("xmlns", ns); svg.setAttribute("width", size); svg.setAttribute("height", size);
  svg.setAttribute("viewBox", geo.vb.join(" "));
  const g = document.createElementNS(ns, "g");   /* the chip's own paint: chalk strokes, no fill, round ends */
  for (const [k, v] of Object.entries({fill: "none", stroke: "#000", "stroke-width": 2, "stroke-linecap": "round",
                                       "stroke-linejoin": "round"})) g.setAttribute(k, v);
  for (const e of geo.el) { const n = document.createElementNS(ns, e.t);
    for (const [k, v] of Object.entries(e.a)) n.setAttribute(k, v); g.appendChild(n); }
  svg.appendChild(g);
  const img = new Image(), px = Math.round(size);
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new XMLSerializer().serializeToString(svg));
  await img.decode();
  const c = document.createElement("canvas"); c.width = c.height = px;
  const ctx = c.getContext("2d"); ctx.drawImage(img, 0, 0, px, px);
  const d = ctx.getImageData(0, 0, px, px).data;
  let ink = 0, x0 = px, y0 = px, x1 = -1, y1 = -1;
  for (let y = 0; y < px; y++) for (let x = 0; x < px; x++) if (d[(y * px + x) * 4 + 3] > 64) {
    ink++; x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return {px, ink: ink / (px * px), span: Math.max(x1 - x0 + 1, y1 - y0 + 1) / px};
};
</script>"""


def test_every_glyph_renders_at_the_chip_and_the_node_floor(tmp_path: Path) -> None:
    chip = _mjs_const(SPECIES / "chip.mjs", "GLYPH")                  # 92: the glyph's box on a chip card
    node = chip * _mjs_const(SPECIES / "flow.mjs", "MIN_K")           # 36.8: a flow node at the smallest it is drawn
    html = tmp_path / "icons.html"
    html.write_text(PAGE, encoding="utf-8")
    bad = {}
    with SP.served(html, 400, 300, prepare=False) as (page, errs):
        for name in (*SUPPLY_CHAIN, *FIRST_FIVE):
            geo = json.loads(B.icon_geometry(name))
            for label, size in (("chip", chip), ("node", node)):
                r = page.evaluate("([g, s]) => window.inkOf(g, s)", [geo, size])
                if r["ink"] < MIN_INK or r["span"] < MIN_SPAN:
                    bad[f"{name}@{label}"] = r
        assert not errs, errs
    assert not bad, f"a glyph that does not read at its size: {bad}"
