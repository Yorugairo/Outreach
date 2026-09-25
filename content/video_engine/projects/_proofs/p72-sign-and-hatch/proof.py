"""P72 T41 - the balance's sign ink (R26-334) and the prop hatch (R26-335): two candidate sheets, each from ONE source.

    python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py                 # both sheets
    python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py --only pills    # the pill-form sheet
    python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py --only hatch    # the hatch sheet
    python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py --out <dir>     # somewhere else
    python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py --refs <dir>    # the Bravos frames' dir

THE PILLS (P72-HG1 item 6, the operator's pick). The balance's opt-in `tone` draws a side's name as a pill in the
palette's sign ink; its FORM is the module's dial `BALANCE.TONE.FORM` (filled | outline | sans). Every candidate is the
SAME two beats served by the SAME engine with only that dial changed (a private copy per form - the committed engine is
never edited): H row 18's own beat (the two-clocks page, its room, its words - "Both are true at once"; the page authors
no tone, so its tones are ILLUSTRATIVE: MOAT pos, PAPER neg), and Bravos's own beat re-staged on a plain charcoal plate
(THREAT neg, OPPORTUNITY pos, the tip toward OPPORTUNITY, as CHN shots 113 / 114). Today's untoned name is the first row.

THE HATCH (P72-HG1 item 7, the operator's read; NO default changes). T6b's resting hatch (PROP_SHADOW.HATCH) and three
stronger strengths, on the charcoal ledger page and on cream: the golden `prop-stamp` (the Fed stamped on the two-clocks
page, at rest) and the same timeline on a cream plate (test_prop_shadow's `light_ground`). Each candidate is a private
engine copy with the HATCH dials swapped. Each carries its MEASURED contrast: the uncovered shadow (inside the thrown
silhouette, outside the mark) against the bare ground beside it - test_prop_shadow's regions, read on the rendered frame -
as a WCAG ratio of the two regions' mean colours and as mean-luma levels. At 1x (native px) and 3x (nearest).

WRITES ONLY the out dir (default `build-lab-sheets/` beside this file, gitignored by `projects/**/build-lab-*/`).
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))

import build_golden_sources as GS          # noqa: E402
import build_scene_timeline_f as B         # noqa: E402
import render_baseline as RB               # noqa: E402
import series_inks as SI                   # noqa: E402

REFS = HERE / "refs"   # the Bravos frames (BRAVOS-FRAME; never committed, E99 s31) - `--refs <dir>`; the sheet names a missing one
BRAVOS = {"113": "bravos-CHN-1910.8.png", "114": "bravos-CHN-1914.8.png", "shadow": "bravos-CHN-0746.png"}
STOPACTION = REPO / "content/video_engine/scripts/kinetics/stopaction.mjs"
W, H = RB.STAGE["16:9"]

FORMS = ("filled", "outline", "sans")
FORM_RE = re.compile(r'(FORM: )"(?:filled|outline|sans)"(,\s*/\* THE PILL\'S FORM)')

# the hatch's candidates: (name, PITCH_PX, WIDTH_PX, CROSS_PITCH_PX, CROSS_WIDTH_PX, TAPER_PX)
HATCHES = (
    ("A  today (T6b)", 2.25, 0.7, 3.75, 0.5, 3),
    ("B  lines x1.5", 2.25, 1.05, 3.75, 0.75, 3),
    ("C  lines x2", 2.25, 1.4, 3.75, 1.0, 3),
    ("D  lines x2, no taper", 2.25, 1.4, 3.75, 1.0, 0),
)
HATCH_KEYS = ("PITCH_PX", "WIDTH_PX", "CROSS_PITCH_PX", "CROSS_WIDTH_PX", "TAPER_PX")
NL = chr(10)        # a label's line break
BARE_CLEAR_PX = 3   # test_prop_shadow's: the bare ground is read this far clear of either silhouette


# ---- private engines: one dial changed, asserted to be found exactly once ----------------------------------------------


def _engine(td: Path, name: str, edit) -> Path:
    src = RB.ENGINE.read_text(encoding="utf-8")
    out = edit(src)
    p = td / f"engine-{name}.mjs"
    p.write_text(out, encoding="utf-8")
    return p


def form_engine(td: Path, form: str) -> Path:
    def edit(src):
        new, n = FORM_RE.subn(lambda m: f'{m.group(1)}"{form}"{m.group(2)}', src)
        if n != 1:
            raise SystemExit(f"the engine carries the pill's FORM dial {n} times (want 1)")
        return new
    return _engine(td, form, edit)


def hatch_engine(td: Path, i: int, vals: tuple) -> Path:
    def edit(src):
        a = src.index("PROP_SHADOW = Object.freeze({")
        z = src.index("});", a)
        block = src[a:z]
        for key, v in zip(HATCH_KEYS, vals):
            block, n = re.subn(rf"(\b{key}: )[0-9.]+,", lambda m: f"{m.group(1)}{v},", block)
            if n != 1:
                raise SystemExit(f"PROP_SHADOW.HATCH.{key} found {n} times in the engine (want 1)")
        return src[:a] + block + src[z:]
    return _engine(td, f"hatch{i}", edit)


# ---- serving --------------------------------------------------------------------------------------------------------


class Served:
    """One timeline on one engine, mounted as the golden harness mounts it."""

    def __init__(self, browser, td: Path, tag: str, tl: dict, uris: dict, engine: Path):
        html = td / f"{tag}.html"
        html.write_text(RB.instantiate(tl, uris, engine=engine), encoding="utf-8")
        self.srv, port = RB.serve(td)
        self.page = browser.new_context(viewport={"width": W, "height": H}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, W, H)

    def frame(self, t: float):
        from PIL import Image
        return Image.open(io.BytesIO(RB.frame_png(self.page, t, (W, H)))).convert("RGB")

    def close(self):
        self.page.context.close()
        self.srv.shutdown()
        if self.errors:
            raise SystemExit(f"the player threw: {self.errors}")


# ---- the pill sources ------------------------------------------------------------------------------------------------


def h_row18(toned: bool):
    """H row 18's own beat (the golden `balance-level`); toned: MOAT pos, PAPER neg - ILLUSTRATIVE (H authors no tone)."""
    saved = [json.loads(json.dumps(x)) for x in GS.BAL_SPECIES]
    try:
        if toned:
            GS.BAL_SPECIES[0]["left"]["tone"], GS.BAL_SPECIES[0]["right"]["tone"] = "pos", "neg"
        tl, uris = GS.balance_level()
        sp = json.loads(json.dumps(GS.BAL_SPECIES[0]))
    finally:
        GS.BAL_SPECIES[:] = saved
    return tl, uris, sp, GS.FRAME_T["balance-level"]


BRAVOS_T = 11.0   # the tip (9.0) settled


def bravos_beat(toned: bool):
    """Bravos's beat on a plain charcoal plate: THREAT, then OPPORTUNITY, then the tip toward OPPORTUNITY."""
    e = {"kind": "balance", "at": 2.0, "dur": 12.0, "target": {"kind": "region", "x0": 0.2, "y0": 0.18, "x1": 0.8, "y1": 0.86},
         "left": {"label": "THREAT", "at": 3.0}, "right": {"label": "OPPORTUNITY", "at": 5.0}, "tip": {"at": 9.0, "to": "right"}}
    if toned:
        e["left"]["tone"], e["right"]["tone"] = "neg", "pos"
    errs = B.validate_species([json.loads(json.dumps(e))], (0, 0, 0), "plate-plain")
    if errs:
        raise SystemExit(f"the bed refuses: {errs}")
    world = {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, GS.RUNTIME], "docks": [], "species": [e]}]
    return GS._timeline("P72 T41: Bravos's beat", scenes, {}, "16:9"), GS._base_uris(), e, BRAVOS_T


def stamped_like_a_build(tl: dict) -> dict:
    """The caption pages as the compiler's main() stamps them at 16:9 (test_balance_scale's `_stamped_like_a_build`): a
    page a readable species overlaps takes the anchor and reserves the rail - a golden's `_timeline` does not, so its
    caption would stand mid-stage over the scale."""
    pages = tl["caption_pages"]
    out = dict(tl)
    out["caption_pages"] = [{**pg, **({"cap_mode": "anchor", "cap_reserve": "readable-species"}
                                      if B._readable_species_during(tl["scenes"], pg["s"], B._caption_display_end(pages, i))
                                      else {"cap_mode": "stage"})} for i, pg in enumerate(pages)]
    return out


def _foot_box(sp: dict, pad: int = 24) -> tuple[int, int, int, int]:
    f = B.balance_footprint(sp, "16:9")
    return (max(0, int(f["x"]) - pad), max(0, int(f["y"]) - pad),
            min(W, int(f["x"] + f["w"]) + pad), min(H, int(f["y"] + f["h"]) + 4 * pad))   # the caption's rail below, whole


# ---- sheet drawing -----------------------------------------------------------------------------------------------------


def _font(px: int):
    from PIL import ImageFont
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(para: str, font, width: int) -> list[str]:
    """One paragraph broken at spaces so no line is wider than `width` px (a label never runs off its tile)."""
    out, cur = [], ""
    for word in para.split(" "):
        trial = (cur + " " + word) if cur else word
        if cur and font.getlength(trial) > width:
            out.append(cur)
            cur = word
        else:
            cur = trial
    return out + [cur]


def _label(img, text: str, px: int = 26, fill=(20, 20, 20), bg=(250, 250, 250)):
    from PIL import Image, ImageDraw
    f = _font(px)
    lines = [w for para in text.split("\n") for w in _wrap(para, f, img.width - 12)]
    lh = px + 8
    out = Image.new("RGB", (img.width, img.height + lh * len(lines) + 8), bg)
    d = ImageDraw.Draw(out)
    for i, ln in enumerate(lines):
        d.text((6, 4 + i * lh), ln, font=f, fill=fill)
    out.paste(img, (0, lh * len(lines) + 8))
    return out


def _row(tiles: list, gap: int = 16, bg=(250, 250, 250)):
    from PIL import Image
    h = max(t.height for t in tiles)
    out = Image.new("RGB", (sum(t.width for t in tiles) + gap * (len(tiles) - 1), h), bg)
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + gap
    return out


def _stack(rows: list, gap: int = 24, bg=(250, 250, 250), pad: int = 24):
    from PIL import Image
    w = max(r.width for r in rows) + 2 * pad
    out = Image.new("RGB", (w, sum(r.height for r in rows) + gap * (len(rows) - 1) + 2 * pad), bg)
    y = pad
    for r in rows:
        out.paste(r, (pad, y))
        y += r.height + gap
    return out


def _ref(name: str, scale: float):
    from PIL import Image
    p = REFS / BRAVOS[name]
    if not p.is_file():
        im = Image.new("RGB", (int(1280 * scale), int(720 * scale)), (60, 60, 60))
        return _label(im, f"(missing: refs/{BRAVOS[name]})")
    im = Image.open(p).convert("RGB")
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


# ---- the pill sheet -----------------------------------------------------------------------------------------------------


def pill_sheet(out: Path) -> Path:
    from PIL import Image
    from playwright.sync_api import sync_playwright
    rows, reads = [], []
    with tempfile.TemporaryDirectory() as tds, sync_playwright() as pw:
        td = Path(tds)
        br = pw.chromium.launch(headless=True)
        variants = [("today - no tone (the default, unchanged)", None)] + [(f"form: {f}", f) for f in FORMS]
        for title, form in variants:
            eng = form_engine(td, form) if form else RB.ENGINE
            tiles = []
            for which, src in (("H row 18 (tones illustrative)", h_row18), ("Bravos's beat, re-staged", bravos_beat)):
                tl, uris, sp, t = src(form is not None)
                tl = stamped_like_a_build(tl)
                s = Served(br, td, f"{form or 'none'}-{which[:5].strip()}", tl, uris, eng)
                im = s.frame(t)
                s.close()
                im.save(out / f"pill-{form or 'none'}-{'h18' if which.startswith('H') else 'bravos'}.png")
                crop = im.crop(_foot_box(sp))
                whole = im.resize((W // 3, H // 3), Image.LANCZOS)
                tiles += [_label(whole, f"{which}\nwhole frame, 1/3 scale"), _label(crop, f"{which}\n1x crop (native px)")]
                reads.append({"form": form, "beat": which, "t": t})
            rows.append(_label(_row(tiles), title.upper(), px=34))
        br.close()
    head = _row([_label(_ref("113", 0.6), "Bravos CHN shot 113 (19:10.8)"), _label(_ref("114", 0.6), "Bravos CHN shot 114 (19:14.8)")])
    q = ("QUESTION: which pill form should a toned balance side wear -\nfilled (our hand), outline (the inked name), "
         "or sans (Bravos's own face)?")
    sheet = _stack([_label(head, "R26-334 - A BALANCE SIDE'S SIGN INK: THE PILL FORMS (P72-HG1 item 6)\n" + q, px=34)] + rows)
    p = out / "sheet-r26-334-pill-forms.png"
    sheet.save(p)
    (out / "pill-reads.json").write_text(json.dumps(reads, indent=1), encoding="utf-8")
    return p


# ---- the hatch sheet ----------------------------------------------------------------------------------------------------


def _throw() -> tuple[float, float]:
    src = f"const s = await import({json.dumps(STOPACTION.as_uri())}); console.log(JSON.stringify(s.PROP_SHADOW));"
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60, check=True)
    ps = json.loads(r.stdout)
    th = math.radians(ps["LIGHT_DEG"] + 180)
    return ps["OFFSET_PX"] * math.cos(th), ps["OFFSET_PX"] * math.sin(th)


def _measure(served: Served, t: float, throw) -> dict:
    """The uncovered shadow against the bare ground beside it, on the rendered frame (test_prop_shadow's regions)."""
    import numpy as np
    import test_prop_shadow as TPS   # its PLANES probe: the hatch canvas's grid, the silhouette thrown and not
    from PIL import Image, ImageFilter
    img = served.frame(t)
    pl = TPS._planes(served.page, throw)
    rgb = np.asarray(img, dtype=float)
    bx, by = int(pl["bx"]), int(pl["by"])
    reg = rgb[by:by + pl["H"], bx:bx + pl["W"]]
    free = (pl["thrown"] == 255) & (pl["own"] == 0)
    either = Image.fromarray(np.maximum(pl["thrown"], pl["own"]))
    bare = ~(np.asarray(either.filter(ImageFilter.MaxFilter(2 * BARE_CLEAR_PX + 1))) > 0)
    sh, bg = reg[free].mean(axis=0), reg[bare].mean(axis=0)
    hexc = lambda c: "#" + "".join(f"{int(round(v)):02X}" for v in c)   # noqa: E731
    luma = lambda c: float(c @ np.array([0.2126, 0.7152, 0.0722]))       # noqa: E731
    ys, xs = np.nonzero(free)
    k = int(np.argmax(xs + ys))   # the shadow's far corner, down the light's fall
    return {"img": img, "box": (bx, by, bx + pl["W"], by + pl["H"]), "corner": (bx + int(xs[k]), by + int(ys[k])),
            "shadow": hexc(sh), "bare": hexc(bg), "ratio": round(SI.contrast(hexc(sh), hexc(bg)), 3),
            "levels": round(luma(bg) - luma(sh), 1), "n_shadow": int(free.sum()), "n_bare": int(bare.sum())}


def _zoom(img, corner, half: int = 60, k: int = 3):
    """A (2 half)^2 window centred on `corner` (the shadow's far corner: the mark, its hatch and the bare ground), at k x."""
    from PIL import Image
    cx, cy = corner
    c = img.crop((cx - half, cy - half, cx + half, cy + half))
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


def _hatch_row(br, td: Path, i: int, cand: tuple, sources: list, t: float, throw, out: Path, reads: list):
    """One candidate: its engine, both grounds served at rest, each measured, cropped at 1x and zoomed at 3x."""
    name, *vals = cand
    eng = hatch_engine(td, i, tuple(vals))
    tiles, caps = [], []
    for ground, tl, uris in sources:
        s = Served(br, td, f"h{i}-{ground[:5]}", copy.deepcopy(tl), dict(uris), eng)
        m = _measure(s, t, throw)
        s.close()
        m["img"].save(out / f"hatch-{i}-{ground.split()[0]}.png")
        x0, y0, x1, y1 = m["box"]
        one = m["img"].crop((x0 - 20, y0 - 20, x1 + 20, y1 + 20))
        caps.append(f"{ground}: shadow {m['shadow']} on ground {m['bare']} = {m['ratio']:.2f}:1, {-m['levels']:+.1f} luma")
        tiles += [_label(one, f"{ground}, 1x", px=22), _label(_zoom(m["img"], m["corner"]), f"{ground}, 3x (nearest)", px=22)]
        reads.append({"candidate": name, "ground": ground, **{k: v for k, v in m.items() if k != "img"}})
    pitch, width, cpitch, cwidth, taper = vals
    title = f"{name}  -  lines {width} / {cwidth} px at pitch {pitch} / {cpitch} px, taper {taper} px"
    return _label(_row(tiles), title + NL + "MEASURED  " + "   |   ".join(caps), px=28)


def hatch_sheet(out: Path) -> Path:
    import test_prop_shadow as TPS
    from playwright.sync_api import sync_playwright
    throw = _throw()
    tl_c, uris_c, _t, _a = RB.load_surface("prop-stamp")
    tl_l, uris_l = TPS.light_ground()
    sources = [("charcoal page", tl_c, uris_c), ("cream plate", tl_l, uris_l)]
    rows, reads = [], []
    with tempfile.TemporaryDirectory() as tds, sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        for i, cand in enumerate(HATCHES):
            rows.append(_hatch_row(br, Path(tds), i, cand, sources, TPS.T_REST, throw, out, reads))
        br.close()
    ref = bravos_shadow()
    head = _label(_row([_label(ref["one"], "Bravos CHN 07:46 (shot 051), 1x of its 720p frame - a SOFT drop shadow, no hatch", px=22),
                        _label(ref["zoom"], "... under the platform's edge, 3x (nearest)", px=22)]), "MEASURED  " + ref["cap"], px=26)
    q = ("QUESTION: on the charcoal page, does today's hatch (A) read as the prop's weight," + NL
         + "or should a stronger strength (B, C or D) replace it for every prop, after HG3?")
    title = "R26-335 - THE PROP'S RESTING HATCH: FOUR STRENGTHS (P72-HG1 item 7) - no default changed" + NL + q
    sheet = _stack([_label(head, title, px=34)] + rows)
    p = out / "sheet-r26-335-hatch-strengths.png"
    sheet.save(p)
    reads.append({"candidate": "Bravos CHN 07:46", **{k: v for k, v in ref.items() if k not in ("one", "zoom")}})
    (out / "hatch-reads.json").write_text(json.dumps(reads, indent=1), encoding="utf-8")
    return p


# Bravos's resting shadow, CHN 07:46 (1280x720): the silos' platform, a SOFT drop shadow down-right on the charcoal ground.
# Its deepest band sits just under the platform's lower-right edge (luma ~8 at x 850, y 546) and fades to the bare ground
# (~23.6) over ~100 px - read off the frame (scratchpad/p72-t41/NOTES.md). The boxes are in the 720p frame's px.
BRAVOS_SHADOW_BOX, BRAVOS_BARE_BOX, BRAVOS_CROP = (840, 545, 860, 565), (1100, 640, 1130, 670), (270, 150, 1180, 700)


def bravos_shadow() -> dict:
    import numpy as np
    from PIL import Image
    p = REFS / BRAVOS["shadow"]
    if not p.is_file():
        blank = Image.new("RGB", (400, 300), (60, 60, 60))
        return {"one": blank, "zoom": blank, "cap": f"(missing: refs/{BRAVOS['shadow']})"}
    im = Image.open(p).convert("RGB")
    a = np.asarray(im, dtype=float)
    mean = lambda b: a[b[1]:b[3], b[0]:b[2]].reshape(-1, 3).mean(axis=0)   # noqa: E731
    hexc = lambda c: "#" + "".join(f"{int(round(v)):02X}" for v in c)     # noqa: E731
    luma = lambda c: float(c @ np.array([0.2126, 0.7152, 0.0722]))       # noqa: E731
    ms, mb = mean(BRAVOS_SHADOW_BOX), mean(BRAVOS_BARE_BOX)
    sh, bg, lv = hexc(ms), hexc(mb), round(luma(ms) - luma(mb), 1)
    cap = (f"Bravos: its deepest shadow {sh} on ground {bg} = {SI.contrast(sh, bg):.2f}:1, {lv:+.1f} luma "
           f"(boxes {BRAVOS_SHADOW_BOX} / {BRAVOS_BARE_BOX}, 720p px)")
    return {"one": im.crop(BRAVOS_CROP), "zoom": _zoom(im, (870, 590)), "cap": cap,
            "shadow": sh, "bare": bg, "ratio": round(SI.contrast(sh, bg), 3), "levels": lv}


def main(argv=None) -> int:
    global REFS
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=HERE / "build-lab-sheets")
    ap.add_argument("--only", choices=("pills", "hatch"))
    ap.add_argument("--refs", type=Path, default=REFS, help="the dir holding the Bravos frames (BRAVOS)")
    a = ap.parse_args(argv)
    REFS = a.refs
    a.out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(REPO / "content/video_engine/tests"))
    if a.only in (None, "pills"):
        print(f"pills: {pill_sheet(a.out)}")
    if a.only in (None, "hatch"):
        print(f"hatch: {hatch_sheet(a.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
