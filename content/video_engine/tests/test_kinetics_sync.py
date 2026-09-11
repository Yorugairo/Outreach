"""P43 T1: the kinetics modules are the source of truth and the template carries an exact
inlined copy of each. `sync_kinetics.py --check` is the contract; these tests pin that it
passes on the committed tree, that it FAILS on drift, that the module syntax is stripped, and
that the write is idempotent (so a --write after a clean --check changes nothing).

P50 T2 widens the contract to a SECOND module dir - content/video_engine/scripts/species/, one
painter per species kind (the operator's module rule, 2026-09-11: no new species is written into
the template's body). Both dirs are scanned into one name space, with the same region grammar,
the same missing-region / missing-module report and the same import-order rule; the tests below
pin each of those three."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import sync_kinetics as SK  # noqa: E402

MODULES = ["ease", "spring", "stroke", "ink", "squash", "idle", "stopaction", "chartxf", "camera", "arap"]   # P43 T1 + P47 T5/T1/T3, in dependency order (the template's region order)
SPECIES = ["chip", "press"]   # P50 T2 on: one module per species kind, inlined into the species block; `press` is the
                              # one that is not a KIND (P50 T3: the press card is a DOCK kind) - it carries the stack's math
                              # and the underline's clock for the dock loop and the callout, and registers no painter


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
    # and nothing that only means something to node survived the inlining. CODE lines only: a block
    # comment may legitimately begin a line with the word `import` (chip.mjs's does, and that is exactly
    # what used to be stripped - test_a_comment_line_beginning_with_import_is_not_stripped below).
    for m in SK.REGION.finditer(html.replace("\r\n", "\n")):
        in_block = False
        for line in m.group(3).split("\n"):
            if not in_block:
                assert not re.match(r"^\s*(import|export)\b", line), (m.group(2), line)
            in_block = SK._block_state(line, in_block)


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
    assert SK.check(tpl, mods, SK.SPECIES_DIR) == ["orphan: kinetics/orphan.mjs has no region in the template"]
    html = tpl.read_text(encoding="utf-8").replace("/* KINETICS:BEGIN spring */", "/* KINETICS:BEGIN ghost */", 1)
    tpl.write_text(html, encoding="utf-8")
    problems = SK.check(tpl, mods, SK.SPECIES_DIR)
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
    assert SK.write(tpl, mods, None) == 2
    assert SK.check(tpl, mods, None) == ["a: imports b but b's region is not earlier in the template"]


def test_write_is_idempotent_and_keeps_the_line_endings(tmp_path: Path) -> None:
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    before = tpl.read_bytes()
    assert SK.write(tpl) == len(MODULES) + len(SPECIES)
    assert tpl.read_bytes() == before


# ---- P50 T2: the SECOND module dir (the operator's module rule, 2026-09-11) --------------------

def test_both_dirs_are_scanned_into_one_name_space() -> None:
    """Every species module is found beside every kinetics module, and each has exactly one region."""
    names = SK.module_files()
    assert set(MODULES) | set(SPECIES) <= set(names)
    html = SK.TEMPLATE.read_text(encoding="utf-8")
    for name in SPECIES:
        assert (SK.SPECIES_DIR / f"{name}.mjs").is_file(), name
        assert names[name].parent == SK.SPECIES_DIR, name
        assert html.count(f"/* KINETICS:BEGIN {name} */") == 1, name


def test_a_species_module_with_no_region_fails_check_by_name(tmp_path: Path) -> None:
    sp = tmp_path / "species"
    sp.mkdir()
    (sp / "nowhere.mjs").write_text("export const paintNowhere = () => 1;\n", encoding="utf-8")
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    problems = SK.check(tpl, SK.MODULES, sp)
    assert "nowhere: species/nowhere.mjs has no region in the template" in problems, problems
    # ... and the reverse, the same way a kinetics region does: a region with no module names both dirs
    html = tpl.read_text(encoding="utf-8").replace("/* KINETICS:BEGIN chip */", "/* KINETICS:BEGIN phantom */", 1)
    tpl.write_text(html, encoding="utf-8")
    assert any(p == "phantom: region in the template but no kinetics/phantom.mjs or species/phantom.mjs"
               for p in SK.check(tpl, SK.MODULES, sp)), SK.check(tpl, SK.MODULES, sp)


def test_a_name_in_both_dirs_is_refused(tmp_path: Path) -> None:
    mods, sp = tmp_path / "kinetics", tmp_path / "species"
    mods.mkdir(); sp.mkdir()
    (mods / "twin.mjs").write_text("export const twin = 1;\n", encoding="utf-8")
    (sp / "twin.mjs").write_text("export const twin = 2;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="one name space"):
        SK.module_files(mods, sp)
    tpl = tmp_path / "t.html"
    shutil.copy(SK.TEMPLATE, tpl)
    problems = SK.check(tpl, mods, sp)
    assert len(problems) == 1 and problems[0].startswith("twin: a module of that name in both"), problems


def test_a_species_module_may_import_a_kinetics_module_whose_region_is_earlier() -> None:
    """The import-order rule across the two dirs: chip reaches spring / idle as ../kinetics/<name>.mjs,
    and their regions sit earlier in the template - which is why the committed tree is in sync."""
    src = (SK.SPECIES_DIR / "chip.mjs").read_text(encoding="utf-8")
    deps = SK.imports_of(src)
    assert "spring" in deps, deps
    html = SK.TEMPLATE.read_text(encoding="utf-8")
    order = [m.group(2) for m in SK.REGION.finditer(html.replace("\r\n", "\n"))]
    for dep in deps:
        assert order.index(dep) < order.index("chip"), dep


def test_a_comment_line_beginning_with_import_is_not_stripped() -> None:
    """The sharp edge P50 T2 hit (2026-09-11): a block comment whose continuation line began with
    the word `import` was dropped, the comment was left UNCLOSED, and it swallowed the code after
    it - silently, because the template still parsed. The chip's painter registered into nothing
    and the species painted no pixels. Module syntax is stripped outside a block comment only."""
    src = "/* a note\n   import this file for the math */\nexport const a = 1;\n"
    assert SK.inline_text(src, "") == "/* a note\n   import this file for the math */\nconst a = 1;"
    # a real import is still stripped, and so is an `export {...}` list
    assert SK.inline_text('import { b } from "./b.mjs";\nexport const c = b;\nexport { c };\n', "") == "const c = b;"
    # ... and the species module that found it keeps its registration through the inlining
    chip = (SK.SPECIES_DIR / "chip.mjs").read_text(encoding="utf-8")
    assert "SPECIES_PAINTERS.chip = paintChip;" in SK.inline_text(chip, "  ")
    assert "SPECIES_PAINTERS.chip = paintChip;" in SK.TEMPLATE.read_text(encoding="utf-8")
