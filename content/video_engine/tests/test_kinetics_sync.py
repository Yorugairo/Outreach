"""P43 T1: the kinetics modules are the source of truth and the template carries an exact
inlined copy of each. `sync_kinetics.py --check` is the contract; these tests pin that it
passes on the committed tree, that it FAILS on drift, that the module syntax is stripped, and
that the write is idempotent (so a --write after a clean --check changes nothing)."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import sync_kinetics as SK  # noqa: E402

MODULES = ["ease", "spring", "stroke", "ink", "squash"]   # the T1 set; later slices append here in the same commit as their module


def test_committed_template_is_in_sync() -> None:
    assert SK.check() == []


def test_every_t1_module_exists_and_has_one_region() -> None:
    html = SK.TEMPLATE.read_text(encoding="utf-8")
    for name in MODULES:
        assert (SK.MODULES / f"{name}.mjs").is_file()
        assert html.count(f"/* KINETICS:BEGIN {name} */") == 1, name
    assert html.count("/* KINETICS:BEGIN ") == html.count("/* KINETICS:END */")


def test_the_moved_functions_are_still_defined_in_the_template() -> None:
    html = SK.TEMPLATE.read_text(encoding="utf-8")
    for fn in ("const minJerk = (u) =>", "const springPop = (u, Mp = 0.04) =>"):
        assert html.count(fn) == 1, fn
    # and nothing that only means something to node survived the inlining
    for m in SK.REGION.finditer(html.replace("\r\n", "\n")):
        assert not re.search(r"^\s*(import|export)\b", m.group(3), re.M), m.group(2)


def test_inline_text_strips_module_syntax() -> None:
    src = 'import { a } from "./ease.mjs";\nexport const b = (u) => a(u);\nexport function c() {}\nexport { b };\n'
    assert SK.inline_text(src, "  ") == "  const b = (u) => a(u);\n  function c() {}"
    with pytest.raises(ValueError):
        SK.inline_text("export default 1;\n")


def test_drift_is_detected(tmp_path: Path) -> None:
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    html = tpl.read_text(encoding="utf-8")
    drifted = html.replace("10 - 15 * u + 6 * u * u", "10 - 15 * u + 7 * u * u", 1)
    assert drifted != html
    tpl.write_text(drifted, encoding="utf-8")
    problems = SK.check(tpl)
    assert problems and problems[0].startswith("ease: drift"), problems


def test_missing_region_and_missing_module_are_reported(tmp_path: Path) -> None:
    mods = tmp_path / "kinetics"
    mods.mkdir()
    for name in MODULES:
        shutil.copy(SK.MODULES / f"{name}.mjs", mods / f"{name}.mjs")
    (mods / "orphan.mjs").write_text("export const orphan = 1;\n", encoding="utf-8")
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    assert SK.check(tpl, mods) == ["orphan: kinetics/orphan.mjs has no region in the template"]
    html = tpl.read_text(encoding="utf-8").replace("/* KINETICS:BEGIN spring */", "/* KINETICS:BEGIN ghost */", 1)
    tpl.write_text(html, encoding="utf-8")
    problems = SK.check(tpl, mods)
    assert any(p.startswith("ghost: region in the template but no") for p in problems), problems
    assert any(p.startswith("spring: kinetics/spring.mjs has no region") for p in problems), problems


def test_import_order_is_the_dependency(tmp_path: Path) -> None:
    mods = tmp_path / "kinetics"
    mods.mkdir()
    (mods / "a.mjs").write_text('import { b } from "./b.mjs";\nexport const a = () => b();\n', encoding="utf-8")
    (mods / "b.mjs").write_text("export const b = () => 1;\n", encoding="utf-8")
    tpl = tmp_path / "t.html"
    tpl.write_text("<script>\n  /* KINETICS:BEGIN a */\n  /* KINETICS:END */\n  /* KINETICS:BEGIN b */\n  /* KINETICS:END */\n</script>\n",
                   encoding="utf-8")
    assert SK.write(tpl, mods) == 2
    assert SK.check(tpl, mods) == ["a: imports b but b's region is not earlier in the template"]


def test_write_is_idempotent_and_keeps_the_line_endings(tmp_path: Path) -> None:
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    before = tpl.read_bytes()
    assert SK.write(tpl) == len(MODULES)
    assert tpl.read_bytes() == before
