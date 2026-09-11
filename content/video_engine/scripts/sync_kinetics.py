"""Inline the kinetics and species modules into the scene-evidence ENGINE (P43 T1; P38 T1's design).

Two things must both hold: the engine carries its own math (no runtime imports - P51 T1 split the
runtime out of the page, not into a module graph), and that math is reachable by `node --test`.
Both do when each `.mjs` module under
content/video_engine/scripts/kinetics/ (the motion laws) or content/video_engine/scripts/species/
(one painter per species kind, P50 T2's module rule) is the source of truth and its text is
physically copied into the engine between markers:

    /* KINETICS:BEGIN <name> */
    ...the module, export/import syntax stripped, indented to the marker...
    /* KINETICS:END */

    python sync_kinetics.py --check    # exit 1 when any inlined copy drifts from its module
    python sync_kinetics.py --write    # rewrite every region from its module

Rules: `export const|let|function|class` loses the `export`; `import` lines and `export {...}`
lists are dropped; `export default` is refused. A module may import another module only when
that module's region sits EARLIER in the engine - the inlined copy has no imports, so order
is the dependency; a species module reaches a kinetics module as `../kinetics/<name>.mjs` and
the same order rule applies across the two dirs. The two dirs share ONE name space (a name in
both is refused), every module has exactly one region and every region one module.

THE MODULE RULE (the operator, 2026-09-11): from P50 T2 on, no new species is written into the
engine's body. A species is a module here that registers its painter as its last statement -
`if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.<kind> = paint<Kind>;` - a plain
assignment, so inlining keeps it and `node --test` (where SPECIES_PAINTERS does not exist) still
imports the module for its pure math.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TEMPLATE = ENGINE      # kept as an alias: every caller means "the file the regions live in"
MODULES = REPO / "content/video_engine/scripts/kinetics"
SPECIES_DIR = REPO / "content/video_engine/scripts/species"

REGION = re.compile(r"^([ \t]*)/\* KINETICS:BEGIN (\w+) \*/\n(.*?)^[ \t]*/\* KINETICS:END \*/", re.M | re.S)
IMPORT = re.compile(r"^\s*import\b.*?\bfrom\s+[\"']\.{1,2}/(?:\w+/)?(\w+)\.mjs[\"'];?\s*$", re.M)
EXPORT_DECL = re.compile(r"^(\s*)export\s+((?:async\s+)?(?:const|let|function|class))\b")


def rel(path: Path) -> str:
    """How a module is named in a problem line: `<dir>/<file>.mjs` - the dir says which kind it is."""
    return f"{path.parent.name}/{path.name}"


def _block_state(line: str, in_block: bool) -> bool:
    """Is the line's END inside a /* block comment */? The same scan the portrait lint uses: a `//`
    outside a block ends the line, and a `/*` or `*/` inside a string literal is not distinguished
    (no module has one - `sync_kinetics --check` is what proves that on every commit)."""
    i = 0
    while i < len(line):
        if in_block:
            j = line.find("*/", i)
            if j < 0:
                return True
            in_block, i = False, j + 2
        else:
            j, k = line.find("/*", i), line.find("//", i)
            if k >= 0 and (j < 0 or k < j):
                return False
            if j < 0:
                return False
            in_block, i = True, j + 2
    return in_block


def inline_text(src: str, indent: str = "  ") -> str:
    """The module as it appears in the engine: no module syntax, indented to the marker.

    Module syntax is stripped only OUTSIDE a block comment. A comment whose continuation line began
    with the word `import` used to be dropped, which left the comment UNCLOSED and swallowed the
    code after it - and did so silently, because the engine still parsed (P50 T2, 2026-09-11:
    the chip's painter registered into nothing and the species painted no pixels)."""
    if re.search(r"^\s*export\s+default\b", src, re.M):
        raise ValueError("export default is not inlinable - name the export")
    out: list[str] = []
    in_block = False
    for line in src.replace("\r\n", "\n").rstrip("\n").split("\n"):
        if not in_block and (re.match(r"^\s*import\b", line) or re.match(r"^\s*export\s*\{", line)):
            in_block = _block_state(line, in_block)
            continue
        if not in_block:
            line = EXPORT_DECL.sub(r"\1\2", line)
        out.append(indent + line if line.strip() else "")
        in_block = _block_state(line, in_block)
    return "\n".join(out)


def module_files(modules: Path = MODULES, species: Path | None = SPECIES_DIR) -> dict[str, Path]:
    """Every module by name across BOTH dirs, kinetics first (the engine's region order).

    One name space on purpose: the region marker carries a bare name, so `kinetics/chip.mjs`
    and `species/chip.mjs` could not both be addressed. ValueError names the collision."""
    out: dict[str, Path] = {}
    for d in (modules, species):
        if d is None or not d.is_dir():
            continue
        for p in sorted(d.glob("*.mjs")):
            if p.stem in out:
                raise ValueError(f"{p.stem}: a module of that name in both {rel(out[p.stem])} and {rel(p)} - "
                                 "kinetics/ and species/ share one name space")
            out[p.stem] = p
    return out


def imports_of(src: str) -> list[str]:
    return IMPORT.findall(src)


def _read(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    return data.decode("utf-8").replace("\r\n", "\n"), b"\r\n" in data


def _write(path: Path, text: str, crlf: bool) -> None:
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def region_text(name: str, indent: str, src: str) -> str:
    return f"{indent}/* KINETICS:BEGIN {name} */\n{inline_text(src, indent)}\n{indent}/* KINETICS:END */"


def check(template: Path = ENGINE, modules: Path = MODULES, species: Path | None = SPECIES_DIR) -> list[str]:
    """Every drift, missing region or missing module, as one entry each. Empty means in sync."""
    html, _ = _read(template)
    try:
        mods = module_files(modules, species)
    except ValueError as exc:
        return [str(exc)]
    problems: list[str] = []
    seen: list[str] = []
    for m in REGION.finditer(html):
        indent, name, _body = m.groups()
        if name in seen:
            problems.append(f"{name}: two regions in the engine")
        seen.append(name)
        if name not in mods:
            problems.append(f"{name}: region in the engine but no kinetics/{name}.mjs or species/{name}.mjs")
            continue
        src = mods[name].read_text(encoding="utf-8")
        for dep in imports_of(src):
            if dep not in seen[:-1]:
                problems.append(f"{name}: imports {dep} but {dep}'s region is not earlier in the engine")
        want = region_text(name, indent, src)
        if m.group(0) != want:
            diff = difflib.unified_diff(m.group(0).split("\n"), want.split("\n"), "template", rel(mods[name]), lineterm="", n=1)
            problems.append(f"{name}: drift\n" + "\n".join(list(diff)[:24]))
    for name, path in mods.items():
        if name not in seen:
            problems.append(f"{name}: {rel(path)} has no region in the engine")
    return problems


def write(template: Path = ENGINE, modules: Path = MODULES, species: Path | None = SPECIES_DIR) -> int:
    """Rewrite every region from its module. Returns the number of regions written."""
    html, crlf = _read(template)
    mods = module_files(modules, species)
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        indent, name, _body = m.groups()
        if name not in mods:
            raise SystemExit(f"{name}: region in the engine but no kinetics/{name}.mjs or species/{name}.mjs")
        count += 1
        return region_text(name, indent, mods[name].read_text(encoding="utf-8"))

    new = REGION.sub(sub, html)
    if new != html:
        _write(template, new, crlf)
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 on drift")
    ap.add_argument("--write", action="store_true", help="rewrite the regions from the modules")
    ap.add_argument("--template", type=Path, default=ENGINE, help="the file the regions live in (the engine)")
    ap.add_argument("--modules", type=Path, default=MODULES)
    ap.add_argument("--species", type=Path, default=SPECIES_DIR, help="the species painters' module dir")
    a = ap.parse_args(argv)
    if a.write:
        n = write(a.template, a.modules, a.species)
        print(f"sync_kinetics: {n} region(s) written into {a.template.name}")
    problems = check(a.template, a.modules, a.species)
    if problems:
        print("sync_kinetics: OUT OF SYNC\n" + "\n".join(problems))
        return 1
    try:
        mods = module_files(a.modules, a.species)
    except ValueError as exc:   # unreachable: check() reports it first
        print(f"sync_kinetics: {exc}")
        return 1
    n_sp = sum(1 for p in mods.values() if a.species is not None and p.parent == a.species)
    print(f"sync_kinetics: in sync ({len(mods)} module(s): {len(mods) - n_sp} kinetics, {n_sp} species)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
