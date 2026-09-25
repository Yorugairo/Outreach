"""A series' NAME wears its series' INK - and an ink too faint for text on its page's ground WARNs (P69 T37b, E99 s118).

The operator, on the solo sheet: "we use plain white text which is pretty low visibility"; offered the record's two
conflicts, he chose SERIES-INKED LABELS - every end tag, series name and series figure in its own line's ink, the way
Bravos colours its legend. The ink is E67's palette, so its contrast on the charcoal is the palette's (TEAL 9.5:1) - but
a name is TEXT, and text owes the text tier's floor (docs/portable/BUILD-PIPELINE.md:307, "Text on a dark pill needs
4.5:1"). A series whose ink falls under it on its page's ground (the lone falling series in `--lp-neg` reads 4.06:1 on
the charcoal) is REPORTED with its ratio: a WARN, never a refusal (E99 s106 - the frame read decides).

Nothing here is re-typed: the inks are read off the engine's own `LP_INK` / `LP_CYCLE` and the grounds and sign colours
off the template, the way test_field_ink_e67 reads them. The engine's colour rule is mirrored exactly
(`buildLedgerLine`): a declared token keeps its ink; an undeclared LONE series takes its sign (a fall `--lp-neg`, a
rise `--lp-pos`); an undeclared series on a multi-series page takes the cycle by its index. The WARN is printed by the
compiler and never stored on the page, so a page's compiled bytes do not move with it.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
TEXT_FLOOR = 4.5            # BUILD-PIPELINE.md:307 - the TEXT tier (a name is text, not a line)
LONGFORM = "longform"
WARN = "WARN ink:"
INKED_BUILDERS = ("dense-line", "combo")   # the builders whose end tags are written in their line's ink


@functools.lru_cache(maxsize=1)
def palette() -> dict:
    """The engine's LP_INK and LP_CYCLE, and the template's sign colours and the two grounds."""
    src = ENGINE.read_text(encoding="utf-8")
    ink_m = re.search(r"const LP_INK = \{([^}]*)\};", src)
    cyc_m = re.search(r"const LP_CYCLE = \[([^\]]*)\];", src)
    if not ink_m or not cyc_m:
        raise ValueError(f"{ENGINE}: LP_INK / LP_CYCLE are not declared where series_inks reads them")
    ink = dict(re.findall(r"(\w+)\s*:\s*\"(#[0-9A-Fa-f]{6})\"", ink_m.group(1)))
    cycle = re.findall(r"\"(\w+)\"", cyc_m.group(1))
    css = TEMPLATE.read_text(encoding="utf-8")
    var = {}
    for k, v in re.findall(r"--(lp-pos|lp-neg|lp-char):\s*(#[0-9A-Fa-f]{6})", css):
        var.setdefault(k, v)   # the page's own declaration (.lp) comes first; a later surface rule is not the ground
    lf = re.search(r"\.lp-page\.lp-readability-longform \{ background: (#[0-9A-Fa-f]{6}); \}", css)
    if not ({"lp-pos", "lp-neg", "lp-char"} <= set(var)) or not lf:
        raise ValueError(f"{TEMPLATE}: the sign colours or the two grounds moved")
    return {"ink": ink, "cycle": cycle, "pos": var["lp-pos"], "neg": var["lp-neg"],
            "ground": {"page": var["lp-char"], LONGFORM: lf.group(1)}}


def _lum(hx: str) -> float:
    h = hx.lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _ends_down(pts) -> bool:
    try:
        return len(pts) > 1 and float(pts[-1][1]) < float(pts[0][1])
    except (TypeError, ValueError, IndexError):
        return False


def series_ink(series: list, i: int) -> tuple[str, str]:
    """The hex the engine draws series i in, and the token (or sign) it came from."""
    pal, s = palette(), series[i]
    tok = s.get("color")
    if tok in pal["ink"]:
        return pal["ink"][tok], str(tok)
    if len(series) == 1:
        return (pal["neg"], "--lp-neg") if _ends_down(s.get("pts") or []) else (pal["pos"], "--lp-pos")
    tok = pal["cycle"][i % len(pal["cycle"])]
    return pal["ink"][tok], tok


def ground_of(page: dict) -> str:
    axes = page.get("axes") or {}
    ro = axes.get("readability") or page.get("readability")
    return palette()["ground"][LONGFORM if isinstance(ro, str) and ro.split(":")[0] == LONGFORM else "page"]


def ink_contrast_warnings(page: dict) -> list[str]:
    """One `WARN ink:` line per named series whose ink reads under the text floor on the page's ground."""
    if page.get("builder") not in INKED_BUILDERS or page.get("surface_from"):
        return []
    series = [s for s in (page.get("series") or []) if isinstance(s, dict)]
    ground, out = ground_of(page), []
    for i, s in enumerate(series):
        name = " ".join(str(v) for v in (s.get("label"), s.get("name")) if v)
        if not name:
            continue
        hx, tok = series_ink(series, i)
        ratio = contrast(hx, ground)
        if ratio < TEXT_FLOOR:
            out.append(f"{WARN} series {i} {name!r} is named in {tok} {hx} at {ratio:.2f}:1 on the ground {ground} - "
                       f"under the text floor {TEXT_FLOOR}:1 (BUILD-PIPELINE.md:307). REPORTED, the frame read decides "
                       "(E99 s106): declare a brighter token, or keep the name short beside the line")
    return out
