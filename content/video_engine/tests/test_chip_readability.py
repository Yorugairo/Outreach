"""Opt-in chip readability checks against the native JavaScript painter."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]
CHIP = ROOT / "content/video_engine/scripts/species/chip.mjs"
NODE = shutil.which("node") or shutil.which("node.exe")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is required for native chip painter checks")


def _paint(spec: dict) -> dict:
    module = json.dumps(CHIP.resolve().as_uri())
    payload = json.dumps(spec)
    source = f"""
import {{ CHIP, chipLabelLines, paintChip }} from {module};
const sp = {payload};
const made = [];
const el = (tag, cls, parent, at) => {{
  const e = {{tag, cls, at: Object.assign({{}}, at || {{}}), kids: [], textContent: "",
    setAttribute(k, v) {{ this.at[k] = v; }},
    getAttribute(k) {{ return this.at[k]; }}
  }};
  made.push(e);
  if (parent && parent.kids) parent.kids.push(e);
  return e;
}};
const icon = JSON.stringify({{vb: [0, 0, 24, 24], el: [{{t: "path", a: {{d: "M12 16h.01"}}}}]}});
paintChip({{
  sp, t: 5, svg: {{kids: []}}, el, A: {{"icon:factory": icon}},
  resolveTarget: (target) => target ? {{x: 960, y: 540, w: 0, h: 0}} : null,
  drawOn: (path, fraction) => path.setAttribute("stroke-dashoffset", fraction.toFixed(3)),
  hash: () => 0.5, idle: () => ({{scale: 1, dx: 0, dy: 0}}), seed: 1, si: 0
}});
const pack = (entry) => ({{tag: entry.tag, cls: entry.cls, at: entry.at, text: entry.textContent,
  kids: entry.kids.map(pack)}});
console.log(JSON.stringify({{made: made.map(pack), lines: chipLabelLines(sp.label), dials: CHIP}}));
"""
    result = subprocess.run([NODE, "--input-type=module", "-e", source], check=True,
                            capture_output=True, text=True)
    return json.loads(result.stdout)


def _one(data: dict, cls: str) -> dict:
    matches = [entry for entry in data["made"] if entry["cls"] == cls]
    assert len(matches) == 1, (cls, data["made"])
    return matches[0]


def test_legacy_chip_label_path_is_unchanged_without_profile():
    data = _paint({"kind": "chip", "at": 4, "dur": 6, "icon": "factory",
                   "label": "LEGACY\nLABEL", "target": {"kind": "point", "x": .5, "y": .5}})
    label = _one(data, "chiplab")
    assert label["text"] == "LEGACY\nLABEL"
    assert label["kids"] == []
    assert "style" not in label["at"]
    assert "style" not in _one(data, "chipcard")["at"]


def test_landscape_phone_chip_uses_high_contrast_three_line_tspans():
    data = _paint({"kind": "chip", "at": 4, "dur": 6, "icon": "factory",
                   "label": "BANK\nFED\nACCOUNTS\nOVERFLOW", "readability": "landscape-phone",
                   "target": {"kind": "point", "x": .5, "y": .5}})
    label = _one(data, "chiplab")
    style = label["at"]["style"]
    assert "font-size:45px" in style and "font-weight:700" in style
    assert "fill:#25313C" in style and "stroke:#F4E6C7" in style
    assert [child["text"] for child in label["kids"]] == ["BANK", "FED", "ACCOUNTS OVERFLOW"]
    assert [child["at"]["dy"] for child in label["kids"]] == [0, 48, 48]
    assert len(label["kids"]) == 3
    assert "fill:#F4E6C7" in _one(data, "chipcard")["at"]["style"]
    assert "stroke:#25313C" in _one(data, "chipglyph")["at"]["style"]
    assert len(data["lines"]) == 3


def test_phone_paint_is_seek_deterministic_and_line_count_is_bounded():
    spec = {"kind": "chip", "at": 4, "dur": 6, "icon": "factory",
            "label": "A\nB\nC\nD\nE", "readability": "landscape-phone",
            "target": {"kind": "point", "x": .5, "y": .5}}
    first, second = _paint(spec), _paint(spec)
    assert first == second
    assert 1 <= len(first["lines"]) <= 3
    assert all("\n" not in line for line in first["lines"])
