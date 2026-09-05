"""G-d - unanchored transform lint (P37 T3). Reports every `scale(` / `rotate(` in the player
template that is applied without an explicit transform origin. INFO on first landing (the
M08 ladder): the template is 2000 lines and the first pass surfaces unknowns, so nothing
blocks yet - the list is the deliverable.

    python lint_template_transforms.py docs/content-video-engine/samples/scene-evidence-player.template.html

Why it matters (42 s42.3 / 43 s43.3): a scale or rotate anchored at the default 50% 50%
grows a figure out of its own centre - feet leave the floor, a card breathes from the
middle instead of its base. The anchor is part of the motion, not a detail.

Two readers:
  CSS  - a rule whose `transform` scales or rotates is anchored if the same rule, or another
         rule for the same selector, declares `transform-origin`
  JS   - an assignment `.style.transform = ...scale(` / `setAttribute("transform", ...rotate(`
         is anchored if `transformOrigin` / `transform-origin` appears within the preceding
         LOOKBACK lines, or the element's id/class has a CSS transform-origin
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LOOKBACK = 40
XFORM = re.compile(r"\b(scale|rotate|scaleX|scaleY)\(")
SRC_G_D = "47 s2 G-d / 42 s42.3, 43 s43.3: a transform without a declared origin animates around the wrong point"


@dataclass(frozen=True)
class Finding:
    where: str      # css:<selector> | js:<line no>
    detail: str

    def line(self) -> str:
        return f"INFO G-d {self.where}: {self.detail}"


def _css_rules(html: str) -> list[tuple[str, str]]:
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    styles = re.sub(r"/\*.*?\*/", "", styles, flags=re.S)
    return [(sel.strip(), body) for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", styles)]


def _names(selector: str) -> set[str]:
    return set(re.findall(r"[#.]([\w-]+)", selector))


def check_css(html: str) -> list[Finding]:
    rules = _css_rules(html)
    # a state rule (#card.on) inherits the origin its base (#card) declares
    anchored: set[str] = set()
    for sel, body in rules:
        if "transform-origin" in body:
            anchored |= _names(sel)
    out = []
    for sel, body in rules:
        if "transform:" in body and XFORM.search(body) and "transform-origin" not in body and not (_names(sel) & anchored):
            out.append(Finding(f"css:{sel}", f"{XFORM.search(body).group(0)}...) with no transform-origin on this rule or its selector"))
    return out


def _css_origin_names(html: str) -> set[str]:
    names = set()
    for sel, body in _css_rules(html):
        if "transform-origin" in body:
            names.update(re.findall(r"[#.]([\w-]+)", sel))
    return names


def check_js(html: str) -> list[Finding]:
    out = []
    lines = html.splitlines()
    anchored_names = _css_origin_names(html)
    for i, ln in enumerate(lines):
        if not ((".style.transform" in ln or 'setAttribute("transform"' in ln) and XFORM.search(ln)):
            continue
        window = "\n".join(lines[max(0, i - LOOKBACK): i + 1])
        # the origin must be set on the SAME receiver: other.style.transform needs other.style.transformOrigin
        m = re.search(r"([\w.$]+?)\.style\.transform\s*[=+]", ln)
        recv = m.group(1) if m else None
        if recv and f"{recv}.style.transformOrigin" in window:
            continue
        if not recv and ("transformOrigin" in window or "transform-origin" in window):
            continue
        if any(name in ln for name in anchored_names):
            continue
        out.append(Finding(f"js:{i + 1}", f"{XFORM.search(ln).group(0)}...) with no transformOrigin within {LOOKBACK} lines: {ln.strip()[:90]}"))
    return out


def check(html: str) -> list[Finding]:
    return check_css(html) + check_js(html)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    args = ap.parse_args()
    findings = check(Path(args.template).read_text(encoding="utf-8"))
    for f in findings:
        print(f.line())
    print(f"VERDICT: INFO ({len(findings)} unanchored transform{'s' if len(findings) != 1 else ''}) - {args.template}\n     {SRC_G_D}")
    return 0   # the ladder: INFO until the list is worked, then this becomes FAIL


if __name__ == "__main__":
    sys.exit(main())
