"""Inline the kinetics modules into the scene-evidence player (P43 T1; P38 T1's design).

Two things must both hold: the template opens STANDALONE (no runtime imports - the player is
one file), and the math is reachable by `node --test`. Both do when each `.mjs` module under
content/video_engine/scripts/kinetics/ is the source of truth and its text is physically copied
into the template between markers:

    /* KINETICS:BEGIN <name> */
    ...the module, export/import syntax stripped, indented to the marker...
    /* KINETICS:END */

    python sync_kinetics.py --check    # exit 1 when any inlined copy drifts from its module
    python sync_kinetics.py --write    # rewrite every region from its module

Rules: `export const|let|function|class` loses the `export`; `import` lines and `export {...}`
lists are dropped; `export default` is refused. A module may import another kinetics module only
when that module's region sits EARLIER in the template - the inlined copy has no imports, so
order is the dependency. Every module has exactly one region and every region one module.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
MODULES = REPO / "content/video_engine/scripts/kinetics"

REGION = re.compile(r"^([ \t]*)/\* KINETICS:BEGIN (\w+) \*/\n(.*?)^[ \t]*/\* KINETICS:END \*/", re.M | re.S)
IMPORT = re.compile(r"^\s*import\b.*?\bfrom\s+[\"']\./(\w+)\.mjs[\"'];?\s*$", re.M)
EXPORT_DECL = re.compile(r"^(\s*)export\s+(const|let|function|class)\b")


def inline_text(src: str, indent: str = "  ") -> str:
    """The module as it appears in the template: no module syntax, indented to the marker."""
    if re.search(r"^\s*export\s+default\b", src, re.M):
        raise ValueError("export default is not inlinable - name the export")
    out: list[str] = []
    for line in src.replace("\r\n", "\n").rstrip("\n").split("\n"):
        if re.match(r"^\s*import\b", line) or re.match(r"^\s*export\s*\{", line):
            continue
        line = EXPORT_DECL.sub(r"\1\2", line)
        out.append(indent + line if line.strip() else "")
    return "\n".join(out)


def module_files(modules: Path = MODULES) -> dict[str, Path]:
    return {p.stem: p for p in sorted(modules.glob("*.mjs"))}


def imports_of(src: str) -> list[str]:
    return IMPORT.findall(src)


def _read(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    return data.decode("utf-8").replace("\r\n", "\n"), b"\r\n" in data


def _write(path: Path, text: str, crlf: bool) -> None:
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def region_text(name: str, indent: str, src: str) -> str:
    return f"{indent}/* KINETICS:BEGIN {name} */\n{inline_text(src, indent)}\n{indent}/* KINETICS:END */"


def check(template: Path = TEMPLATE, modules: Path = MODULES) -> list[str]:
    """Every drift, missing region or missing module, as one entry each. Empty means in sync."""
    html, _ = _read(template)
    mods = module_files(modules)
    problems: list[str] = []
    seen: list[str] = []
    for m in REGION.finditer(html):
        indent, name, _body = m.groups()
        if name in seen:
            problems.append(f"{name}: two regions in the template")
        seen.append(name)
        if name not in mods:
            problems.append(f"{name}: region in the template but no kinetics/{name}.mjs")
            continue
        src = mods[name].read_text(encoding="utf-8")
        for dep in imports_of(src):
            if dep not in seen[:-1]:
                problems.append(f"{name}: imports {dep} but {dep}'s region is not earlier in the template")
        want = region_text(name, indent, src)
        if m.group(0) != want:
            diff = difflib.unified_diff(m.group(0).split("\n"), want.split("\n"), "template", f"kinetics/{name}.mjs", lineterm="", n=1)
            problems.append(f"{name}: drift\n" + "\n".join(list(diff)[:24]))
    for name in mods:
        if name not in seen:
            problems.append(f"{name}: kinetics/{name}.mjs has no region in the template")
    return problems


def write(template: Path = TEMPLATE, modules: Path = MODULES) -> int:
    """Rewrite every region from its module. Returns the number of regions written."""
    html, crlf = _read(template)
    mods = module_files(modules)
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        indent, name, _body = m.groups()
        if name not in mods:
            raise SystemExit(f"{name}: region in the template but no kinetics/{name}.mjs")
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
    ap.add_argument("--template", type=Path, default=TEMPLATE)
    ap.add_argument("--modules", type=Path, default=MODULES)
    a = ap.parse_args(argv)
    if a.write:
        n = write(a.template, a.modules)
        print(f"sync_kinetics: {n} region(s) written into {a.template.name}")
    problems = check(a.template, a.modules)
    if problems:
        print("sync_kinetics: OUT OF SYNC\n" + "\n".join(problems))
        return 1
    print(f"sync_kinetics: in sync ({len(module_files(a.modules))} module(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
