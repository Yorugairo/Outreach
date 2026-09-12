"""P43 T1: the kinetics modules are the source of truth and the ENGINE carries an exact
inlined copy of each (P51 T1 moved the regions out of the page and into scene-evidence-engine.mjs). `sync_kinetics.py --check` is the contract; these tests pin that it
passes on the committed tree, that it FAILS on drift, that the module syntax is stripped, and
that the write is idempotent (so a --write after a clean --check changes nothing).

P50 T2 widens the contract to a SECOND module dir - content/video_engine/scripts/species/, one
painter per species kind (the operator's module rule, 2026-09-11: no new species is written into
the engine's body). Both dirs are scanned into one name space, with the same region grammar,
the same missing-region / missing-module report and the same import-order rule; the tests below
pin each of those three.

P52 T5 (R26-41) adds THE SPACE: a species module may declare `/* SPACE: page */` or
`/* SPACE: stage */` on its first line, and `--check` holds it to the registry that space paints
through - PAGE_PAINTERS for the page's perform layer, SPECIES_PAINTERS for the stage overlay -
and to a region placed where that registration can be reached and the painter closed over. The
tests below pin the declaration on span (the first page species), both wrong-registry directions
with the space named in the message, the region-order rule and the default (no declaration is
stage, which is why no module written before P52 T5 had to change)."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import sync_kinetics as SK  # noqa: E402

MODULES = ["ease", "spring", "stagger",   # P52 T10: the caption's stagger envelope - after spring, before the caption block uses it
           "stroke", "clothoid", "ink", "squash", "idle", "stopaction", "homography", "chartxf",
           "camera", "arap",   # P50 T7 (homography): the planar projection that lands a card on a plate's declared surface - it imports nothing, and its region sits after the stop action whose impact it composes with
           "morph_a"]   # P43 T1 + P47 T5/T1/T3 + P50 T12 (morph_a: doc 43 s43.5 Method A, after arap - it imports it)
                                              # + P50 T14 the clothoid fitter, beside the stroke it is drawn by; in dependency order (the template's region order)
SPECIES = ["tiers", "treemap", "breakthrough", "chip", "press", "flow", "span", "vecmap",
           "thread",    # P50 T15 / HF-16: the WIRE - a page species' carry math, so it registers no painter either (span's case)
           "tippill",   # P50 T11: R26-34's pill - a line PAGE's option rather than a targeted kind, so it registers no painter   # P50 T2 on: one module per species kind, inlined into the species block; `press` is the
           "newsreel", "countarray", "agenda", "ring", "melt"]   # P52 T6 / T7 / T8 / T9: the wave-3 species, in the engine's region order (melt registers no painter - an exit)
                              # `breakthrough` (P50 T10/T13) is a third that registers no painter: the burst is a PAGE
                              # mechanic painted by lpPaintBreakthrough off the page's build clock, and it PREDATES the
                              # module rule - only its new math (the placeholder, the axis capsule, the stepped cadence)
                              # moved here. Its region sits with the kinetics laws, after stopaction, whose cadence it reads.
                              # `tiers` (P50 T9) and `treemap` (P50 T6) are neither kinds nor painters: they are the math of
                              # two PAGE BUILDERS - the bands of a small-multiple page, and the clock and X marks of a census
                              # page whose layout is python's. Their regions sit with the kinetics laws, and first, because
                              # the page's builders and its perform layer both close over them.
                              # one that is not a KIND (P50 T3: the press card is a DOCK kind) - it carries the stack's math
                              # and the underline's clock for the dock loop and the callout, and registers no painter.
                              # `span` (P50 T4) is a KIND and, since P52 T5 (R26-41), registers paintSpan into the PAGE
                              # registry - PAGE_PAINTERS, not SPECIES_PAINTERS: a page species is painted by the page's
                              # perform layer, in the chart's viewBox, so its region sits with the kinetics laws where that
                              # layer can close over it. `flow` registers paintFlow the way the chip does. `vecmap` (P50 T5)
                              # registers THREE painters (light, arc, stamp) and also carries the WORLD the three paint on -
                              # the template's vecmap branch calls paintVecmapWorld, so the map's fit lives with its species.


def test_committed_engine_is_in_sync() -> None:
    assert SK.check() == []


def test_every_t1_module_exists_and_has_one_region() -> None:
    html = SK.ENGINE.read_text(encoding="utf-8")
    for name in MODULES:
        assert (SK.MODULES / f"{name}.mjs").is_file()
        assert html.count(f"/* KINETICS:BEGIN {name} */") == 1, name
    assert html.count("/* KINETICS:BEGIN ") == html.count("/* KINETICS:END */")


def test_the_moved_functions_are_still_defined_in_the_template() -> None:
    html = SK.ENGINE.read_text(encoding="utf-8")
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
    shutil.copy(SK.ENGINE, tpl)
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
    shutil.copy(SK.ENGINE, tpl)
    assert SK.check(tpl, mods, SK.SPECIES_DIR) == ["orphan: kinetics/orphan.mjs has no region in the engine"]
    html = tpl.read_text(encoding="utf-8").replace("/* KINETICS:BEGIN spring */", "/* KINETICS:BEGIN ghost */", 1)
    tpl.write_text(html, encoding="utf-8")
    problems = SK.check(tpl, mods, SK.SPECIES_DIR)
    assert any(p.startswith("ghost: region in the engine but no") for p in problems), problems
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
    assert SK.check(tpl, mods, None) == ["a: imports b but b's region is not earlier in the engine"]


def test_write_is_idempotent_and_keeps_the_line_endings(tmp_path: Path) -> None:
    tpl = tmp_path / "t.html"
    shutil.copy(SK.ENGINE, tpl)
    before = tpl.read_bytes()
    assert SK.write(tpl) == len(MODULES) + len(SPECIES)
    assert tpl.read_bytes() == before


# ---- P50 T2: the SECOND module dir (the operator's module rule, 2026-09-11) --------------------

def test_both_dirs_are_scanned_into_one_name_space() -> None:
    """Every species module is found beside every kinetics module, and each has exactly one region."""
    names = SK.module_files()
    assert set(MODULES) | set(SPECIES) <= set(names)
    html = SK.ENGINE.read_text(encoding="utf-8")
    for name in SPECIES:
        assert (SK.SPECIES_DIR / f"{name}.mjs").is_file(), name
        assert names[name].parent == SK.SPECIES_DIR, name
        assert html.count(f"/* KINETICS:BEGIN {name} */") == 1, name


def test_a_species_module_with_no_region_fails_check_by_name(tmp_path: Path) -> None:
    sp = tmp_path / "species"
    sp.mkdir()
    (sp / "nowhere.mjs").write_text("export const paintNowhere = () => 1;\n", encoding="utf-8")
    tpl = tmp_path / "t.html"
    shutil.copy(SK.ENGINE, tpl)
    problems = SK.check(tpl, SK.MODULES, sp)
    assert "nowhere: species/nowhere.mjs has no region in the engine" in problems, problems
    # ... and the reverse, the same way a kinetics region does: a region with no module names both dirs
    html = tpl.read_text(encoding="utf-8").replace("/* KINETICS:BEGIN chip */", "/* KINETICS:BEGIN phantom */", 1)
    tpl.write_text(html, encoding="utf-8")
    assert any(p == "phantom: region in the engine but no kinetics/phantom.mjs or species/phantom.mjs"
               for p in SK.check(tpl, SK.MODULES, sp)), SK.check(tpl, SK.MODULES, sp)


def test_a_name_in_both_dirs_is_refused(tmp_path: Path) -> None:
    mods, sp = tmp_path / "kinetics", tmp_path / "species"
    mods.mkdir(); sp.mkdir()
    (mods / "twin.mjs").write_text("export const twin = 1;\n", encoding="utf-8")
    (sp / "twin.mjs").write_text("export const twin = 2;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="one name space"):
        SK.module_files(mods, sp)
    tpl = tmp_path / "t.html"
    shutil.copy(SK.ENGINE, tpl)
    problems = SK.check(tpl, mods, sp)
    assert len(problems) == 1 and problems[0].startswith("twin: a module of that name in both"), problems


def test_a_species_module_may_import_a_kinetics_module_whose_region_is_earlier() -> None:
    """The import-order rule across the two dirs: chip reaches spring / idle as ../kinetics/<name>.mjs,
    and their regions sit earlier in the template - which is why the committed tree is in sync."""
    src = (SK.SPECIES_DIR / "chip.mjs").read_text(encoding="utf-8")
    deps = SK.imports_of(src)
    assert "spring" in deps, deps
    html = SK.ENGINE.read_text(encoding="utf-8")
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
    assert "SPECIES_PAINTERS.chip = paintChip;" in SK.ENGINE.read_text(encoding="utf-8")


# ---- P52 T5: THE SPACE a species is painted in (R26-41) ----------------------------------------

PAGE_MODULE = """/* SPACE: page */
/* a page species, painted by the perform layer in the chart's viewBox */
export const paintMine = (sd, t, st, ctx) => ctx.pointsNow(st, sd.si);
if (typeof REGISTRY !== "undefined") REGISTRY.mine = paintMine;
"""

STAGE_MODULE = """/* a stage species, painted on the stage-px overlay - it declares nothing, which IS the declaration */
export const paintYours = (ctx) => ctx.svg;
if (typeof REGISTRY !== "undefined") REGISTRY.yours = paintYours;
"""

SYNTH_ENGINE = """<script>
  const PAGE_PAINTERS = Object.create(null);
  /* KINETICS:BEGIN mine */
  /* KINETICS:END */
  const paintPerform = (st, scene, t, pg) => {};
  const SPECIES_PAINTERS = Object.create(null);
  /* KINETICS:BEGIN yours */
  /* KINETICS:END */
</script>
"""


def _synth(tmp_path: Path, mine: str, yours: str, engine: str = SYNTH_ENGINE) -> tuple[Path, Path, Path]:
    """A two-region engine with both registries and a perform layer, and the two modules that fill it."""
    mods, sp = tmp_path / "kinetics", tmp_path / "species"
    mods.mkdir(parents=True); sp.mkdir(parents=True)
    (sp / "mine.mjs").write_text(mine, encoding="utf-8")
    (sp / "yours.mjs").write_text(yours, encoding="utf-8")
    tpl = tmp_path / "engine.mjs"
    tpl.write_text(engine, encoding="utf-8")
    assert SK.write(tpl, mods, sp) == 2
    return tpl, mods, sp


def test_span_declares_the_page_space_and_registers_into_the_page_registry() -> None:
    """The first page species through the registry (R26-41): the declaration, the registration and
    the region's place - before paintPerform, which closes over the painter it calls."""
    src = (SK.SPECIES_DIR / "span.mjs").read_text(encoding="utf-8")
    assert SK.space_of(src) == "page"
    assert SK.registrations_of(src) == [("PAGE_PAINTERS", "span")]
    assert "PAGE_PAINTERS.span = paintSpan;" in SK.inline_text(src, "  ")
    html = SK.ENGINE.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "PAGE_PAINTERS.span = paintSpan;" in html
    decl, region = html.index("const PAGE_PAINTERS = Object.create(null);"), html.index("/* KINETICS:BEGIN span */")
    assert decl < region < SK.PERFORM_DEF.search(html).start()
    # ... and the perform layer paints no span of its own: the engine's body signature is gone and
    # the only page-registry lookup in the engine is the hook
    assert "const paintSpan = (sd, t, st) =>" not in html
    assert html.count("PAGE_PAINTERS[") == 1, "one hook, no second route into the page registry"


def test_a_page_module_that_registers_into_the_stage_registry_fails_by_space(tmp_path: Path) -> None:
    tpl, mods, sp = _synth(tmp_path, PAGE_MODULE.replace("REGISTRY", "SPECIES_PAINTERS"),
                           STAGE_MODULE.replace("REGISTRY", "SPECIES_PAINTERS"))
    problems = SK.check(tpl, mods, sp)
    assert problems == ["species/mine.mjs declares SPACE: page but registers into SPECIES_PAINTERS "
                        "(the stage registry) - a page species registers into PAGE_PAINTERS"], problems


def test_a_stage_module_that_registers_into_the_page_registry_fails_the_same_way(tmp_path: Path) -> None:
    tpl, mods, sp = _synth(tmp_path, PAGE_MODULE.replace("REGISTRY", "PAGE_PAINTERS"),
                           STAGE_MODULE.replace("REGISTRY", "PAGE_PAINTERS"))
    problems = SK.check(tpl, mods, sp)
    assert problems == ["species/yours.mjs declares SPACE: stage but registers into PAGE_PAINTERS "
                        "(the page registry) - a stage species registers into SPECIES_PAINTERS"], problems


def test_a_module_with_no_declaration_is_stage() -> None:
    """Why no existing species had to be touched: stage is the default, and every species written
    before P52 T5 paints there. A module that registers no painter is held to nothing at all."""
    assert SK.space_of(STAGE_MODULE) == "stage"
    assert SK.space_of((SK.SPECIES_DIR / "chip.mjs").read_text(encoding="utf-8")) == "stage"
    assert SK.space_of((SK.MODULES / "ease.mjs").read_text(encoding="utf-8")) == "stage"
    for name in ("press", "tippill", "thread", "tiers", "treemap", "breakthrough"):
        src = (SK.SPECIES_DIR / f"{name}.mjs").read_text(encoding="utf-8")
        assert SK.registrations_of(src) == [], name
        assert SK.space_problems(SK.SPECIES_DIR / f"{name}.mjs", src, "", 0) == [], name


def test_a_space_nobody_paints_in_is_refused(tmp_path: Path) -> None:
    tpl, mods, sp = _synth(tmp_path, PAGE_MODULE.replace("SPACE: page", "SPACE: overlay").replace("REGISTRY", "PAGE_PAINTERS"),
                           STAGE_MODULE.replace("REGISTRY", "SPECIES_PAINTERS"))
    problems = SK.check(tpl, mods, sp)
    assert problems == ["species/mine.mjs declares SPACE: overlay - the only spaces are page and stage "
                        "(a module that paints nothing declares neither)"], problems


def test_a_page_region_after_the_perform_layer_fails_on_the_order(tmp_path: Path) -> None:
    """The order IS the dependency (the inlined copy has no imports): a page painter that lands
    after paintPerform is not there to be closed over, and a registration before its registry's
    declaration cannot reach it."""
    late = """<script>
  const PAGE_PAINTERS = Object.create(null);
  const paintPerform = (st, scene, t, pg) => {};
  /* KINETICS:BEGIN mine */
  /* KINETICS:END */
  const SPECIES_PAINTERS = Object.create(null);
  /* KINETICS:BEGIN yours */
  /* KINETICS:END */
</script>
"""
    tpl, mods, sp = _synth(tmp_path, PAGE_MODULE.replace("REGISTRY", "PAGE_PAINTERS"),
                           STAGE_MODULE.replace("REGISTRY", "SPECIES_PAINTERS"), late)
    problems = SK.check(tpl, mods, sp)
    assert problems == ["species/mine.mjs declares SPACE: page but its region sits AFTER the engine's "
                        "paintPerform, which has to close over the painter it calls"], problems
    early = late.replace("  const PAGE_PAINTERS = Object.create(null);\n", "") \
                .replace("</script>", "  const PAGE_PAINTERS = Object.create(null);\n</script>")
    tpl2, mods2, sp2 = _synth(tmp_path / "b", PAGE_MODULE.replace("REGISTRY", "PAGE_PAINTERS"),
                              STAGE_MODULE.replace("REGISTRY", "SPECIES_PAINTERS"), early)
    problems = SK.check(tpl2, mods2, sp2)
    assert any("sits BEFORE the engine's PAGE_PAINTERS declaration" in p for p in problems), problems
